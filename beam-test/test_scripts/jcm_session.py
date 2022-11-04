#!/usr/bin/env python3



import argparse
import logging
import traceback
import re
import os
import random
import threading
import sys

from paramiko import SSHClient, SSHException, AutoAddPolicy, \
                    BadHostKeyException, AuthenticationException, buffered_pipe


class jcm_session():
    '''
    Represents a session on the JCM. This class is used to simplify the operation
    and control of the JCM.

    ssh_client: if None, there is no ssh_client open. If not None, represents the ssh_client.
    jcm_ip_addr: IP address of the JCM (string)
    logging: The logger used by the session messages
    jtag_clock: Clock rate for JTAG operations
    stdout: the output file handle (default is sys.stdout)
    stdout_prefix: the prefix string for lines going to stdout
    username: username for ssh connection
    password: password for ssh connection
    '''

    # JCM constants
    JCM_CONNECTION_TIMEOUT = 30 # Max amount of time to try to connect to JCM
    JCM_LOGIN_ATTEMPTS = 5
    JCM_DEFAULT_CLOCK_RATE = 10_000_000

    def __init__(self, jcm_ip_addr:str, logging, part,
        jtag_clock = JCM_DEFAULT_CLOCK_RATE, 
        stdout = sys.stdout,
        stdout_prefix = "",
        username='root', password='chrec') -> None:

        self.ssh_client = None
        self.jcm_ip_addr = jcm_ip_addr
        self.logging = logging
        self.part = part
        self.jtag_clock = jtag_clock
        self.stdout = stdout
        self.stdout_prefix = stdout_prefix
        self.username = username
        self.password = password

        self.scrubbing_active = False
        self.stop_scrubbing_flag = False

    def close_jcm(self):
        ''' Closes JCM SSH session'''
        if self.ssh_client:
            self.ssh_client.close()
            self.logging.info("JCM SSH closed")
        else:
            self.logging.info("JCM SSH session not open - cannot close")

    def open_jcm(self):
        ''' Opens a JCM SSH session '''
        self.logging.info("Logging in to JCM")
        login_success = False
        for i in range(self.JCM_LOGIN_ATTEMPTS):
            try:
                new_client = SSHClient()
                new_client.load_system_host_keys()
                new_client.set_missing_host_key_policy(AutoAddPolicy())
                self.logging.info("Connecting to JCM over SSH... (Attempt {})", (i+1))
                new_client.connect(self.jcm_ip_addr, username=self.username, password=self.password, 
                    timeout=self.JCM_CONNECTION_TIMEOUT)
                self.logging.info("SSH successful!")
                login_success = True
                break
            except (BadHostKeyException, AuthenticationException,
                SSHException, socket.error, buffered_pipe.PipeTimeout, socket.timeout) as error:
                self.logging.error(error)
                new_client.close()
                new_client = None
        return login_success

    def _print_std_out(self, line):
        ''' Print line to std_out '''
        print((self.stdout_prefix + line), file=self.stdout)

    def is_scrubbing(self):
        ''' Indicates whether the JCM is scrubbing '''
        return self.scrubbing_active

    def stop_scrubbing(self):
        ''' Set flag to halt scrubbing '''
        self.stop_scrubbing_flag = True

    # Configure the FPGA using jcm_config.elf
    def configure_fpga(self, bitstream_filename):

        if not self.ssh_client:
            self.logging.error("Cannot perform configuration: no ssh client")
            return False

        self.logging.info("Sending config command to JCM")

        # Default configuration command
        CONFIGURATION_COMMAND = "~/jcm_apps/jcm_config.elf --part {part} -c {clock_rate} --jtag --config_file {bitstream}"

        config_command = CONFIGURATION_COMMAND.format(part=self.part, clock = self.jtag_clock, bitstream=bitstream_filename)
        self.logging.info(config_command)

        # Configuration command
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(config_command,timeout=self.JCM_CONNECTION_TIMEOUT)
        except SSHException as error:
            self.logging.error(error)
            self.logging.error("SSHException: Timeout occured or execution failed.")
            return False

        # Iterate over the output until the program executes
        configure_success = False
        while not stdout.channel.exit_status_ready():
            try:
                line = stdout.readline()
                # Copy line to output
                self._print_std_out(line)

                # Success message?
                if "Success" in line:
                    configure_success = True
            
            except(buffered_pipe.PipeTimeout, socket.timeout) as error:
                self.logging.error(error)
                return False
        if not configure_success:
            self.logging.error("Configuration Failed")
            return False

        # Configure was successful
        return True

    # Spawn a thread to perform JCM scrubbing. inject_faults indicates the number of faults to inject per scrub
    # Note that the JCM login session has already been established
    def spawn_jcm_scrubbing(self, iterations, frads_file = None, readback_file = None, inject_faults=0):

        if not self.ssh_client:
            self.logging.error("Cannot perform scrubbing: no ssh client")
            return False

        if self.is_scrubbing():
            self.logging.error("Scrubbing already started: cannot start another scrubbing")
            return False

        # Prepare flag for being stopped externally
        self.stop_scrubbing_flag = False

        self.logging.info("Starting JCM scrubber")
        
        # Scrubbing and fault injection commands
        SCRUBBING_COMMAND = "~/jcm_apps/jcm_scrubbing.elf --part {part} -c {clock} --jtag --interations {iterations}"
        command = SCRUBBING_COMMAND.format(part=self.part, clock=self.jtag_clock, iterations=iterations)
        if frads_file:
            command += f" --frad_file {frads_file}"
        if readback_file:
            command += f" --readback_file {readback_file}"
        if inject_faults > 0:
            command += f" --inject_fault {inject_faults}"

        self.logging.info("scrubbing command:" + command)

        # attempt to execute command
        try:
            self.scrub_stdin, self.scrub_stdout, self.scrub_stderr = self.ssh_client.exec_command(command,timeout=self.JCM_CONNECTION_TIMEOUT)
        except SSHException as error:
            self.logging.error("scrubbing error:" + error)
            return False

        # At this point the scrubbing command started successfully and is running
        self.scrubbing_active = True

        # Spawn scrubbing thread
        self.scrubbing_thread = threading.Thread(target=self._scrubbing_thread, args=())
        self.scrubbing_thread.start()

        # Scrubbing started and the thread is going
        return True

    def _scrubbing_thread(self):
        ''' Thread function for scrubber. This thread will exit when the scrubbing process
        ends or when the external flag stops the process
        '''

        # Iterate over the lines until the process ends
        while not self.scrub_stdout.channel.exit_status_ready():
            
            if self.stop_scrubbing_flag:
                # Send a Ctrl-C to the scrubber or kill scrubber directly
                self.scrub_stdin.shutdown(2)
                #self.scrub_stdout.shutdown(2)
                # This should cause the exit_status_ready() to return false

            # See if the flag has been set to stop the scrubbing
            try:
                line = self.scrub_stdout.readline()
                self._print_std_out(line)

                # TODO: We may want to parse the JCM scrubber so that we detect SEFIs or scrubbing anomolise

            except(buffered_pipe.PipeTimeout, socket.timeout) as error:
                self.logging.error("Scrubbing: ",error)
        
        # Scrubbing done: reset flag
        self.scrubbing_active = False
        return

    def jcm_group_args(parser):
        ''' Static function for creating JCM argument group '''
        jcm_arg_group = parser.add_argument_group("JCM")
        jcm_arg_group.add_argument("--jcm_ip", help="JCM IP Address", required=True)
        jcm_arg_group.add_argument("--jcm_part", help="JCM Part Name", required=True)
        jcm_arg_group.add_argument("--jcm_clock", help="JCM Clock Rate", type=int, default = 10_000_000)

    def create_jcm_from_args(args):
        ''' Static function for creating JCM argument group '''
        jcm_ip = args.jcm_ip
        jcm_part = args.jcm_part
        jcm_clock = args.jcm_clock

        jcm = jcm_session(args.jcm_ip)

        pass

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--jcm_ip", help="JCM IP Address", required=True)
    args = parser.parse_args()

    jcm = jcm_session(args.jcm_ip)
    def __init__(self, jcm_ip_addr:str, logging, part,
        jtag_clock = JCM_DEFAULT_CLOCK_RATE, 
        stdout = sys.stdout,
        stdout_prefix = "",
        username='root', password='chrec') -> None:

    parser.add_argument("--netbooter-port", help="netbooter outlet number that the FPGA is connected to", 
        default=NETBOOTER_PORT, type=int, required=False)
    parser.add_argument("--mem-burst-length", help="Bist memory burst length", default=BURST_LENGTH, type=int, required=False)
    parser.add_argument("--addr-mode", help="Address mode, how Bist should read and write memory: 0=fixed, 1=linear, 2=random", default=RAND_ARG, type=int, required=False)

    # Set up logger settings
    logging.basicConfig(filename="times_20.txt", level=logging.INFO, datefmt=TIME_STRING_FORMAT, 
        format='%(asctime)s %(levelname)-8s %(message)s')
    
    experiment = build_experiment()
    experiment.start()
    print(f"Experiment finished in state: {experiment.get_current_state()}")


if __name__ == "__main__":
    main()

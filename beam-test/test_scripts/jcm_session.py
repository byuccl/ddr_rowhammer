#!/usr/bin/env python3



import argparse
import logging
import traceback
import re
import os
import random
import threading
import sys
import time
import subprocess

class jcm_session():
    '''
    Represents a session on the JCM. This class is used to simplify the operation
    and control of the JCM.

    ssh_client: if None, there is no ssh_client open. If not None, represents the open jcm ssh_client.
    jcm_ip_addr: IP address of the JCM (string)
    logging: The logger used by the session messages
    jtag_clock: Clock rate for JTAG operations
    jcm_print: Print function for JCM output (takes arguments of str)
    username: username for ssh connection
    password: password for ssh connection
    '''

    # JCM constants
    JCM_CONNECTION_TIMEOUT = 30 # Max amount of time to try to connect to JCM
    JCM_LOGIN_ATTEMPTS = 5
    JCM_DEFAULT_CLOCK_RATE = 10_000_000

    #def _default_jcm_print(str):
    #    ''' Default function for printing JCM output. This can be overriden in the constructor. '''
    #    print(str, end="")

    def __init__(self, 
        jcm_ip_addr:str, 
        part, 
        jtag_clock = JCM_DEFAULT_CLOCK_RATE, 
        status_logging = None,
        stdout_logging = None,
        username='root', password='chrec') -> None:

        self.ssh_client = None
        self.jcm_ip_addr = jcm_ip_addr
        self.logging = logging
        self.part = part
        self.jtag_clock = jtag_clock
        self.status_logging = status_logging,
        self.std_logging = stdout_logging,
        self.username = username
        self.password = password
        # references to the I/O of the JCM commands
        self.jcm_stdin = None
        self.jcm_stdout = None
        self.jcm_stderr = None
        # Thread object for executing JCM thread
        self.jcm_thread = None

        # Flag indicating the jcm execution thread is active
        self.jcm_active = False
        # Flag instructing the jcm execution thread to stop
        self.halt_jcm_flag = False


    def _info(self, str):
        ''' Send an 'info' message to the logger. '''
        if self.status_logging:
            self.logging.info(str)

    def _error(self, str):
        ''' Send an 'error' message to the logger. '''
        if self.status_logging:
            self.logging.error(str)

    def _print_std_out(self, line):
        ''' Print JCM standard output '''
        if self.stdout_logging:
            self.stdout_logging.into(line)

    def close_jcm(self):
        ''' Closes JCM SSH session'''
        if self.ssh_client:
            self.ssh_client.close()
            self._info("JCM SSH closed")
        else:
            self._info("JCM SSH session not open - cannot close")

    def open_jcm(self):
        ''' Opens a JCM SSH session.
        returns True if session is successfully open, False otherwise
        '''
        self._info("Logging in to JCM")
        login_success = False
        for i in range(self.JCM_LOGIN_ATTEMPTS):
            try:
                new_client = SSHClient()
                new_client.load_system_host_keys()
                new_client.set_missing_host_key_policy(AutoAddPolicy())
                self._info("Connecting to JCM over SSH... (Attempt {})", (i+1))
                new_client.connect(self.jcm_ip_addr, username=self.username, password=self.password, 
                    timeout=self.JCM_CONNECTION_TIMEOUT)
                self._info("SSH successful!")
                login_success = True
                break
            except (BadHostKeyException, AuthenticationException,
                SSHException, socket.error, buffered_pipe.PipeTimeout, socket.timeout) as error:
                self._error(error)
                new_client.close()
                new_client = None
        return login_success

    def is_active(self):
        ''' Indicates whether the JCM has an active command thread '''
        return self.jcm_active

    def stop_jcm(self):
        ''' Set flag to halt jcm '''
        self.halt_jcm_flag = True

    # Execute an arbitrary JCM command
    def execute_jcm_command(self, command, block=True, save_output=False):
        ''' Execute an arbitrary JCM command. This method will attempt to start the command
        immediately. If the command cannot be started successfully, this function will return
        a False. If the command starts successfully, a new thread will be created for the full
        execution of the command. If 'block' is True, this function will not return until the 
        command finished execution. The return value will be the return value of the execution
        of the program. If 'block' is False, this function will return 'True' and allow the thread
        to continue. Other functions will need to block on this thread or can stop the thread
        by setting the stop flag.

        '''

        if not self.ssh_client:
            self._error(f"No open JCM client. Cannot perform command\n{command}")
            return True

        if self.jcm_active:
            self._error(f"JCM currently executing a command. Cannot perform command\n{command}")
            return True

        # Prepare flag for being stopped externally
        self.stop_scrubbing_flag = False

        self._info("Executing commmand on JCM\n{command}")

        # Attempt to start the command
        try:
            (self.jcm_stdin, self.jcm_stdout, self.jcm_stderr) = \
                self.ssh_client.exec_command(command,timeout=self.JCM_CONNECTION_TIMEOUT)
        except SSHException as error:
            self._error(error)
            return False

        # Command started successfully. Create new thread for execution of command
        self.jcm_active = True
        self.jcm_thread = threading.Thread(target=self._jcm_execution_thread, args=(save_output))
        self.scrubbing_thread.start()

        # Block?
        if block:
            (index, thread) = self.jcm_thread
            thread.join()  # Add timeout? Catch exception?
        return True

    def _jcm_execution_thread(self,save_output):
        ''' Thread function for jcm command. This thread will exit when the exdecution process
        ends or when the external flag stops the process
        '''

        # Clear the list of JCM execution output lines
        self.jcm_command_output = []
        # Iterate over the lines until the process ends
        while not self.jcm_stdout.channel.exit_status_ready():
            
            if self.stop_scrubbing_flag:
                # Send a Ctrl-C to the scrubber or kill scrubber directly
                self.scrub_stdin.shutdown(2)
                #self.scrub_stdout.shutdown(2)
                # This should cause the exit_status_ready() to return false

            # See if the flag has been set to stop the scrubbing
            try:
                line = self.scrub_stdout.readline()
                if save_output:
                    self.jcm_command_output.append(line)
                self._print_std_out(line)

                # TODO: We may want to parse the JCM scrubber so that we detect SEFIs or scrubbing anomolise

            except(buffered_pipe.PipeTimeout, socket.timeout) as error:
                self.logging.error("Scrubbing: ",error)
                # return?

        # Scrubbing done: reset flag
        self.scrubbing_active = False
        return

    def configure_fpga(self, bitstream_filename):

        self._info("JCM configuration")

        # Default configuration command
        CONFIGURATION_COMMAND = "~/jcm_apps/jcm_config.elf --part {part} -c {clock_rate} --jtag --config_file {bitstream}"
        config_command = CONFIGURATION_COMMAND.format(part=self.part, clock = self.jtag_clock, bitstream=bitstream_filename)

        command_ret = self.execute_jcm_command(self, config_command, block=True, save_output=True)
        if not command_ret:
            return False
            
        # Iterate over the output to see if it configured correcty
        for line in self.jcm_command_output:
            if "Success" in line:
                self._info("JCM Configuration Success")
                return True
        self._error("JCM Configuration Failed")
        return False

    def scrub_fpga(self, iterations=10_000_000, frads_file = None, readback_file = None, inject_faults=0, block=False):

        self._info("Starting JCM scrubber")
        
        # Scrubbing and fault injection commands
        SCRUBBING_COMMAND = "~/jcm_apps/jcm_scrubbing.elf --part {part} -c {clock} --jtag --interations {iterations}"
        command = SCRUBBING_COMMAND.format(part=self.part, clock=self.jtag_clock, iterations=iterations)
        if frads_file:
            command += f" --frad_file {frads_file}"
        if readback_file:
            command += f" --readback_file {readback_file}"
        if inject_faults > 0:
            command += f" --inject_fault {inject_faults}"

        self._info("scrubbing command:" + command)

        command_ret = self.execute_jcm_command(self, command, block=block, save_output=False)
        if not command_ret:
            return False

        # Scrubbing started and the thread is going
        return True

    def jcm_ping(self):
        command = ['ping', "-c", '1', self.jcm_ip_addr]
        return subprocess.call(command) == 0

    def jcm_group_args(parser):
        ''' Static function for creating JCM argument group '''
        jcm_arg_group = parser.add_argument_group("JCM")
        jcm_arg_group.add_argument("--jcm_ip", help="JCM IP Address", required=True)
        jcm_arg_group.add_argument("--jcm_part", help="JCM Part Name", required=True)
        jcm_arg_group.add_argument("--jcm_clock", help="JCM Clock Rate", type=int, default = 10_000_000)

    def create_jcm_from_args(args, status_logging, stdout_logging, username="root", password="chrec"):
        ''' Static function for creating JCM argument group '''

        jcm = jcm_session(args.jcm_ip, args.jcm_part, jtag_clock=args.jcm_clock, status_logging = status_logging,
            stdout_logging = stdout_logging, username = username, password = password
        )
        return jcm

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument_group(jcm_session.jcm_group_args(parser))
    # Add arguments
    parser.add_argument("--bitfile",required=True)


    args = parser.parse_args()

    # create jcm object
    jcm = jcm_session.create_jcm_from_args(args)

    # 1. Connect with JCM
    if not jcm.open_jcm():
        return 1

    # 2. Configure with a bitfile
    bitstream_filename = args.bitfile
    #BITFILE = "./newtobetmred_tmr.bit"
    # --bitfile ./newtobetmred_tmr.bit
    if not jcm.configure_fpga(bitstream_filename):
        return 1

    # 3. Perform scrubbing (blocking, no frads file, no readback file)
    if not jcm.scrub_fpga(iterations=10, block=True):
        return 1

    # 4. Perform scrubbing, JCM ends scrubber, wait on thread (no blocking, no frads file, no readback file)
    if not jcm.scrub_fpga(iterations=10, block=False):
        return 1
    # Wait for thread to end
    (index, thread) = jcm.jcm_thread
    thread.join()

    # 5. Perform scrubbing, JCM ends scrubber, wait on flag (no blocking, no frads file, no readback file)
    if not jcm.scrub_fpga(iterations=10, block=False):
        return 1
    # Wait for thread to end
    while jcm.jcm_active:
        print("JCM still active")
        time.sleep(10)
    print("JCM finished scrubbing")

    # 5. Perform scrubbing, main thread ends scrubber (no blocking, no frads file, no readback file)
    if not jcm.scrub_fpga(iterations=1_000_000, block=False):
        return 1
    # Allow scrubber to operate for a bit
    print("Allowing Scrubber to run for a bit")
    time.sleep(20)
    # Stop JCM execution
    jcm.stop_jcm()
    # Wait for thread to stop
    (index, thread) = jcm.jcm_thread
    thread.join()
    print("JCM stopped")


if __name__ == "__main__":
    main()

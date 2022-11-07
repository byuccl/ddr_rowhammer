#!/usr/bin/env python3

#  python3 jcm_session.py --jcm_ip 169.254.132.152 --jcm_part xc7a200t --bitfile ~/newtobetmred_tmr.bit

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

from paramiko import SSHClient, SSHException, AutoAddPolicy, \
                    BadHostKeyException, AuthenticationException, buffered_pipe

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
    JCM_DEFAULT_IP = "169.254.132.152"

    #def _default_jcm_print(str):
    #    ''' Default function for printing JCM output. This can be overriden in the constructor. '''
    #    print(str, end="")

    def __init__(self, 
        jcm_ip_addr:str, 
        part, 
        jtag_clock = JCM_DEFAULT_CLOCK_RATE, 
        status_logging = None,
        stdout = None,
        stdout_timeprefix = None,
        username='root', password='chrec') -> None:

        self.ssh_client = None
        self.jcm_ip_addr = jcm_ip_addr
        self.logging = status_logging
        self.part = part
        self.jtag_clock = jtag_clock
        self.status_logging = status_logging
        self.stdout = stdout
        self.stdout_timeprefix = stdout_timeprefix
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
            self.logging.info("JCM:"+str)

    def _error(self, str):
        ''' Send an 'error' message to the logger. '''
        if self.status_logging:
            self.logging.error("JCM:"+str)

    def _print_std_out(self, line):
        ''' Print JCM standard output '''
        if self.stdout:
            if self.stdout_timeprefix:
                time_prefix = str("["+time.strftime(self.stdout_timeprefix)+"] ")
                line = time_prefix + line
            self.stdout.write(line)

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
                self._info(str(f"Connecting to JCM over SSH... (Attempt {(i+1)})"))
                new_client.connect(self.jcm_ip_addr, username=self.username, password=self.password, 
                    timeout=self.JCM_CONNECTION_TIMEOUT)
                self._info("SSH successful")
                login_success = True
                self.ssh_client = new_client
                break
            except (BadHostKeyException, AuthenticationException,
                SSHException, socket.error, buffered_pipe.PipeTimeout, socket.timeout) as error:
                self._error(error)
                new_client.close()
                self.ssh_client = None
        return login_success

    def is_active(self):
        ''' Indicates whether the JCM has an active command thread '''
        return self.jcm_active

    def stop_jcm(self):
        ''' Set flag to halt jcm '''
        self.halt_jcm_flag = True

    # Execute an arbitrary JCM command
    def execute_jcm_command(self, command:str, block=True, save_output=False):
        ''' Execute an arbitrary JCM command. This method will attempt to start the command
        immediately. If the command cannot be started successfully, this function will return
        a False. If the command starts successfully, the function will eventually return
        True. A new thread will be created for the full
        execution of the command. If 'block' is True, this function will not return until the 
        command finished execution. 
        
        Other functions will need to block on this thread or can stop the thread
        by setting the stop flag.

        '''

        if not self.ssh_client:
            self._error(f"No open JCM client. Cannot perform command\n{command}")
            return True

        if self.jcm_active:
            self._error(f"JCM currently executing a command. Cannot perform command\n{command}")
            return True

        # Prepare flag for being stopped externally
        self.halt_jcm_flag = False

        self._info(f"Executing commmand on JCM\n\t{command}")

        # Attempt to start the command
        try:
            (self.jcm_stdin, self.jcm_stdout, self.jcm_stderr) = \
                self.ssh_client.exec_command(command,timeout=self.JCM_CONNECTION_TIMEOUT)
        except SSHException as error:
            self._error(error)
            return False

        # Command started successfully. Create new thread for execution of command
        self.jcm_thread_output = []
        self.jcm_active = True
        self.jcm_thread = threading.Thread(target=self._jcm_execution_thread, args=(save_output,))
        self.jcm_thread.start()
 
        # Block?
        if block:
            thread = self.jcm_thread
            thread.join()  # Add timeout? Catch exception?
            # Done with command - set active to false
            self.jcm_active = False
        return True

    def _jcm_execution_thread(self,save_output):
        ''' Thread function for jcm command. This thread will exit when the execution process
        ends or when the external flag stops the process.

        save_output: indicates that the stdout for the thread should be saved in the class member: 'jcm_thread_output'
        '''

        # Iterate over the lines until the process ends
        while not self.jcm_stdout.channel.exit_status_ready():
            
            if self.halt_jcm_flag:
                # Send a Ctrl-C to the scrubber or kill scrubber directly
                self.jcm_stdin.shutdown(2)
                #self.scrub_stdout.shutdown(2)
                # This should cause the exit_status_ready() to return false

            # See if the flag has been set to stop the scrubbing
            try:
                # Read line from stdout
                line = self.jcm_stdout.readline()
                if save_output:
                    self.jcm_thread_output.append(line)
                if len(line) > 0:
                    self._print_std_out(line)
                # Read line from stderr
                '''
                line = self.jcm_stderr.readline()
                if "\n" in line:
                    if save_output:
                        self.jcm_thread_output.append(line)
                    self._print_std_out(line)
                '''
 
            except(buffered_pipe.PipeTimeout, socket.timeout) as error:
                self.logging.error("Scrubbing: ",error)
                # return?

        # Scrubbing done: reset flag
        self.scrubbing_active = False
        return

    def configure_fpga(self, bitstream_filename):

        self._info("Attempting JCM configuration")

        # Default configuration command
        CONFIGURATION_COMMAND = "~/jcm_apps/jcm_config.elf --part {part} -c {clock_rate} --jtag --config_file {bitstream}"
        config_command = CONFIGURATION_COMMAND.format(part=self.part, clock_rate = self.jtag_clock, bitstream=bitstream_filename)

        command_ret = self.execute_jcm_command(config_command, block=True, save_output=True)
        if not command_ret:
            return False
            
        # Iterate over the output to see if it configured correcty
        for line in self.jcm_thread_output:
            #print(line)
            if "Success" in line:
                self._info("Configuration Success")
                return True
        self._error("Configuration Failed")
        # Print output for failure
        for line in self.jcm_thread_output:
            print(line)

        return False

    def create_frad_list(self, frads_filename):
        pass

    def scrub_fpga(self, iterations=10_000_000, frads_file = None, readback_file = None, inject_faults=0, block=False):

        self._info("Starting JCM scrubber")
        
        # Scrubbing and fault injection commands
        SCRUBBING_COMMAND = "~/jcm_apps/jcm_scrubbing.elf --part {part} -c {clock} --jtag --iterations {iterations}"
        command = SCRUBBING_COMMAND.format(part=self.part, clock=self.jtag_clock, iterations=iterations)
        if frads_file:
            command += f" --frad_file {frads_file}"
        if readback_file:
            command += f" --readback_file {readback_file}"
        if inject_faults > 0:
            command += f" --inject_fault {inject_faults}"

        command_ret = self.execute_jcm_command(command, block=block, save_output=False)
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
        jcm_arg_group.add_argument("--jcm_ip", help="JCM IP Address", default = jcm_session.JCM_DEFAULT_IP)
        jcm_arg_group.add_argument("--jcm_part", help="JCM Part Name", required=True)
        jcm_arg_group.add_argument("--jcm_clock", help="JCM Clock Rate", type=int, default = jcm_session.JCM_DEFAULT_CLOCK_RATE)

    def create_jcm_from_args(args, status_logging, stdout, stdout_timeprefix = None, username="root", password="chrec"):
        ''' Static function for creating JCM argument group '''

        jcm = jcm_session(args.jcm_ip, args.jcm_part, jtag_clock=args.jcm_clock, status_logging = status_logging,
            stdout = stdout, stdout_timeprefix = stdout_timeprefix, username = username, password = password
        )
        return jcm

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument_group(jcm_session.jcm_group_args(parser))
    # Add arguments
    parser.add_argument("--bitfile",required=True)
    parser.add_argument("--fradlist",default="xc7a200t_frad.txt")

    args = parser.parse_args()

    # create jcm object
    logging.basicConfig(level=logging.INFO)
    jcm_output = sys.stdout
    TIME_STRING_FORMAT = "%Y-%m-%d %H:%M:%S"
    jcm = jcm_session.create_jcm_from_args(args, logging, stdout = jcm_output, stdout_timeprefix=TIME_STRING_FORMAT)

    # 1. Connect with JCM
    print("Main:Attempting to open JCM")
    if not jcm.open_jcm():
        print("JCM open failed")
        return 1

    # 2. Configure with a bitfile
    bitstream_filename = args.bitfile
    # --bitfile /root/newtobetmred_tmr.bit
    print("Main:Attempting to configure with JCM using bitfile ",bitstream_filename)
    if not jcm.configure_fpga(bitstream_filename):
        print("Main:Failed configure")
        return 1

    # 3. Perform scrubbing (blocking, no frads file, no readback file)
    frads_file = args.fradlist
    print("Main:Attempting to scrub and block")
    if not jcm.scrub_fpga(iterations=2, block=True, frads_file = frads_file):
        print("Main:Failed scrubbing")
        return 1

    # 4. Perform scrubbing (blocking, no frads file, no readback file) and inject faults
    frads_file = args.fradlist
    print("Main:Attempting to scrub and block and inject faults")
    if not jcm.scrub_fpga(iterations=2, block=True, frads_file = frads_file, inject_faults=1):
        print("Main:Failed scrubbing")
        return 1

    # 5. Perform scrubbing, JCM ends scrubber, wait on thread (no blocking, no frads file, no readback file)
    print("Main:Attempting to scrub and no block (wait on thread)")
    if not jcm.scrub_fpga(iterations=2, frads_file = frads_file, block=False):
        return 1
    # Wait for thread to end
    jcm.jcm_thread.join()

    return 0

    # 5. Perform scrubbing, JCM ends scrubber, wait on flag (no blocking, no frads file, no readback file)
    print("Main:Attempting to scrub and no block (wait on flag)")
    if not jcm.scrub_fpga(iterations=2, frads_file = frads_file, block=False):
        return 1
    # Wait for thread to end
    while jcm.jcm_active:
        print("Main:JCM still active")
        time.sleep(10)
    print("Main:JCM finished scrubbing")

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

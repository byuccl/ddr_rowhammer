#!/usr/bin/env python3


# BAsed on 
# https://github.com/byuccl/VexLinuxTMR/blob/main/JCM_repo/lancse_radiation_tmr_logging.py

import pexpect
import argparse
import telnetlib
import logging
import traceback
import cffi
import sys
import time
import re
import os
import numpy as np
import random
import socket

import threading

from paramiko import SSHClient, SSHException, AutoAddPolicy, \
                    BadHostKeyException, AuthenticationException, buffered_pipe

from distutils.log import error
from mimetypes import init
from multiprocessing.spawn import old_main_modules
from nis import match
# from this import d
from unittest import result
from urllib.parse import _NetlocResultMixinStr

from pkg_resources import require
# from asyncio.timeouts import timeout
from serial import Serial
from pexpect.fdpexpect import fdspawn
from datetime import date, datetime
from experiment_machine import Transition, ExperimentState, Experiment


# Format string for printing the date and time
TIME_STRING_FORMAT = "%Y-%m-%d %H:%M:%S"

# UART port connection constants
MAX_TTYUSB_INDEX = 10 #  Largest port number to search for (/dev/ttyUSB0 to /dev/ttyUSB9)
STARTING_FILE_NUM = -1 # Start at -1. If file exists, send num 0-9 otherwise -1.
MAX_NUM_TIMES_BOOT_UP = 5 # Max number attempts at finding board plugged in
UART_CONNECTION_ATTEMPT_DELAY = 10 # Number of seconds to delay before trying to connect to the UART again

GIVE_UP_MESSAGE_DELAY = 60 * 10 # Message delay every ten minutes

# Netbooter times in seconds
TIMEOUT_NETBOOTER = 3.0 # Timeout connecting to netbooter
SLEEPTIME_NETBOOTER = 1 # Time between creating connected instance of Telnet,
                        # turning board off, then on again.

# Timeout times in seconds
WAIT_TEXT_TIMEOUT = 15 # Wait for data or title to output
SDRAM_INIT_TIMEOUT = 5 # Time expected at least for scrubbing/init commands to run
CLOSE_BIST_TIMEOUT = 10 # Time expected to close bist
BOARD_REPROGRAM_TIMEOUT = 10 # Time expected to connect or reconnect to litex
FAULT_TIMER_MAX = 2 # 2 second fault injections

LITEX_BAUDRATE = 115200 # Baud rate to innitialize comm port object

# Control which command should send to correct errors
RESTART_BIST_INDEX = 1
SDRAM_MODE_SCRUB_INDEX = 2
SDRAM_DELAY_SCRUB_INDEX = 3
SDRAM_CALLIBRATE_INDEX = 4
SDRAM_INIT_INDEX = 5
SOC_REBOOT_INDEX = 6

MAX_NUM_UNICODE_EXCEPTIONS = 20 # Catch unicodedecode exception after 20 tries

# Data output
ERROR_MSG_INDEX = 3 # Error number at index 3 of matched string
SEC_MSG_INDEX = 4 # Sec error number at index 4 of matched string
DED_MSG_INDEX = 5 # Ded error number at index 5 of matched string
TITLE_INDEX = 0 # Returns this index if title is in matched string
DATA_INDEX = 1 # Returns this index if data is in matched string
MAX_ERROR_CNT = 0xFFFFFFFF # Errors have maxed out if either value reaches this value.

MAX_ERROR_CNT_CYCLES = 30 # After 30 cycles of errors incrementing, make transition.
MAX_PAUSE_ERROR_CNT_CYCLES = 10 # After 10 cycles of errors non_incrementing, make transition

JCM_IP_ADDRESS = "169.254.132.152"
PART = "xc7a200t"
BITFILE = "./newtobetmred_tmr.bit"
FRADS = "~/jcm_apps/a200t.frad"
JCM_LOGIN_LOOPS = 10
JCM_TIMEOUT_IN_SECONDS = 15
NUC_SEED = None
DESIGN = "digilent_nexys_video"

NETBOOTER_IP = "169.254.131.160"
NETBOOTER_PORT = 1 # Default netbooter port
BURST_LENGTH = 0x2000 # Default burst length
RAND_ARG = 1 # Start reading/writing data with addresses linearly.

FAULT_INJECTION_ENABLED = True # Run fault injection.

class jcm_session():
    '''
    Represents a session on the JCM. This class is used to simplify the operation
    and control of the JCM.

    ssh_client: if None, there is no ssh_client open. If not None, represents the ssh_client.
    jcm_ip_addr: IP address of the JCM (string)
    jtag_clock: Clock rate for JTAG operations
    username: username for ssh connection
    password: password for ssh connection
    '''

    # JCM constants
    JCM_CONNECTION_TIMEOUT = 30 # Max amount of time to try to connect to JCM
    JCM_LOGIN_ATTEMPTS = 5
    JCM_DEFAULT_CLOCK_RATE = 10_000_000

    def __init__(self, jcm_ip_addr:str, jtag_clock = JCM_DEFAULT_CLOCK_RATE, username='root', password='chrec') -> None:
        self.ssh_client = None
        self.jcm_ip_addr = jcm_ip_addr
        self.jtag_clock = jtag_clock
        self.username = username
        self.password = password

    def close_jcm(self):
        ''' Closes JCM SSH session'''
        if self.ssh_client:
            self.ssh_client.close()
            print("JCM SSH closed")
        else:
            print("JCM SSH session not open - cannot close")

    def open_jcm(self):
        ''' Opens a JCM SSH session '''
        print("Logging in to JCM")
        login_success = False
        for i in range(self.JCM_LOGIN_ATTEMPTS):
            try:
                new_client = SSHClient()
                new_client.load_system_host_keys()
                new_client.set_missing_host_key_policy(AutoAddPolicy())
                print("Connecting to JCM over SSH... (Attempt {})", (i+1), file=print_jcm_fout)
                new_client.connect(self.jcm_ip_addr, username=self.username, password=self.password, 
                    timeout=self.JCM_CONNECTION_TIMEOUT)
                print("SSH successful!", file=print_jcm_fout)
                login_success = True
                break
            except (BadHostKeyException, AuthenticationException,
                SSHException, socket.error, buffered_pipe.PipeTimeout, socket.timeout) as error:
                print(error, file=print_jcm_fout)
                new_client.close()
                new_client = None
        return login_success

    # Configure the FPGA using jcm_config.elf
    def configure_fpga(self, part, bitstream_filename):
        print("Sending config command to JCM, Time: ", file=print_jcm_fout)

        # Default configuration command
        CONFIGURATION_COMMAND = "~/jcm_apps/jcm_config.elf --part {part} -c {clock_rate} --jtag --config_file {bitstream}"

        config_command = CONFIGURATION_COMMAND.format(part=part, bitstream=bitstream_filename)
        print(config_command, file=print_jcm_fout)

        try:
            print("Running config command, Time: ", datetime.now().time(), file=print_jcm_fout)
            stdin, stdout, stderr = ssh_client.exec_command(config_command,timeout=JCM_TIMEOUT_IN_SECONDS)
        except SSHException as error:
            print(error, file=print_jcm_fout)
            logging.info("SSHException: Timeout occured or request was rejected opening channel to JCM. Retrying command.")
            print("[", time.strftime(TIME_STRING_FORMAT), "] SSHException: Timeout occured or request was rejected opening channel to JCM. Retrying command.")
            ssh_client = jcm_control.login_to_jcm(JCM_IP_ADDRESS)

        while not stdout.channel.exit_status_ready():
            try:
                line = stdout.readline()
                if (not line.isspace()) and line != '':
                    print("[", time.strftime(TIME_STRING_FORMAT), "] : ", line, file=print_jcm_fout)
                if (not line.isspace()) and line != '':
                    line = "[{}] ".format(time.strftime(TIME_STRING_FORMAT)) + line
                    print(line, file=print_jcm_fout)

                    if "Success" in line:
                        print("Configured Successfully!", file=print_jcm_fout)
                        break
                    else:
                        print("ERROR in configure_fpga", file=print_jcm_fout)
                        break
            
            except(buffered_pipe.PipeTimeout, socket.timeout) as error:
                print("ERROR in fonfigure_fpga", file=print_jcm_fout)
                print(error, file=print_jcm_fout)
                return 1
        return 0

    # Spawn a thread to perform JCM scrubbing. inject_faults indicates the number of faults to inject per scrub
    # Note that the JCM login session has already been established
    def spawn_jcm_scrubbing(ssh_client, fpga_part, frads_file, readback_file, iterations, inject_faults=0):
        #print("Sending config command to JCM, Time: ", datetime.now().time(), file=print_jcm_fout)

        # This is a global variable that is used to let the main thread know that scrubbing is OK.
        # When there is a problem with scrubbing, this variable is set to 0
        global SCRUBBING_OK
        SCRUBBING_OK = True
        # This flag is set by the main thread. We will check this flag and halt scrubbing
        # when it is set to zero
        global CONTINUE_SCRUBBING
        
        # Scrubbing and fault injection commands
        SCRUBBING_COMMAND = "~/jcm_apps/jcm_scrubbing.elf --part {fpga} -c 38000000 --jtag " \
                        "--frad_file {frads_file} --iterations {iterations} --readback_file {readback}"
        FAULT_INJECTION_COMMAND = SCRUBBING_COMMAND + " --inject_fault {faults}"


        if inject_faults > 0:
            # Inject faults
            config_command = SCRUBBING_COMMAND.format(fpga=fpga_part, frads_file= frads_file, iterations=iterations, 
                readback_file = readback_file,faults = inject_faults)
        else:
            # No fault injection
            config_command = FAULT_INJECTION_COMMAND.format(fpga=fpga_part, frads_file= frads_file, iterations=iterations, 
                readback_file = readback_file)

        print(config_command, file=print_jcm_fout)

        command_success = False
        for i in range(JCM_LOGIN_LOOPS):
            try:
                print("Running scrubbing command, Time {} attempt {} ", datetime.now().time(), i+1, file=print_jcm_fout)
                stdin, stdout, stderr = ssh_client.exec_command(config_command,timeout=JCM_TIMEOUT_IN_SECONDS)
                command_success = True
                break
            except SSHException as error:
                print(error, file=print_jcm_fout)
                logging.info("SSHException: Timeout occured or request was rejected opening channel to JCM. Retrying command.")
                print("[", time.strftime(TIME_STRING_FORMAT), "] SSHException: Timeout occured or request was rejected opening channel to JCM. Retrying command.")
                # TODO: We should NOT try to login again. We already ahve logged in. 
                #print("TODO: Fix this")
                #ssh_client = jcm_control.login_to_jcm(JCM_IP_ADDRESS)
        if not command_success:
            SCRUBBING_OK = False
            return 1


        while not stdout.channel.exit_status_ready():
            try:
                line = stdout.readline()
                line = "[{}] ".format(time.strftime(TIME_STRING_FORMAT)) + line
                print(line, file=print_jcm_fout)

                # TODO: We may want to parse the JCM scrubber so that we detect SEFIs or scrubbing anomolise

                # Check flag for scrubbing. If the flag goes low, kill the scrubber and exit
                if not CONTINUE_SCRUBBING:
                    print("CONTINUE_SCRUBBING now false. Quitting scrubber.")
                    TODO: send a "Ctrl-C" to the scrubber to kill it
                    SCRUBBING_OK = False
                    return 1

            except(buffered_pipe.PipeTimeout, socket.timeout) as error:
                print("ERROR in scrubbing", file=print_jcm_fout)
                print(error, file=print_jcm_fout)
                SCRUBBING_OK = False
                return 1
        
        SCRUBBING_OK = False
        return 0



class boardcontrol():
    '''
    This class includes the actions to be performed in the states.

    It also includes the state variables of the experiment that the action functions must query.
    '''
    """Set variables to pass around"""

    # Number for dev port in /dev/ttyUSBX (int)
    serial_port = None

    # Object controlling JCM (jcm_control)
    jcm_client = None

    # The Serial object opening the file (fd) and
    # the fdspawn object controlling pexpect.
    fd = None
    fdspawn_obj = None

    # Error count variables, new and old (int)
    new_error_cnt = None
    new_sec_cnt = None
    new_ded_cnt = None
    old_error_cnt = None
    old_sec_cnt = None
    old_ded_cnt = None

    # Variable to control which error correction function to use (int)
    degree_of_max_error = None

    # Timers for 'check if errors increment' state (int)
    stopped_increment_error_count = None
    increment_error_count = None

    # Timer for checking unexpected input state (int)
    unexpected_output_timer = None

    # Boolean variables for tracking if invalid data occured. (bool)
    data_output_before_title = None
    first_run = None

    # Netbooter port and ip address variables
    netbooter_ip = None     # (str)
    netbooter_port = None   # (int)

    # Settings for bist: 
    #   mem-burst-length: Bist memory burst length (str)
    #   addr-mode: Address mode, how bist should read and write memory (str)
    mem_burst_length = None
    addr_mode = None

    # UnicodeDecode error flag. If litex restarts because of a UnicodeDecodeException,
    # this flag will set, and the board will reconfigure. (bool)
    unicode_decode_prev_error = None


    """ Record time and data in both log and output 
    Parameters:
        output_str (str): The string to output in a log file and in stdout.
        supress_log (bool): True if log should NOT print message, false if it should."""
    def _record_data(output_str, supress_log = False):
        print("[", time.strftime(TIME_STRING_FORMAT), "] ", output_str)
        if not (supress_log):
            logging.info(output_str)



    def init_funct():
        boardcontrol.new_error_cnt = 0
        boardcontrol.new_sec_cnt = 0
        boardcontrol.new_ded_cnt = 0
        boardcontrol.old_error_cnt = 0
        boardcontrol.old_sec_cnt = 0
        boardcontrol.old_ded_cnt = 0
        boardcontrol.stopped_increment_error_count = 0
        boardcontrol.increment_error_count = 0

        boardcontrol.data_output_before_title = False
        boardcontrol.first_run = False
        boardcontrol.unicode_decode_prev_error = False

        boardcontrol.unexpected_output_timer = 0



    def start_actions(experiment, state):
        '''
        Actions performed at the very start of a new test
        '''
        boardcontrol._record_data("Test Start")

    def board_plugged_in_actions(experiment, state):
        """ Check if dev port exists, confirm the nexys video board is plugged in.
            
            Attributes:
                tty_port_num (int) = This holds the dev_port number, otherwise
                -1 if the dev port file could not be found.
                give_up_time (bool): True if time to give up on checking board, 
                otherwise false.
        """
        boardcontrol._record_data("Confirming board plugged in")
        experiment.tty_port_num = STARTING_FILE_NUM
        experiment.give_up_time = False

        if not hasattr(experiment, 'give_up_timer'):
            experiment.give_up_timer = 0
        
        # Set starting number to -1, send command to see if /dev/ttyUSBX
        # file exists, interpret by reading resulting output string.
        # ?? Why looking for the max? Will there be more than one?
        max_num = STARTING_FILE_NUM
        for i in range(0, MAX_TTYUSB_INDEX):
            tty_dev = "/dev/ttyUSB" + str(i)
            output_str = pexpect.run("ls "+tty_dev, encoding="utf-8", logfile=sys.stdout)
            if not ("cannot access '" + tty_dev + "': No such file or directory" in output_str and (i > max_num)):
                max_num = i

        # Set attribute file_num as the dev port number. If dev port doesn't 
        # exist, file_num is -1.
        boardcontrol.serial_port = max_num
        if (max_num > 0):
            # Found a tty port
            boardcontrol._record_data("Board plugged in, using /dev/ttyUSB{max_int}.".format(max_int=max_num))
            experiment.tty_port_num = max_num
            experiment.give_up_timer = 0
        else:
            # Failed to find a tty port
            boardcontrol._record_data("Board not plugged in.")
            experiment.give_up_timer += 1
            if (experiment.give_up_timer >= MAX_NUM_TIMES_BOOT_UP):
                # Give up if maximum number of attempts made
                experiment.give_up_time = True
            else:
                # Wait before trying again
                time.sleep(UART_CONNECTION_ATTEMPT_DELAY)




    """ Stay here indefinitely, board is not plugged in or usable."""
    def give_up_actions(experiment, state):
        boardcontrol._record_data("Giving up")
        while(True):
            time.sleep(GIVE_UP_MESSAGE_DELAY)
            boardcontrol._record_data("Given up loop")



    """Create SSHclient connection to JCM. """
    def jcm_login_actions(experiment, state):
        boardcontrol._record_data("Logging in to JCM")
        
        # Make SSHclient object to connect to JCM. Check that this is open
        # during transitions
        boardcontrol.jcm_client = jcm_control.login_to_jcm(JCM_IP_ADDRESS)



    """Send board configuration command to JCM, configure nexys video board with program.
        Attributes:
            jcm_configured (bool): True if jcm successfully configured board, else False.
    """
    def jcm_configure_board_actions(experiment, state):
        boardcontrol._record_data("Configuring JCM with new program")

        experiment.jcm_configured = False
        if (jcm_control.configure_fpga(boardcontrol.jcm_client) == 0):
            experiment.jcm_configured = True



    """Connect to Litex Terminal by fdspawn 
        Attributes:
            connection_return_val (int) = 0 if connected, all is well. 1 if a timeout or
            problem with connection occured.
    """
    def connect_to_litex_serial_actions(experiment, state):
        boardcontrol._record_data("Starting litex with /dev/ttyUSB{}".format(str(boardcontrol.serial_port)))
        experiment.connection_return_val = 0

        serial_str = r"/dev/ttyUSB" +  str(boardcontrol.serial_port)
        boardcontrol.fd = Serial(serial_str, baudrate = LITEX_BAUDRATE)

        try:
            boardcontrol.fdspawn_obj = fdspawn(boardcontrol.fd, encoding="utf-8", logfile=sys.stdout, timeout=BOARD_REPROGRAM_TIMEOUT)
            return 
        except pexpect.exceptions.TIMEOUT:
            boardcontrol._record_data("Timeout occured connecting to litex terminal")
            experiment.connection_return_val = 1
            boardcontrol.fdspawn_obj = None
            return 
        except Exception:
            boardcontrol._record_data("Unexpected exception connecting to litex terminal")
            experiment.connection_return_val = 1
            boardcontrol.fdspawn_obj = None
            return 



    """Expect 'LITEX>>' prompt
        This function will simply expect a litex>> prompt.
        Attributes:
            expect_litex_return_val (int) = Returns 0 if no problems occured, 1 if 
            a timeout error occured or if a UnicodeDecode error occured more than 20x
            
        """
    def expect_litex_prompt_actions(experiment, state):
        boardcontrol._record_data("Expecting Litex Prompt")

        experiment.expect_litex_return_val = 0
        unicode_decode_counter = 0
        while (True):
            try:
                boardcontrol.fdspawn_obj.sendline("\n")
                boardcontrol.fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=CLOSE_BIST_TIMEOUT)
                break
            except pexpect.exceptions.TIMEOUT:
                boardcontrol._record_data("Timeout occured expecting Litex>> prompt")
                experiment.expect_litex_return_val = 1
                break
            except UnicodeDecodeError:
                boardcontrol._record_data("Unicode error occured, retrying up to 20x")
                unicode_decode_counter += 1
                if (unicode_decode_counter >= MAX_NUM_UNICODE_EXCEPTIONS):
                    boardcontrol._record_data("Max number of unicode errors reached")
                    experiment.expect_litex_return_val = 1
                    break



    """Use JCM to launch first fault injection
    """
    def create_first_fault_actions(experiment, state):
        boardcontrol._record_data("Injected first fault")
        jcm_control.inject_fault(boardcontrol.jcm_client)



    """Send bist command to terminal, initialize error counts
    """
    def send_bist_cmd_actions(experiment, state):
        boardcontrol._record_data("Starting bist")

        cmd_str = "sdram_bist " + str(boardcontrol.mem_burst_length) + " " + str(boardcontrol.addr_mode)
        boardcontrol.fdspawn_obj.sendline(cmd_str)

        # Set old error counts to zero
        boardcontrol.old_error_cnt = 0
        boardcontrol.old_sec_cnt = 0
        boardcontrol.old_ded_cnt = 0

        # Set first run variable to True
        boardcontrol.first_run = True



    """ Expect title, line of data as the bist runs
        Attributes:
            isUnicodeError (bool): True if a UnicodeDecode exception occured
            isSecondUnicodeError (bool): Litex has restarted, we are still getting UnicodeDecode exceptions
            isTimeOut (bool): True if a Timeout exception occured
            isEOFError (bool): True if an EOF exception occured.
            isError (bool): True if another exception occured.
            gotTitle (bool): True if title printed out
            gotData (bool): True if data printed out, returns values of error counts
            invalid_input(bool): True if data not recognized between title outputs, 
            otherwise False.
        """
    def expect_title_line_actions(experiment, state):
        # boardcontrol._record_data("expect title line", True)
        experiment.isUnicodeError = False
        experiment.isSecondUnicodeError = False
        experiment.isTimeOut = False
        experiment.isEOFError = False
        experiment.isError = False
        experiment.gotTitle = False
        experiment.gotData = False
        experiment.invalid_input = False

        # Error correction, Data must be read between titles, otherwise 
        # data output is no good.

        unicode_error_index = 0

        boardcontrol.new_error_cnt = 0
        boardcontrol.new_sec_cnt = 0
        boardcontrol.new_ded_cnt = 0

        while (True):
            try:
                match_index = boardcontrol.fdspawn_obj.expect(["WR-BW\(MiB/s\) RD-BW\(MiB/s\)  TESTED\(MiB\)     ERRORS        SEC        DED", # Title
                                        "\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*"],                  # Reg Expression matching 6 arguments
                                        timeout=WAIT_TEXT_TIMEOUT)
            
                if boardcontrol.fdspawn_obj.match:

                    if match_index == TITLE_INDEX:
                        experiment.gotTitle = True

                        # Check that valid input has outputted, or its the first run
                        if (boardcontrol.data_output_before_title or boardcontrol.first_run):
                            boardcontrol.data_output_before_title = False
                            boardcontrol.first_run = False
                        else:
                            experiment.invalid_input = True

                        boardcontrol._record_data("", True)
                        break

                    elif match_index == DATA_INDEX:

                        # Match to familiar data, set SecondUnicodeDecode to false if occured beforehand
                        boardcontrol.unicode_decode_prev_error = False

                        # Data recognized
                        boardcontrol.data_output_before_title = True

                        # Split apart, take data and return error counts
                        result_str = str(boardcontrol.fdspawn_obj.match.group(0)).split()

                        boardcontrol.new_error_cnt = int(result_str[ERROR_MSG_INDEX])
                        boardcontrol.new_sec_cnt = int(result_str[SEC_MSG_INDEX])
                        # boardcontrol.new_ded_cnt = int(result_str[DED_MSG_INDEX
                        ded_string = result_str[DED_MSG_INDEX]
                        ded_string_int = "0"
                        if (ded_string.find('\'', 0) == -1):
                            ded_string_int = ded_string
                        else :
                            ded_string_int = ded_string[:ded_string.find('\'', 0):]
                        boardcontrol.new_ded_cnt = int(ded_string_int)

                        experiment.gotData = True

                        boardcontrol._record_data("", True)
                        break

                else:
                    # Reach here if no match found
                    boardcontrol._record_data("Unexpected, no match found")
                    break

                
            except pexpect.exceptions.TIMEOUT:
                boardcontrol._record_data("Time out whie expecting title or data")
                experiment.isTimeOut = True
                break

            except pexpect.exceptions.EOF:
                boardcontrol._record_data("EOF exception while expecting title or data")
                experiment.isEOFError = True
                break

            except UnicodeDecodeError:
                boardcontrol._record_data("UnicodeDecodeException whie expecting title or data")
                unicode_error_index += 1

                if (boardcontrol.unicode_decode_prev_error):
                    boardcontrol._record_data("UnicodeDecode exceptions occuring again")
                    experiment.isSecondUnicodeError = True
                    boardcontrol.unicode_decode_prev_error = False
                    break

                if (unicode_error_index >= MAX_NUM_UNICODE_EXCEPTIONS):
                    boardcontrol._record_data("Too many UnicodeDecode exceptions")
                    experiment.isUnicodeError = True
                    boardcontrol.unicode_decode_prev_error = True
                    break

            except Exception:
                boardcontrol._record_data("Other exception occured whie expecting title or data")
                boardcontrol._record_data(str(Exception))

                experiment.isError = True
                break



    """ Check if errors have come up. This resets the line of fixing dram errors
        by setting degree_of_max_error to zero, also error timers for checking if
        errors increment.
        Attributes:
            errors_exist (bool): True if errors exist, otherwise false.
    """
    def check_if_errors_exist_actions(experiment, state):
        # boardcontrol._record_data("check if errors exist", True)
        experiment.errors_exist = False
        
        if (boardcontrol.new_error_cnt > 0 or boardcontrol.new_sec_cnt > 0 or boardcontrol.new_ded_cnt > 0):
            experiment.errors_exist = True
        else:
            boardcontrol.degree_of_max_error = 0
            boardcontrol.increment_error_count = 0
            boardcontrol.stopped_increment_error_count = 0



    """ Check if the errors that do exist are incrementing or not after each cycle.
        Attributes:
            errors_incrementing (bool): True if errors exist, otherwise false.
            errors_stopped_incrementing (bool): True if errors exist, otherwise false.
    """
    def check_if_errors_increment_actions(experiment, state):
        # boardcontrol._record_data("check_if_errors_increment", True)
        experiment.errors_incrementing = False
        experiment.errors_stopped_incrementing = False

        # Output to user if dram errors begin to exist
        if ((boardcontrol.old_error_cnt == 0) and 
            (boardcontrol.old_sec_cnt == 0) and
            (boardcontrol.old_ded_cnt == 0)):
            boardcontrol._record_data("Errors detected")

        if ((boardcontrol.new_error_cnt > boardcontrol.old_error_cnt) or 
            (boardcontrol.new_sec_cnt > boardcontrol.old_sec_cnt) or
            (boardcontrol.new_ded_cnt > boardcontrol.old_ded_cnt)):
            
            boardcontrol.stopped_increment_error_count = 0
            boardcontrol.increment_error_count += 1
            if (boardcontrol.increment_error_count >= MAX_ERROR_CNT_CYCLES):
                experiment.errors_incrementing = True
                boardcontrol.increment_error_count = 0

        else:
            boardcontrol.stopped_increment_error_count += 1
            boardcontrol.increment_error_count = 0
            if (boardcontrol.stopped_increment_error_count >= MAX_PAUSE_ERROR_CNT_CYCLES):
                experiment.errors_stopped_incrementing = True
                boardcontrol.stopped_increment_error_count = 0


        boardcontrol.old_error_cnt = boardcontrol.new_error_cnt
        boardcontrol.old_sec_cnt = boardcontrol.new_sec_cnt
        boardcontrol.old_ded_cnt = boardcontrol.new_ded_cnt



    """ Check if time to correct and inject fault
        Attributes: 
            isTimeToInject (bool): True if time to inject
            this cycle, otherwise false."""

    def correct_inject_fault_time_actions(experiment, state):
        # boardcontrol._record_data("inject fault time", True)
        experiment.isTimeToInject = False

        if not hasattr(experiment, '_correct_inject_fault_timer'):
            experiment._correct_inject_fault_timer = 0
        experiment._correct_inject_fault_timer += 1

        if (experiment._correct_inject_fault_timer >= FAULT_TIMER_MAX):
            experiment.isTimeToInject = True
            experiment._correct_inject_fault_timer = 0



    """ Correct fault and inject fault 
    """
    def correct_inject_fault_actions(experiment, state):
        # boardcontrol._record_data("Fault injected!", True)
        jcm_control.correct_fault(boardcontrol.jcm_client)
        jcm_control.inject_fault(boardcontrol.jcm_client)



    """ Close bist, reopen. Happens if errors are not incrementing
        Attributes:
            timeout_occured (bool): Timeout occured while expecting 'litex>>' prompt
    """
    def restart_bist_actions(experiment, state):
        boardcontrol._record_data("Restart bist")

        experiment.timeout_occured = False

        try:
            boardcontrol.fdspawn_obj.sendline("\n")
            boardcontrol.fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=CLOSE_BIST_TIMEOUT)

            boardcontrol._record_data("Bist closed, sending bist command")
            cmd_str = "sdram_bist " + str(boardcontrol.mem_burst_length) + " " + str(boardcontrol.addr_mode)
            boardcontrol.fdspawn_obj.sendline(cmd_str)

            # Set old error counts to zero
            boardcontrol.old_error_cnt = 0
            boardcontrol.old_sec_cnt = 0
            boardcontrol.old_ded_cnt = 0

            # Set first run variable to true
            boardcontrol.first_run = True

        except pexpect.exceptions.TIMEOUT:
            boardcontrol._record_data("Timeout occured restarting bist")
            experiment.timeout_occured = True



    """ Close bist, correct fault, prep to go through cycle of error fixing 
        Attributes: 
            timeout_occured (bool): True if timeout occured, otherwise false
    """
    def close_bist_correct_fault_actions(experiment, state):
        boardcontrol._record_data("closing bist, correcting fault")
        experiment.timeout_occured = False

        try:
            boardcontrol._record_data("Closing bist")
            boardcontrol.fdspawn_obj.sendline("\n")
            boardcontrol.fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=CLOSE_BIST_TIMEOUT)
        except pexpect.exceptions.TIMEOUT:
            experiment.timeout_occured = True
            return

        # After closing bist, correct one fault
        jcm_control.correct_fault(boardcontrol.jcm_client)



    """ Go through a list of actions of what to do, one by one, until
        there are no more errors outputting.
        A single fault will be injected if this function succeeds, otherwise
        nothing will happen with the jcm.
        
        Attributes:
            failed_to_correct_errors (bool): True if we've gone through the whole
            cycle, errors still appear
    """
    def debug_error_actions(experiment, state):
        boardcontrol._record_data("Send sdram command")
        experiment.failed_to_correct_errors = False
        experiment.timeout_occured_in_debug = False

        # This is set to zero in the state checking if errors exist.
        boardcontrol.degree_of_max_error += 1
        try:
            if (boardcontrol.degree_of_max_error == RESTART_BIST_INDEX):
                # Do nothing, simply restart bist
                pass
            elif (boardcontrol.degree_of_max_error == SDRAM_MODE_SCRUB_INDEX):

                boardcontrol.fdspawn_obj.sendline("sdram_mr_scrub")
                boardcontrol.fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)

            elif (boardcontrol.degree_of_max_error == SDRAM_DELAY_SCRUB_INDEX):

                boardcontrol.fdspawn_obj.sendline("sdram_delay_scrub")
                boardcontrol.fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)

            elif (boardcontrol.degree_of_max_error == SDRAM_CALLIBRATE_INDEX):

                boardcontrol.fdspawn_obj.sendline("sdram_cal")
                boardcontrol.fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)

            elif (boardcontrol.degree_of_max_error == SDRAM_INIT_INDEX):

                boardcontrol.fdspawn_obj.sendline("sdram_init")
                boardcontrol.fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)

            elif (boardcontrol.degree_of_max_error == SOC_REBOOT_INDEX):

                boardcontrol.fdspawn_obj.sendline("reboot")
                boardcontrol.fd.close()
                boardcontrol.fd.open()
                boardcontrol.fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)

            else:

                experiment.failed_to_correct_errors = True

            if not experiment.failed_to_correct_errors:   

                # Inject one fault
                jcm_control.inject_fault(boardcontrol.jcm_client)

                # Restart bist
                cmd_str = "sdram_bist " + str(boardcontrol.mem_burst_length) + " " + str(boardcontrol.addr_mode)
                boardcontrol.fdspawn_obj.sendline(cmd_str)

                # Set old error counts to zero
                boardcontrol.old_error_cnt = 0
                boardcontrol.old_sec_cnt = 0
                boardcontrol.old_ded_cnt = 0

                # Set first run variable to true 
                boardcontrol.first_run = True

        except pexpect.exceptions.TIMEOUT:
            experiment.timeout_occured_in_debug = True



    """ Correct fault
    """
    def correct_fault_actions(experiment, state):
        boardcontrol._record_data("Correct fault")

        jcm_control.correct_fault(boardcontrol.jcm_client)



    """ Attempt to restart Litex (s)
        Attributes:
            restart_success: True if litex resets, False if otherwise.
        """
    def restart_litex_actions(experiment, state):
        boardcontrol._record_data("Restart litex")
        experiment.restart_success = False

        try:
            boardcontrol.fd.close()
            boardcontrol.fd.open()
            boardcontrol.fdspawn_obj = fdspawn(boardcontrol.fd, encoding="utf-8", logfile=sys.stdout, timeout=BOARD_REPROGRAM_TIMEOUT)
            boardcontrol.fdspawn_obj.sendline("\n")
            boardcontrol.fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=BOARD_REPROGRAM_TIMEOUT)
            experiment.restart_success = True
        except pexpect.exceptions.TIMEOUT:
            boardcontrol._record_data("Timeout occured restarting Litex")
        except Exception:
            boardcontrol._record_data("Other exception occured restarting Litex")
            boardcontrol._record_data(str(Exception))


    """ Repower board, turn netbooter outlet off, then on.
    """
    def repower_board_actions(experiment, state):
        boardcontrol._record_data("Repower board")
        
        # Stop JCM
        jcm_control.close_jcm(boardcontrol.jcm_client)

        teln = telnetlib.Telnet(boardcontrol.netbooter_ip, None, timeout=TIMEOUT_NETBOOTER)

        # Turn off
        s = teln.read_some()
        time.sleep(SLEEPTIME_NETBOOTER)

        s = ("pset " + str(boardcontrol.netbooter_port) + " 0").encode("ascii") + b"\r\n\r\n"
        teln.write(s)
        time.sleep(SLEEPTIME_NETBOOTER)

        # Turn back on
        s = ("pset " + str(boardcontrol.netbooter_port) + " 1").encode("ascii") + b"\r\n\r\n"
        teln.write(s)
        time.sleep(SLEEPTIME_NETBOOTER)
        teln.close()

def build_experiment():
    '''
    Builds the experiment object and its related states for the experiment state machine.
    '''

    # State constants
    INITIAL_STARTING_STATE = "Initial Starting State"
    REPOWER_STATE = "Repower State"

    PLUGGED_IN_STATE = "Plugged In State"
    TTY_CONNECTION_FAILURE = "TTY Connection Failure"
    LOGIN_JCM_STATE = "Login JCM State"
    CONFIGURE_FPGA_STATE = "Configure FPGA State"
    CONNECT_TO_LITEX_STATE = "Connect To Litex"
    EXPECT_LITEX_PROMPT_STATE = "Expect Litex Prompt State"
    #INJECT_FIRST_FAULT_STATE = "Inject First Fault State"
    SEND_BIST_COMMAND_STATE = "Send Bist Command State"
    EXPECT_TITLE_OR_DATA_STATE = "Expect Title Or Data State"
    SPAWN_SCRUBBING_STATE = "Spawn Configuration Scrubbing State"
    #CORRECT_FAULT_RECONFIGURE_BOARD_STATE = "Correct Fault Reconfigure Board"
    #CORRECT_FAULT_STATE = "Correct Fault State"
    CHECK_IF_ERRORS_EXIST_STATE = "Check If Errors Exist State"
    CHECK_IF_ERRORS_INCREMENT_STATE = "Check If Errors Increment State"
    CHECK_IF_FAULT_INJECT_STATE = "Check If Fault Inject State"
    FAULT_CORRECT_INJECT_STATE = "Fault Correct Inject State"
    CLOSE_RESTART_BIST_STATE = "Close Restart Bist State"
    CLOSE_BIST_CORRECT_FAULT_STATE = "Close Bist Correct Fault State"
    FIX_ERRORS_STATE = "Fix Errors State"
    RESTART_LITEX_STATE = "Restart Litex State"

    # Create a new experiment object
    experiment = Experiment()

    # Initialize class
    boardcontrol.init_funct()

    # INITIAL_STARTING_STATE
    # - perform any initial messages or setup
    experiment.add_state(ExperimentState(
        INITIAL_STARTING_STATE,
        boardcontrol.start_actions,
        Transition(lambda ex, st: True, REPOWER_STATE)
    ))

    # REPOWER_STATE
    experiment.add_state(ExperimentState(
        REPOWER_STATE,
        boardcontrol.repower_board_actions,
        Transition(lambda ex, st: True, PLUGGED_IN_STATE)
    ))

    # PLUGGED_IN_STATE
    # - Check for the UART port and for UART connection
    experiment.add_state(ExperimentState(
        PLUGGED_IN_STATE,
        boardcontrol.board_plugged_in_actions,
        Transition(lambda ex, st: ex.give_up_time,TTY_CONNECTION_FAILURE),
        Transition(lambda ex, st: ex.tty_port_num < 0, PLUGGED_IN_STATE),
        Transition(lambda ex, st: True, LOGIN_JCM_STATE)
    ))

    # TTY_CONNECTION_FAILURE
    experiment.add_state(ExperimentState(
        TTY_CONNECTION_FAILURE,
        boardcontrol.give_up_actions,
        # Should never get to this transition
        Transition(lambda ex, st: True, TTY_CONNECTION_FAILURE)
    ))

    # LOGIN_JCM_STATE
    experiment.add_state(ExperimentState(
        LOGIN_JCM_STATE,
        boardcontrol.jcm_login_actions,
        Transition(lambda ex, st: True, CONFIGURE_FPGA_STATE)
    ))

    # CONFIGURE_FPGA_STATE
    experiment.add_state(ExperimentState(
        CONFIGURE_FPGA_STATE,
        boardcontrol.jcm_configure_board_actions,
        Transition(lambda ex, st: ex.jcm_configured, CONNECT_TO_LITEX_STATE),
        Transition(lambda ex, st: True, PLUGGED_IN_STATE)
    ))

    # CONNECT_TO_LITEX_STATE
    experiment.add_state(ExperimentState(
        CONNECT_TO_LITEX_STATE,
        boardcontrol.connect_to_litex_serial_actions,
        Transition(lambda ex, st: ex.connection_return_val == 0, EXPECT_LITEX_PROMPT_STATE),
        Transition(lambda ex, st: True, REPOWER_STATE)
    ))

    # EXPECT_LITEX_PROMPT_STATE
    experiment.add_state(ExperimentState(
        EXPECT_LITEX_PROMPT_STATE,
        boardcontrol.expect_litex_prompt_actions,
        Transition(lambda ex, st: ex.expect_litex_return_val == 0, SPAWN_SCRUBBING_STATE),
        Transition(lambda ex, st: True, REPOWER_STATE)
    ))

    # SPAWN_SCRUBBING_STATE
    experiment.add_state(ExperimentState(
        SPAWN_SCRUBBING_STATE,
        boardcontrol.spawn_jcm_scrubbing,
        Transition(lambda ex, st: True, SEND_BIST_COMMAND_STATE)
    ))

    # Create inject first fault state
    '''
    experiment.add_state(ExperimentState(
        INJECT_FIRST_FAULT_STATE,
        boardcontrol.create_first_fault_actions,
        Transition(lambda ex, st: True, SEND_BIST_COMMAND_STATE)
    ))
    '''

    # Create send bist command state
    experiment.add_state(ExperimentState(
        SEND_BIST_COMMAND_STATE,
        boardcontrol.send_bist_cmd_actions,
        Transition(lambda ex, st: True, EXPECT_TITLE_OR_DATA_STATE)
    ))

    # Create expect title or data state
    #  - If a title comes out, it comes back to this state
    #  - If a data line comes out, checks data for errors
    experiment.add_state(ExperimentState(
        EXPECT_TITLE_OR_DATA_STATE,
        boardcontrol.expect_title_line_actions,
        Transition(lambda ex, st: ex.isSecondUnicodeError, CORRECT_FAULT_RECONFIGURE_BOARD_STATE),
        Transition(lambda ex, st: (ex.isError or ex.isEOFError or ex.isTimeOut or ex.isUnicodeError or ex.invalid_input), CORRECT_FAULT_STATE),
        Transition(lambda ex, st: ex.gotData, CHECK_IF_ERRORS_EXIST_STATE),
        Transition(lambda ex, st: ex.gotTitle, EXPECT_TITLE_OR_DATA_STATE),
        Transition(lambda ex, st: True, TTY_CONNECTION_FAILURE)
    ))

    experiment.add_state(ExperimentState(
        CORRECT_FAULT_RECONFIGURE_BOARD_STATE,
        boardcontrol.correct_fault_actions,
        Transition(lambda ex, st: True, CONFIGURE_FPGA_STATE)
    ))

    # Create check if errors exist state
    experiment.add_state(ExperimentState(
        CHECK_IF_ERRORS_EXIST_STATE,
        boardcontrol.check_if_errors_exist_actions,
        Transition(lambda ex, st: ex.errors_exist, CHECK_IF_ERRORS_INCREMENT_STATE),
        Transition(lambda ex, st: True, CHECK_IF_FAULT_INJECT_STATE)
    ))

    # Create check if fault inject state
    experiment.add_state(ExperimentState(
        CHECK_IF_FAULT_INJECT_STATE,
        boardcontrol.correct_inject_fault_time_actions,
        Transition(lambda ex, st: ex.isTimeToInject, FAULT_CORRECT_INJECT_STATE),
        Transition(lambda ex, st: True, EXPECT_TITLE_OR_DATA_STATE)
    ))

    # Create fault correct inject state
    experiment.add_state(ExperimentState(
        FAULT_CORRECT_INJECT_STATE,
        boardcontrol.correct_inject_fault_actions,
        Transition(lambda ex, st: True, EXPECT_TITLE_OR_DATA_STATE)
    ))

    # Create check if Errors increment state
    experiment.add_state(ExperimentState(
        CHECK_IF_ERRORS_INCREMENT_STATE,
        boardcontrol.check_if_errors_increment_actions,
        Transition(lambda ex, st: ex.errors_stopped_incrementing, CLOSE_RESTART_BIST_STATE),
        Transition(lambda ex, st: ex.errors_incrementing, CLOSE_BIST_CORRECT_FAULT_STATE),
        Transition(lambda ex, st: True, CHECK_IF_FAULT_INJECT_STATE)
    ))

    # Create close restart bist state
    experiment.add_state(ExperimentState(
        CLOSE_RESTART_BIST_STATE,
        boardcontrol.restart_bist_actions,
        Transition(lambda ex, st: ex.timeout_occured, CORRECT_FAULT_STATE),
        Transition(lambda ex, st: True, EXPECT_TITLE_OR_DATA_STATE)
    ))

    # Create close bist correct fault state
    experiment.add_state(ExperimentState(
        CLOSE_BIST_CORRECT_FAULT_STATE,
        boardcontrol.close_bist_correct_fault_actions,
        Transition(lambda ex, st: ex.timeout_occured, CORRECT_FAULT_STATE),
        Transition(lambda ex, st: True, FIX_ERRORS_STATE)
    ))

    # Create fix errors state
    experiment.add_state(ExperimentState(
        FIX_ERRORS_STATE,
        boardcontrol.debug_error_actions,
        Transition(lambda ex, st: (ex.timeout_occured_in_debug or ex.failed_to_correct_errors), RESTART_LITEX_STATE),
        Transition(lambda ex, st: True, EXPECT_TITLE_OR_DATA_STATE)
    ))

    # Create correct fault state
    experiment.add_state(ExperimentState(
        CORRECT_FAULT_STATE,
        boardcontrol.correct_fault_actions,
        Transition(lambda ex, st: True, RESTART_LITEX_STATE)
    ))

    experiment.add_state(ExperimentState(
        RESTART_LITEX_STATE,
        boardcontrol.restart_litex_actions,
        Transition(lambda ex, st: ex.restart_success, INJECT_FIRST_FAULT_STATE),
        Transition(lambda ex, st: True, CONFIGURE_FPGA_STATE)
    ))

    experiment.set_next_state(INITIAL_STARTING_STATE)
    return experiment

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--netbooter-port", help="netbooter outlet number that the FPGA is connected to", 
        default=NETBOOTER_PORT, type=int, required=False)
    parser.add_argument("--netbooter-ip", help="Ip address to connect to netbooter", default=NETBOOTER_IP, required=False)
    parser.add_argument("--mem-burst-length", help="Bist memory burst length", default=BURST_LENGTH, type=int, required=False)
    parser.add_argument("--addr-mode", help="Address mode, how Bist should read and write memory: 0=fixed, 1=linear, 2=random", default=RAND_ARG, type=int, required=False)
    args = parser.parse_args()

    # Set BIST settings
    boardcontrol.netbooter_port = args.netbooter_port
    boardcontrol.netbooter_ip = args.netbooter_ip
    boardcontrol.mem_burst_length = args.mem_burst_length
    boardcontrol.addr_mode = args.addr_mode

    # Set up logger settings
    logging.basicConfig(filename="times_20.txt", level=logging.INFO, datefmt=TIME_STRING_FORMAT, 
        format='%(asctime)s %(levelname)-8s %(message)s')
    
    experiment = build_experiment()
    experiment.start()
    print(f"Experiment finished in state: {experiment.get_current_state()}")


if __name__ == "__main__":
    main()


'''
Updated state machine using threads

1. Init state
   - Just a start message
2. Power down JCM and NexysVideo
2. Repower/Reboot JCM (But don't log in - do other steps while the JCM boots)
   - Make sure JCM is in a good state
2. Repower FPGA board
   - We want to start the experiment in a fresh state
3. Initialize UART connection (for UARTBone and UART serial)
  - Force repower the UART connection?
  - Log the UART serial from here out
4. JCM Login
  - Do some pings until the network is up
  - All JCM traffic logged to a dedicated file
5. JCM Configuration
  - This is blocking - we don't move to the next state until this is done.
6. JCM Scrubbing
  - This is a separate thread
     - SCRUBBING_OK global variable set to 1 indicating scrubbing is working correctly.
       - Main thread will periodically check this and jump to a recovery state if it goes to zero
     - If scrubbing fails, this variable is set to zero
       - Scrubber ends, or connection to JCM fails
     - Main thread has a flag CONTINUE_SCRUBBING set to 1
       - Scrubbing thread watches this variable and closes scrubbing and exits thread if this is set to 0     
  - Flag to support scrubbing with and without fault injection
  - Listen to a global variable controlled by the script that indicates when scrubbing should stop
6a. Read UARTBone registers as baseline (and any other baseline values)
7. Connect to litex serial
8. Wait for Litex prompt
9. Send BIST command (initialize error counts)
10. Expect title line actions
11. check_for_errors_state

Error response:

DRAM Errors
- Scrubbing is going on in the background so wait a bit to see if the errors go away
- Scrub mode registers
- scrub delay/bitslip registers
- Recalibrate memory
- Reinitialize memory
- reboot command
- Uartbone reset
- COnfigure
- Repower


CPU Hang:
- Sent Ctrl-C & Enter to see if prompt returns
- Disconnect terminal (SW) and reconnect to see if you can reconnect
- Unpower/repower uart and see if you can connect
- Offline CPU debug
  - Read debug UART bone registers
  - Issue uart bone reset

UART Bone Registers:
- Read PC (twice?)
- MMCM lock toggle count
- MMCM Lock value
- Clock frequency value
- MMCM drp bits?
- Bitslip bits?
- External reset

Questions:
- Do we reset the system over uart bone at the start? (to catch the boot process while the UART is trying to connect)
  - Is there a way to delay bootup? (give connection time)
- Can we do a capture at the end of a hang?
  Capture 1: while clock is running (FFs)
  Capture 2: with reset held to get decent BRAM data (to compare for BRAM upsets)


'''


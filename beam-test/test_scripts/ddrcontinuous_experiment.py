#!/usr/bin/env python3

# Questions?
# - Do I need to give a message at the start of each action? 
# shrec@nuc4.ee.byu.edu (pass:shrec)
# Todo: Need to catch ctrl-c so we can exit JCM safely

import pexpect
import argparse
import telnetlib
import logging
import traceback
#import cffi
import sys
import time
import re
import os
#import numpy as np
import random
import socket
from pathlib import Path
from datetime import datetime
from subprocess import run


from netbooter_control import netbooter_control
from jcm_session import jcm_session
from uart_control import uart_control

from paramiko import SSHClient, SSHException, AutoAddPolicy, \
                    BadHostKeyException, AuthenticationException, buffered_pipe

#from distutils.log import error
from mimetypes import init
from multiprocessing.spawn import old_main_modules
from nis import match
# from this import d
from unittest import result
from urllib.parse import _NetlocResultMixinStr

from pkg_resources import require
# from asyncio.timeouts import timeout
from serial import Serial  # from pyserial
from datetime import date, datetime
from experiment_machine import Transition, ExperimentState, Experiment
from usb_uart_base import usb_uart_base
from usb_uart_bone import usb_uart_bone

# Format string for printing the date and time
TIME_STRING_FORMAT = "%Y-%m-%d %H:%M:%S"
# Number of JCM pings before failure
JCM_PING_COUNT_LIMIT = 10
# JCM Ping Delay
JCM_PING_DELAY = 10

UARTBONE_UART_BASENAME = "uartbone"

NEXYS_VIDEO_BOARDNAME = "nexys_video"
NEXYS4DDR_BOARDNAME = "nexys4ddr"
DATABOARD_BOARDNAME = "databoard"

DEFAULT_PREFIX = "CTRL"
BIST_ERROR_MSG_REGEX = "\d+:  \d+"

DEFAULT_BIST_BURST_LENGTH = 0xfffffff # Default burst length
DEFAULT_BIST_DELAY_SECONDS = 0 # Default number of seconds to delay.
DEFAULT_BIST_ADDR_MODE = 1 # Start reading/writing data with addresses linearly.
DEFAULT_BIST_PATTERN = 0xa5a5a5a4 # Start reading/writing data with addresses linearly.
DEFAULT_DELAY_BIST_STARTING_ADDR = 0x0 # Start the reading/writing at address 0
DEFAULT_DELAY_BIST_LENGTH = 0xfffffff
DEFAULT_BIST_NONCONT_DELAY_SEC = 300

LITEX_LOGIN_DELAY = 12

MAX_ERRORS_TO_DISPLAY = 1000
MAX_BIST_ERRORS_BEFORE_REBOOT = 100
MAX_CONSEC_BAD_TITLES_DATA = 5
MAX_CONSECUTIVE_UNICODE_ERRORS = 20

UARTBONE_RESET_ADDR = 0xf0000800     # csr_base,ctrl
UARTBONE_IDENT_ADDR = 0xf0002000     # csr_base,identifier_mem
UARTBONE_DEBUG_ADDR = 0xf0001800     # csr_base,debug module
UARTBONE_FSM_STATE_ADDR = 0xf00000c8 # csr_base,fsm_state
UARTBONE_DEBUG_I_ADDR = 0x0 


# Timing settings for the Antmicro Datacenter board
class antmicro_databoard():
    
    def __init__(self):
        
        MIN_BIST_TIME_DIFF_SECONDS = 2.5
        LITEX_LOGIN_DELAY = 10
        
        self.execution_speed = MIN_BIST_TIME_DIFF_SECONDS
        self.litex_login_delay = LITEX_LOGIN_DELAY
        
        
# Timing settings for the digilent nexys video board.
class digilent_nexys_video():
    
    def __init__(self):
        
        MIN_BIST_TIME_DIFF_SECONDS = 0.3
        LITEX_LOGIN_DELAY = 10
        
        self.execution_speed = MIN_BIST_TIME_DIFF_SECONDS
        self.litex_login_delay = LITEX_LOGIN_DELAY
        
# Timing settings for the digilent nexys video board.
class digilent_nexys4ddr():
    
    def __init__(self):
        
        MIN_BIST_TIME_DIFF_SECONDS = 0.15
        LITEX_LOGIN_DELAY = 15
        
        self.execution_speed = MIN_BIST_TIME_DIFF_SECONDS
        self.litex_login_delay = LITEX_LOGIN_DELAY
        


class bist_common(object):

    def __init__(self, 
        bist_mem_burst_length:int,
        bist_pattern:int,
        ) -> None:
        ''' Initialize class '''
        self.bist_mem_burst_length = bist_mem_burst_length
        self.bist_pattern = bist_pattern

        self.error_cnt = 0

    def get_bist_pattern_command_str(self):
        '''
        litex> sdram_bist_pat
        sdram_bist_pat <value>
        '''
        cmd_str = "sdram_bist_pat " + str(self.bist_pattern)
        return cmd_str

    def clear_data(self):
        ''' Clear's the error counts of the class.'''
        self.error_cnt = 0

    def new_data_str(self,result_str):
        ''' Evaluates data string. Returns False if no new errors. True with new errors. '''
        error = self.new_errors(result_str)
        if error > 0:
            return True
        return False



class bist_continuous_state(bist_common):
    ''' This class keeps track of the state of a continuously-running bist command '''

    def __init__(self, 
        bist_mem_burst_length:int,
        bist_pattern:int,
        bist_addr_mode:int,
        ):
        self.bist_addr_mode = bist_addr_mode
        bist_common.__init__(self, 
                             bist_mem_burst_length=bist_mem_burst_length,
                             bist_pattern = bist_pattern)

    def get_bist_command_str(self):
        ''' Creates a string for the sdram_bist command (Based on parameters of this object)
        litex> sdram_bist
        sdram_bist <base> <length> [<max_errors>] [<addr_mode>] [<write_mode>] [<error_break>] [<delay>]
        base_addr    : Starting address of BIST
        length       : Number of transactions per read write (1 = 80 bits)
        max_errors   : Max number of errors to display (default: 0)
        addr_mode    : 0=fixed (starts at zero), 1=inc (default: 1)
        write_mode   : 0=read_always, 1=write_once_read_always, 2=write_and_read_always (default: 0)
        error_break  : 0=dont stop BIST if errors found, 1=stop BIST if errors found (default: 0)
        delay        : Number of seconds to delay after each check (default: 0)
        '''
        #cmd_str = "sdram_bist " + str(self.bist_mem_burst_length) + " " + str(self.bist_addr_mode)
        # address_mode = 1 (increment)
        # data_mode = 0 (pattern)
        # write_mode = 2 (write and read)
        cmd_str = "sdram_bist 0x0 " + str(self.bist_mem_burst_length) + " " + str(MAX_ERRORS_TO_DISPLAY) + " 0 1 0 0"
        return cmd_str
    
    def new_errors(self,result_str):
        ''' Evaluates data string. New errors as a tuple. '''
        ERROR_MSG_INDEX = 2 # 7 # Error number at index 7 of matched string

        result_list = result_str.split()
        # print(result_list)
        # print(len(result_list))
        new_error_cnt = int(result_list[len(result_list) - ERROR_MSG_INDEX])
        # new_errors = new_error_cnt - self.error_cnt
        
        # update internal variables
        self.error_cnt = new_error_cnt
        return new_error_cnt #, new_sec_errors, new_ded_errors)






class bist_delay_state(bist_common):
    ''' This class keeps track of the state of multiple non-continuous bist commands '''

    def __init__(self,
                 bist_pattern:int,
                 beg_addr:int = DEFAULT_DELAY_BIST_STARTING_ADDR, 
                 bist_mem_burst_length:int = DEFAULT_DELAY_BIST_LENGTH,
                 ):
        self.beg_addr = beg_addr
        self.length = bist_mem_burst_length
        bist_common.__init__(self, 
                             bist_mem_burst_length=bist_mem_burst_length,
                             bist_pattern = bist_pattern)

    def get_bist_write_command_str(self):
        ''' Creates a string for the sdram_bist_writer command (Based on parameters of this object)
        litex> sdram_bist_writer
        sdram_bist_writer <beginning_address> <length>
        beginning address : Starting address
        length : Length of burst writes to write
        '''
        
        cmd_str = "sdram_bist_writer " + str(self.beg_addr) + " " + str(self.length)
        return cmd_str
    
    def get_bist_read_command_str(self):
        ''' Creates a string for the sdram_bist_writer command (Based on parameters of this object)
        litex> sdram_bist_reader
        sdram_bist_reader <beginning_address> <length> <max_error_out>
        beginning address : Starting address
        length : Length of burst writes to write
        max_error_out: Max number of errors to display (default: 0)
        '''
        
        cmd_str = "sdram_bist_reader " + str(self.beg_addr) + " " + str(self.length) + " " + str(MAX_ERRORS_TO_DISPLAY)
        return cmd_str
    
    def new_errors(self,result_str):
        ''' Evaluates data string. New errors as a tuple. '''
        NONCONT_BIST_LITEX_PROMPT = '\x1b[92;1mlitex\x1b[0m>'
        ERROR_MSG_INDEX_FROM_END = 2

        result_list = result_str.split()
        # print(result_list)

        new_error_cnt = int(result_list[len(result_list) - ERROR_MSG_INDEX_FROM_END])
        # new_errors = new_error_cnt - self.error_cnt
        
        # update internal variables
        self.error_cnt = new_error_cnt
        return new_error_cnt #, new_sec_errors, new_ded_errors)





def signal_handler(sig, frame):
    ''' Ctrl-C handler so we can exit more gracefully. '''
    print('Ctrl+C Pressed. ')
    '''
#!/usr/bin/env python
import signal
import sys

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
signal.pause()
    '''
    sys.exit(0)

def variable_update_experiment_initialization(ex):
    ''' Initializes global variables that are used accross states at the 
    start of the experiment. '''
    ex.failed_initial_login = 0
    ex.unrecoverable = False
    ex.previous_reboot_state = 0 # variable indicating if state machine has attempted reboot

def variable_update_successful_bist(ex):
    ''' Initalize/clear all variables that hold error state between
    states. Used when a successful BIST execution sequence occurs. '''
    # Flag indicating that this is a fresh BIST (not coming in with errors)
    ex.previous_bist_uart_error = False             # Flag indicating a previous BIST system error occured
    ex.previous_bist_data_repair = 0                # variable indicating what repair has been made
    ex.previous_bist_max_consecutive_bad_titles = 0 # variable indicating previous bad title lines occured
    ex.previous_bist_max_consecutive_data_lines = 0 # variable indicating previous bad data lines occured.
    ex.issued_reset = False # Indicates a reset value was recently initiated
    ex.unrecoverable = False

def setup_logger(log_filename:str, include_level = True, print_stdout = False):
    ''' Static method for creating custom loggers '''
    if include_level:
        formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(message)s', datefmt=TIME_STRING_FORMAT)
    else:
        formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt=TIME_STRING_FORMAT)
    try:
        handler = logging.FileHandler(log_filename)
    except (FileNotFoundError) as error:
        print("Logging File "+log_filename+"cannot be opened")
        return None

    handler.setFormatter(formatter)
    logger = logging.getLogger("main_log")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    if print_stdout:
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(formatter)
        logger.addHandler(consoleHandler)

    return logger

def expect_prompt(ex, number_of_enters=1,expect_timeout=LITEX_LOGIN_DELAY):
    ''' Send "Enter" and expects the "litex" prompt (does this once)
        Does NOT set state (state actions should set state)
        Returns True if expect was successful, False otherwise
          Calling functions should query for details about failed expect
    '''
    # Todo: Allow multiple attempts (if boot is slow)
    LITEX_LOGIN_PATTERN = "^.*litex[^>]*> "
    for i in range(number_of_enters):
        ex.uart.sendline("\n\n")
    ex.uart.expect(LITEX_LOGIN_PATTERN,timeout=expect_timeout)
    if ex.uart.has_error():
        return False
    return True

def initial_experiment_logging(ex):
    ''' Logs information at the start of the execution (shared with multiple experiments) '''
    # Print information about the current version of the code (what is committed)
    ex.logger.info("git commit information")
    # Get the commit tag
    p = run( [ 'git', 'show', '--oneline', '-s' ], capture_output=True )
    out = p.stdout.decode().strip()
    ex.logger.info("\tgit commit:"+out)
    # Get the commit information (message and date)
    p = run( [ 'git', 'log', '-1', '--format=%cd', '--date=local' ], capture_output=True )
    out = p.stdout.decode().strip()
    ex.logger.info("\tgit commit date:"+out)
    # Get the current git status (to see if something hadn't been committed)
    p = run( [ 'git', 'status', '--porcelain', ], capture_output=True )
    lines =  p.stdout.decode().strip()
    print(lines)
    if lines and len(lines) > 0:
        ex.logger.info("\tgit status:"+out)
        lines = lines.splitlines()
        for line in lines:
            ex.logger.info("\t\t"+line.strip())

    # Print the value of all the options when the executable was run
    ex.logger.info("Command line information")
    ex.logger.info("\tCommand line:"+str(sys.argv))
    dict_args = vars(ex.args)
    for arg in dict_args:
        ex.logger.info("\targ:"+arg+"="+str(dict_args[arg]))

def initial_starting_state_actions(ex, st):
    ''' Entry point for the experiment. Executed only once. 
        No state change
    '''
    initial_experiment_logging(ex)

def netbooter_setup_state_actions(ex, st):
    ''' Checks for the netbooter network connectivity
        sets: ex.netbooter_ok
    '''
    ex.netbooter_ok = False
    netbooter_ip = ex.args.netbooter_ip
    ex.netbooter = netbooter_control(netbooter_ip,ex.logger)
    if not ex.netbooter.ping_netbooter():
        ex.logger.error("Netbooter not on network")
        return
    ex.netbooter_ok = True

def jcm_setup_state_actions(ex, st):
    ''' Power cycles JCM (if needed), creates JCM log file, creates the JCM object, and opens the JCM
        sets: ex.jcm_ok
    '''

    # TODO: this has been moved to the jcm_session class

    ex.jcm_ok = False
    # First power off JCM (if necessary)
    if ex.args.repower_jcm:
        ex.netbooter.turn_off_port(ex.args.jcm_netbooter_port)
        time.sleep(3)
    # Power on JCM (may already be powered)
    ex.netbooter.turn_on_port(ex.args.jcm_netbooter_port)

    # Create JCM output logger
    jcm_log_filename = create_log_path("JCM",ex.filebasename, ex.log_dir)
    # Create JCM log file
    jcm_log_file = open(jcm_log_filename,"w")
    # TODO: need to close jcm_log_file: where?

    # Create JCM object
    ex.jcm = jcm_session.create_jcm_from_args(ex.args,ex.logger,jcm_log_file,stdout_timeprefix = TIME_STRING_FORMAT)
    # Ping JCM (wait until ping before trying to connect)
    for i in range(JCM_PING_COUNT_LIMIT):
        ping_true = ex.jcm.jcm_ping()
        ex.logger.info(f"JCM ping attempt {i+1}")
        if ping_true:
            break
        time.sleep(JCM_PING_DELAY)
    if not ping_true:
        ex.logger.error("JCM ping failed")
        return
    # Create JCM ssh connection
    if not ex.jcm.open_jcm():
        return
    ex.jcm_ok = True

def uart_setup_state_actions(ex, st):
    # create uart object but do not connect uart

    # Create UART stdout
    uart_log_filename = create_log_path("UART",ex.filebasename, ex.log_dir)
    # Create UART log file
    uart_log_file = open(uart_log_filename,"w")

    # Create UART control object
    ex.uart = uart_control(ex.args.usb_uart_phys_port, ex.args.usb_uart_phys_if, uart_stdout = uart_log_file, logging = ex.logger, timestampformat = TIME_STRING_FORMAT)


def power_board_state_actions(ex, st):
    ''' Power cycle board board (no status) '''
    turn_off_cmd = ex.netbooter.turn_off_port(ex.args.board_netbooter_port)
    turn_on_cmd = ex.netbooter.turn_on_port(ex.args.board_netbooter_port)
    ex.netbooter_ok = turn_off_cmd and turn_on_cmd
    # Initialize global state variables when starting over
    variable_update_experiment_initialization(ex)

def connect_uart_state_actions(ex, st):
    ''' Creates UART std_out path, creates uart_control object, and creates uart spawn fd object
        sets: ex.uart_ok
    '''

    # Create a spawned file handle for reading/writing to the serial port
    serial_fdspawn = ex.uart.create_uart_spawn()
    if not serial_fdspawn:
        return
    ex.uart_ok = True

def configure_board_state_actions(ex, st):
    ''' Configures the board
        sets: ex.configure_ok
    '''

    # Stop scrubbing (if it is going)
    if ex.jcm.is_active():
        ex.jcm.stop_scrub()
        ex.jcm.jcm_thread.join()

    # Print id code
    result = ex.jcm.read_device_dna()
    if not result:
        ex.logger.error("Failed to read DNA")
    else:
        ex.logger.info("Device DNA:"+result[0] +" "+result[1])
    ex.configure_ok = False
    result = ex.jcm.configure_fpga(ex.args.bitstream)
    ex.configure_ok = result

def setup_uartbone_state_actions(ex, st):
    ''' Connects to UART bone
    '''
    if ex.args.no_uart_bone:
        ex.logger.info("Not creating UART bone")
        # ex.uartbone will not exist. All uartbone references should check to see that ex.uartbone exists before accessing
        ex.uartbone = None
        return

    ex.uartbone = usb_uart_bone.create_uartbone_from_args(ex.args, UARTBONE_UART_BASENAME, ex.logger)
    if not ex.uartbone:
        ex.logger.error("Failed to create UART Bone")
    ex.uart_fd = ex.uartbone.create_uart_serial()
    if not ex.uart_fd:
        ex.logger.error("Failed to connect to UART Bone")
    uart_bone_ident_addr = int(ex.args.uart_bone_ident,16)
    try:
        ident_str = ex.uartbone.read_ident(uart_bone_ident_addr)
        ex.logger.info("UARTBONE ID Str="+ident_str)
    except:
        ex.logger.error("UARTBone Timeout")
    # Read the current address in the debug
    try:
        i_addr = ex.uartbone.read(UARTBONE_DEBUG_ADDR + UARTBONE_DEBUG_I_ADDR)
        ex.logger.info(f"UARTBONE I ADDR={i_addr:08X}")
    except:
        ex.logger.error("UARTBone Timeout")

def enable_scrubbing_state_actions(ex, st):
    ''' Starts the scrubber
        sets: ex.scrubbing_ok
    '''

    if ex.args.disable_scrubbing:
        ex.scrubbing_ok = True
        return

    ex.scrubbing_ok = False
    frads_file = None
    if ex.args.frads_file:
        frads_file = ex.args.frads_file
    ITERATIONS = 100_000_000

    if ex.args.fault_injection:
        inject_faults = ex.args.fault_injection
    else:
        inject_faults = 0

    result = ex.jcm.scrub_fpga(iterations=ITERATIONS, frads_file = frads_file, inject_faults = inject_faults, block=False)
    # TODO: do some real checking on scrubbing
    result = True
    ex.scrubbing_ok = result

def initial_litex_prompt_state_actions(ex, st):
    ''' Check for initial litex prompt.         
        sets: ex.login_litex (encapsulates uart issues) 
    '''
    
    # Choose board for timing settings
    if ex.args.test_board_name == NEXYS4DDR_BOARDNAME:
        ex.board = digilent_nexys4ddr()
    elif ex.args.test_board_name == NEXYS_VIDEO_BOARDNAME:
        ex.board = digilent_nexys_video()
    elif ex.args.test_board_name == DATABOARD_BOARDNAME:
        ex.board = antmicro_databoard()
    
    MAX_LOGIN_ATTEMPS = 3
    ex.login_litex = False
    ex.initial_login_terminate = False
    expect_result = expect_prompt(ex, expect_timeout = ex.board.litex_login_delay)
    if expect_result:
        # All is good - move on
        ex.login_litex = True
        ex.failed_initial_login = 0  # Reset counter for next time around
    else:
        # Failed login, go back to repower the board until max attempts
        if ex.failed_initial_login >= MAX_LOGIN_ATTEMPS:
            # Failed too many times - give up
            ex.initial_login_terminate = True
        else:
            # Try again
            ex.failed_initial_login += 1

def start_bist_state_actions(ex, st):
    ''' Issues the BIST command
        sets: does not impact state
    '''

    # Choose a class based on desired mode
    if ex.args.continuous_bist_mode:
        ex.bist = bist_continuous_state(
            bist_mem_burst_length = ex.args.bist_mem_burst_length, 
            bist_addr_mode = ex.args.bist_addr_mode, 
            bist_pattern = ex.args.bist_pattern)
    else:
        ex.bist = bist_delay_state(
            bist_mem_burst_length = ex.args.bist_mem_burst_length, 
            bist_pattern = ex.args.bist_pattern,
        )

    # Send initial bist pattern
    bist_command = ex.bist.get_bist_pattern_command_str()
    result = ex.uart.sendline(bist_command)
    expect_result = expect_prompt(ex)

    # For the noncontinuous mode, finish here and send the 
    # first command in the next state, else send a continuous
    # BIST command to the controller.
        
    if ex.args.continuous_bist_mode:
        # Send initial bist command
        bist_command = ex.bist.get_bist_command_str()
        result = ex.uart.sendline(bist_command)
    
    # Initialize all cross state variables
    variable_update_successful_bist(ex)
    

def bist_execution_continuous_state_actions(ex, st):
    ''' Watch the execution of the BIST command and respond to errors. 
    The experiment should operate in this state for most of the time. 
    sets:
        sets: uart_ok (uart_errors), dram_error, reconfigure
    '''

    expecting_title = True # State variable: when we should expect to see a title line
    # Clear internal consecutive error counters
    consecutive_unicode_errors = 0
    consecutive_bad_title_lines = 0
    consecutive_bad_data_lines = 0
    consecutive_data_errors = 0
    total_bist_error_messages = 0

    # Set to False with system errors (bad text/timeouts)
    ex.uart_ok = True
    ex.bist_error = False
    ex.dram_error = False
    ex.bist_error_max = False
    # Initialize the BIST data error counters
    ex.bist.clear_data()
    # Flag counting valid data lines during BIST execution
    valid_data_lines = 0
    first_title_line = True  # no check on data for first title line
    last_successful_bist = None # Time stamp when last BIST completed

    # BIST title line
    #^M                          WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED
    #BIST_TITLE_REGEX = "WR-BW\(MiB/s\) RD-BW\(MiB/s\)  TESTED\(MiB\)     ERRORS        SEC        DED"
    # BIST_TITLE_REGEX = "WR-BW\(MiB/s\) RD-BW\(MiB/s\)  TESTED\(MiB\)     ERRORS(        SEC        DED)?"
    BIST_TITLE_REGEX = " WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED\(MiB/s\)  RD-SPEED\(MiB/s\)      ADDRESSES TESTED     ERRORS"
    # BIST data line
    #^M                                   646          654          324          0          0          0
    BIST_DATA_REGEX = "\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+"
    #ERRORS (CPU): 0
    # BIST_ERROR_MSG_REGEX = "ERRORS (CPU): (\d+)"


    BIST_TEXT_DELAY = 15
    MAX_CONSECUTIVE_BAD_TITLE_LINES = 10
    MAX_CONSECUTIVE_BAD_DATA_LINES = 10
    MAX_CONSECUTIVE_BAD_DATA_ERRORS = 8
    DRAM_ERROR_THRESHOLD = 100

    # Iterate over lines until an error occurs (will need to break out on an error condition)
    while(1):

        # Constants indicating position in regex array of each expression
        TITLE_INDEX=0
        DATA_INDEX=1
        ERROR_MSG_INDEX=2

        # Get a line of data
        match_index = ex.uart.expect([BIST_TITLE_REGEX,BIST_DATA_REGEX,BIST_ERROR_MSG_REGEX],timeout=BIST_TEXT_DELAY)
        # print("Match index: ", match_index)

        # Process expect system errors
        if ex.uart.has_uart_error():
            # General UART errors (Timeout, etc)
            ex.uart_ok = False # State change to repair uart
            return 

        elif ex.uart.unicode_error:
            # Unicode errors over UART (look for a consecutive number of them)
            consecutive_unicode_errors += 1
            if consecutive_unicode_errors == 1:
                ex.logger.info("BIST:First Unicode Error")
                # Don't process this unicode error line
                continue
            elif consecutive_unicode_errors >= MAX_CONSECUTIVE_UNICODE_ERRORS:
                ex.logger.error("BIST:Max Consecitive Unicode Errors:",consecutive_unicode_errors)
                ex.uart_ok = False # State change to repair uart
                return
        else:
            # No UART/system errors at this point
            # Clear any unicode flags and go to title state 
            #  (not sure where we are in bist execution - will likely get data errors after this)
            if consecutive_unicode_errors > 0:
                consecutive_unicode_errors == 0
                expecting_title = True # Start looking or titles (may get errors)

        # No system errors in string - evaluate the string
        if expecting_title: 
            # print("Expecting title")
            
            # is this an error message line? If so, ignore
            if ex.uart.serial_fdspawn.match and match_index == ERROR_MSG_INDEX:
                # print("ERR MSG")
                continue

            # Is this a valid title line?
            if ex.uart.serial_fdspawn.match and match_index == TITLE_INDEX:
                # execpting a title and received a title

                # Determine what annotation to give to header message:
                # "first" if first title line "ok"=executed 8 good data lines, 1-7 ()
                if first_title_line:
                    bist_status = "first"
                    first_title_line = False
                else:
                    if valid_data_lines == 9:
                        # received 8 valid data lines
                        bist_status = "ok"
                        ###############################
                        # Successful execution of BIST: clear all error hoistory
                        ###############################

                        # there is a failure mode in which the BIST completes much faster than it should.
                        # Check to make sure that the BIST delay is greater than some minimum.
                        current_successful_bist = datetime.now()
                        if last_successful_bist:  # Has there been a first successful bist?
                            # Compute delay between now and 
                            bist_time_difference = current_successful_bist - last_successful_bist
                            # If the BIST occurred too quickly, exit and start over
                            execution_diff = bist_time_difference.total_seconds()
                            if execution_diff < ex.board.execution_speed:
                                ex.logger.error(f"BIST: Execution completed too fast ({execution_diff} s)")
                                ex.bist_error = True
                                return
                        else: # this is the first successful bist
                            last_successful_bist = datetime.now()
                        # Update the last successful bist time
                        last_successful_bist = current_successful_bist
                        variable_update_successful_bist(ex)
                        variable_update_experiment_initialization(ex)
                    else:
                        errors = 8 - valid_data_lines
                        bist_status = f"err {errors}"
                valid_data_lines = 0  # Clear valid data lines for next iteration
                
                # Print message indicating status of header
                ex.logger.info(f"BIST:Header ({bist_status})")
                expecting_title = False # Now expecting data
                consecutive_bad_title_lines = 0 # Clear any bad title line errors
                DataLineNumber = 0 # initialize data counter
                continue
            else: # have an invalid title line
                consecutive_bad_title_lines += 1
                ex.logger.info(f"BIST:Bad title line ({consecutive_bad_title_lines}):"+ex.uart.serial_fdspawn.match.group(0))
                if ex.previous_bist_max_consecutive_bad_titles >= MAX_CONSEC_BAD_TITLES_DATA:
                    ex.logger.error("BIST:Max consecutive times of consecutive bad title lines reached (no. {lines})".format(lines = ex.previous_bist_max_consecutive_bad_titles))
                    ex.bist_error_max = True
                    break
                if consecutive_bad_title_lines > MAX_CONSECUTIVE_BAD_TITLE_LINES:
                    ex.previous_bist_max_consecutive_bad_titles += 1
                    ex.logger.error("BIST:Max consecutive bad title lines (no. {lines})".format(lines = ex.previous_bist_max_consecutive_bad_titles))
                    ex.bist_error = True # System error: will go to a recovery state
                    break
                # Skip to next line for bad title
                continue

        else: # Expecting Data
            # print("expecting data")

            # is this an error message line? If so, ignore
            if ex.uart.serial_fdspawn.match and match_index == ERROR_MSG_INDEX:
                # print("ERR MSG")
                continue

            if ex.uart.serial_fdspawn.match and match_index == DATA_INDEX:
                # execpting data and received valid data line
                expect_str = ex.uart.serial_fdspawn.match.group(0)
                DataLineNumber += 1
                if DataLineNumber == 9: 
                    expecting_title = True # Now expecting title
                # Check for data errors
                # (err,sec,ded) = ex.bist.new_errors(expect_str)
                (err) = ex.bist.new_errors(expect_str)
                total_errors = err #+sec+ded
                if total_errors > 0:            
                    consecutive_data_errors += 1
                    # ex.logger.error(f"BIST:Data Errors ({err},{sec},{ded}:{total_errors}/{consecutive_data_errors}-{total_bist_error_messages})")
                    ex.logger.error(f"BIST:Data Errors ({err}:{total_errors}/{consecutive_data_errors}-{total_bist_error_messages})")
                    ex.logger.error(f"BIST: expect string:{expect_str}")
                    # print(ex.uart.serial_fdspawn.match.group(0))
                    total_bist_error_messages += 1
                    if total_bist_error_messages >= MAX_BIST_ERRORS_BEFORE_REBOOT:
                        # Reboot
                        ex.logger.error(f"BIST:Max BIST Errors reached")
                        ex.bist_error_max = True


                    #if (total_errors) > DRAM_ERROR_THRESHOLD or \
                    #    consecutive_data_errors >= MAX_CONSECUTIVE_BAD_DATA_ERRORS:
                    if consecutive_data_errors >= MAX_CONSECUTIVE_BAD_DATA_ERRORS:
                        # Need to repair data errors
                        ex.dram_error = True
                        return
                else: # no new errors
                    valid_data_lines += 1
                    consecutive_data_errors = 0 # Clear consecutive error flag
                    continue

            else: # bad data line
                consecutive_bad_data_lines += 1
                ex.logger.info(f"BIST:Bad data line ({consecutive_bad_data_lines})")
                if (ex.previous_bist_max_consecutive_data_lines >= MAX_CONSEC_BAD_TITLES_DATA):
                    ex.logger.error("BIST:Max consecutive times of consecutive bad data lines reached (no. {lines})".format(lines = ex.previous_bist_max_consecutive_data_lines))
                    ex.bist_error_max = True 
                    break
                if consecutive_bad_data_lines >= MAX_CONSECUTIVE_BAD_DATA_LINES:
                    ex.previous_bist_max_consecutive_data_lines += 1
                    ex.logger.error("BIST:Max consecutive bad data lines (no. {lines})".format(lines = ex.previous_bist_max_consecutive_data_lines))
                    ex.bist_error = True # System error: will go to a recovery state
                    break



def bist_execution_delay_state_actions(ex, st):
    ''' 
    Continually send non-continuous BIST commands to the DRAM.

    Watch the execution of the BIST command and respond to errors. 
    The experiment should operate in this state for most of the time. 
    sets:
        sets: uart_ok (uart_errors), dram_error, reconfigure
    '''
    BIST_SINGLECMD_DELAY = 30
    BIST_TITLE_DATA_REGEX = " WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED\(MiB\/s\)  RD-SPEED\(MiB\/s\)      ADDRESSES TESTED     ERRORS\n\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+0x[0-9a-fA-F]{7}-0x[0-9a-fA-F]{7}\s+\d+"
    LITEX_LOGIN_PATTERN = "^.*litex[^>]*> "
    LITEX_LOGIN_PATTERN_INDEX = 0
    ERR_DISPLAY_INDEX = 1
    DLAY_STATE_MAX_CONSECUTIVE_BAD_DATA_ERRORS = 3

    delay_state_consecutive_bad_data_lines = 0
    consecutive_data_errors = 0
    ex.delay_state_uart_ok = True
    ex.delay_state_consecutive_unicode_errors = 0
    ex.bist_max_error = False
    
    
    # Concatenate everything to check for UART errors in one function.
    def check_for_uart_errors(ex):
        
        # Process expect system errors
        if ex.uart.has_uart_error():
            # General UART errors (Timeout, etc)
            ex.delay_state_uart_ok = False # State change to repair uart
            return False

        elif ex.uart.unicode_error:
            # Unicode errors over UART (look for a consecutive number of them)
            ex.delay_state_consecutive_unicode_errors += 1
            if ex.delay_state_consecutive_unicode_errors == 1:
                ex.logger.info("BIST:First Unicode Error")
                # Don't process this unicode error line
                return None
            elif ex.delay_state_consecutive_unicode_errors >= MAX_CONSECUTIVE_UNICODE_ERRORS:
                ex.logger.error("BIST:Max Consecitive Unicode Errors:",ex.delay_state_consecutive_unicode_errors)
            ex.delay_state_uart_ok = False # State change to repair uart
            return False
        else:
            if ex.delay_state_consecutive_unicode_errors > 0:
                ex.delay_state_consecutive_unicode_errors == 0
        return True
        
        
    #Initially print out the delay of this state in seconds
    ex.logger.info("BIST:Starting delay state machine ({time} second delay)".format(time = ex.args.noncontinuous_bist_delay))

    while(1):

        ex.logger.info("BIST:Starting Writer")
        # # Start by sending a write command, expect result back.
        # bist_command = ex.bist.get_bist_write_command_str()
        # result = ex.uart.sendline(bist_command)

        # match_index = ex.uart.expect([LITEX_LOGIN_PATTERN],timeout=BIST_SINGLECMD_DELAY)
        
        # uart_result = check_for_uart_errors(ex)
        # # If timeout, EOF, or many unicode errors occur, exit.
        # if uart_result == False:
        #     return
        # # If one unicode error occurs, try again.
        # elif uart_result == None:
        #     continue
        
        if True:# (ex.uart.serial_fdspawn.match and 
            # match_index == LITEX_LOGIN_PATTERN_INDEX and
            # re.search(BIST_TITLE_DATA_REGEX, ex.uart.serial_fdspawn.match.group(0)) != None):
            ex.logger.info("BIST:Writer successful")
            delay_state_consecutive_bad_data_lines = 0
            
        else:
            delay_state_consecutive_bad_data_lines += 1
            ex.logger.info(f"BIST:Bad data (match_index:{match_index}):({delay_state_consecutive_bad_data_lines}):"+ex.uart.serial_fdspawn.match.group(0))
            
            if (delay_state_consecutive_bad_data_lines >= DLAY_STATE_MAX_CONSECUTIVE_BAD_DATA_ERRORS):
                ex.logger.error("BIST:Max consecutive bad data lines reached")
                ex.bist_max_error = True
                return
            continue
        
        while(1):
            
            ex.logger.info("BIST:Starting Reader")
            # Send a read command, expect result back.
            bist_command = ex.bist.get_bist_read_command_str()
            result = ex.uart.sendline(bist_command)

            time.sleep(1)
            
            match_index = ex.uart.expect([LITEX_LOGIN_PATTERN, BIST_ERROR_MSG_REGEX],timeout=BIST_SINGLECMD_DELAY)

            # If errors are displayed, ignore until the litex prompt appears
            while(match_index == ERR_DISPLAY_INDEX):
                match_index = ex.uart.expect([LITEX_LOGIN_PATTERN, BIST_ERROR_MSG_REGEX],timeout=BIST_SINGLECMD_DELAY)
            
            uart_result = check_for_uart_errors(ex)
            if uart_result == False:
                return
            elif uart_result == None:
                continue

            # Check for a match and that it matches the correct index
            if(ex.uart.serial_fdspawn.match and 
               match_index == LITEX_LOGIN_PATTERN_INDEX and
               re.search(BIST_TITLE_DATA_REGEX, ex.uart.serial_fdspawn.match.group(0)) != None):

                ex.logger.info("BIST:Reader successful")

                # Get the matched string
                expect_str = ex.uart.serial_fdspawn.match.group(0)

                # Get the new errors
                (err) = ex.bist.new_errors(expect_str)

                # If errors found, display string
                if err > 0:
                    consecutive_data_errors += 1

                    ex.logger.error(f"BIST:Data Errors ({err}:{err}/{consecutive_data_errors})")
                    # ex.logger.error(f"BIST: expect string:{expect_str}")
                    # print(ex.uart.serial_fdspawn.match.group(0))

                    if consecutive_data_errors >= DLAY_STATE_MAX_CONSECUTIVE_BAD_DATA_ERRORS:
                        # Need to repair data errors
                        ex.dram_error = True
                        return
                    
                    break

                else: # no new errors
                    consecutive_data_errors = 0 # Clear consecutive error flag
                    ex.logger.info("BIST:Delay for {delay} seconds".format(delay = ex.args.noncontinuous_bist_delay))
                    time.sleep(ex.args.noncontinuous_bist_delay)
                    continue
            else:
                delay_state_consecutive_bad_data_lines += 1
                ex.logger.info(f"BIST:Bad data (match_index:{match_index}):({delay_state_consecutive_bad_data_lines}):"+ex.uart.serial_fdspawn.match.group(0))
                
                if (delay_state_consecutive_bad_data_lines >= DLAY_STATE_MAX_CONSECUTIVE_BAD_DATA_ERRORS):
                    ex.logger.error("BIST:Max consecutive bad data lines reached")
                    ex.bist_max_error = True
                    break
                continue
                    


            scrubbing_flag = False


def reboot_state_actions(ex, st):
    '''
    Set of methods to run a reboot cmd. Board is reconfigured if 
    '''
    
    NO_REBOOT_ATTEMPT = 0
    ATTEMPTED_REBOOT_CMD = 1
    ATTEMPTED_REBOOT_UARTBONE = 2

    
    ex.uart_ok = True
    ex.reboot_uartbone = False
    ex.reconfigure = False
    
    # Stop BIST command
    ex.uart.sendline("\n\n")
    
    # Expect Litex Prompt
    expect_result = expect_prompt(ex)
    if not expect_result:
        ex.uart_ok = False
        return
    
    if ex.previous_reboot_state == NO_REBOOT_ATTEMPT:
        ex.logger.info("BIST:Reboot")
        ex.previous_reboot_state = ATTEMPTED_REBOOT_CMD
        # ex.previous_bist_data_repair = DRAM_REBOOT_STEP
        ex.uart.sendline("reboot")
        if not expect_prompt(ex):
            ex.uart_ok = False
        return
    elif ex.previous_reboot_state == ATTEMPTED_REBOOT_CMD:
        ex.logger.info("BIST:Previous reboot cmd attempted, using uartbone")
        ex.previous_reboot_state = ATTEMPTED_REBOOT_UARTBONE
        ex.reboot_uartbone = True
        return
    else:
        ex.logger.info("BIST:Reboot methods attempted, reconfiguring")
        ex.reconfigure = True
        return

    

def dram_recovery_state_actions(ex, st):
    ''' 
    Attempts to repair the DRAM interface
    '''
    ex.uart_ok = True
    ex.reboot = False
    # Stop BIST command
    ex.uart.sendline("\n\n")
    # Search for Litex prompt
    expect_result = expect_prompt(ex)
    if not expect_result:
        ex.uart_ok = False
        return

    NO_BIST_ERROR = 0
    RESTART_BIST_STEP = 1
    DRAM_MR_SCRUB_STEP = 2
    DRAM_DELAY_SCRUB_STEP = 3
    DRAM_CALIBRATE_STEP = 4
    DRAM_INIT_STEP = 5

    ex.logger.info(f"BIST:Recovery level={ex.previous_bist_data_repair}")

    if ex.previous_bist_data_repair == NO_BIST_ERROR:
        # This is the first repair for data
        ex.logger.info("BIST:Restart BIST")
        ex.previous_bist_data_repair = RESTART_BIST_STEP
        return
    elif ex.previous_bist_data_repair == RESTART_BIST_STEP:
        ex.logger.info("BIST:SDRAM MR Scrub")
        ex.previous_bist_data_repair = DRAM_MR_SCRUB_STEP
        ex.uart.sendline("sdram_mr_scrub")
        if not expect_prompt(ex):
            ex.uart_ok = False
        return
    elif ex.previous_bist_data_repair == DRAM_MR_SCRUB_STEP:
        ex.logger.info("BIST:SDRAM Delay Scrub")
        ex.previous_bist_data_repair = DRAM_DELAY_SCRUB_STEP
        ex.uart.sendline("sdram_delay_scrub")
        if not expect_prompt(ex):
            ex.uart_ok = False
        return
    elif ex.previous_bist_data_repair == DRAM_DELAY_SCRUB_STEP:
        ex.logger.info("BIST:SDRAM Calibrate Scrub")
        ex.previous_bist_data_repair = DRAM_CALIBRATE_STEP
        ex.uart.sendline("sdram_cal")
        if not expect_prompt(ex):
            ex.uart_ok = False
        return
    elif ex.previous_bist_data_repair == DRAM_CALIBRATE_STEP:
        ex.logger.info("BIST:SDRAM INIT Scrub")
        ex.previous_bist_data_repair = DRAM_INIT_STEP
        ex.uart.sendline("sdram_init")
        if not expect_prompt(ex):
            ex.uart_ok = False
        return
    elif ex.previous_bist_data_repair == DRAM_INIT_STEP:
        ex.logger.info("BIST:Failed all scrubbing commands - reboot")
        ex.reboot = True
        return

    # If I get here, we have exhausted all tests. Just reconfigure
    # ex.logger.info("BIST:Failed all recovery - reconfigure")
    # ex.reconfigure = True

def bist_recovery_state_actions(ex, st):
    ''' This action is performed when the BIST command is acting up and we want
    to try and restart it. If the UART fails, try to recover the terminal,
    otherwise continue with the bist command.
    '''
    ex.uart_ok = True
    # Send a few new lines to try to stop the BIST command
    ex.uart.sendline("\n\n\n")
    time.sleep(1)
    # Search for Litex prompt
    expect_result = expect_prompt(ex)
    if not expect_result:
        ex.uart_ok = False
        return
    
    # Set BIST pattern command
    bist_command = ex.bist.get_bist_pattern_command_str()
    result = ex.uart.sendline(bist_command + "\n\n")
    expect_result = expect_prompt(ex)
    if not expect_result:
        ex.uart_ok = False
        return

    # Restart BIST command (if in continuous mode)
    if ex.args.continuous_bist_mode:
        bist_command = ex.bist.get_bist_command_str()
        result = ex.uart.sendline(bist_command)

def terminal_recovery_state_actions(ex, st):
    ''' This action is performed when there was some sort of UART problem. 
    The purpose of this action is to try and repair the UART connection.
    If it succeeds, the BIST command should be restarted.
    If it fails, it moves to a new recovery state.
    At the end of this state the uart connection is still open
    
    Try to reconnect the terminal: close, reopen, and get login prompt. 
    sets the ex.uart_ok, ex.login_litex
    '''
    # Close the existing serial port (and spawn object)
    ex.uart.close_uart_serial()   
    ex.login_litex = False
    ex.uart_ok = False
    time.sleep(1)

    # Check previous uart error. If so, then just reconfigure
    if ex.previous_bist_uart_error:
        return # uart_ok flag is False causing failure
    ex.previous_bist_uart_error = True

    # Create a spawned file handle for reading/writing to the serial port
    serial_fdspawn = ex.uart.create_uart_spawn()
    if not serial_fdspawn:
        # Failed uart: shouldn't get here unless there is a connection issue
        return
    ex.uart_ok = True
    # Search for Litex prompt
    expect_result = expect_prompt(ex)
    if not expect_result:
        # Exit without closing the uart
        return
    ex.login_litex = True
    # Set BIST pattern command
    bist_command = ex.bist.get_bist_pattern_command_str()
    result = ex.uart.sendline(bist_command)
    expect_result = expect_prompt(ex)
    if not expect_result:
        ex.uart_ok = False
        return
    # Restart BIST command (if in continuous mode)
    if ex.args.continuous_bist_mode:
        bist_command = ex.bist.get_bist_command_str()
        result = ex.uart.sendline(bist_command)

def reset_recovery_state_actions(ex, st):

    # Enter this state from the terminal recovery state in error
    # where the UART is inactive.

    if ex.uartbone:
        try:
            i_addr = ex.uartbone.read(UARTBONE_DEBUG_ADDR + UARTBONE_DEBUG_I_ADDR)
            ex.logger.info(f"UARTBONE I ADDR={i_addr:08X}")
        except (RuntimeError) as error:
            ex.logger.error("UARTBone Timeout")
    else:
        ex.logger.info("No UARTBONE for I ADDR read")

    # Was a reset issued previously? If so, previous reset failed
    if ex.issued_reset:
        ex.logger.info("Previous reset recovery failed")
        ex.unrecoverable = True
    # Make sure we have a UARTbone
    if not ex.uartbone:
        ex.logger.info("No UART bone available for reset")
        ex.unrecoverable = True
        return

    # See if we have an open UART connection
    if not ex.uart.serial_fd:
        ex.logger.info("UART not available for reset recovery")
        ex.unrecoverable = True
        return

    # Issue the reset
    ex.issued_reset = True
    ex.logger.info("Issuing UART bone reset")
    ex.uartbone.write(UARTBONE_RESET_ADDR, 1)
    time.sleep(1)

    if ex.uartbone:
        try:
            i_addr = ex.uartbone.read(UARTBONE_DEBUG_ADDR + UARTBONE_DEBUG_I_ADDR)
            ex.logger.info(f"UARTBONE I ADDR={i_addr:08X}")
        except (RuntimeError) as error:
            ex.logger.error("UARTBone Timeout")


def unrecoverable_postmortum_state_actions(ex, st):
    '''
    TODO:
    - Add steps for figuring out what happened here (uart_bone, readback, etc.)
    - Reconfigure/Repower
    '''

    # Close the UART
    ex.uart.close_uart_serial()

    # at this point, the previous reset didn't work (or wasn't issued).
    # stop scrubbing and reconfigure

    # ex.jcm.stop_scrub()

def terminating_state_actions(ex, st):
    ''' Terminates experiment
        no state change
    '''
    # # Stop scrubbing (if it is going)
    # if ex.jcm.is_active():
    #     ex.jcm.stop_scrub()
    #     ex.jcm.jcm_thread.join()

    # # Close the JCM (if it was setup properly)
    # if ex.jcm_ok:
    #     ex.jcm.close_jcm()

    # Close the uart?

    ex.stop()

def build_experiment(args,logger,single_step=False):
    '''
    Builds the experiment object and its related states for the experiment state machine.
    '''

    # State constants
    INITIAL_STARTING_STATE = "Initial Starting State"
    NETBOOTER_SETUP_STATE = "Netbooter Setup State"
    JCM_SETUP_STATE = "JCM Setup State"
    UART_SETUP_STATE = "UART Setup State"
    POWER_BOARD_STATE = "Power Board State"
    CONNECT_UART_STATE = "Connect UART State"
    CONFIGURE_BOARD_STATE = "Configure Board State"
    SETUP_UARTBONE_STATE = "Setup UARTBone State"
    ENABLE_SCRUBBING_STATE = "Enable Scrubbing State"
    LITEX_PROMPT_STATE = "LiteX Login State"
    START_BIST_DELAY_STATE = "Start BIST Delay State"
    BIST_EXECUTION_DELAY_STATE = "BIST Execution Delay State"
    START_BIST_CONTINUOUS_STATE = "Start BIST Continuous State"
    BIST_EXECUTION_CONTINUOUS_STATE = "BIST Execution Continuous State"
    TERMINAL_RECOVERY_STATE = "Terminal Recovery State"
    REBOOT_RECOVERY_STATE = "Reboot Recovery State"
    RESET_RECOVERY_STATE = "Reset Recovery State"
    BIST_RECOVERY_STATE = "BIST Recovery State"
    DRAM_RECOVERY_STATE = "DRAM Recovery State"
    UNRECOVERABLE_POSTMORTUM_STATE = "Unrecoverable Postmortum State"

    TERMINATING_STATE = "Terminating State"

    # Create a new experiment object
    experiment = Experiment(logger,single_step=single_step)

    # Save the arguments
    experiment.args = args
    experiment.logger = logger


    # INITIAL_STARTING_STATE
    # - Do nothing: place holder for start
    experiment.add_state(ExperimentState(
        INITIAL_STARTING_STATE,
        initial_starting_state_actions,
        Transition(lambda ex, st: True, NETBOOTER_SETUP_STATE)
    ))

    # No netbooter for now 

    # NETBOOTER_SETUP_STATE
    # - Check for netbooter and initialize data structures. Make sure it responds on the network
    experiment.add_state(ExperimentState(
        NETBOOTER_SETUP_STATE,
        netbooter_setup_state_actions,
        Transition(lambda ex, st: ex.netbooter_ok, UART_SETUP_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # No JCM for now

    # # JCM_SETUP_STATE
    # # - Intialize JCM data structure, repower (if necessary), and create connection
    # experiment.add_state(ExperimentState(
    #     JCM_SETUP_STATE,
    #     jcm_setup_state_actions,
    #     Transition(lambda ex, st: ex.jcm_ok, UART_SETUP_STATE),
    #     Transition(lambda ex, st: True, TERMINATING_STATE)
    # ))

    # UART_SETUP_STATE
    # - Intialize JCM data structure, repower (if necessary), and create connection
    experiment.add_state(ExperimentState(
        UART_SETUP_STATE,
        uart_setup_state_actions,
        Transition(lambda ex, st: True, POWER_BOARD_STATE)
    ))

    # No netbooter for now

    # POWER_BOARD_STATE
    # - Intialize JCM data structure, repower (if necessary), and create connection
    experiment.add_state(ExperimentState(
        POWER_BOARD_STATE,
        power_board_state_actions,
        Transition(lambda ex, st: ex.netbooter_ok, CONNECT_UART_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # CONNECT_UART_STATE
    # - Connect the UART
    experiment.add_state(ExperimentState(
        CONNECT_UART_STATE,
        connect_uart_state_actions,
        Transition(lambda ex, st: ex.uart_ok, SETUP_UARTBONE_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # # CONFIGURE_BOARD_STATE
    # # - Configure FPGA
    # experiment.add_state(ExperimentState(
    #     CONFIGURE_BOARD_STATE,
    #     configure_board_state_actions,
    #     Transition(lambda ex, st: ex.configure_ok, SETUP_UARTBONE_STATE),
    #     Transition(lambda ex, st: True, TERMINATING_STATE)
    # ))

    # SETUP_UARTBONE_STATE
    experiment.add_state(ExperimentState(
        SETUP_UARTBONE_STATE,
        setup_uartbone_state_actions,
        #Transition(lambda ex, st: ex.configure_ok, ENABLE_SCRUBBING_STATE),
        Transition(lambda ex, st: True, LITEX_PROMPT_STATE) #ENABLE_SCRUBBING_STATE)
    ))

    # # ENABLE_SCRUBBING_STATE
    # # - Turn on scrubbing
    # experiment.add_state(ExperimentState(
    #     ENABLE_SCRUBBING_STATE,
    #     enable_scrubbing_state_actions,
    #     Transition(lambda ex, st: ex.scrubbing_ok, LITEX_PROMPT_STATE),
    #     Transition(lambda ex, st: True, TERMINATING_STATE)
    # ))

    # LITEX_PROMPT_STATE
    # - Wait for LITEX login
    experiment.add_state(ExperimentState(
        LITEX_PROMPT_STATE,
        initial_litex_prompt_state_actions,
        Transition(lambda ex, st: ex.login_litex, START_BIST_CONTINUOUS_STATE),
        Transition(lambda ex, st: not ex.initial_login_terminate, POWER_BOARD_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # START_BIST_CONTINUOUS_STATE
    # - Start BIST command
    experiment.add_state(ExperimentState(
        START_BIST_CONTINUOUS_STATE,
        start_bist_state_actions,
        Transition(lambda ex, st: ex.args.continuous_bist_mode, BIST_EXECUTION_CONTINUOUS_STATE),
        Transition(lambda ex, st: True, BIST_EXECUTION_DELAY_STATE)
    ))

    ############################################################################################
    # Added states for non-continuous mode
    ############################################################################################

    # BIST_EXECUTION_DELAY_STATE
    # - Process an execution of the BIST
    experiment.add_state(ExperimentState(
        BIST_EXECUTION_DELAY_STATE,
        bist_execution_delay_state_actions,
        Transition(lambda ex, st: ex.bist_max_error, REBOOT_RECOVERY_STATE), 
        Transition(lambda ex, st: not ex.delay_state_uart_ok, TERMINAL_RECOVERY_STATE),        
        Transition(lambda ex, st: ex.dram_error, DRAM_RECOVERY_STATE),
        # Shouldn't get here
        Transition(lambda ex, st: True, UNRECOVERABLE_POSTMORTUM_STATE)
    ))

    ############################################################################################

    ############################################################################################
    # Original states for continuous mode
    ############################################################################################

    # BIST_EXECUTION_CONTINUOUS_STATE
    # - Process an execution of the BIST
    experiment.add_state(ExperimentState(
        BIST_EXECUTION_CONTINUOUS_STATE,
        bist_execution_continuous_state_actions,
        Transition(lambda ex, st: ex.bist_error_max, REBOOT_RECOVERY_STATE), 
        Transition(lambda ex, st: not ex.uart_ok, TERMINAL_RECOVERY_STATE),        
        Transition(lambda ex, st: ex.bist_error, BIST_RECOVERY_STATE),
        Transition(lambda ex, st: ex.dram_error, DRAM_RECOVERY_STATE),
        # Shouldn't get here
        Transition(lambda ex, st: True, UNRECOVERABLE_POSTMORTUM_STATE)
    ))

    ############################################################################################

    # DRAM_RECOVERY_STATE
    experiment.add_state(ExperimentState(
        DRAM_RECOVERY_STATE,
        dram_recovery_state_actions,
        Transition(lambda ex, st: ex.reboot, REBOOT_RECOVERY_STATE),
        Transition(lambda ex, st: ex.uart_ok, BIST_RECOVERY_STATE),
        Transition(lambda ex, st: not ex.uart_ok, UNRECOVERABLE_POSTMORTUM_STATE),
        Transition(lambda ex, st: True, UNRECOVERABLE_POSTMORTUM_STATE)
    ))
    
    experiment.add_state(ExperimentState(
        REBOOT_RECOVERY_STATE,
        reboot_state_actions,
        Transition(lambda ex, st: not ex.uart_ok, TERMINAL_RECOVERY_STATE),
        Transition(lambda ex, st: ex.reboot_uartbone, RESET_RECOVERY_STATE),
        Transition(lambda ex, st: ex.reconfigure, UNRECOVERABLE_POSTMORTUM_STATE),
        # Shouldn't get here
        Transition(lambda ex, st: True, BIST_RECOVERY_STATE)
    ))

    # BIST_RECOVERY_STATE
    experiment.add_state(ExperimentState(
        BIST_RECOVERY_STATE,
        bist_recovery_state_actions,
        Transition(lambda ex, st: ex.uart_ok and ex.args.continuous_bist_mode, BIST_EXECUTION_CONTINUOUS_STATE),
        Transition(lambda ex, st: ex.uart_ok, BIST_EXECUTION_DELAY_STATE),
        Transition(lambda ex, st: True, TERMINAL_RECOVERY_STATE)
    ))

    # TERMINAL_RECOVERY_STATE
    experiment.add_state(ExperimentState(
        TERMINAL_RECOVERY_STATE,
        terminal_recovery_state_actions,
        Transition(lambda ex, st: ex.uart_ok and ex.login_litex and ex.args.continuous_bist_mode, BIST_EXECUTION_CONTINUOUS_STATE),
        Transition(lambda ex, st: ex.uart_ok and ex.login_litex, BIST_EXECUTION_DELAY_STATE),
        Transition(lambda ex, st: True, RESET_RECOVERY_STATE)
    ))

    # RESET_RECOVERY_STATE
    experiment.add_state(ExperimentState(
        RESET_RECOVERY_STATE,
        reset_recovery_state_actions,
        Transition(lambda ex, st: ex.unrecoverable, UNRECOVERABLE_POSTMORTUM_STATE),
        Transition(lambda ex, st: True, LITEX_PROMPT_STATE)
    ))

    # UNRECOVERABLE_POSTMORTUM_STATE
    experiment.add_state(ExperimentState(
        UNRECOVERABLE_POSTMORTUM_STATE,
        unrecoverable_postmortum_state_actions,
        # Currently, the way to reconfigure is with flash memory.
        Transition(lambda ex, st: True, POWER_BOARD_STATE) #CONNECT_UART_STATE 
    ))

    # TERMINATING_STATE
    # - Do nothing: place holder for ending state. Will set experiment to "stop"
    # - Enter this state when the experiment cannot continue
    experiment.add_state(ExperimentState(
        TERMINATING_STATE,
        terminating_state_actions,
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # Set initial state
    experiment.set_next_state(INITIAL_STARTING_STATE)
    return experiment

def create_log_path(prefix,basename,path_dir=None,prefix_first=False):
    ''' Creates a Path to a log file'''

    if prefix_first:
        filename = str(prefix+"_"+basename+".log")
    else:
        filename = str(basename+"_"+prefix+".log")

    if path_dir:
        filepath = Path(path_dir , filename)
    else:
        filepath = filename
    return filepath

def create_base_filename(bitstream_filename, prefix="CTRL"):
    ''' Create a base filename used for all files generated by this experiment '''

    # See if the bitstream exists
    p = Path(bitstream_filename)
    #print(p,p.cwd())
    #if not p.exists():
    #    return None
    # Strip the path and suffix
    filename_stem = p.stem
    return create_base_filename_identifier(prefix,filename_stem)

def create_base_filename_identifier(prefix,identifier):
    ''' Create a base filename used for all files generated by this experiment '''
    current_date_time = datetime.now().strftime("%B_%d_%Y__%H_%M_%S")
    # Add CTRL as the prefix to specify it is a DDR controller test
    #  (the bistream is not enough - the same bitstream may be used for the DDR test)
    return str(prefix + "_" + identifier + "_" + current_date_time)

def main():

    parser = argparse.ArgumentParser()
    #parser.add_argument("--bitstream", help="filename of bitstream", type=str, required=True)
    parser.add_argument("--test_name", help="Name for test", type=str, required=True)
    parser.add_argument("--test_board_name", help="Name of the board being tested to add board settings (Options: "+NEXYS4DDR_BOARDNAME+", "+NEXYS_VIDEO_BOARDNAME+", "+DATABOARD_BOARDNAME+")", 
                        choices=[NEXYS4DDR_BOARDNAME, NEXYS_VIDEO_BOARDNAME, DATABOARD_BOARDNAME], 
                        required=True)
    parser.add_argument_group(netbooter_control.netbooter_group_args(parser))
    parser.add_argument_group(jcm_session.jcm_group_args(parser))
    parser.add_argument_group(uart_control.uart_group_args(parser))
    uartbone_args = usb_uart_base.uart_group_args(parser,UARTBONE_UART_BASENAME, 
        default_phys_port="1-4.4.1", default_phys_if=0, default_baud = 115200)
    parser.add_argument_group(uartbone_args)
    parser.add_argument("--repower_jcm", help="Repower JCM at start of experiment", action='store_true')
    parser.add_argument("--disable_scrubbing", help="Do not enable the scrubber", action='store_true')
    parser.add_argument("--fault_injection", help="Enable fault injection during scrubbing. Param=# of faults per cycle", type=int)
    parser.add_argument("--frads_file", help="Name of frads filename", type=str)
    parser.add_argument("--jcm_netbooter_port", help="Netbooter port for JCM", type=int, default=1)
    parser.add_argument("--board_netbooter_port", help="Netbooter port for specific board", type=int, default=2)
    parser.add_argument("--log_dir", help="Directory to store log files", type=str)
    parser.add_argument("--single_step", help="Single step through state machine", action='store_true')
    parser.add_argument("--bist_mem_burst_length", help="Burst length of BIST command", type=int, default = DEFAULT_BIST_BURST_LENGTH)
    parser.add_argument("--bist_addr_mode", help="Burst length of BIST command", type=int, default=DEFAULT_BIST_ADDR_MODE)
    parser.add_argument("--bist_pattern", help="BIST Pattern for memory test", type=int, default=DEFAULT_BIST_PATTERN)
    parser.add_argument("--no_uart_bone", help="Disable UART wishbone interface", action='store_true')
    parser.add_argument("--uart_bone_ident", help="Hex Address of uart bone identifier register", default=UARTBONE_IDENT_ADDR)
    parser.add_argument("--continuous_bist_mode", help="Run the BIST in continuous mode", action='store_true')
    parser.add_argument("--noncontinuous_bist_delay", help="Argument to control the delay between commands (in seconds)", type=int, default=DEFAULT_BIST_NONCONT_DELAY_SEC)
    parser.add_argument("--test_prefix", help="Test Prefix (CTRL, DDR4, etc.)", default=DEFAULT_PREFIX)
    args = parser.parse_args()

    # Set up logger settings
    filebasename = create_base_filename(args.test_name, prefix=args.test_prefix)
    log_dir = Path(".")
    if args.log_dir:
        log_dir = Path(args.log_dir)

    log_filepath = create_log_path("LOG",filebasename, log_dir)
    if not log_filepath:
        # Can't create log file
        return 1

    print("Base filename:", log_filepath)

    logger = setup_logger(log_filepath,print_stdout = True)
    
    experiment = build_experiment(args,logger,single_step = args.single_step)
    experiment.filebasename = filebasename
    experiment.log_dir = log_dir

    experiment.start()



if __name__ == "__main__":
    main()


'''


Error response:

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


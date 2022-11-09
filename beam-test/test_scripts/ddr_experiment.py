#!/usr/bin/env python3

# Questions?
# - Do I need to give a message at the start of each action? 
# shrec@nuc4.ee.byu.edu (pass:shrec)
# token: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
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


# Format string for printing the date and time
TIME_STRING_FORMAT = "%Y-%m-%d %H:%M:%S"
# Number of JCM pings before failure
JCM_PING_COUNT_LIMIT = 10
# JCM Ping Delay
JCM_PING_DELAY = 10

DEFAULT_BIST_BURST_LENGTH = 0x2000 # Default burst length
DEFAULT_BIST_ADDR_MODE = 1 # Start reading/writing data with addresses linearly.

class bist_state(object):
    ''' This class keeps track of a running bist command '''

    def __init__(self, 
        bist_mem_burst_length:int,
        bist_addr_mode:int,
        ) -> None:

        self.bist_mem_burst_length = bist_mem_burst_length
        self.bist_addr_mode = bist_addr_mode
        self.new_title = True

        self.error_cnt = 0
        self.sec_cnt = 0
        self.ded_cnt = 0

    def get_bist_command_str(self):
        cmd_str = "sdram_bist " + str(self.bist_mem_burst_length) + " " + str(self.bist_addr_mode)
        return cmd_str

    def new_bist_title(self):
        self.new_title = True

    def new_data_str(self,result_str):
        ERROR_MSG_INDEX = 3 # Error number at index 3 of matched string
        SEC_MSG_INDEX = 4 # Sec error number at index 4 of matched string
        DED_MSG_INDEX = 5 # Ded error number at index 5 of matched string
        result_list = result_str.split()
        new_error_cnt = int(result_list[ERROR_MSG_INDEX])
        new_sec_cnt = int(result_list[SEC_MSG_INDEX])
        # What is going on here?
        ded_string = result_list[DED_MSG_INDEX]
        ded_string_int = "0"
        if (ded_string.find('\'', 0) == -1):
            ded_string_int = ded_string
        else :
            ded_string_int = ded_string[:ded_string.find('\'', 0):]
        new_ded_cnt = int(ded_string_int)
        self.new_title = False

def setup_logger(log_filename:str, include_level = True, print_stdout = False):
    ''' Static method for creating custom loggers '''
    if include_level:
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt=TIME_STRING_FORMAT)
    else:
        formatter = logging.Formatter('%(asctime)s %(message)s', datefmt=TIME_STRING_FORMAT)
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

def initial_starting_state_actions(ex, st):
    pass

def netbooter_setup_state_actions(ex, st):
    ex.netbooter_ok = False
    netbooter_ip = ex.args.netbooter_ip
    ex.netbooter = netbooter_control(netbooter_ip,ex.logger)
    if not ex.netbooter.ping_netbooter():
        ex.logger.error("Netbooter not on network")
        return
    ex.netbooter_ok = True

def jcm_setup_state_actions(ex, st):
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
    #jcm_stdout_logger = setup_logger(jcm_log_filename, include_level = False)

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

def power_nexys_state_actions(ex, st):
    ex.netbooter.turn_off_port(ex.args.nexys_netbooter_port)
    ex.netbooter.turn_on_port(ex.args.nexys_netbooter_port)

def connect_uart_state_actions(ex, st):
    ex.uart_ok = False

    # Create UART stdout
    uart_log_filename = create_log_path("UART",ex.filebasename, ex.log_dir)
    # Create UART log file
    uart_log_file = open(uart_log_filename,"w")

    # Create UART control object
    ex.uart = uart_control(ex.args.usb_uart_phys_port, uart_stdout = uart_log_file, logging = ex.logger)

    # Determine device name for uart
    serial_fdspawn = ex.uart.create_uart_spawn()
    if not serial_fdspawn:
        return

    ex.uart_ok = True

def configure_nexys_state_actions(ex, st):
    ex.configure_ok = False
    result = ex.jcm.configure_fpga(ex.args.bitstream)
    ex.configure_ok = result

def litex_prompt_state_actions(ex, st):
    ex.login_litex = False
    # Todo: Allow multiple attempts (if boot is slow)
    LITEX_LOGIN_PATTERN = "^.*litex[^>]*> "
    LITEX_LOGIN_DELAY = 10
    ex.uart.sendline("\n")
    ex.uart.expect(LITEX_LOGIN_PATTERN,timeout=LITEX_LOGIN_DELAY)
    ex.login_litex = True

def start_bist_state_actions(ex, st):
    ex.bist = bist_state(ex.args.bist_mem_burst_length, ex.args.bist_addr_mode)
    bist_command = ex.bist.get_bist_command_str()
    result = ex.uart.sendline(bist_command)

def bist_result_state_actions(ex, st):

    # Wait for the BIST title
    #^M                          WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED
    BIST_TITLE_REGEX = "WR-BW\(MiB/s\) RD-BW\(MiB/s\)  TESTED\(MiB\)     ERRORS        SEC        DED"
    BIST_TEXT_DELAY = 15
    ex.uart.expect(BIST_TITLE_REGEX,timeout=BIST_TEXT_DELAY)
    # New title: reset the title flag
    ex.bist.new_bist_title()

    # Wait for the BIST Data
    #^M                                   646          654          324          0          0          0
    BIST_DATA_REGEX = "\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+"
    for i in range(16):
        ex.uart.expect(BIST_DATA_REGEX,timeout=BIST_TEXT_DELAY)
        result = ex.uart.get_expect_str()
        ex.bist.new_data_str(result)     


def terminating_state_actions(ex, st):
    # Stop scrubbing (if it is going)
    if ex.jcm.is_active():
        ex.jcm.stop_scrub()
        ex.jcm.jcm_thread.join()

    # Close the JCM (if it was setup properly)
    if ex.jcm_ok:
        ex.jcm.close_jcm()
        
    ex.stop()

def build_experiment(args,logger,single_step=False):
    '''
    Builds the experiment object and its related states for the experiment state machine.
    '''

    # State constants
    INITIAL_STARTING_STATE = "Initial Starting State"
    NETBOOTER_SETUP_STATE = "Netbooter Setup State"
    JCM_SETUP_STATE = "JCM Setup State"
    POWER_NEXYS_STATE = "Power Nexys State"
    CONNECT_UART_STATE = "Connect UART State"
    CONFIGURE_NEXYS_STATE = "Configure Nexys State"
    ENABLE_SCRUBBING_STATE = "Enable Scrubbing State"
    LITEX_PROMPT_STATE = "LiteX Login State"
    START_BIST_STATE = "Start BIST State"
    BIST_RESULT_STATE = "BIST Result State"

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

    # NETBOOTER_SETUP_STATE
    # - Check for netbooter and initialize data structures. Make sure it responds on the network
    experiment.add_state(ExperimentState(
        NETBOOTER_SETUP_STATE,
        netbooter_setup_state_actions,
        Transition(lambda ex, st: ex.netbooter_ok, JCM_SETUP_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # JCM_SETUP_STATE
    # - Intialize JCM data structure, repower (if necessary), and create connection
    experiment.add_state(ExperimentState(
        JCM_SETUP_STATE,
        jcm_setup_state_actions,
        Transition(lambda ex, st: ex.jcm_ok, POWER_NEXYS_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # POWER_NEXYS_STATE
    # - Intialize JCM data structure, repower (if necessary), and create connection
    experiment.add_state(ExperimentState(
        POWER_NEXYS_STATE,
        power_nexys_state_actions,
        Transition(lambda ex, st: True, CONNECT_UART_STATE)
    ))

    # CONNECT_UART_STATE
    # - Connect the UART
    # Does the FPGA needs to be configured before connecting
    # to the UART? 
    experiment.add_state(ExperimentState(
        CONNECT_UART_STATE,
        connect_uart_state_actions,
        Transition(lambda ex, st: ex.uart_ok, CONFIGURE_NEXYS_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # CONFIGURE_NEXYS_STATE
    # - Configure FPGA
    experiment.add_state(ExperimentState(
        CONFIGURE_NEXYS_STATE,
        configure_nexys_state_actions,
        Transition(lambda ex, st: ex.configure_ok, ENABLE_SCRUBBING_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # ENABLE_SCRUBBING_STATE
    # - Turn on scrubbing
    experiment.add_state(ExperimentState(
        ENABLE_SCRUBBING_STATE,
        enable_scrubbing_state_actions,
        Transition(lambda ex, st: ex.scrubbing_ok, LITEX_PROMPT_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # LITEX_PROMPT_STATE
    # - Wait for LITEX login
    experiment.add_state(ExperimentState(
        LITEX_PROMPT_STATE,
        litex_prompt_state_actions,
        Transition(lambda ex, st: ex.login_litex, START_BIST_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # START_BIST_STATE
    # - Start BIST command
    experiment.add_state(ExperimentState(
        START_BIST_STATE,
        start_bist_state_actions,
        Transition(lambda ex, st: ex.login_litex, BIST_RESULT_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # BIST_RESULT_STATE
    # - Process an execution of the BIST
    experiment.add_state(ExperimentState(
        BIST_RESULT_STATE,
        bist_result_state_actions,
        #Transition(lambda ex, st: ex.login_litex, TERMINATING_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
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

def create_log_path(prefix,basename,path_dir=None):
    ''' Creates a Path to a log file'''
    filename = str(prefix+"_"+basename+".log")
    if path_dir:
        filepath = Path(path_dir , filename)
    else:
        filepath = filename
    return filepath

def create_base_filename(bitstream_filename):
    ''' Create a base filename used for all files generated by this experiment '''

    # See if the bitstream exists
    p = Path(bitstream_filename)
    #print(p,p.cwd())
    #if not p.exists():
    #    return None
    # Strip the path and suffix
    filename_stem = p.stem
    # Add a timestamp
    current_date_time = datetime.now().strftime("%B_%d__%H_%M_%S")
    return str(filename_stem + "_" + current_date_time)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--bitstream", help="filename of bitstream", type=str, required=True)
    parser.add_argument_group(netbooter_control.netbooter_group_args(parser))
    parser.add_argument_group(jcm_session.jcm_group_args(parser))
    parser.add_argument_group(uart_control.uart_group_args(parser))
    parser.add_argument("--repower_jcm", help="Repower JCM at start of experiment", action='store_true')
    parser.add_argument("--jcm_netbooter_port", help="Netbooter port for JCM", type=int, default=1)
    parser.add_argument("--nexys_netbooter_port", help="Netbooter port for Nexys", type=int, default=2)
    parser.add_argument("--log_dir", help="Directory of logs", type=str)
    parser.add_argument("--single_step", help="Single step through state machine", action='store_true')
    parser.add_argument("--bist_mem_burst_length", help="Burst length of BIST command", type=int, default = DEFAULT_BIST_BURST_LENGTH)
    parser.add_argument("--bist_addr_mode", help="Burst length of BIST command", type=int, default=DEFAULT_BIST_ADDR_MODE)
    args = parser.parse_args()

    # Set up logger settings
    filebasename = create_base_filename(args.bitstream)
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
Updated state machine using threads

1. Init state
   - Just a start message
2. Repower board
   - We want to start the experiment in a fresh state
3. Initialize UART connection (for UARTBone and UART serial)
  - Force repower the UART connection?
  - Log the UART serial from here out
4. JCM Login
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
- Configure
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


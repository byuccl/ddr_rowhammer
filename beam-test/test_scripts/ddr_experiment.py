#!/usr/bin/env python3

# Questions?
# - Do I need to give a message at the start of each action? 
# shrec@nuc4.ee.byu.edu (pass:shrec)
# token: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

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
from pathlib import Path
from datetime import datetime
import netbooter
import jcm_session

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
from datetime import date, datetime
from experiment_machine import Transition, ExperimentState, Experiment


# Format string for printing the date and time
TIME_STRING_FORMAT = "%Y-%m-%d %H:%M:%S"
# Number of JCM pings before failure
JCM_PING_COUNT_LIMIT = 10
# JCM Ping Delay
JCM_PING_DELAY = 10

def setup_logger(log_filename:str, include_level = True):
    ''' Create a custom logger '''
    if include_level:
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt=TIME_STRING_FORMAT)
    else:
        formatter = logging.Formatter('%(asctime)s %(message)s', datefmt=TIME_STRING_FORMAT)
    handler = logging.FileHandler(log_filename)        
    handler.setFormatter(formatter)
    logger = logging.getLogger("main_log")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

def initial_starting_state_actions(ex, st):
    pass

def netbooter_setup_state_actions(ex, st):
    ex.netbooter_ok = False
    netbooter_ip = ex.args.netbooter_ip
    ex.netbooter = netbooter(netbooter_ip,ex.logger)
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
    jcm_log_filename = str("JCM_"+ex.filebasename)
    jcm_stdout_logger = setup_logger(jcm_log_filename, include_level = False)
    # Create JCM object
    ex.jcm = jcm_session.create_jcm_from_args(ex.args,ex.logger,jcm_stdout_logger)
    # Ping JCM (wait until ping before trying to connect)
    for i in range(JCM_PING_COUNT_LIMIT):
        ping_true = ex.jcm.jcm_ping()
        ex.logger.info("JCM ping attempt {}",i+1)
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
    ex.netbooter.turn_on_port(ex.args.nexys_netbooter_port)

def terminating_state_actions(ex, st):
    # Close the JCM (if it was setup properly)
    if ex.jcm_ok:
        ex.jcm.close()
        
    ex.stop()

def build_experiment(args,logger):
    '''
    Builds the experiment object and its related states for the experiment state machine.
    '''

    # State constants
    INITIAL_STARTING_STATE = "Initial Starting State"
    NETBOOTER_SETUP_STATE = "Netbooter Setup State"
    JCM_SETUP_STATE = "JCM Setup State"
    POWER_NEXYS_STATE = "Power Nexys State"

    TERMINATING_STATE = "Terminating State"

    # Create a new experiment object
    experiment = Experiment(logger)

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
        Transition(lambda ex, st: ex.netbooter_ok, POWER_NEXYS_STATE),
        Transition(lambda ex, st: True, TERMINATING_STATE)
    ))

    # POWER_NEXYS_STATE
    # - Intialize JCM data structure, repower (if necessary), and create connection
    experiment.add_state(ExperimentState(
        POWER_NEXYS_STATE,
        power_nexys_state_actions,
        Transition(lambda ex, st: True, UNKNOWN_STATE)
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

def create_base_filename(bitstream_filename):
    ''' Create a base filename used for all files generated by this experiment '''

    # See if the bitstream exists
    p = Path(bitstream_filename)
    #if not p.exists():
    #    return None
    # Strip the path and suffix
    filename_stem = p.stem()
    # Add a timestamp
    current_date_time = datetime.now().strftime("%B_%d_%H_%M")
    return str(filename_stem + "_" + current_date_time)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--bitstream", help="filename of bitstream", type=str, required=False)
    parser.add_argument_group(netbooter.netbooter_group_args(parser))
    parser.add_argument_group(jcm_session.jcm_group_args(parser))
    parser.add_argument("--repower_jcm", help="Repower JCM at start of experiment", action='store_true')
    parser.add_argument("--jcm_netbooter_port", help="Netbooter port for JCM", type=int, default=1)
    parser.add_argument("--nexys_netbooter_port", help="Netbooter port for Nexys", type=int, default=2)
    args = parser.parse_args()

    # Set up logger settings
    filebasename = create_base_filename(args.bitstream)
    log_filename = str("LOG_"+filebasename)
    logger = setup_logger(log_filename)
    
    experiment = build_experiment(args,logger)
    experiment.filebasename = filebasename
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


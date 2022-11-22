#!/usr/bin/env python3

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
import usb_uart_expect
from usb_uart_base import usb_uart_base

#from usb_uart_expect import create_usbuartexpect_from_args

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
from new_experiment_machine import ExperimentState, NewExperiment
from ddrctrl_experiment import create_log_path, setup_logger, initial_experiment_logging, create_base_filename_identifier

TIME_STRING_FORMAT = "%Y-%m-%d %H:%M:%S"
UART_BASENAME = "uart"
UART_BAUD_RATE = 115200
UART_PHYS_PORT = "1-4.1"
UART_PHYS_IF = 0
DEFAULT_LITEX_LOGIN_DELAY = 15
DEFAULT_IDENT_ADDRESS = 0xf0001800

# State constants
INITIAL_STARTING_STATE = "Initial Starting State"
NETBOOTER_SETUP_STATE = "Netbooter Setup State"
JCM_SETUP_STATE = "JCM Setup State"
UART_SETUP_STATE = "UART Setup State"
POWER_NEXYS_STATE = "Power Nexys State"
CONNECT_UART_STATE = "Connect UART State"
CONFIGURE_NEXYS_STATE = "Configure Nexys State"
ENABLE_SCRUBBING_STATE = "Enable Scrubbing State"
LITEX_PROMPT_STATE = "LiteX Login State"


TERMINATING_STATE = "Terminating State"

def expect_prompt(ex, number_of_enters=1,expect_timeout=DEFAULT_LITEX_LOGIN_DELAY):
    ''' Send "Enter" and expects the "litex" prompt (does this once)
        Does NOT set state (state actions should set state)
        Returns True if expect was successful, False otherwise
          Calling functions should query for details about failed expect
    '''
    # Todo: Allow multiple attempts (if boot is slow)
    LITEX_LOGIN_PATTERN = "^.*litex[^>]*> "
    for i in range(number_of_enters):
        ex.uart.sendline("\n")
    ex.uart.expect(LITEX_LOGIN_PATTERN,timeout=expect_timeout)
    if ex.uart.has_error():
        return False
    return True

def initial_starting_state_actions(ex):
    ''' Do nothing - just an entry point for the experiment. Executed only once. 
        No state change
    '''
    initial_experiment_logging(ex)
    return NETBOOTER_SETUP_STATE

def netbooter_setup_state_actions(ex):
    netbooter_ip = ex.args.netbooter_ip
    ex.netbooter = netbooter_control(netbooter_ip,ex.logger)
    if not ex.netbooter.ping_netbooter():
        ex.logger.error("Netbooter not on network")
        return TERMINATING_STATE

    # Netbooter ok
    return JCM_SETUP_STATE

def jcm_setup_state_actions(ex):

    if ex.args.disable_jcm:
        return UART_SETUP_STATE

    # First power off JCM (if necessary)
    if ex.args.repower_jcm:
        ex.netbooter.turn_off_port(ex.args.jcm_netbooter_port)
        time.sleep(3)
    # Power on JCM (may already be powered)
    ex.netbooter.turn_on_port(ex.args.jcm_netbooter_port)

    # Create a JCM log filename
    jcm_log_filename = create_log_path("JCM",ex.filebasename, ex.log_dir)

    # Create the JCM
    ex.jcm = jcm_session.jcm_setup(jcm_log_filename,ex.args,ex.logger)
    if not ex.jcm:
        return TERMINATING_STATE
    return UART_SETUP_STATE

def uart_setup_state_actions(ex):
    # create uart object but do not connect uart

    # Create UART stdout
    uart_log_filename = create_log_path("UART",ex.filebasename, ex.log_dir)
    # Create UART log file
    uart_log_file = open(uart_log_filename,"w")

    # Create UART control object
    ex.uart = usb_uart_expect.create_usbuartexpect_from_args(ex.args, UART_BASENAME, ex.logger, uart_log_file, 
        TIME_STRING_FORMAT, logger_prefix="UART")
    if not ex.uart:
        return TERMINATING_STATE

    return POWER_NEXYS_STATE

def power_nexys_state_actions(ex):
    ''' Power cycle nexys board (no status) '''
    turn_off_cmd = ex.netbooter.turn_off_port(ex.args.nexys_netbooter_port)
    turn_on_cmd = ex.netbooter.turn_on_port(ex.args.nexys_netbooter_port)
    if not (turn_off_cmd and turn_on_cmd):
        return TERMINATING_STATE
    #variable_update_experiment_initialization(ex)
    return CONNECT_UART_STATE

def connect_uart_state_actions(ex):
    # Create a spawned file handle for reading/writing to the serial port
    serial_fdspawn = ex.uart.create_uart_spawn()
    if not serial_fdspawn:
        return TERMINATING_STATE
    return CONFIGURE_NEXYS_STATE

def configure_nexys_state_actions(ex):
    if ex.args.disable_jcm:
        return ENABLE_SCRUBBING_STATE
    result = ex.jcm.configure_fpga(ex.args.bitstream)
    if not result:
        return TERMINATING_STATE
    return ENABLE_SCRUBBING_STATE

def enable_scrubbing_state_actions(ex):
    if ex.args.disable_jcm:
        return LITEX_PROMPT_STATE

    if ex.args.disable_scrubbing:
        ex.scrubbing_ok = True
        return LITEX_PROMPT_STATE

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
    return LITEX_PROMPT_STATE

def initial_litex_prompt_state_actions(ex):
    MAX_LOGIN_ATTEMPS = 3
    ex.login_litex = False
    ex.initial_login_terminate = False
    expect_result = expect_prompt(ex)
    if expect_result:
        # All is good - move on
        return TERMINATING_STATE
        #ex.login_litex = True
        #ex.failed_initial_login = 0  # Reset counter for next time around
    else:
        # Failed login, go back to repower of NEXYS until max attempts
        if ex.failed_initial_login >= MAX_LOGIN_ATTEMPS:
            # Failed too many times - give up
            ex.initial_login_terminate = True
        else:
            # Try again
            ex.failed_initial_login += 1
    return TERMINATING_STATE

def terminating_state_actions(ex):
    ''' Terminates experiment
        no state change
    '''
    ex.stop()
    return TERMINATING_STATE


def build_experiment(args,logger,single_step=False):
    '''
    Builds the experiment object and its related states for the experiment state machine.
    '''


    # Create a new experiment object
    experiment = NewExperiment(logger,single_step=single_step)

    # Save the arguments
    experiment.args = args
    experiment.logger = logger

    # INITIAL_STARTING_STATE
    # - Do nothing: place holder for start
    experiment.add_state(ExperimentState(
        INITIAL_STARTING_STATE,
        initial_starting_state_actions,
    ))

    # NETBOOTER_SETUP_STATE
    experiment.add_state(ExperimentState(
        NETBOOTER_SETUP_STATE,
        netbooter_setup_state_actions,
    ))

    # JCM_SETUP_STATE
    experiment.add_state(ExperimentState(
        JCM_SETUP_STATE,
        jcm_setup_state_actions,
    ))

    # UART_SETUP_STATE
    experiment.add_state(ExperimentState(
        UART_SETUP_STATE,
        uart_setup_state_actions,
    ))

    # POWER_NEXYS_STATE
    experiment.add_state(ExperimentState(
        POWER_NEXYS_STATE,
        power_nexys_state_actions,
    ))

    # CONNECT_UART_STATE
    experiment.add_state(ExperimentState(
        CONNECT_UART_STATE,
        connect_uart_state_actions,
    ))

    # CONFIGURE_NEXYS_STATE
    experiment.add_state(ExperimentState(
        CONFIGURE_NEXYS_STATE,
        configure_nexys_state_actions,
    ))

    # ENABLE_SCRUBBING_STATE
    experiment.add_state(ExperimentState(
        ENABLE_SCRUBBING_STATE,
        enable_scrubbing_state_actions,
    ))

    # LITEX_PROMPT_STATE
    experiment.add_state(ExperimentState(
        LITEX_PROMPT_STATE,
        initial_litex_prompt_state_actions,
    ))

    # TERMINATING_STATE
    # - Do nothing: place holder for ending state. Will set experiment to "stop"
    # - Enter this state when the experiment cannot continue
    experiment.add_state(ExperimentState(
        TERMINATING_STATE,
        terminating_state_actions,
    ))
    return experiment

def main():

    parser = argparse.ArgumentParser()
    # Netbooter arguments
    parser.add_argument_group(netbooter_control.netbooter_group_args(parser))
    parser.add_argument("--nexys_netbooter_port", help="Netbooter port for Nexys", type=int, default=2)
    parser.add_argument("--jcm_netbooter_port", help="Netbooter port for JCM", type=int, default=1)
    # JCM arguments
    parser.add_argument_group(jcm_session.jcm_group_args(parser))
    parser.add_argument("--repower_jcm", help="Repower JCM at start of experiment", action='store_true')
    parser.add_argument("--disable_jcm", help="Disable JCM", action='store_true')
    # UART arguments
    parser.add_argument_group(
        usb_uart_base.uart_group_args(parser,UART_BASENAME, default_phys_port = UART_PHYS_PORT, 
        default_phys_if = UART_PHYS_IF, default_baud = UART_BAUD_RATE))

    parser.add_argument("--log_dir", help="Directory to store log files", type=str)
    parser.add_argument("--single_step", help="Single step through state machine", action='store_true')
    args = parser.parse_args()

    # Set up logger settings
    #filebasename = create_base_filename(args.bitstream)
    filebasename = create_base_filename_identifier("DDR","bitstream")
    print(filebasename)

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

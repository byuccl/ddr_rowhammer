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
from ddrctrl_experiment import create_log_path, setup_logger, initial_experiment_logging, create_base_filename_identifier, create_base_filename

TIME_STRING_FORMAT = "%Y-%m-%d %H:%M:%S"
UART_BASENAME = "uart"
UART_BAUD_RATE = 115200
UART_PHYS_PORT = "1-4.2"
UART_PHYS_IF = 0
DEFAULT_LITEX_LOGIN_DELAY = 15
DEFAULT_IDENT_ADDRESS = 0xf0001800
DEFAULT_BIST_PATTERN = 0x5a
DDR_INITIAL_ADDR = 0x0
DDR_SIZE = 0x20000000
DDR_DEFAULT_BIST_MODE = 0

DEFAULT_BIST_BLOCK_SIZE = 0x2000 # 4k blocks
DEFAULT_BIST_ADDR_MODE = 1       # "inc" address mode
DEFAULT_BIST_DATA_MODE = 0       # pattern data
DEFAULT_BIST_WRITE_MODE =1       # write once

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
INIT_MEM_STATE = "Initialize Memory State"
RUN_BIST_STATE = "Run Bist State"
UART_RECOVERY_STATE = "UART recovery state"

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

def sdram_bist_pat_command(pattern):
    ''' Generate command for setting the sdram bist pattern. 
    Set the byte pattern used by BIST for memory testing
    This will set all four bytes of a word to the same value.
    It will only accept one byte (last byte in value you give it)
    
    Usage:
    
    litex> sdram_bist_pat
    sdram_bist_pat <value>
    
    Example:
    
    sdram_bist_pat 0x5a 
    '''
    bist_pattern_command = f"sdram_bist_pat {pattern}"
    return bist_pattern_command

def sdram_bist_gen_command(base = DDR_INITIAL_ADDR, length = DDR_SIZE, data_mode = DDR_DEFAULT_BIST_MODE):
    ''' Generate the sdram_bist_gen command for initializing memory
    Initialize the memory. This command will write a word
    using four bytes of the pattern to all locations specified
    by the arguments. The first argument is the base address
    to do the write. This is the DRAM base address meaning
    that the first address is 0x0 (Even though it is mapped
    to another location within the system address space).
    The next argument is the length in bytes. The DDR size
    is 0x20000000 bytes or 512 MiB. The last
    argument is the data mode. We are using the '0'
    pattern mode.
    
    Usage:
    
    litex> sdram_bist_gen
    sdram_bist_gen <base> <length> [<data_mode>]
    base     : base address (starts at zero)
    length   : DMA block size in bytes
    data_mode: 0=pattern, 1=inc, 2=random
    
    Example:
    
    sdram_bist_gen 0x0 0x20000000 0        
    '''
    bist_command = f"sdram_bist_pat {base} {length} {str(data_mode)}"
    return bist_command

def sdram_bist_chk_command(base = DDR_INITIAL_ADDR, length = DDR_SIZE, data_mode = DDR_DEFAULT_BIST_MODE):
    ''' Check the memory
    Check memory. This command checks the memory using DMA against the given data mode.
    The first argument is the base, the second is the length, and the third the mode.
    
    Usage:
    
    litex> sdram_bist_chk
    sdram_bist_chk <base> <length> [<data_mode>]
    base     : base address (starts at zero)
    length   : DMA block size in bytes
    data_mode: 0=pattern, 1=inc, 2=random
    
    '''
    bist_check_command = f"sdram_bist_chk {str(base)} {str(length)} {str(data_mode)}"
    return bist_check_command

def sdram_bist_command(length = DEFAULT_BIST_BLOCK_SIZE, addr_mode = DEFAULT_BIST_ADDR_MODE, 
    data_mode = DEFAULT_BIST_DATA_MODE, write_mode = DEFAULT_BIST_WRITE_MODE):
    ''' Start the bist check command

litex> sdram_bist
sdram_bist <length> [<addr_mode>] [<data_mode>] [<write_mode>]
length    : DMA block size in bytes
addr_mode : 0=fixed (starts at zero), 1=inc, 2=random
data_mode : 0=pattern, 1=inc, 2=random
write_mode: 0=no_write, 1=write_once, 2=write_and_read

    length: The size of the DMA block check (0x2000 = 4K)
            (Breaks up the full bist check into blocks)
    addr_mode: stay at same place, increment, or pick random
    data_mode: data type to write
    write_mode: how often to write

    example:

litex> sdram_bist 0x1000 1 0 1    
    '''
    bist_check_command = f"sdram_bist {str(length)} {str(addr_mode)} {str(data_mode)} {str(write_mode)}"
    return bist_check_command

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

    if not ex.args.enable_scrubbing:
        ex.scrubbing_ok = True
        ex.logger.info("Scrubber disabled")
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
    expect_result = expect_prompt(ex,number_of_enters=2)
    if expect_result:
        # All is good - move on
        return INIT_MEM_STATE
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
    # Too many failed attempts - terminate
    return TERMINATING_STATE

def init_mem_state_actions(ex):

    # 1. Get litex prompt
    expect_result = expect_prompt(ex)
    if not expect_result:
        # Problem: for now exit
        return TERMINATING_STATE

    # 2. Set the bist pattern
    bist_pattern_command = sdram_bist_pat_command(ex.args.default_bist_pattern)
    result = ex.uart.sendline(bist_pattern_command)

    # Check for prompt
    expect_result = expect_prompt(ex, number_of_enters=0)
    if not expect_result:
        # Problem: for now exit
        return TERMINATING_STATE

    # Start the bist command
    bist_set_cmd = sdram_bist_command()    # Use defaults for now
    result = ex.uart.sendline(bist_set_cmd)

    return RUN_BIST_STATE

def run_bist_state_actions(ex):
    ''' The bist command has been started when this state commences. Parse the
    bist data. '''

    BIST_TEXT_DELAY = 15
    MAX_CONSECUTIVE_UNICODE_ERRORS = 20
    MAX_CONSECUTIVE_UNMATCHED_LINES = 10
    # BIST title line
    #                          WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED
    #WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS
    #BIST_TITLE_REGEX = "WR-BW\(MiB/s\) RD-BW\(MiB/s\)  TESTED\(MiB\)     ERRORS(        SEC        DED){0,1}"
    BIST_TITLE_REGEX = "WR-BW\(MiB/s\) RD-BW\(MiB/s\)  TESTED\(MiB\)     ERRORS\n"
    # BIST data line
    #           0         1296         2282          2
    #BIST_DATA_REGEX = "\d+\s+\d+\s+\d+\s+\d+(\s+\d+\s+\d+){0,1}"
    BIST_DATA_REGEX = "\d+\s+\d+\s+\d+\s+\d+\n"
    # Error message
    #error addr: 0x40001000, content: 0xa5a5a4a5, expected: 0xa5a5a5a5
    ERROR_MSG_REGEX = "error addr: (0x[a-f0-9]{8}), content: (0x[a-f0-9]{8}), expected: (0x[a-f0-9]{8})"
    # Error summary
    #ERRORS (CPU): 1
    ERROR_SUMMARY_REGEX = "ERRORS \(CPU\): (\d+)"

    consecutive_unicode_errors = 0
    consecutive_invalid_line = 0

    while(1):
        # Constants indicating position in regex array of each expression
        TITLE_INDEX=0
        DATA_INDEX=1
        ERROR_MSG_INDEX=2
        ERROR_SUMMARY_INDEX=3

        # Get a line of data
        match_index = ex.uart.expect([BIST_TITLE_REGEX,BIST_DATA_REGEX,ERROR_MSG_REGEX,ERROR_SUMMARY_REGEX],timeout=BIST_TEXT_DELAY)
        #match_index = ex.uart.expect("(.*)\r",timeout=BIST_TEXT_DELAY)

        # Process expect system errors
        if ex.uart.has_uart_error():
            # General UART errors (Timeout, etc)
            return UART_RECOVERY_STATE

        elif ex.uart.unicode_error:
            # Unicode errors over UART (look for a consecutive number of them)
            consecutive_unicode_errors += 1
            ex.logger.info(f"BIST:Unicode error (consecutive_unicode_errors)")
            if consecutive_unicode_errors >= MAX_CONSECUTIVE_UNICODE_ERRORS:
                ex.logger.info(f"BIST:Max Unicode Errors")
                return UART_RECOVERY_STATE
                # Don't process this unicode error line
            continue
        else:
            # No UART/system errors at this point
            # Clear any unicode flags and go to title state 
            #  (not sure where we are in bist execution - will likely get data errors after this)
            if consecutive_unicode_errors > 0:
                consecutive_unicode_errors == 0

        if ex.uart.serial_fdspawn.match:
            consecutive_invalid_line = 0
            #print("before:"+ex.uart.serial_fdspawn.before)
            #for c in ex.uart.serial_fdspawn.before:
            #    print(f"{c}:{ord(c)} ",end="")
            #print()
            #print("match:"+ex.uart.serial_fdspawn.match.group(0))
            #print("after:"+ex.uart.serial_fdspawn.after)
            #continue
            # matching line
            if match_index == TITLE_INDEX:
                # valid title - move on
                ex.logger.info(f"BIST:Header")
                continue
            if match_index == DATA_INDEX:
                # valid data - move on
                #ex.logger.info(f"BIST:Data")
                continue
            if match_index == ERROR_MSG_INDEX:
                address = ex.uart.serial_fdspawn.match.group(1)
                received = int(ex.uart.serial_fdspawn.match.group(2),16)
                expected = int(ex.uart.serial_fdspawn.match.group(3),16)
                diff = received ^ expected
                ex.logger.error(f"BIST:ERROR {address} XOR=0x{diff:08X}")
                #ex.logger.error(f"BIST:ERROR {address} received={received:08X} expected={expected:08X} XOR=0x{diff:08X}")
                continue
            if match_index == ERROR_SUMMARY_INDEX:
                error_count = ex.uart.serial_fdspawn.match.group(1)
                #strigd = ex.uart.serial_fdspawn.match.group(0)
                ex.logger.error(f"BIST:Errors={error_count}")
                continue
            ex.logger.error(f"BIST:Shouldn't get here"+ex.uart.serial_fdspawn.match.group(0))
            continue
        else:
            # Does not match a line
            consecutive_invalid_line += 1
            ex.logger.error(f"BIST:Invalid line {consecutive_invalid_line}:"+ex.uart.serial_fdspawn.match.group(0))
            if consecutive_invalid_line > MAX_CONSECUTIVE_UNMATCHED_LINES:
                ex.logger.error(f"BIST:too many invalid lines")
                return UART_RECOVERY_STATE

'''
           0         1296          743          2
           0         1296         2044          2
           0         1296         3345          2
error addr: 0x40001000, content: 0xa5a5a4a5, expected: 0xa5a5a5a5
ERRORS (CPU): 1
           0         1296          551          3
           0         1296         1852          3
WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS
           0         1296         3153          3
           0         1296          358          3

    '''

def uart_recovery_state_actions(ex):
    ''' For now, terminate
    '''
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

    # INIT_MEM_STATE
    experiment.add_state(ExperimentState(
        INIT_MEM_STATE,
        init_mem_state_actions,
    ))

    # RUN_BIST_STATE
    experiment.add_state(ExperimentState(
        RUN_BIST_STATE,
        run_bist_state_actions,
    ))

    # UART_RECOVERY_STATE
    experiment.add_state(ExperimentState(
        UART_RECOVERY_STATE,
        uart_recovery_state_actions,
    ))

    '''
    # INIT_MEM_STATE
    # - Start BIST command
    experiment.add_state(ExperimentState(
        INIT_MEM_STATE,
        init_mem_state_actions,
    ))

    # CHECK_MEM_STATE
    # - Start BIST command
    experiment.add_state(ExperimentState(
        CHECK_MEM_STATE,
        check_mem_state_actions,
    ))
    '''


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
    # Ungrouped arguments
    parser.add_argument("--bitstream", help="filename of bitstream", type=str)
    parser.add_argument("--default_bist_pattern", help="Pattern for memory test (i.e., 0x5a)", default = DEFAULT_BIST_PATTERN)
    parser.add_argument("--log_dir", help="Directory to store log files", type=str)
    parser.add_argument("--enable_scrubbing", help="Directory to store log files", action='store_true')
    parser.add_argument("--single_step", help="Single step through state machine", action='store_true')
    args = parser.parse_args()

    # Bitstream/JCM?
    if args.disable_jcm:
        # Assume bitstream is programmed from PROM on power up
        # Come up with random name
        filebasename = create_base_filename_identifier("DDR","unknown")
    else:
        filebasename = create_base_filename(args.bitstream, prefix="DDR") # from ddrctrl_Experiment
    print(filebasename)

    # Set up logger settings
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

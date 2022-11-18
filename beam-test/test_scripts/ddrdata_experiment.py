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

# State constants
INITIAL_STARTING_STATE = "Initial Starting State"
TERMINATING_STATE = "Terminating State"

def initial_starting_state_actions(ex):
    ''' Do nothing - just an entry point for the experiment. Executed only once. 
        No state change
    '''
    initial_experiment_logging(ex)
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

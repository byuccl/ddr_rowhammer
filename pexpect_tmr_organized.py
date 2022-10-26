#!/usr/bin/env python3


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


# print_fout = open('times_4.txt', 'w+')

MAX_FILE_NUM = 10

TIMEOUT_NETBOOTER = 3.0
SLEEPTIME_NETBOOTER = 1
LITEX_BAUDRATE = 115200

WAIT_TEXT_TIMEOUT = 15 # 15 seconds
WAIT_FOR_BOARD_BOOTUP = 40 # 40 seconds
RUN_JCM_TIMEOUT = 30 # 30 seconds
SDRAM_CAL_TIMEOUT = 5 # 5 seconds
SDRAM_INIT_TIMEOUT = 5 # 5 seconds
TERMINAL_REBOOT_CMD_TIMEOUT = 10 # 10 seconds
BOARD_REPOWER_TIMEOUT = 30 # 30 seconds
BOARD_REPROGRAM_TIMEOUT = 10 # 10 seconds
RESET_LITEX_TIMEOUT = 10 # 10 seconds
FAULT_TIMER_MAX = 2 # 2 second fault injections

RESTART_BIST_INDEX = 1
SDRAM_MODE_SCRUB_INDEX = 2
SDRAM_DELAY_SCRUB_INDEX = 3
SDRAM_CALLIBRATE_INDEX = 4
SDRAM_INIT_INDEX = 5
SOC_REBOOT_INDEX = 6

MAX_NUM_INC_FAULT_READS = 20
MAX_NUM_UNICODE_EXCEPTIONS = 20
AUTO_NUM_ERRORS = 1
STARTING_FILE_NUM = -1
MEM_INDEX = 2
ERROR_MSG_INDEX = 3
SEC_MSG_INDEX = 4
DED_MSG_INDEX = 5
MAX_LINES_CODE_MAX_OUT_ERROR =120
MAX_NUM_TIMES_BOOT_UP = 5
MAX_MIB_TO_READ = 0x1000
MAX_ALIVE_CNT = 30
MAX_BEGINNING_LINES_FOR_ERRORS = 10
TITLE_INDEX = 0
DATA_INDEX = 1

MAX_ERROR_CNT_CYCLES = 30
MAX_PAUSE_ERROR_CNT_CYCLES = 10

PLUG_IN_DELAY = 10
MAX_ERROR_CNT = 0xFFFFFFFF

CORRECTION_FAULT_INJECTION_COMMAND = "~/jcm_apps/jcm_fault_inject.elf --part {fpga} -c 20000000 --jtag --frad_file {frads} --readback_file {design}.rb --target_frame {frame} --target_word {word} --target_bit {bit}"
FAULT_INJECTION_COMMAND = "~/jcm_apps/jcm_random_fault_inject.elf --part {fpga} -c 20000000 --jtag --frad_file {frads} --seed {seed} --readback_file ~/jcm_apps/jcm_readback.rb"
CONFIGURATION_COMMAND = "~/jcm_apps/jcm_config.elf --part {part} -c 20000000 --jtag --config_file {bitstream}"
JCM_IP_ADDRESS = "169.254.132.152"
PART = "xc7a200t"
BITFILE = "./digilent_nexys_video.bit"
FRADS = "~/jcm_apps/a200t.frad"
JCM_LOGIN_LOOPS = 10
JCM_TIMEOUT_IN_SECONDS = 15
NUC_SEED = None
DESIGN = "digilent_nexys_video"

NETBOOTER_IP = "169.254.131.160"
NETBOOTER_PORT = "1"
BURST_LENGTH = 0x2000
RAND_ARG = 1


# # Used to control which level of dram init to do
# global degree_of_max_error
# degree_of_max_error = 0


print_jcm_fout = open('jcm_times_18.txt', 'w')


class jcm_control():

    def close_jcm(new_client):
        new_client.close()
        print("SSH closed")

# Logs into the jcm using paramiko. 
# Returns a SSHClient object
    def login_to_jcm(ip_addr:str):
        print("Logging in to JCM, Time: ", file=print_jcm_fout)
        while(1):
            try:
                new_client = SSHClient()
                new_client.load_system_host_keys()
                new_client.set_missing_host_key_policy(AutoAddPolicy())
                print("Connecting to JCM over SSH...", file=print_jcm_fout)
                new_client.connect(ip_addr, username='root', password='chrec', timeout=None)
                print("SSH successful!", file=print_jcm_fout)
                break
            except (BadHostKeyException, AuthenticationException,
                SSHException, socket.error, buffered_pipe.PipeTimeout, socket.timeout) as error:
                print(error, file=print_jcm_fout)
                new_client.close()
        return new_client


# Configure the FPGA using jcm_config.elf
    def configure_fpga(ssh_client):
        print("Sending config command to JCM, Time: ", datetime.now().time(), file=print_jcm_fout)

        config_command = CONFIGURATION_COMMAND.format(part=PART, bitstream=BITFILE)
        print(config_command, file=print_jcm_fout)

        for i in range(JCM_LOGIN_LOOPS):
            try:
                print("Running config command, Time: ", datetime.now().time(), file=print_jcm_fout)
                stdin, stdout, stderr = ssh_client.exec_command(config_command,timeout=JCM_TIMEOUT_IN_SECONDS)
                break
            except SSHException as error:
                print(error, file=print_jcm_fout)
                logging.info("SSHException: Timeout occured or request was rejected opening channel to JCM. Retrying command.")
                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] SSHException: Timeout occured or request was rejected opening channel to JCM. Retrying command.")
                ssh_client = jcm_control.login_to_jcm(JCM_IP_ADDRESS)

        while not stdout.channel.exit_status_ready():
            try:
                line = stdout.readline()
                if (not line.isspace()) and line != '':
                    print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] : ", line, file=print_jcm_fout)
                if (not line.isspace()) and line != '':
                    line = "[{}] ".format(time.strftime("%Y-%m-%d %H:%M:%S")) + line
                    print(line, file=print_jcm_fout)

                    if "Success" in line:
                        print("Configured Successfully!", file=print_jcm_fout)
                        break

                    if "[root@arch" in line:
                        print("ERROR in configure_fpga", file=print_jcm_fout)
                        break
            
            except(buffered_pipe.PipeTimeout, socket.timeout) as error:
                print("ERROR in fonfigure_fpga", file=print_jcm_fout)
                print(error, file=print_jcm_fout)
                return 1
        return 0

    def inject_fault(ssh_client):
        '''
        Injects a fault
        '''

        global frame_to_correct
        global word_to_correct
        global bit_to_correct
        global location_to_correct
        
        print(time.strftime("%Y-%m-%d %H:%M:%S"),"Injecting Location", file=print_jcm_fout)

        if NUC_SEED is None:
            jcm_seed = str(np.uint32(time.time() * 1000))
        else:
            jcm_seed = random.randint(0, 4000000000)

        command = FAULT_INJECTION_COMMAND.format(fpga = PART, frads = FRADS,seed=jcm_seed)

        print("Before", file=print_jcm_fout)
        for i in range(JCM_LOGIN_LOOPS):
            try:
                stdin, stdout, stderr = ssh_client.exec_command(command, timeout = JCM_TIMEOUT_IN_SECONDS)
                break
            except SSHException as error:
                print(error, file=print_jcm_fout)
                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] SSHException: Timeout occured or request was rejected opening channel to JCM. Retrying exec_command.")
                

        print("After", file=print_jcm_fout)
        
        line = ""
        keep_reading = True

        time_start = time.time()
        while keep_reading:
            cur_time = time.time()
            if (cur_time - time_start > 30):
                print("Restarting script", file=print_jcm_fout)
                os.execv(sys.executable, ['python3'] + sys.argv) # Restarts the program
            
            line = stdout.readline()
            if (not line.isspace()) and line != '':
                print(time.strftime("%Y-%m-%d %H:%M:%S"),   " : ", line, file=print_jcm_fout)
                line = "[{}] ".format(time.strftime("%Y-%m-%d %H:%M:%S")) + line
                if "Failed!" in line:
                    return 1
                if "Injecting Frame" in line:
                    search_string = "Frame (0x[0-9A-F]{8})"
                    m = re.search(search_string, line)
                    if m:
                        frame_to_correct = m.group(1)
                    search_string = "word ([0-9]+ )"
                    m = re.search(search_string, line)
                    if m:
                        word_to_correct = m.group(1)
                    search_string = "bit ([0-9]+)"
                    m = re.search(search_string, line)
                    if m:
                        bit_to_correct = m.group(1)

                    location_to_correct = frame_to_correct + ' ' + word_to_correct + bit_to_correct
                    # write_to_log("Injected location " + location_to_correct, jcm_log)
                    
                if "Fault Injection Succeeded!" in line:
                    line = "[{}] ".format(time.strftime("%Y-%m-%d %H:%M:%S")) + "Fault Injected!\n"
                    print("Fault injection succeeded!", file=print_jcm_fout)
                    keep_reading = False


    def correct_fault(ssh_client):
        '''
        Injects a fault to correct it
        '''
        global frame_to_correct
        global word_to_correct
        global bit_to_correct
        global location_to_correct
        global CORRECTION_FAULT_INJECTION_COMMAND
        global DESIGN
        global FAULT_INJECTION_ENABLED

        location = location_to_correct[2:]
        location = location.split()
        inject_address = hex(int(location[0],16))
        inject_word = int(location[1])
        inject_bit = int(location[2])

        command = CORRECTION_FAULT_INJECTION_COMMAND.format(fpga = PART, frads = FRADS, design = DESIGN, frame = inject_address, word = inject_word, bit = inject_bit)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        line = ""
        time_start = time.time()
        keep_reading = True
        while keep_reading:
            
            if not FAULT_INJECTION_ENABLED:
                return 1
            
            cur_time = time.time()
            if (cur_time-time_start >30):
                os.execv(sys.executable, ['python3'] + sys.argv) # Restarts the program
            line = stdout.readline()
            if (not line.isspace()) and line != '':
                print(time.strftime("%Y-%m-%d %H:%M:%S"), " : ", line, file=print_jcm_fout)
                line = "[{}] ".format(time.strftime("%Y-%m-%d %H:%M:%S")) + line
                if "Failed!" in line:
                    return 1
                if "Fault Injection Succeeded!" in line:
                    line = "[{}] ".format(time.strftime("%Y-%m-%d %H:%M:%S")) + "Fault Corrected!\n"
                    print("Fault correction succeeded!", file=print_jcm_fout)
                    keep_reading = False



""" Record time and data in both log and output 

Parameters:
    output_str (str): The string to output in a log file and in stdout."""
def _record_data(output_str):
    print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] ", output_str)
    logging.info(output_str)



"""Does nothing, transition to the board_plugged_in state."""
def start_actions(experiment, state):
    _record_data("Starting test")
    pass



""" Check if dev port exists, confirm the nexys video board
    is plugged in.
    
    Attributes:
        board_powered_on (int) = This holds the dev_port number, otherwise
        -1 if the dev port file could not be found.
        give_up_time (bool): True if time to give up on checking board, 
        otherwise false.
"""
def board_plugged_in_actions(experiment, state):
    _record_data("Confirming board plugged in")
    experiment.board_powered_on = -1
    experiment.give_up_time = False

    if not hasattr(experiment, 'give_up_timer'):
        experiment.give_up_timer = 0
    
    # Set starting number to -1, send command to see if /dev/ttyUSBX
    # file exists, interpret by reading resulting output string.
    max_num = STARTING_FILE_NUM
    for i in range(0, MAX_FILE_NUM):
        output_str = pexpect.run("ls /dev/ttyUSB" + str(i), encoding="utf-8", logfile=sys.stdout)
        if not ("cannot access '/dev/ttyUSB" + str(i) + "': No such file or directory" in output_str and (i > max_num)):
            max_num = i

    # Set attribute file_num as the dev port number. If dev port doesn't 
    # exist, file_num is -1.
    global serial_port
    serial_port = max_num
    if (max_num > 0):
        _record_data("Board plugged in, using /dev/ttyUSB{max_int}.".format(max_int=max_num))
        experiment.board_powered_on = max_num
        experiment.give_up_timer = 0
    else:
        _record_data("Board not plugged in.")
        experiment.give_up_timer += 1
        if (experiment.give_up_timer >= MAX_NUM_TIMES_BOOT_UP):
            experiment.give_up_time = True
        else:
            time.sleep(10)




""" Stay here indefinitely, board is not plugged in or usable."""
def give_up_actions(experiment, state):
    _record_data("Giving up")
    while(True):
        time.sleep(1)



"""Create SSHclient connection to JCM. """
def jcm_login_actions(experiment, state):
    _record_data("Logging in to JCM")
    
    # Make SSHclient object to connect to JCM. Check that this is open
    # during transitions
    global jcm_client
    jcm_client = jcm_control.login_to_jcm(JCM_IP_ADDRESS)



"""Send board configuration command to JCM, configure nexys video board with program.

    Attributes:
        jcm_configured (bool): True if jcm successfully configured board, else False.
"""
def jcm_configure_board_actions(experiment, state):
    _record_data("Configuring JCM with new program")

    experiment.jcm_configured = False
    if (jcm_control.configure_fpga(jcm_client) == 0):
        experiment.jcm_configured = True



"""Connect to Litex Terminal by fdspawn 

    Attributes:
        connection_return_val (int) = 0 if connected, all is well. 1 if a timeout or
        problem with connection occured.

"""
def connect_to_litex_serial_actions(experiment, state):
    _record_data("Starting litex with /dev/ttyUSB{}".format(str(serial_port)))
    experiment.connection_return_val = 0

    serial_str = r"/dev/ttyUSB" +  str(serial_port)
    global fd
    fd = Serial(serial_str, baudrate = LITEX_BAUDRATE)

    try:
        global fdspawn_obj
        fdspawn_obj = fdspawn(fd, encoding="utf-8", logfile=sys.stdout, timeout=BOARD_REPROGRAM_TIMEOUT)
        return 
    except pexpect.exceptions.TIMEOUT:
        _record_data("Timeout occured connecting to litex terminal")
        experiment.connection_return_val = 1
        fdspawn_obj = None
        return 
    except Exception:
        _record_data("Unexpected exception connecting to litex terminal")
        experiment.connection_return_val = 1
        fdspawn_obj = None
        return 



"""Expect 'LITEX>>' prompt

    This function will simply expect a litex>> prompt.

    Attributes:
        expect_litex_return_val (int) = Returns 0 if no problems occured, 1 if 
        a timeout error occured or a UnicodeDecode error occured more than 20x
        
    """
def expect_litex_prompt_actions(experiment, state):
    _record_data("Expecting Litex Prompt")

    experiment.expect_litex_return_val = 0
    unicode_decode_counter = 0
    while (True):
        try:
            fdspawn_obj.sendline("\n")
            fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=BOARD_REPOWER_TIMEOUT)
            break
        except pexpect.exceptions.TIMEOUT:
            _record_data("Timeout occured expecting Litex>> prompt")
            experiment.expect_litex_return_val = 1
            break
        except UnicodeDecodeError:
            _record_data("Unicode error occured, retrying up to 20x")
            unicode_decode_counter += 1
            if (unicode_decode_counter >= MAX_NUM_UNICODE_EXCEPTIONS):
                _record_data("Max number of unicode errors reached")
                experiment.expect_litex_return_val = 1
                break



"""Use JCM to launch first fault injection
"""
def create_first_fault_actions(experiment, state):
    _record_data("Injected first fault")
    jcm_control.inject_fault(jcm_client)



"""Send bist command to terminal

    """
def send_bist_cmd_actions(experiment, state):
    _record_data("Starting bist")

    cmd_str = "sdram_bist " + str(BURST_LENGTH) + " " + str(RAND_ARG)
    fdspawn_obj.sendline(cmd_str)



""" Expect title, line of data as the bist runs

    Attributes:
        isUnicodeError (bool): True if a UnicodeDecode exception occured
        isTimeOut (bool): True if a Timeout exception occured
        isEOFError (bool): True if an EOF exception occured.
        isError (bool): True if another exception occured.
        gotTitle (bool): True if title printed out
        gotData (bool): True if data printed out, returns values of error counts
        invalid_input(bool): True if data not recognized between title outputs, 
        otherwise False.
    """
def expect_title_line_actions(experiment, state):
    experiment.isUnicodeError = False
    experiment.isTimeOut = False
    experiment.isEOFError = False
    experiment.isError = False
    experiment.gotTitle = False
    experiment.gotData = False
    experiment.invalid_input = False

    # Error correction, Data must be read between titles, otherwise 
    # data output is no good.
    if not (hasattr(experiment, '_data_output_before_title')):
        experiment._data_output_before_title = False
    if not (hasattr(experiment, '_first_run')):
        experiment._first_run = True

    unicode_error_index = 0

    global new_error_cnt
    global new_sec_cnt
    global new_ded_cnt

    new_error_cnt = 0
    new_sec_cnt = 0
    new_ded_cnt = 0

    while (True):
        try:
            match_index = fdspawn_obj.expect(["WR-BW\(MiB/s\) RD-BW\(MiB/s\)  TESTED\(MiB\)     ERRORS        SEC        DED", # Title
                                    "\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*"],                  # Reg Expression matching 6 arguments
                                    timeout=WAIT_TEXT_TIMEOUT)
        
            if fdspawn_obj.match:

                if match_index == TITLE_INDEX:
                    experiment.gotTitle = True

                    # Check that valid input has outputted, or its the first run
                    if (experiment._data_output_before_title or experiment._first_run):
                        experiment._data_output_before_title = False
                        experiment._first_run = False
                    else:
                        experiment.invalid_input = True

                    _record_data("")

                elif match_index == DATA_INDEX:

                    # Data recognized
                    experiment._data_output_before_title = True

                    # Split apart, take data and return error counts
                    result_str = str(fdspawn_obj.match.group(0)).split()

                    new_error_cnt = int(result_str[ERROR_MSG_INDEX])
                    new_sec_cnt = int(result_str[SEC_MSG_INDEX])
                    # new_ded_cnt = int(result_str[DED_MSG_INDEX
                    ded_string = result_str[DED_MSG_INDEX]
                    ded_string_int = "0"
                    if (ded_string.find('\'', 0) == -1):
                        ded_string_int = ded_string
                    else :
                        ded_string_int = ded_string[:ded_string.find('\'', 0):]
                    new_ded_cnt = int(ded_string_int)

                    experiment.gotData = True

                    _record_data("")

            else:
                # Reach here if no match found
                _record_data("Unexpected, no match found")

            
        except pexpect.exceptions.TIMEOUT:
            _record_data("Time out whie expecting title or data")
            experiment.isTimeOut = True
            # Set this for the next time we expect title or data
            experiment._first_run = True
            break

        except pexpect.exceptions.EOF:
            _record_data("EOF exception while expecting title or data")
            experiment.isEOFError = True
            # Set this for the next time we expect title or data
            experiment._first_run = True
            break

        except UnicodeDecodeError:
            _record_data("UnicodeDecodeException whie expecting title or data")
            unicode_error_index += 1

            if (unicode_error_index >= MAX_NUM_UNICODE_EXCEPTIONS):
                _record_data("Too many UnicodeDecode exceptions")
                experiment.isUnicodeError = True
                # Set this for the next time we expect title or data
                experiment._first_run = True
                break

        except Exception:
            _record_data("Other exception occured whie expecting title or data")
            _record_data(str(Exception))
            experiment.isError = True
            # Set this for the next time we expect title or data
            experiment._first_run = True
            break



""" Check if errors have come up. This resets the line of fixing dram errors
    by setting degree_of_max_error to zero

    Attributes:
        errors_exist (bool): True if errors exist, otherwise false.
        
"""
def check_if_errors_exist_actions(experiment, state):
    experiment.errors_exist = False
    
    if (new_error_cnt > 0 or new_sec_cnt > 0 or new_ded_cnt > 0):
        experiment.errors_exist = True
    else:
        global degree_of_max_error
        degree_of_max_error = 0



""" Check if errors have come up, after 30x or so it will return true.

    Attributes:
        errors_incrementing (bool): True if errors exist, otherwise false.
        errors_stopped_incrementing (bool): True if errors exist, otherwise false.
"""
def check_if_errors_increment_actions(experiment, state):
    experiment.errors_incrementing = False
    experiment.errors_stopped_incrementing = False

    if not hasattr(experiment, '_increment_error_count'):
        experiment._increment_error_count = 0
    if not hasattr(experiment, '_stopped_increment_error_count'):
        experiment._increment_error_count = 0
    if not hasattr(experiment, '_old_error_cnt'):
        experiment._old_error_cnt = 0
    if not hasattr(experiment, '_old_sec_cnt'):
        experiment._old_sec_cnt = 0
    if not hasattr(experiment, '_old_ded_cnt'):
        experiment._old_ded_cnt = 0

    # Output to user if dram errors begin to exist
    if ((experiment._old_error_cnt == 0) and 
        (experiment._old_sec_cnt == 0) and
        (experiment._old_ded_cnt == 0)):
        _record_data("Errors detected")

    if ((new_error_cnt > experiment._old_error_cnt) or 
        (new_sec_cnt > experiment._old_sec_cnt) or
        (new_ded_cnt > experiment._old_ded_cnt)):
        
        experiment._stopped_increment_error_count = 0
        experiment._increment_error_count += 1
        if (experiment._increment_error_count >= MAX_ERROR_CNT_CYCLES):
            experiment.errors_incrementing = True
            experiment._increment_error_count = 0

    else:
        experiment._stopped_increment_error_count += 1
        experiment._increment_error_count = 0
        if (experiment._stopped_increment_error_count >= MAX_PAUSE_ERROR_CNT_CYCLES):
            experiment.errors_stopped_incrementing = True
            experiment._stopped_increment_error_count = 0


    experiment._old_error_cnt = new_error_cnt
    experiment._old_sec_cnt = new_sec_cnt
    experiment._old_ded_cnt = new_ded_cnt



""" Check if time to correct and inject fault

    Attributes: 
        isTimeToInject (bool): True if time to inject
        this cycle, otherwise false."""

def correct_inject_fault_time_actions(experiment, state):
    experiment.isTimeToInject = False

    if not hasattr(experiment, '_correct_inject_fault_timer'):
        experiment._correct_inject_fault_timer = 0
    _record_data("Value of inject fault timer: {}".format(experiment._correct_inject_fault_timer))
    experiment._correct_inject_fault_timer += 1
    _record_data("Value of inject fault timer: {}".format(experiment._correct_inject_fault_timer))

    if (experiment._correct_inject_fault_timer >= FAULT_TIMER_MAX):
        experiment.isTimeToInject = True



""" Correct fault and inject fault 
"""
def correct_inject_fault_actions(experiment, state):
    _record_data("Fault injected!")
    jcm_control.correct_fault(jcm_client)
    jcm_control.inject_fault(jcm_client)



""" Close bist, correct fault. Happens if errors are incrementing

    Attributes:
        timeout_occured (bool): Timeout occured while expecting 'litex>>' prompt
"""
def restart_bist_actions(experiment, state):

    experiment.timeout_occured = False

    try:
        _record_data("Closing bist")
        fdspawn_obj.sendline("\n")
        fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=BOARD_REPOWER_TIMEOUT)

        cmd_str = "sdram_bist " + str(BURST_LENGTH) + " " + str(RAND_ARG)
        fdspawn_obj.sendline(cmd_str)

    except pexpect.exceptions.TIMEOUT:
        _record_data("Timeout occured restarting bist")
        experiment.timeout_occured = True



""" Close bist, correct fault, prep to go through cycle of error fixing 

    Attributes: 
        timeout_occured (bool): True if timeout occured, otherwise false
"""
def close_bist_correct_fault_actions(experiment, state):
    experiment.timeout_occured = False

    try:
        _record_data("Closing bist")
        fdspawn_obj.sendline("\n")
        fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=BOARD_REPOWER_TIMEOUT)
    except pexpect.exceptions.TIMEOUT:
        experiment.timeout_occured = True
        return

    # After closing bist, correct one fault
    jcm_control.correct_fault(jcm_client)



""" Go through a list of actions of what to do, one by one, until
    there are no more errors outputting.
    A single fault will be injected if this function succeeds, otherwise
    nothing will happen with the jcm.
    
    Attributes:
        failed_to_correct_errors (bool): True if we've gone through the whole
        cycle, errors still appear
"""
def debug_error_actions(experiment, state):
    experiment.failed_to_correct_errors = False
    experiment.timeout_occured_in_debug = False

    # This is set to zero in the state checking if errors exist.
    degree_of_max_error += 1
    try:
        if (degree_of_max_error == RESTART_BIST_INDEX):
            # Do nothing, simply restart bist
            pass
        elif (degree_of_max_error == SDRAM_MODE_SCRUB_INDEX):

            fdspawn_obj.sendline("sdram_mr_scrub")
            fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)

        elif (degree_of_max_error == SDRAM_DELAY_SCRUB_INDEX):

            fdspawn_obj.sendline("sdram_delay_scrub")
            fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)

        elif (degree_of_max_error == SDRAM_CALLIBRATE_INDEX):

            fdspawn_obj.sendline("sdram_cal")
            fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)

        elif (degree_of_max_error == SDRAM_INIT_INDEX):

            fdspawn_obj.sendline("sdram_init")
            fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)

        elif (degree_of_max_error == SOC_REBOOT_INDEX):

            fdspawn_obj.sendline("reboot")
            fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)

        else:

            experiment.failed_to_correct_errors = True

        if not experiment.failed_to_correct_errors:   

            # Inject one fault
            jcm_control.inject_fault(jcm_client)

            # Restart bist
            cmd_str = "sdram_bist " + str(BURST_LENGTH) + " " + str(RAND_ARG)
            fdspawn_obj.sendline(cmd_str)

    except pexpect.exceptions.TIMEOUT:
        experiment.timeout_occured_in_debug = True



""" Correct fault
"""
def correct_fault_actions(experiment, state):

    jcm_control.correct_fault(jcm_client)



""" Attempt to restart Litex 
    """
def restart_litex_actions(experiment, state):
    experiment.restart_success = False

    try:
        fd.close()
        fd.open()
        fdspawn_obj = fdspawn(fd, encoding="utf-8", logfile=sys.stdout, timeout=BOARD_REPROGRAM_TIMEOUT)
        fdspawn_obj.sendline("\n")
        fdspawn_obj.expect(pattern="^.*litex[^>]*> ", timeout=BOARD_REPROGRAM_TIMEOUT)
        experiment.restart_success = True
    except pexpect.exceptions.TIMEOUT:
        _record_data("Timeout occured restarting Litex")
    except Exception:
        _record_data("Other exception occured restarting Litex")
        _record_data(str(Exception))


    
def repower_board_actions(experiment, state):
    
    # Stop JCM
    jcm_control.close_jcm(jcm_client)

    teln = telnetlib.Telnet(NETBOOTER_IP, None, timeout=TIMEOUT_NETBOOTER)

    # Turn off
    s = teln.read_some()
    time.sleep(SLEEPTIME_NETBOOTER)

    s = ("pset " + str(NETBOOTER_IP) + " 0").encode("ascii") + b"\r\n\r\n"
    teln.write(s)
    time.sleep(SLEEPTIME_NETBOOTER)

    # Turn back on
    s = ("pset " + str(NETBOOTER_IP) + " 1").encode("ascii") + b"\r\n\r\n"
    teln.write(s)
    time.sleep(SLEEPTIME_NETBOOTER)
    teln.close()



def main():
    # Set up logger settings
    logging.basicConfig(filename="times_18.txt", level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S', format='%(asctime)s %(levelname)-8s %(message)s')
    
    # Create a new experiment object
    experiment = Experiment()

    # Create initial state
    experiment.add_state(ExperimentState(
        "Initial Starting State",
        start_actions,
        Transition(lambda ex, st: True, "Plugged In State")
    ))

    # Create plugged in state
    experiment.add_state(ExperimentState(
        "Plugged In State",
        board_plugged_in_actions,
        Transition(lambda ex, st: ex.give_up_time, "Give Up State"),
        Transition(lambda ex, st: ex.board_powered_on < 0, "Plugged In State"),
        Transition(lambda ex, st: True, "Login JCM State")
    ))

    # Create give up state
    experiment.add_state(ExperimentState(
        "Give Up State",
        give_up_actions,
        Transition(lambda ex, st: True, "Give Up State")
    ))

    # Create login jcm state
    experiment.add_state(ExperimentState(
        "Login JCM State",
        jcm_login_actions,
        Transition(lambda ex, st: True, "Configure FPGA State")
    ))

    # Create configure fpga state
    experiment.add_state(ExperimentState(
        "Configure FPGA State",
        jcm_configure_board_actions,
        Transition(lambda ex, st: ex.jcm_configured, "Connect To Litex"),
        Transition(lambda ex, st: True, "Plugged In State")
    ))

    # Create connect to litex state
    experiment.add_state(ExperimentState(
        "Connect To Litex",
        connect_to_litex_serial_actions,
        Transition(lambda ex, st: ex.connection_return_val == 0, "Expect Litex Prompt State"),
        Transition(lambda ex, st: True, "Configure FPGA State")
    ))

    # Create expect litex prompt state
    experiment.add_state(ExperimentState(
        "Expect Litex Prompt State",
        expect_litex_prompt_actions,
        Transition(lambda ex, st: ex.expect_litex_return_val == 0, "Inject First Fault State"),
        Transition(lambda ex, st: True, "Repower State")
    ))

    # Create repower state
    experiment.add_state(ExperimentState(
        "Repower State",
        repower_board_actions,
        Transition(lambda ex, st: True, "Plugged In State")
    ))

    # Create inject first fault state
    experiment.add_state(ExperimentState(
        "Inject First Fault State",
        create_first_fault_actions,
        Transition(lambda ex, st: True, "Send Bist Command State")
    ))

    # Create send bist command state
    experiment.add_state(ExperimentState(
        "Send Bist Command State",
        send_bist_cmd_actions,
        Transition(lambda ex, st: True, "Expect Title Or Data State")
    ))

    # Create expect title or data state
    experiment.add_state(ExperimentState(
        "Expect Title Or Data State",
        expect_title_line_actions,
        Transition(lambda ex, st: (ex.isError or ex.isEOFError or ex.isTimeOut or ex.isUnicodeError or ex.invalid_input), "Correct Fault State"),
        Transition(lambda ex, st: ex.gotData, "Check If Errors Exist State"),
        Transition(lambda ex, st: True, "Give Up State")
    ))

    # Create check if errors exist state
    experiment.add_state(ExperimentState(
        "Check If Errors Exist State",
        check_if_errors_exist_actions,
        Transition(lambda ex, st: ex.errors_exist, "Check If Errors Increment State"),
        Transition(lambda ex, st: True, "Check If Fault Inject State")
    ))

    # Create check if fault inject state
    experiment.add_state(ExperimentState(
        "Check If Fault Inject State",
        correct_inject_fault_time_actions,
        Transition(lambda ex, st: ex.isTimeToInject, "Fault Correct Inject State"),
        Transition(lambda ex, st: True, "Expect Title Or Data State")
    ))

    # Create fault correct inject state
    experiment.add_state(ExperimentState(
        "Fault Correct Inject State",
        correct_inject_fault_actions,
        Transition(lambda ex, st: True, "Expect Title Or Data State")
    ))

    # Create check if Errors increment state
    experiment.add_state(ExperimentState(
        "Check If Errors Increment State",
        check_if_errors_increment_actions,
        Transition(lambda ex, st: ex.errors_stopped_incrementing, "Close Restart Bist State"),
        Transition(lambda ex, st: ex.errors_incrementing, "Close Bist Correct Fault State"),
        Transition(lambda ex, st: True, "Check If Fault Inject State")
    ))

    # Create close restart bist state
    experiment.add_state(ExperimentState(
        "Close Restart Bist State",
        restart_bist_actions,
        Transition(lambda ex, st: ex.timeout_occured, "Correct Fault State"),
        Transition(lambda ex, st: True, "Expect Title Or Data State")
    ))

    # Create close bist correct fault state
    experiment.add_state(ExperimentState(
        "Close Bist Correct Fault State",
        close_bist_correct_fault_actions,
        Transition(lambda ex, st: ex.timeout_occured, "Correct Fault State"),
        Transition(lambda ex, st: True, "Fix Errors State")
    ))

    # Create fix errors state
    experiment.add_state(ExperimentState(
        "Fix Errors State",
        debug_error_actions,
        Transition(lambda ex, st: (ex.timeout_occured_in_debug or ex.failed_to_correct_errors), "Restart Litex State"),
        Transition(lambda ex, st: True, "Expect Title Or Data State")
    ))

    # Create correct fault state
    experiment.add_state(ExperimentState(
        "Correct Fault State",
        correct_fault_actions,
        Transition(lambda ex, st: True, "Restart Litex State")
    ))

    experiment.add_state(ExperimentState(
        "Restart Litex State",
        restart_litex_actions,
        Transition(lambda ex, st: ex.restart_success, "Inject First Fault State"),
        Transition(lambda ex, st: True, "Configure FPGA State")
    ))

    experiment.set_next_state("Initial Starting State")
    experiment.start()
    print(f"Experiment finished in state: {experiment.get_current_state()}")


if __name__ == "__main__":
    main()

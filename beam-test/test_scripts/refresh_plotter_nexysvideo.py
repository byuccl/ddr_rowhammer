#!/usr/bin/env python3




'''
An executable to get data (number of errors) based on 
chosen refresh time and wait time. Ideally, the order
of writing will occur as follows:

WRITE  ->  WAIT  ->  READ/CHECK ERROR COUNT

Wait time is currently in seconds. 
Refresh time is currently in clock cycles. 
The Universal standard refresh time in drams is 7.8us.
(586 ck for 7.8us refresh time in nexys4ddr   (clk freq. of 75000000Hz),
 782 ck for 7.8us refresh time in nexys_video (clk freq. of 100000000Hz))

Build/load the bitstream before running this program.
'''


import argparse
import time
import re
import os
import matplotlib.pyplot as plt
import numpy as np

from serial import Serial
from pexpect.fdpexpect import fdspawn
from timestampedfile_modified import TimestampedFile
from pathlib import Path
from matplotlib.collections import PolyCollection





DEFAULT_SERIAL_BAUDRATE = 115200
BEG_TEST = 1
DOUBLE_REFRESH = 2

DEFAULT_TTY_STR = "/dev/ttyUSB"
TIME_STRING_FORMAT = "%Y-%m-%d %H:%M:%S"
LITEX_LOGIN_PATTERN = "^.*litex[^>]*> "
FILE_BEG_STR = b"\n\nPoints are organized as follows: \n\n(REFRESH-RATE(IN CK), WAIT-TIME(IN SEC), WRITING_ALL_ONES/ZEROS) : (ERROR-RANGE, ERROR-COUNT, ERROR-LIST-LENGTH)\n\n\n\n\n"
FILE_POINT_STR = "(refresh-rate(ck)={refresh_rate}, wait-time(sec)={wait_time}, writing all {ones_zeros}) : (error-range={error_range}, error-count={error_count}, list-length={list_length})\n"
PROGRESS_STR = "Test ({testnum}/{total_tests}): Test wait time = {wait_time}s"
WRITING_ONES_STR = "ones"
WRITING_ZEROS_STR = "zeros"
WRITING_ONES_CMD_STR = "0xffffffff"
WRITING_ZEROS_CMD_STR = "0x00000000"
BIST_REFRESH_CMD_RESET_STR = "sdram_refresh_set 782"
BIST_REFRESH_CMD_SR = "sdram_refresh_set {refresh_rate}"
BIST_PAT_CMD_STR = "sdram_bist_pat {bist_pat_str}"
BIST_WRITER_CMD_STR = "sdram_bist_writer 0x0 0xfffffff"
BIST_READER_CMD_STR = "sdram_bist_reader 0x0 0xfffffff {err_lim}"
BEG_NEW_REFRESH_RATE_STR="\n\n\n###################################################################\n# Refresh rate {rfsh_rate}\n###################################################################\n\n"
TOT_NUM_TESTS_STR = "Total number of tests: "

BIST_ERROR_MSG_REGEX = b'0x[a-f0-9]{7}:  [ a-f0-9]{7}[a-f0-9] [ a-f0-9]{7}[a-f0-9] [ a-f0-9]{7}[a-f0-9] [ a-f0-9]{7}[a-f0-9]'
BIST_ERROR_RANGE_REGEX = b'Error address range: 0x[0-9a-f]{6,7}-0x[0-9a-f]{6,7},'
BIST_ERROR_CNT_REGEX = b'Num Errors: [0-9]+,'

DRAM_WAIT_TIMES = [300]




def create_display_subplot(args, input_list, refresh_list, max_error_cnt, write_ones:bool):
    # Plot everything
    # Set subplot up
    ax = plt.figure().add_subplot(projection='3d')

    # Get colors for each graph
    facecolors = plt.colormaps['viridis_r'](np.linspace(0, 1, len(input_list)))

    poly = PolyCollection(input_list, facecolors=facecolors)
    ax.add_collection3d(poly, zs=refresh_list, zdir='y')
    ax.set(xlim=(DRAM_WAIT_TIMES[0], DRAM_WAIT_TIMES[len(DRAM_WAIT_TIMES) - 1]), ylim=(0, args.end_refresh_rate), zlim=(0, max_error_cnt), xlabel='Wait time (sec)', ylabel='Refresh rate (ck)', zlabel='Errors') # xlim=(0, 10), ylim=(1, 9), zlim=(0, 0.35),
    # ax.add_collection3d(poly, zs=range(0, len(refresh_list)), zdir='y')
    # ax.set(xlim=(DRAM_WAIT_TIMES[0], DRAM_WAIT_TIMES[len(DRAM_WAIT_TIMES) - 1]), ylim=(0, len(refresh_list)), zlim=(0, max_error_cnt), xlabel='Wait time (sec)', ylabel='Refresh rate tests', zlabel='Errors') # xlim=(0, 10), ylim=(1, 9), zlim=(0, 0.35),

    if write_ones:
        plt.title("Writing All Ones")
    else:
        plt.title("Writing All Zeros")

    plt.show(block=False)




def extract_err_range_cnt_num(output_str : str):

    '''
    Take a string and get three things:
    Error address range (str)
    Error Count (int)
    Error List (list of strings)
    '''

    addr_range = ""
    temp_str = ""
    err_count = 0
    err_list = []
    
    # First verify and extract error address range
    matched_str = re.search(pattern=BIST_ERROR_RANGE_REGEX, string=output_str)
    if (matched_str != None):
        # Get the matched string
        addr_range = matched_str.group(0)
        # Take off unecessary characters
        addr_range = addr_range[21:len(addr_range) - 1]
    

    # Now verify and extract error count
    matched_str = re.search(pattern=BIST_ERROR_CNT_REGEX, string=output_str)
    if (matched_str != None):
        # Get the matched string
        temp_str = matched_str.group(0)
        # Take off unecessary characters
        err_count = int(temp_str[12:len(temp_str) - 1])

    # Finally extract the list of errors
    err_list = re.findall(pattern=BIST_ERROR_MSG_REGEX, string=output_str)
    
    return addr_range, err_count, err_list



# Run all the bist commands for the test
def run_bist_cmds(args, refresh_rate : int, wait_time : int, serial_fdspawn : fdspawn, with_ones : bool):

    # First set the refresh rate
    serial_fdspawn.sendline(BIST_REFRESH_CMD_SR.format(refresh_rate=str(refresh_rate)))
    serial_fdspawn.expect(LITEX_LOGIN_PATTERN, timeout=30)

    # Next set the pattern
    if (with_ones):
        serial_fdspawn.sendline(BIST_PAT_CMD_STR.format(bist_pat_str=WRITING_ONES_CMD_STR))
    else:
        serial_fdspawn.sendline(BIST_PAT_CMD_STR.format(bist_pat_str=WRITING_ZEROS_CMD_STR))
    serial_fdspawn.expect(LITEX_LOGIN_PATTERN, timeout=30)

    # Start the BIST Writer
    serial_fdspawn.sendline(BIST_WRITER_CMD_STR)
    serial_fdspawn.expect(LITEX_LOGIN_PATTERN, timeout=30)
    time.sleep(wait_time)

    # Reset the refresh rate to normal
    serial_fdspawn.sendline(BIST_REFRESH_CMD_RESET_STR)
    serial_fdspawn.expect(LITEX_LOGIN_PATTERN, timeout=30)

    # Start the BIST reader
    serial_fdspawn.sendline(BIST_READER_CMD_STR.format(err_lim=str(args.error_limit)))
    serial_fdspawn.expect(LITEX_LOGIN_PATTERN, timeout=None)

    # Return match object 
    return serial_fdspawn



def run_test_get_results(args, err_list_file, serial_fdspawn:fdspawn, refresh_rate:int, wait_time:int, with_ones:bool):

    # Output if writing all ones or zeros
    if with_ones:
        ones_zeros = WRITING_ONES_STR
    else:
        ones_zeros = WRITING_ZEROS_STR

    # Write all ones first
    serial_fdspawn = run_bist_cmds(
        args=args,
        refresh_rate=refresh_rate,
        wait_time=wait_time,
        serial_fdspawn=serial_fdspawn,
        with_ones=with_ones)

    # Obtain all point data and write it to file
    addr_range, err_count, err_list = extract_err_range_cnt_num(serial_fdspawn.match.group(0))
    err_point_str = FILE_POINT_STR.format(
        refresh_rate=str(refresh_rate), 
        wait_time=str(wait_time), 
        ones_zeros=ones_zeros, 
        error_range=addr_range, 
        error_count=err_count, 
        list_length=str(len(err_list)))
    # err_list_file.write(bytes(err_point_str, 'utf-8'))

    # Write all the errors under the point
    # string_to_write = ""
    # if len(err_list) > 0:
    #     string_to_write = b"\n".join(error for error in err_list)
    #     err_list_file.write(string_to_write + b"\n\n")
    # else:
    #     pass
    #     err_list_file.write(b"\n")

    # Return the point
    return err_count, (wait_time, err_count)



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




def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--tty_port", help="Port number of ttyUSB device to use", type=int, required=True)
    parser.add_argument("--filename", help="Filename for log", type=str, required=True)
    parser.add_argument("--log_dir", help="Directory to store log files", type=str)
    parser.add_argument("--error_limit", help="Set limit of errors to print out in bist", default=1000, type=int)
    parser.add_argument("--beg_refresh_rate", help="Beginning refresh rate", default=586, type=int)
    parser.add_argument("--end_refresh_rate", help="Ending refresh rate", default=4000000000, type=int)
    args = parser.parse_args()

    # Create list to hold all points for writing zeros and ones
    ones_error_point_list = []
    zeros_error_point_list = []

    # Create path for logfile
    log_dir = Path(".")
    if args.log_dir:
        if not os.path.exists(args.log_dir):
            os.makedirs(args.log_dir)
        log_dir = Path(args.log_dir)

        # Create files to hold all errors output
        # zeros_err_list_file = open(args.log_dir + '/' + args.filename + '_WRITING_ZEROS.log', 'wb')
        # ones_err_list_file = open(args.log_dir + '/' + args.filename + '_WRITING_ONES.log', 'wb')
    else:

        # Create files to hold all errors output
        # zeros_err_list_file = open(args.filename + '_WRITING_ZEROS.log', 'wb')
        # ones_err_list_file = open(args.filename + '_WRITING_ONES.log', 'wb')
        pass
    
    

    # Begin writing to files
    # zeros_err_list_file.write(FILE_BEG_STR)
    # ones_err_list_file.write(FILE_BEG_STR)

    # # Create uart stdout and log file
    # uart_log_filename = create_log_path("UART",args.filename, log_dir)
    # uart_log_file = open(uart_log_filename,"wb")

    # # Format logfile
    # logfile = TimestampedFile(uart_log_file, timestampformat = TIME_STRING_FORMAT)

    # # Get serial device string for Serial object
    # serial_dev = DEFAULT_TTY_STR + str(args.tty_port)

    # # Create serial object to open with fdspawn
    # serial_fd = Serial(serial_dev, baudrate=DEFAULT_SERIAL_BAUDRATE)

    # # Open the port
    # serial_fdspawn = fdspawn(serial_fd, logfile=logfile)

    # Save beginning refresh rate
    refresh_rate = args.beg_refresh_rate

    # Create list of refresh rates
    refresh_list = []
    while refresh_rate <= args.end_refresh_rate:
        refresh_list.append(refresh_rate)
        if (refresh_rate == 0):
            refresh_rate += 1
        else:
            refresh_rate *= DOUBLE_REFRESH

    # Calculate total number of tests, output progression
    total_tests = DOUBLE_REFRESH * len(refresh_list) * len(DRAM_WAIT_TIMES)
    print(TOT_NUM_TESTS_STR, total_tests)

    # Run bist commands for every refresh time and wait time
    testindex = BEG_TEST
    max_error_cnt = 0
    for refresh_rate in refresh_list:


        # Create uart stdout and log file
        uart_log_filename = create_log_path("UART_refresh_rate_" + str(refresh_rate),args.filename, log_dir)
        uart_log_file = open(uart_log_filename,"wb")

        # Format logfile
        logfile = TimestampedFile(uart_log_file, timestampformat = TIME_STRING_FORMAT)

        # Get serial device string for Serial object
        serial_dev = DEFAULT_TTY_STR + str(args.tty_port)

        # Create serial object to open with fdspawn
        serial_fd = Serial(serial_dev, baudrate=DEFAULT_SERIAL_BAUDRATE)

        # Open the port
        serial_fdspawn = fdspawn(serial_fd, logfile=logfile)




        # Create list for holding error points
        zeros_error_point_graph = []
        ones_error_point_graph = []
        ones_error_point_graph.append((DRAM_WAIT_TIMES[0], 0))
        zeros_error_point_graph.append((DRAM_WAIT_TIMES[0], 0))

        # Print new refresh rate (for organization)
        # zeros_err_list_file.write(bytes(BEG_NEW_REFRESH_RATE_STR.format(rfsh_rate=refresh_rate), 'utf-8'))
        # ones_err_list_file.write(bytes(BEG_NEW_REFRESH_RATE_STR.format(rfsh_rate=refresh_rate), 'utf-8'))

        for wait_time in DRAM_WAIT_TIMES:

            ####################################################################
            # Switch here
            ####################################################################

            # Print progress
            print(PROGRESS_STR.format(testnum=testindex, total_tests=total_tests, wait_time=wait_time), end="\r")

            # Write all ones
            error_cnt, pnt = run_test_get_results(
                args=args,
                err_list_file='', # ones_err_list_file, 
                serial_fdspawn=serial_fdspawn,
                refresh_rate=refresh_rate, 
                wait_time=wait_time,
                with_ones=True)
            
            ones_error_point_graph.append(pnt)
            max_error_cnt = max(max_error_cnt, error_cnt)
            
            # Print progress
            testindex += 1

            ####################################################################

            print(PROGRESS_STR.format(testnum=testindex, total_tests=total_tests, wait_time=wait_time), end="\r")

            # Write all zeros
            error_cnt, pnt = run_test_get_results(
                args=args,
                err_list_file='', # zeros_err_list_file, 
                serial_fdspawn=serial_fdspawn,
                refresh_rate=refresh_rate, 
                wait_time=wait_time,
                with_ones=False)
            
            zeros_error_point_graph.append(pnt)
            max_error_cnt = max(max_error_cnt, error_cnt)
            
            # Count number of tests
            testindex += 1


            ####################################################################

            ####################################################################

        # To complete graphing shapes, add the final point
        ones_error_point_graph.append((DRAM_WAIT_TIMES[len(DRAM_WAIT_TIMES) - 1], 0))
        zeros_error_point_graph.append((DRAM_WAIT_TIMES[len(DRAM_WAIT_TIMES) - 1], 0))
    
        # Add points to lists
        ones_error_point_list.append(ones_error_point_graph)
        zeros_error_point_list.append(zeros_error_point_graph)

        refresh_rate *= DOUBLE_REFRESH

        # Close the port?
        serial_fd.close()

        # Close file?
        logfile.close()

        

    print(ones_error_point_list)
    print(zeros_error_point_list)
    print(refresh_list)

    # Create plots of both
    # create_display_subplot(args, ones_error_point_list, refresh_list, max_error_cnt, write_ones=True)
    # create_display_subplot(args, zeros_error_point_list, refresh_list, max_error_cnt, write_ones=False)

    # zeros_err_list_file.close()
    # ones_err_list_file.close()

    input("Press Enter to continue...       ")


if __name__ == "__main__":
    main()
#!/usr/bin/python3

"""
Parses the ctrl test data files and provides some analysis.


"""

import argparse # Command line argument parser

# Manages file paths
import pathlib 
from pathlib import Path 

# Shell utility for copying
import re 
import os

# For time delay
import time
import statistics
import pickle

# For enum variables
from enum import Enum

UART_TIME_REGEX = "\[2023-0((6-(2[6-9]|30))|(7-0[1-3])) [0-2][0-9]:[0-5][0-9]:[0-5][0-9]\]"
LITEX_PROMPT_REGEX = UART_TIME_REGEX + " [\x1B]\[92;1mlitex[\x1B]\[0m> "

TYPE_BOOT_REGEX = 0
TYPE_LITEX_PROMPT_REGEX = 1
TYPE_BIST_PAT_SETUP_REGEX = 2
TYPE_BIST_CONTINUOUS_REGEX = 3
TYPE_BIST_CONTINUOUS_ERROR_REGEX = 4
TYPE_BIST_IDLE_REGEX = 5
TYPE_BIST_IDLE_ERROR_REGEX = 6
TYPE_UNKNOWN = 7

LINE_TYPE_BEG = -1
BEG_LINE_INDEX = 1
TIME_NUM_ARGS = 6
LITEX_PROMPT_FOUND = 0
ERROR_LIST_INDEX = 3
ERROR_INFO_INDEX = 0
ERROR_DATA_OUTPUT_INDEX_CONT_FIRST = 4
ERROR_DATA_OUTPUT_INDEX_CONT_SECOND = 5
ERROR_DATA_OUTPUT_INDEX_IDLE = 7
NOERROR_DATA_OUTPUT_INDEX_IDLE = 9

READING_FILE_STR = "\nReading File: "
NUM_UART_FILE_LINES_STR = "Number of lines in uart file: "
IDLE_TESTNAME = "IDLE"
CONTINUOUS_TESTNAME = "CONTINUOUS"


class bist_utils:

    """
    A class to hold functions to set up the parser. These include 
    variables holding the regular expressions and checking 
    the test to see if its continuous.
    """

    # Get all the regular expressions needed for our parser
    def regex_setup(self):
        

        # Setup regular expressions for boot-up output from boards.
        self.boot_regex_list = {}
        self.boot_regex_list[0] = UART_TIME_REGEX + " [\x1B]\[1m        __   _ __      _  __[\x1B]\[0m\n"
        self.boot_regex_list[1] = UART_TIME_REGEX + " [\x1B]\[1m       \/ \/  \(_\) \/____ \| \|\/_\/[\x1B]\[0m\n"
        self.boot_regex_list[2] = UART_TIME_REGEX + " [\x1B]\[1m      \/ \/__\/ \/ __\/ -_\)>  <[\x1B]\[0m\n"
        self.boot_regex_list[3] = UART_TIME_REGEX + " [\x1B]\[1m     \/____\/_\/\\\\__\/\\\\__\/_\/\|_\|[\x1B]\[0m\n"
        self.boot_regex_list[4] = UART_TIME_REGEX + " [\x1B]\[1m   Build your hardware, easily![\x1B]\[0m\n"
        self.boot_regex_list[5] = UART_TIME_REGEX + "  \(c\) Copyright 2012-2023 Enjoy-Digital\n"
        self.boot_regex_list[6] = UART_TIME_REGEX + "  \(c\) Copyright 2007-2015 M-Labs\n"
        self.boot_regex_list[7] = UART_TIME_REGEX + "  BIOS built on (Jun|July) [0-9]{2} 2023 [0-9]{2}:[0-9]{2}:[0-9]{2}\n"
        self.boot_regex_list[8] = UART_TIME_REGEX + "  BIOS CRC passed \(((df9f327e)|(630265f5)|(9a6f6908))\)\n"
        self.boot_regex_list[9] = UART_TIME_REGEX + "  LiteX git sha1: f1da8a0c\n"
        self.boot_regex_list[10] = UART_TIME_REGEX + " --=============== [\x1B]\[1mSoC[\x1B]\[0m ==================--\n"
        self.boot_regex_list[11] = UART_TIME_REGEX + " [\x1B]\[1mCPU[\x1B]\[0m:		VexRiscv @ (75|100)MHz\n"
        self.boot_regex_list[12] = UART_TIME_REGEX + " [\x1B]\[1mBUS[\x1B]\[0m:		WISHBONE 32-bit @ 4GiB\n"
        self.boot_regex_list[13] = UART_TIME_REGEX + " [\x1B]\[1mCSR[\x1B]\[0m:		32-bit data\n"
        self.boot_regex_list[14] = UART_TIME_REGEX + " [\x1B]\[1mROM[\x1B]\[0m:		128.0KiB\n"
        self.boot_regex_list[15] = UART_TIME_REGEX + " [\x1B]\[1mSRAM[\x1B]\[0m:		8.0KiB\n"
        self.boot_regex_list[16] = UART_TIME_REGEX + " [\x1B]\[1mL2[\x1B]\[0m:		8.0KiB\n"
        self.boot_regex_list[17] = UART_TIME_REGEX + " [\x1B]\[1mSDRAM[\x1B]\[0m:		((128.0MiB 16-bit @ 300MT\/s \(CL-3 CWL-2\)\n)|(512.0MiB 16-bit @ 800MT\/s \(CL-7 CWL-5\)\n)|(16.0GiB 64-bit @ 800MT\/s \(CL-9 CWL-9\)\n))"
        self.boot_regex_list[18] = UART_TIME_REGEX + " [\x1B]1mMAIN-RAM[\x1B]\[0m:	128.0MiB\n"
        self.boot_regex_list[19] = UART_TIME_REGEX + " [\x1B]\[1mMAIN-RAM[\x1B]\[0m:	((128.0MiB)|(1.0GiB)|(512.0MiB))\n"
        self.boot_regex_list[20] = UART_TIME_REGEX + " --========== [\x1B]\[1mInitialization[\x1B]\[0m ============--\n"
        self.boot_regex_list[21] = UART_TIME_REGEX + " Initializing SDRAM @0x40000000...\n"
        self.boot_regex_list[22] = UART_TIME_REGEX + " Switching SDRAM to software control.\n"
        self.boot_regex_list[23] = UART_TIME_REGEX + " Write latency calibration:\n"
        self.boot_regex_list[24] = UART_TIME_REGEX + " ([\x00\x00]|)m0:6 m1:6 m2:6 m3:6 m4:6 m5:6 m6:6 m7:6 m8:6 m9:6 m10:6 m11:6 m12:6 m13:6 m14:6 m15:6 \n"
        self.boot_regex_list[25] = UART_TIME_REGEX + " Read leveling:\n"
        self.boot_regex_list[26] = UART_TIME_REGEX + "   m[0-9][0-9]*, b0[0-7]: \|[01]{32}\| delays: ((-)|([0-9]{2}\+\-[0-9]{2}))\n"
        self.boot_regex_list[27] = UART_TIME_REGEX + "   best: m[0-9][0-9]*, b0[0-7] delays: ((-)|([0-9]{2}\+\-[0-9]{2}))\n"
        self.boot_regex_list[28] = UART_TIME_REGEX + " Switching SDRAM to hardware control.\n"
        self.boot_regex_list[29] = UART_TIME_REGEX + " Memtest at 0x40000000 \(2.0MiB\)...\n"
        self.boot_regex_list[30] = UART_TIME_REGEX + "   Write: 0x40000000-0x40[0-2][02468ace]0000 ((0|128.0Ki|256.0Ki|384.0Ki|512.0Ki|640.0Ki|768.0Ki|896.0Ki)B|(1.[01235678]|2.0)MiB)   \n"
        self.boot_regex_list[31] = UART_TIME_REGEX + "    Read: 0x40000000-0x40[0-2][02468ace]0000 ((0|128.0Ki|256.0Ki|384.0Ki|512.0Ki|640.0Ki|768.0Ki|896.0Ki)B|(1.[01235678]|2.0)MiB)   \n"
        self.boot_regex_list[32] = UART_TIME_REGEX + " Memtest OK\n"
        self.boot_regex_list[33] = UART_TIME_REGEX + " Memspeed at 0x40000000 \(Sequential, 2.0MiB\)...\n"
        self.boot_regex_list[34] = UART_TIME_REGEX + "   Write speed: (25.3|35.9|85.4)MiB\/s\n"
        self.boot_regex_list[35] = UART_TIME_REGEX + "    Read speed: (34.0|46.8|70.2)MiB\/s\n"
        self.boot_regex_list[36] = UART_TIME_REGEX + " --============== [\x1B]\[1mBoot[\x1B]\[0m ==================--\n"
        self.boot_regex_list[37] = UART_TIME_REGEX + " Booting from serial...\n"
        self.boot_regex_list[38] = UART_TIME_REGEX + " Press Q or ESC to abort boot completely.\n"
        self.boot_regex_list[39] = UART_TIME_REGEX + " sL5DdSMmkekro\n"
        self.boot_regex_list[40] = UART_TIME_REGEX + " Timeout\n"
        self.boot_regex_list[41] = UART_TIME_REGEX + " No boot medium found\n"
        self.boot_regex_list[42] = UART_TIME_REGEX + " --============= [\x1B]\[1mConsole[\x1B]\[0m ================--\n"

        # Regular expression for litex prompt
        self.litex_promt_regex = LITEX_PROMPT_REGEX + "\n"

        # Setup regular expressions for bist setup output from boards.
        self.bist_pat_setup_regex_list = {}
        self.bist_pat_setup_regex_list[0] = LITEX_PROMPT_REGEX + "sdram_bist_pat 2779096485\n"
        self.bist_pat_setup_regex_list[1] = UART_TIME_REGEX + " sdram_bist_pat 2779096485\n"
        self.bist_pat_setup_regex_list[2] = UART_TIME_REGEX + " Pattern set to: ((a5a5a5a5 a5a5a5a5 ){1,2}|(a5a5a5a5 a5a5a5a5 ){8})\n"
        self.bist_pat_setup_regex_list[3] = LITEX_PROMPT_REGEX + "sdram_mr_scrub\n"
        self.bist_pat_setup_regex_list[4] = LITEX_PROMPT_REGEX + "sdram_delay_scrub\n"
        self.bist_pat_setup_regex_list[5] = LITEX_PROMPT_REGEX + "sdram_mr_scrub\n"
        self.bist_pat_setup_regex_list[6] = UART_TIME_REGEX + " Setting SDRAM Mode Register to defaults.\n"
        self.bist_pat_setup_regex_list[7] = LITEX_PROMPT_REGEX + "sdram_cal\n"
        self.bist_pat_setup_regex_list[8] = LITEX_PROMPT_REGEX + "sdram_init\n"
        self.bist_pat_setup_regex_list[9] = LITEX_PROMPT_REGEX + "reboot\n"
        self.bist_pat_setup_regex_list[10] = UART_TIME_REGEX + " sdram_cal\n"
        self.bist_pat_setup_regex_list[11] = UART_TIME_REGEX + " sdram_init\n"
        self.bist_pat_setup_regex_list[12] = UART_TIME_REGEX + " reboot\n"

        # Setup regular expressions for the bist continuous experiment.
        self.bist_continuous_regex_list = {}
        self.bist_continuous_regex_list[0] = LITEX_PROMPT_REGEX + "sdram_bist 0x0 268435455 1000 (0|1) 1 0 0\n"
        self.bist_continuous_regex_list[1] = UART_TIME_REGEX + " sdram_bist 0x0 268435455 1000 (0|1) 1 0 0\n"
        self.bist_continuous_regex_list[2] = UART_TIME_REGEX + " DRAM controller has address width (24, data width 64|25, data width 128|28, data width 512) in bits\n"
        self.bist_continuous_regex_list[3] = UART_TIME_REGEX + " Starting Bist with length 268435455, address mode (0|1), wmode 1 at clock frequency (75000000|100000000)\n"
        self.bist_continuous_regex_list[4] = UART_TIME_REGEX + "  WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED\(MiB\/s\)  RD-SPEED\(MiB\/s\)      ADDRESSES TESTED     ERRORS\n"
        self.bist_continuous_regex_list[5] = UART_TIME_REGEX + "(            0     178443[345][0-9]            0     16777216                0              534   0x0000000-0x0ffffff          0\n|            0     3877[12][0-9]{3}            0     33554432                0             1315   0x0000000-0x1ffffff          0\n|            0    30339[45][0-9]{3}            0    268435456                0             5379   0x0000000-0xfffffff          0\n)"
        self.bist_continuous_regex_list[6] = UART_TIME_REGEX + "(     18164[01][0-9]{2}     178443[345][0-9]     16777216     16777216              524              534   0x0000000-0x0ffffff          0\n|     39422[345][0-9]{2}     3877[12][0-9]{3}     33554432     33554432             1293             1315   0x0000000-0x1ffffff          0\n|    308980[34][0-9]{2}    30339[45][0-9]{3}    268435456    268435456             5282             5379   0x0000000-0xfffffff          0\n)"

        # Setup regular expressions for the times errors occur in the bist continuous experiment.
        self.bist_continuous_error_regex_list = {}
        self.bist_continuous_error_regex_list[0] = UART_TIME_REGEX + " Error address range: 0x[0-9a-f]{1,7}-0x[0-9a-f]{1,7}, Num Errors: [0-9]*, Data expected: \n"
        self.bist_continuous_error_regex_list[1] = UART_TIME_REGEX + " ((a5a5a5a5 a5a5a5a5 ){1,2}|(a5a5a5a5 a5a5a5a5 ){8})\n"
        self.bist_continuous_error_regex_list[2] = UART_TIME_REGEX + "    ADDRESS    DATA\n"
        self.bist_continuous_error_regex_list[3] = UART_TIME_REGEX + "  0x[0-9a-f]{7}:  (([ 0-9a-f]{1,8} [ 0-9a-f]{1,8} ){1,2}|([ 0-9a-f]{1,8} [ 0-9a-f]{1,8} ){8})\n"
        self.bist_continuous_error_regex_list[4] = UART_TIME_REGEX + "(            0     178443[345][0-9]            0     16777216                0              534   0x0000000-0x0ffffff  *[0-9]*\n|            0     3877[12][0-9]{3}            0     33554432                0             1315   0x0000000-0x1ffffff  *[0-9]*\n|            0    30339[45][0-9]{3}            0    268435456                0             5379   0x0000000-0xfffffff  *[0-9]*\n)"
        self.bist_continuous_error_regex_list[5] = UART_TIME_REGEX + "(     18164[01][0-9]{2}     178443[345][0-9]     16777216     16777216              524              534   0x0000000-0x0ffffff  *[0-9]*\n|     39422[345][0-9]{2}     3877[12][0-9]{3}     33554432     33554432             1293             1315   0x0000000-0x1ffffff  *[0-9]*\n|    308980[34][0-9]{2}    30339[45][0-9]{3}    268435456    268435456             5282             5379   0x0000000-0xfffffff  *[0-9]*\n)"

        
        # Setup regular expressions for the bist idle experiment.
        self.bist_idle_regex_list = {}
        self.bist_idle_regex_list[0] = LITEX_PROMPT_REGEX + "sdram_bist_writer 0 268435455\n"
        self.bist_idle_regex_list[1] = UART_TIME_REGEX + " sdram_bist_writer 0 268435455\n"
        self.bist_idle_regex_list[2] = LITEX_PROMPT_REGEX + "sdram_bist_reader 0 268435455 1000\n"
        self.bist_idle_regex_list[3] = UART_TIME_REGEX + " sdram_bist_reader 0 268435455 1000\n"
        self.bist_idle_regex_list[4] = UART_TIME_REGEX + " Writing from address 0 to address [1f]{0,1}ffffff ...Done\n"
        self.bist_idle_regex_list[5] = UART_TIME_REGEX + " Reading from address 0 to address [1f]{0,1}ffffff\n"
        self.bist_idle_regex_list[6] = UART_TIME_REGEX + " DRAM controller has address width (24, data width 64|25, data width 128|28, data width 512) in bits\n"
        self.bist_idle_regex_list[7] = UART_TIME_REGEX + "  WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED\(MiB\/s\)  RD-SPEED\(MiB\/s\)      ADDRESSES TESTED     ERRORS\n"
        self.bist_idle_regex_list[8] = UART_TIME_REGEX + "(     18164[01][0-9]{2}            0     16777216            0              524                0   0x0000000-0x0ffffff          0\n|     39422[345][0-9]{2}            0     33554432            0             1293                0   0x0000000-0x1ffffff          0\n|    308980[34][0-9]{2}            0    268435456            0             5282                0   0x0000000-0xfffffff          0\n)"
        self.bist_idle_regex_list[9] = UART_TIME_REGEX + "(            0     178443[345][0-9]            0     16777216                0              534   0x0000000-0x0ffffff          0\n|            0     3877[12][0-9]{3}            0     33554432                0             1315   0x0000000-0x1ffffff          0\n|            0    30339[45][0-9]{3}            0    268435456                0             5379   0x0000000-0xfffffff          0\n)"

        # Setup regular expressions for the times errors occur in the bist idle experiment.
        self.bist_idle_error_regex_list = {}
        self.bist_idle_error_regex_list[0] = UART_TIME_REGEX + " Error address range: 0x[0-9a-f]{1,7}-0x[0-9a-f]{1,7}, Num Errors: [0-9]*, Data expected: \n"
        self.bist_idle_error_regex_list[1] = UART_TIME_REGEX + " ((a5a5a5a5 a5a5a5a5 ){1,2}|(a5a5a5a5 a5a5a5a5 ){8})\n"
        self.bist_idle_error_regex_list[2] = UART_TIME_REGEX + "    ADDRESS    DATA\n"
        self.bist_idle_error_regex_list[3] = UART_TIME_REGEX + "  0x[0-9a-f]{7}:  (([ 0-9a-f]{1,8} [ 0-9a-f]{1,8} ){1,2}|([ 0-9a-f]{1,8} [ 0-9a-f]{1,8} ){8})\n"
        self.bist_idle_error_regex_list[4] = UART_TIME_REGEX + "(            0     178443[345][0-9]            0     16777216                0              534   0x0000000-0x0ffffff  *[0-9]*\n|            0     3877[12][0-9]{3}            0     33554432                0             1315   0x0000000-0x1ffffff  *[0-9]*\n|            0    30339[45][0-9]{3}            0    268435456                0             5379   0x0000000-0xfffffff  *[0-9]*\n)"

# Take a filename, return true if "Continuous" is in the name,
# else return false if "Idle" is in the name, else return None.
def type_bist_continuous(filename):
    if (CONTINUOUS_TESTNAME in filename):
        return True
    elif (IDLE_TESTNAME in filename):
        return False
    return None






# Bist line token attributes held in this class
class BistLine:
    """
    Represents one line from output

    Attributes:
        fileLineNum: The line number this line appears on in the file.
        wholeStr: The entire string of the line.
        lineStr: The message part of the line (without the date)
        lineType: The type of line it is (compared to the regexs)
        lineTypeIndex: Type index (regex dictionary index)
        sec: The part of the time specifying seconds.
        min: The part of the time specifying minutes.
        hour: The part of the time specifying hours.
        day: The part of the time specifying which day.
        month: The part of the time specifying the month.
    """

    def __init__(self, fileLineNum: int, wholeStr: str, lineStr: str = None, lineType: int = -1, lineTypeIndex: int = -1, sec: int = -1, min: int = -1, hour:int = -1, day:int = -1, month:int = -1):
        
        self.fileLineNum = fileLineNum
        self.wholeStr = wholeStr
        self.lineStr = lineStr
        self.lineType = lineType
        self.lineTypeIndex = lineTypeIndex
        self.sec = sec
        self.min = min
        self.hour = hour
        self.day = day
        self.month = month

    def __str__(self):
        return "linenum: " + str(self.fileLineNum) + "\nwholeStr: " + str(self.wholeStr) + "\nlineStr: " + str(self.lineStr) + "\nlineType: " + str(self.lineType) + "\nsec: " + str(self.sec) + "\nmin: " + str(self.min) + "\nhour: " + str(self.hour) + "\nday: " + str(self.day) + "\nmonth: " + str(self.month) + "\n\n\n"




class BistData:
    """
    A class holding all the BIST Lines 

    Attributes:
        fileName: The name of the file
        numTotalLines: The total number of lines in the file
        continuous_test: True if test is continuous, false if idle.
    """

    def __init__(self, fileName:str, numTotalLines:int, continuous_test:bool):
         
        self.fileName = fileName
        self.numTotalLines = numTotalLines
        self.continuous_test = continuous_test

        # Initialize a list to hold the Bist Lines
        self.bistLines = []

    def add_bistLine(self, bistLineObj:BistLine):

        # Add an object to the list previously created
        self.bistLines.append(bistLineObj)





# For the given filename, create and return object to hold bist line tokens and an object holding the open file.
def bistdata_obj_setup(filename:str, continuous_test:bool):
    
    # First extract the file name and the total number of lines in the file
    filename = str(filename)
    openFile = open(filename, "r")

    for count, line in enumerate(openFile):
        pass
    openFile.close()


    # Then craete a BistData Object to save both the filename, number of lines, and all the Bist lines.
    print(READING_FILE_STR, filename)
    print(NUM_UART_FILE_LINES_STR, str(count))

    # Open the file for reading and return to complete setup
    openFile = open(filename, "r")

    return BistData(fileName=filename, numTotalLines=count, continuous_test=continuous_test), openFile





class DataLog:
    """
    Take a file, strip it into tokens to be interpreted (BistLine objects), store in BistData.
    Provides helper functions for obtaining data.
    Arguments:
        uart_filename: The name of the uart file.
        continuous_test: Determine if the test is continuous or not (True for yes, False for no)
        uart_regex_dicts: All the regular expressions needed for sorting the BistLines.
    """

    def __init__(self, uart_filename, continuous_test: bool = None, uart_regex_dicts:bist_utils = None): #log_filename

        # Assert the file exists and that the argument continuous_test is not None.
        assert continuous_test != None
        assert os.path.isfile(uart_filename) == True

        # Setup the utils
        uart_regex_dicts.regex_setup()

        # Open the file and create an object to store log data lines
        self.uartData, openFile = bistdata_obj_setup(filename=uart_filename, continuous_test=continuous_test)

        # For the uart data, extract and sort necessary data from line, and
        # create a Bistline object to hold the information and add it to the container.
        for count, line in enumerate(openFile):

            # print("[{line}]".format(line=line)) # This line for debugging

            # See if time was printed out in line, and extract if it is (should be for every line)
            timeFound = re.compile(UART_TIME_REGEX)
            timeFoundResult = timeFound.search(line)

            # If time is found, split apart and save it, else save the line number and whole string at least.
            if (timeFoundResult != None):
                timeStr = str(timeFoundResult.group(0))
                lineStr_noTime = line.replace(timeStr, "")

                # First parse the time and check the number of arguments
                timeList = re.findall('\d+', timeStr)
                assert len(timeList) == TIME_NUM_ARGS

                # Find the type of line this is
                uart_regex_dicts.boot_regex_list
                uart_regex_dicts.litex_promt_regex
                uart_regex_dicts.bist_pat_setup_regex_list
                uart_regex_dicts.bist_continuous_regex_list
                uart_regex_dicts.bist_continuous_error_regex_list
                uart_regex_dicts.bist_idle_regex_list
                uart_regex_dicts.bist_idle_error_regex_list

                # Find line type and index number
                lineType = LINE_TYPE_BEG
                lineTypeIndex = LINE_TYPE_BEG
                

                # Sort the lines to the exact regular expressions they match
                if(continuous_test):

                    # See if regular expression is in the list of expected bist-continuous lines
                    for index in range(len(uart_regex_dicts.bist_continuous_regex_list)):
                        if re.search(uart_regex_dicts.bist_continuous_regex_list[index], line) != None:
                            lineType = TYPE_BIST_CONTINUOUS_REGEX
                            lineTypeIndex = index
                            break

                    # See if regular expression is in the list of expected bist-continuous lines that show errors occured.
                    if (lineType == LINE_TYPE_BEG):
                        for index in range(len(uart_regex_dicts.bist_continuous_error_regex_list)):
                            if re.search(uart_regex_dicts.bist_continuous_error_regex_list[index], line) != None:
                                lineType = TYPE_BIST_CONTINUOUS_ERROR_REGEX
                                lineTypeIndex = index
                                break

                else:

                    # See if regular expression is in the list of expected bist-idle lines.
                    for index in range(len(uart_regex_dicts.bist_idle_regex_list)):
                            if re.search(uart_regex_dicts.bist_idle_regex_list[index], line) != None:
                                lineType = TYPE_BIST_IDLE_REGEX
                                lineTypeIndex = index
                                break

                    # See if regular expression is in the list of expected bist-idle lines taht show errors occured.
                    if (lineType == LINE_TYPE_BEG):
                        for index in range(len(uart_regex_dicts.bist_idle_error_regex_list)):
                            if re.search(uart_regex_dicts.bist_idle_error_regex_list[index], line) != None:
                                lineType = TYPE_BIST_IDLE_ERROR_REGEX
                                lineTypeIndex = index
                                break

                # If lines are not categorized yet, check if line is part of setting BIST pattern
                if (lineType == LINE_TYPE_BEG):
                    for index in range(len(uart_regex_dicts.bist_pat_setup_regex_list)):
                        if re.search(uart_regex_dicts.bist_pat_setup_regex_list[index], line) != None:
                            lineType = TYPE_BIST_PAT_SETUP_REGEX
                            lineTypeIndex = index
                            break

                # Check if line is part of Bootup 
                if (lineType == LINE_TYPE_BEG):
                    for index in range(len(uart_regex_dicts.boot_regex_list)): 
                        if re.search(uart_regex_dicts.boot_regex_list[index], line) != None:
                            lineType = TYPE_BOOT_REGEX
                            lineTypeIndex = index
                            break

                # Finally, see if the Litex Prompt is found in the line
                if (lineType == LINE_TYPE_BEG):
                    if re.search(uart_regex_dicts.litex_promt_regex, line) != None:
                        lineType = TYPE_LITEX_PROMPT_REGEX
                        lineTypeIndex = LITEX_PROMPT_FOUND

                # If the line isn't matched, set to unknown
                if (lineType == LINE_TYPE_BEG):
                    lineType = TYPE_UNKNOWN

                # Add all information to the BISTLINE Object
                newBistLine = BistLine(
                    fileLineNum = count + 1,
                    wholeStr = line,
                    lineStr = lineStr_noTime,
                    lineType = lineType,
                    lineTypeIndex = lineTypeIndex,
                    sec = int(timeList[5]),
                    min = int(timeList[4]),
                    hour = int(timeList[3]),
                    day = int(timeList[2]),
                    month = int(timeList[1])
                )
                self.uartData.add_bistLine(newBistLine)

            else:

                # Save basic line info, move to next line.
                newBistLine = BistLine(
                    fileLineNum = count + 1, 
                    wholeStr = line, 
                    lineType = TYPE_UNKNOWN,
                )
                self.uartData.add_bistLine(newBistLine)


    # With both the previous errors and current errors, print the errors dynamically.
    def _print_new_old_errors(self, error_prev_dict:dict, error_cur_list:list, error_freq_dict:dict):

        # Set all the boolean values to false. 
        for key in error_prev_dict:
            error_prev_dict[key] = False

        # Read the error:
        #   If the error is not found in the dictionary, print them out as new errors and
        #   store them in the dictionary with the value 'True'.
        #   Else if the value is found in the dictionary, set the value to 'True' and move on.
        for line in error_cur_list:
            line = str(line).rstrip()
            if not (line in error_prev_dict):
                print("Error New: ", line)
            if not (line in error_freq_dict):
                error_freq_dict[line] = 1
            else:
                error_freq_dict[line] += 1
            error_prev_dict[line] = True

        # Once done, read all the values in the dictionary.
        #   If any values are set to false, print them out as errors gone and delete the 
        #   corresponding element in the dictionary.
        keys_to_delete = []
        for key in error_prev_dict:
            if error_prev_dict[key] == False:
                print("Error Gone: ", key)
                keys_to_delete.append(key)

        # Delete the keys
        for key in keys_to_delete:
            error_prev_dict.pop(key)

        return error_prev_dict, error_freq_dict
    


    def _print_time(self, index):
        
        print(
            "\n\n\n[",                    self.uartData.bistLines[index].month,
            "/",                    self.uartData.bistLines[index].day,
            "/2023 at ",            self.uartData.bistLines[index].hour,
            ":",                    self.uartData.bistLines[index].min,
            ":",                    self.uartData.bistLines[index].sec,
            "]")


    # Print the error-group information with the index of the beginning error and
    # the error group number.
    def _print_error_cnt(self, error_group_num, index):

        ERR_INFO_BACK_INDEX = 3

        self._print_time(index - ERR_INFO_BACK_INDEX)

        # Print the error group information
        print("\nError group count: ", error_group_num)

        # Print the time of this group of errors
        errorCompile = re.compile("Num Errors: [0-9]*")
        if ((self.uartData.bistLines[index - ERR_INFO_BACK_INDEX].lineType == TYPE_BIST_IDLE_ERROR_REGEX and
            self.uartData.bistLines[index - ERR_INFO_BACK_INDEX].lineTypeIndex == ERROR_INFO_INDEX) or 
            (self.uartData.bistLines[index - ERR_INFO_BACK_INDEX].lineType == TYPE_BIST_CONTINUOUS_ERROR_REGEX and
            self.uartData.bistLines[index - ERR_INFO_BACK_INDEX].lineTypeIndex == ERROR_INFO_INDEX)):

            errorResult = errorCompile.search(self.uartData.bistLines[index - ERR_INFO_BACK_INDEX].wholeStr)
            if errorResult != None:
                print("\n", errorResult.group(0), "\n")
            else:
                print("\nError count not displayed, edge case\n")

        else:

            print("\nError count not displayed, type: {type} index: {index} line: {line}\n".format(
                type = self.uartData.bistLines[index - ERR_INFO_BACK_INDEX].lineType,
                index = self.uartData.bistLines[index - ERR_INFO_BACK_INDEX].lineTypeIndex,
                line = self.uartData.bistLines[index - ERR_INFO_BACK_INDEX].wholeStr,
            ))
        


    # Print the error counts for each group and all the dynamic errors seen
    def print_dynamic_errors(self, display_err_freq: bool = None, continuous_test: bool = None):
        print("Printing Dynamic Errors")
        

        try:
            assert continuous_test != None
            assert display_err_freq != None
        except AssertionError:
            print("Specify if test is continuous or not, and if all errors and their frequencies should be displayed.\n")
            return
        
        # Dictionary with previous errors as keys to boolean values. 
        error_prev_dict = {}
        error_freq_dict = {}
        error_cur_list = []
        error_group_index = 0
        errors_found = False

        # Loop index
        index = 0


        # # For debugging parser
        # print("Printing order of linetypes and linetypeindexes:\n")

        # for i in range(len(self.uartData.bistLines)):
        #     print("LineType: {type} LineTypeIndex: {index} Line: {line}".format(type=self.uartData.bistLines[i].lineType, index=self.uartData.bistLines[i].lineTypeIndex, line=str(self.uartData.bistLines[i].wholeStr).rstrip()))
        
        if continuous_test:

            # Cycle through all the tokens in the order they were read
            while index < len(self.uartData.bistLines):

                # Find the beginning of where error addresses and data start and cycle through them
                if  (self.uartData.bistLines[index].lineType == TYPE_BIST_CONTINUOUS_ERROR_REGEX and 
                    self.uartData.bistLines[index].lineTypeIndex == ERROR_LIST_INDEX):

                    error_group_index += 1

                    errors_found = True

                    # Print the error group information (now that errors have been found)
                    self._print_error_cnt(error_group_index, index)

                    # While we have not reached the end of the error list/section for the 
                    # time errors are read, send the dynamic errors to be output.
                    while (index < len(self.uartData.bistLines)) and not (((self.uartData.bistLines[index].lineTypeIndex == ERROR_DATA_OUTPUT_INDEX_CONT_FIRST or
                                                                         self.uartData.bistLines[index].lineTypeIndex == ERROR_DATA_OUTPUT_INDEX_CONT_SECOND) and
                                                                         self.uartData.bistLines[index].lineType == TYPE_BIST_CONTINUOUS_ERROR_REGEX) or
                                                                         self.uartData.bistLines[index].lineType != TYPE_BIST_CONTINUOUS_ERROR_REGEX):

                        # I've noticed in the data that there are times when random lines 
                        # are output while errors are seen. This ensures we only read lines
                        # that truly show errros.
                        if (self.uartData.bistLines[index].lineType == TYPE_BIST_CONTINUOUS_ERROR_REGEX and 
                            self.uartData.bistLines[index].lineTypeIndex == ERROR_LIST_INDEX):

                            # This is the list of current errors, and the variable lineStr 
                            # is the string containing both address and data without the time.
                            error_cur_list.append(self.uartData.bistLines[index].lineStr)

                        index += 1
                    
                    # After the list of errors has been created, decide which errors to output.
                    error_prev_dict, error_freq_dict = self._print_new_old_errors(error_prev_dict, error_cur_list, error_freq_dict)
                    error_cur_list.clear()

                    # If timeout occured or something else unexpected happened, let the user know
                    if (index >= len(self.uartData.bistLines)):
                        print("\nReached end of file with error count\n")
                    elif (self.uartData.bistLines[index].lineType != TYPE_BIST_CONTINUOUS_ERROR_REGEX):
                        print("\nUnexpected data printed or Timeout occured\n")

                index += 1

        else:

            # Cycle through all the tokens in the order they were read
            while index < len(self.uartData.bistLines):

                # Find the beginning of where error addresses and data start and cycle through them
                if (self.uartData.bistLines[index].lineType == TYPE_BIST_IDLE_ERROR_REGEX and 
                    self.uartData.bistLines[index].lineTypeIndex == ERROR_LIST_INDEX):

                    error_group_index += 1

                    errors_found = True

                    # Print the error group information (now that errors have been found)
                    self._print_error_cnt(error_group_index, index)

                    while (index < len(self.uartData.bistLines)) and ((self.uartData.bistLines[index].lineType == TYPE_BIST_IDLE_ERROR_REGEX and 
                                                                       self.uartData.bistLines[index].lineTypeIndex == ERROR_LIST_INDEX) or
                                                                        (((index + 1) < len(self.uartData.bistLines)) and
                                                                        (self.uartData.bistLines[index + 1].lineTypeIndex == ERROR_LIST_INDEX) and 
                                                                        (self.uartData.bistLines[index + 1].lineType == TYPE_BIST_IDLE_ERROR_REGEX))):

                        # I've noticed in the data that there are times when random lines 
                        # are output while errors are seen. This ensures we only read lines
                        # that truly show errros.
                        if (self.uartData.bistLines[index].lineType == TYPE_BIST_IDLE_ERROR_REGEX and 
                            self.uartData.bistLines[index].lineTypeIndex == ERROR_LIST_INDEX):

                            # This is the list of current errors, and the variable lineStr 
                            # is the string containing both address and data without the time.
                            error_cur_list.append(self.uartData.bistLines[index].lineStr)

                        index += 1

                    # After the list of errors has been created, decide which errors to output.
                    error_prev_dict, error_freq_dict = self._print_new_old_errors(error_prev_dict, error_cur_list, error_freq_dict)
                    error_cur_list.clear()

                    # If timeout occured or something else unexpected happened, let the user know
                    if (index >= len(self.uartData.bistLines)):
                        print("\nReached end of file with error count\n")
                    elif (self.uartData.bistLines[index].lineType != TYPE_BIST_IDLE_REGEX):
                        print("\nUnexpected data printed or Timeout occured\n")

                elif (errors_found and self.uartData.bistLines[index].lineTypeIndex == NOERROR_DATA_OUTPUT_INDEX_IDLE and
                                        self.uartData.bistLines[index].lineType == TYPE_BIST_IDLE_REGEX):

                    errors_found = False

                    self._print_time(index)
                    print("\nAll errors gone\n")
                    for key in error_prev_dict:
                        print("Error Gone: ", key)
                    error_prev_dict.clear()

                index += 1



        # For format, print a line to separate output
        print("\n###################################################################################################################################################################\n\n")



        # If desired, all errors and the number of times they showed up will be displayed at the end.
        if display_err_freq:

            # Display all the errors and their frequencies
            print("Printing Errors found and their frequencies: ")
            print("| Frequency    | Error")

            # In the dictionary, sort items by the frequency counts
            # and display the errors with the highest count appearing first.
            for k, v in sorted(error_freq_dict.items(), key=lambda p:p[1], reverse=True):
                print("| %12d | %s" % (v, k))

            # For format, print a line to separate output
            print("\n###################################################################################################################################################################\n\n")
            


    # Print unknown data lines
    def print_unknown_linetypes(self):

        print("Printing Unmatched BIST lines:\n")
        for i in range(len(self.uartData.bistLines)):
            if self.uartData.bistLines[i].lineType == 7:
                print(self.uartData.bistLines[i].wholeStr)
        

    


def main():

    parser = argparse.ArgumentParser(description="Parse Litex Log Files")
    parser.add_argument("--log_filename",       type=str,                    help="Filename of file holding Log output for experiments.")
    parser.add_argument("--uart_filename",      type=str,                    help="Filename of file holding Uart output for experiments.")
    parser.add_argument("--with_all_err_freq_cnts",     action="store_true", help="Display all errors and their frequencies")
    parser.add_argument("--no_log_output",              action="store_true", help="No log output")
    parser.add_argument("--no_uart_output",             action="store_true", help="No uart output")
    args = parser.parse_args()

    # Setup regular expressions that match UART data.
    regex_dicts = bist_utils()

    # Open log and uart files, split into tokens and store in object
    datalog_obj = DataLog(uart_filename=args.uart_filename, continuous_test=type_bist_continuous(args.uart_filename), uart_regex_dicts=regex_dicts) # log_filename=args.log_filename

    print(len(datalog_obj.uartData.bistLines))

    # Print all the seen dynamic errors
    datalog_obj.print_dynamic_errors(args.with_all_err_freq_cnts, continuous_test=type_bist_continuous(args.uart_filename))

    # Print lines unrecognized (if any, usually the first line is blank and will be unknown)
    datalog_obj.print_unknown_linetypes()


if __name__ == "__main__":
	main()







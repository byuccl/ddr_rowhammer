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

MAX_STRING_CHARS_EXIST = 21
TIME_NUMS = 6
TWENTY_SEC = 20
BEGIN_HOUR = 23
BEGIN_MIN_SEC = 59

MAX_ERROR_COUNT = 10000000

HEADER_MATCHED_STR = "MATCH HEADER"
DATA_MATCHED_STR = "MATCH DATA"
UNMATCHED_STR = "UNMATCHED"
BEG_HEADER_STR = "BIST:Header (first)"
BEG_NONCONTINUOUS_HEADER_STR = "BIST:Starting Writer"
ERROR_STR = "ERROR"
ERROR_LOWERC_STR = "error"
TIMEOUT_STR = "timeout"
INFO_STR = "INFO"
NONE_STR = "None"
LOG_DEBUG_STR = "{} [2022-12-{} {}:{}:{}] {} {}"
TIME_ERR_STR = "LOG_FILE_INFO: Line {} time wasn't read properly, skipping. Data: {}"
LOG_ERR_STR = "LOG_FILE_INFO: Line {} has no log data, skipping. Data: {}"
HEADER_DATA_REGEX = "\[2023-06-[23][0-9] [012][0-9]:[0-5][0-9]:[0-5][0-9]\] WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED\(MiB/s\)  RD-SPEED\(MiB/s\)      ADDRESSES TESTED     ERRORS"
STATS_DATA_REGEX = "\[2023-06-[23][0-9] [012][0-9]:[0-5][0-9]:[0-5][0-9]\]\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+0x[0-9a-fA-F]{7}-0x[0-9a-fA-F]{7}\s+\d+"
TIME_REGEX = "\[2023-06-[23][0-9] [012][0-9]:[0-5][0-9]:[0-5][0-9]\]"
SUMMARY_STR = "\n\n\n\n\nTest contains the following single or groups of events:\n{} memory, {} timeout, {} other, {} spike"
READING_FILE_STR = "\nReading File: "
NUM_LOG_FILE_LINES_STR = "Number of lines in log file: "
NUM_UART_FILE_LINES_STR = "Number of lines in uart file: "
MEM_ERR_HEADER_STR = "\nMem event group {}, File: {}"
TIMEOUT_ERR_HEADER_STR = "\nTimeout event group {}, File: {}"
OTHER_ERR_HEADER_STR = "\nOther event group {}, File: {}"
SPIKE_ERR_HEADER_STR = "\nSpike event group {}, File: {}"
END_OF_TEST_STR = "\nEnd of test"

ERROR_DATA_CUT_INDEX = 23

class ErrorType(Enum):
    TIMEOUT_ERR = 0
    MEM_ERR = 1
    OTHER_ERR = 2
    NO_ERR = 3
    SPIKE_ERR = 4


class BistLine:
    """
    Represents one line from output.
    
    Attributes:
        wholeStr: Whole String (for debugging)
        lineStr: Message string 
        lineNum: Number of line it appears on log
        sec, min, hour, day: All ints containing time of outputted line.
        lineType: String with type of line: For logs, tells if logger output "ERROR" or "INFO" at that line. For uart input, 
            tells if uart output matches a header line, a number data line, or something else.
        address: If counting errors, address holds the address of error, otherwise None.
        fileSize: The number of lines in the file examined 
        fileName: File name to display
    """
    def __init__(self, lineNum: int, wholeStr: str, fileName: str, fileSize = -1, lineStr = None, sec=-1, min=-1, hour=-1, day=-1, lineType = None, address=None):

        self.wholeStr = wholeStr #str
        self.lineStr = lineStr   #str
        self.lineNum = lineNum   #int
        self.sec = sec           #int
        self.min = min           #int
        self.hour = hour         #int
        self.day = day           #int
        self.lineType = lineType #str
        self.address = address   #int
        self.fileSize = fileSize #int
        self.fileName = fileName #str

    def logdebug(self):
        return LOG_DEBUG_STR

    # Check to see if time of self is greater than another bistLine object
    def isTimeLessThan(self, bistLineObj):
        if (self.day < bistLineObj.day):
            return True
        elif (self.day == bistLineObj.day) and (self.hour < bistLineObj.hour):
            return True
        elif (self.day == bistLineObj.day) and (self.hour == bistLineObj.hour) and (self.min < bistLineObj.min):
            return True
        elif (self.day == bistLineObj.day) and (self.hour == bistLineObj.hour) and (self.min == bistLineObj.min) and (self.sec < bistLineObj.sec):
            return True
        return False

    # Check to see if time of self is greater than another bistLine object
    def isTimeGreaterThan(self, bistLineObj):
        if (self.day > bistLineObj.day):
            return True
        elif (self.day == bistLineObj.day) and (self.hour > bistLineObj.hour):
            return True
        elif (self.day == bistLineObj.day) and (self.hour == bistLineObj.hour) and (self.min > bistLineObj.min):
            return True
        elif (self.day == bistLineObj.day) and (self.hour == bistLineObj.hour) and (self.min == bistLineObj.min) and (self.sec > bistLineObj.sec):
            return True
        return False

    
    def goBack20Seconds(self):
        for index in range(TWENTY_SEC):
            if (self.sec == 0):
                if (self.min == 0):
                    if (self.hour == 0):
                        self.day = self.day - 1
                        self.hour = BEGIN_HOUR
                    else:
                        self.hour = self.hour - 1
                    self.min = BEGIN_MIN_SEC
                else:
                    self.min = self.min - 1
                self.sec = BEGIN_MIN_SEC
            else:
                self.sec = self.sec - 1

    
    def __str__(self):
        return self.wholeStr



class LogData:
    """
    A class to hold all the useful information from the logs

    Attributes: 
        self.log_data_tokens: This holds all the lines of data from the data log
    """

    def __init__(self):
        self.log_data_tokens = []


    # Get list of tokens in specified time range from these BistLine containers.
    def get_tokens_in_range(self, startBistLineTime: BistLine, endBistLineTime: BistLine):

        listToReturn = []

        # File Size counted with starting line as line 0. Add 1 to make up.
        for index in range(len(self.log_data_tokens)):
            if not self.log_data_tokens[index].isTimeLessThan(startBistLineTime) and not self.log_data_tokens[index].isTimeGreaterThan(endBistLineTime):
                listToReturn.append(self.log_data_tokens[index])
        
        return listToReturn



class UartData:
    """
    A class to hold all the uart information

    Attributes: 
        self.uart_data_tokens: This holds all the lines of data from the data log
    """

    def __init__(self):
        self.uart_data_tokens = []

    # Print out all data in the list
    def print_out_data(self):
        for index in range(len(self.uart_data_tokens)):
            print(self.uart_data_tokens[index])

    # Get list of tokens in specified time range from these BistLine containers.
    def get_tokens_in_range(self, startBistLineTime: BistLine, endBistLineTime: BistLine):

        listToReturn = []

        # File Size counted with starting line as line 0. Add 1 to make up.
        for index in range(len(self.uart_data_tokens)):
            if not self.uart_data_tokens[index].isTimeGreaterThan(endBistLineTime) and not self.uart_data_tokens[index].isTimeLessThan(startBistLineTime):
                listToReturn.append(self.uart_data_tokens[index])
        
        return listToReturn


class DataLog: 
    """ 
    Take a file or files, strip it into tokens to be interpreted (BistLine objects), store in BistData.
    Provides helper functions for obtaining data.

    Attributes:
        filename_log: Map with all files in arguments (with filenames as keys)
        bist_data
    """

    def __init__(self, log_filename, uart_filename, uart_skip_lines=0):

        self.logData = LogData()
        self.uartData = UartData()
        
        ###################################################################
        # Collect data from log files
        ###################################################################

        
        filename = str(log_filename)
        openFile = open(filename, "r")

        # Find number of lines

        # Get the number of lines in the file
        for count, line in enumerate(openFile):
            pass
        openFile.close()
        
        print(READING_FILE_STR, filename)
        print(NUM_LOG_FILE_LINES_STR, str(count))

        # Save file size to add to tokens
        fileSize = count

        # Open file again
        openFile = open(filename, "r")

        # First, find the beginning header string. Set flag until found.
        firstHeaderFound = False

        # For each file, get the line number and line
        for count, line in enumerate(openFile):

            # Take off endstring whitespace, get numbers
            line = str(line).rstrip()

            # Check if substring "BIST:Header (first)" is contained (marks first header),
            # set flag to true and continue to next data input
            if (line.find(BEG_NONCONTINUOUS_HEADER_STR) > 0): #BEG_HEADER_STR
                firstHeaderFound = True
                continue

            # Don't start parsing strings until first header is found.
            if not firstHeaderFound:
                continue

            # Create a holder for a line of data with the line number, and add the entire string.
            logLine = BistLine(count, line, filename, fileSize)
            
            # Find what type of log output this is, INFO or ERROR
            if (line.find(ERROR_STR) > 0):
                logLine.lineType = ERROR_STR
            elif(line.find(INFO_STR) > 0):
                logLine.lineType = INFO_STR
            else:
                # Must be a line without log info. We have the whole string saved, so set lineType to "None" and move on.
                logLine.lineType = NONE_STR
                print(LOG_ERR_STR.format(str(count), line)) 
                continue

            # We've asserted the line type. Split the string into a 2-element list with time in the first element and data in the second.
            timeDataList = re.split(logLine.lineType, line)

            # First parse the time
            timeList = re.findall('\d+', timeDataList[0]) # Should have year, month, day, 
                                                            # hour, min, sec in that order.
            
            # Assert number of arguments is correct
            if (len(timeList) != TIME_NUMS):
                # Edge case. We've saved the whole line, so print error has occurd, continue and move on
                print(TIME_ERR_STR.format(str(count), line))
                continue

            # Now add the time to the bistline object
            logLine.day  = int(timeList[2]) # Get the day
            logLine.hour = int(timeList[3]) # Get hour
            logLine.min  = int(timeList[4]) # Get minutes
            logLine.sec  = int(timeList[5]) # Get seconds 

            # Get rid of edge white space of data part in list, save it.
            logLine.lineStr = timeDataList[1].strip()

            # Now that we have all needed data, add this to a list of log tokens.
            self.logData.log_data_tokens.append(logLine)


        ###################################################################
        # Collect data from uart files
        ###################################################################

       
        filename = str(uart_filename)
        openFile = open(filename, "r")

        # Find number of lines

        # Get the number of lines in the file
        for count, line in enumerate(openFile):
            pass
        openFile.close()
        print(NUM_UART_FILE_LINES_STR, str(count))

        # Save file size to add to tokens
        fileSize = count

        # Open file again
        openFile = open(filename, "r")

        # For each file, get the line number and line
        for count, line in enumerate(openFile):

            # Take off endstring whitespace
            line = str(line).rstrip()

            # Skip litex introduction uart output
            if (count < uart_skip_lines):
                continue

            # Create a holder for a line of data with the line number, and add the entire string.
            uartLine = BistLine(count, line, filename, fileSize)

            # Check if line matches, is a header or data
            if (re.search(HEADER_DATA_REGEX, line) != None):
                uartLine.lineType = HEADER_MATCHED_STR
            elif (re.search(STATS_DATA_REGEX, line) != None):
                uartLine.lineType = DATA_MATCHED_STR
            else:
                uartLine.lineType = UNMATCHED_STR

            # See if time was printed out in line, and extract if it is.
            timeFound = re.compile(TIME_REGEX)
            timeFoundResult = timeFound.search(line)

            # If time was found, extract time into token
            if (timeFoundResult != None):
                timeStr = str(timeFoundResult.group(0))

                # First parse the time
                timeList = re.findall('\d+', timeStr) # Should have year, month, day, 
                                                                # hour, min, sec in that order.
                
                # Assert number of arguments is correct
                if (len(timeList) != TIME_NUMS):
                    # Edge case. We've saved the whole line, so print error has occurd, continue and move on
                    print(TIME_ERR_STR.format(str(count), line))
                    continue

                # Now add the time to the bistline object
                uartLine.day  = int(timeList[2]) # Get the day
                uartLine.hour = int(timeList[3]) # Get hour
                uartLine.min  = int(timeList[4]) # Get minutes
                uartLine.sec  = int(timeList[5]) # Get seconds 

            # Now that we have all needed data, add this to a list of log tokens.
            self.uartData.uart_data_tokens.append(uartLine) 



    def display_dynamic_errors_continuous(self, display_error_info:bool = False, display_spike_error:bool = False):

        # Bist line object that will hold the beginning time
        starting_time = BistLine(0, "", "")
        starting_time.day = 0
        starting_time.hour = 0
        starting_time.min = 0
        starting_time.sec = 0
        
        # Keep array of previous errors for logging
        error_prev_list = {}

        # Keep track of when we see errors
        start_of_errors = False

        error_cnt = 0
        old_err_count = 0
        # Parse through uart data to get new and old errors
        for index in range(len(self.uartData.uart_data_tokens)):

            # The string after this string holds the starting data error information. Continue to the next.
            if re.search("ADDRESS    DATA", self.uartData.uart_data_tokens[index].wholeStr) != None:
                start_of_errors = True
                starting_time.day = self.uartData.uart_data_tokens[index].day
                starting_time.hour = self.uartData.uart_data_tokens[index].hour
                starting_time.min = self.uartData.uart_data_tokens[index].min
                starting_time.sec = self.uartData.uart_data_tokens[index].sec
                continue

            # End of errors being output at this point
            elif start_of_errors and re.search("\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+0x[0-9a-fA-F]{7}-0x[0-9a-fA-F]{7}\s+\d+", self.uartData.uart_data_tokens[index].wholeStr) != None:
                
                new_line = re.split(" ", self.uartData.uart_data_tokens[index].wholeStr)
                # print(new_line)
                error_cnt = int(new_line[len(new_line) - 1])
                
                if(error_cnt != old_err_count):
                    print(f"\n\n\n[June {self.uartData.uart_data_tokens[index].day}, {self.uartData.uart_data_tokens[index].hour}:{self.uartData.uart_data_tokens[index].min}:{self.uartData.uart_data_tokens[index].sec}] Error count: {error_cnt}")
                
                    if (max(error_cnt, old_err_count) - min(error_cnt, old_err_count) < MAX_ERROR_COUNT):
                        
                        groupErrors = self.uartData.get_tokens_in_range(starting_time, self.uartData.uart_data_tokens[index - 1])
                        
                        cutFirstIndex = 0
                        cutEndIndex = len(groupErrors)

                        # Get the first index for the cut 
                        for line in groupErrors:
                            cutFirstIndex += 1
                            if re.search("ADDRESS    DATA", line.wholeStr) != None:
                                break

                        # Get the last index of the cut
                        for index in range(len(groupErrors) - 1, -1, -1):
                            if re.search("0x[0-9a-fA-F]+:  [0-9a-fA-F]+", groupErrors[index].wholeStr) != None:
                                break
                            else:
                                cutEndIndex -= 1
                                
                        # Set group errors
                        groupErrors = groupErrors[cutFirstIndex:cutEndIndex]
                        
                        for key in error_prev_list:
                            error_prev_list[key] = 0

                        # Get the new errors for that time
                        for error in groupErrors:
                            if (error.wholeStr[ERROR_DATA_CUT_INDEX:] in error_prev_list):
                                error_prev_list[error.wholeStr[ERROR_DATA_CUT_INDEX:]] = 1
                            else:
                                error_prev_list[error.wholeStr[ERROR_DATA_CUT_INDEX:]] = 1
                                print("Error new:  ", error.wholeStr[ERROR_DATA_CUT_INDEX:])

                        # Get the errors that are gone for that time
                        map_keys = []
                        for key in error_prev_list:
                            if error_prev_list[key] == 0:
                                print("Error gone: ", key)
                                map_keys.append(key)
                        
                        # Remove deleted errors from list.
                        for key in map_keys:
                            error_prev_list.pop(key)
                            
                    # Set old error count to new error count.
                    old_err_count = error_cnt
                


        pass


  
    def display_dynamic_errors_idle(self, display_error_info:bool = False, display_spike_error:bool = False):

        
        
        # self.uartData.uart_data_tokens
        # self.logData.log_data_tokens

        print("Timeline:")

        # Save error count for comparison
        error_cnt = 0

        # Keep array of previous errors for logging
        error_prev_list = {}

        # Set starting time
        starting_time = BistLine(0, "", "")
        starting_time.day = 0
        starting_time.hour = 0
        starting_time.min = 0
        starting_time.sec = 0
        
        # Parse through all the lines in the log
        for logLine in self.logData.log_data_tokens:

            # Set the starting time of possible errors
            if re.search("BIST:Starting Reader", logLine.lineStr):

                # Set the starting time 
                starting_time.day = logLine.day
                starting_time.hour = logLine.hour
                starting_time.min = logLine.min
                starting_time.sec = logLine.sec

            # Find the lines in the log that display the error count.
            
            elif re.search("BIST:Data Errors \(", logLine.lineStr) != None:

                # Get error count string
                instance = re.findall("\(\d+:", logLine.lineStr)

                # Shave off the beginning and ending characters
                instance = instance[0][1:len(instance) - 2]

                # Convert to integer and compare to last error count
                new_error_cnt = int(instance)

                # If the error count has changed only slightly, display the errors
                if (error_cnt != new_error_cnt):

                    # Display time, error count, then errors
                    print(f"\n\n\n[June {logLine.day}, {logLine.hour}:{logLine.min}:{logLine.sec}] Error count: {new_error_cnt}")

                    if display_error_info and (max(error_cnt, new_error_cnt) - min(error_cnt, new_error_cnt) < MAX_ERROR_COUNT):
                        
                        # Get the errors, set in list of bistline objects
                        groupErrors = self.uartData.get_tokens_in_range(starting_time, logLine)

                        cutFirstIndex = 0
                        cutEndIndex = len(groupErrors)

                        # Get the first index for the cut 
                        for line in groupErrors:
                            cutFirstIndex += 1
                            if re.search("ADDRESS    DATA", line.wholeStr) != None:
                                break

                        # Get the last index of the cut
                        for index in range(len(groupErrors) - 1, -1, -1):
                            if re.search("0x[0-9a-fA-F]+:  [0-9a-fA-F]+", groupErrors[index].wholeStr) != None:
                                break
                            else:
                                cutEndIndex -= 1
                        
                        # Set group errors
                        groupErrors = groupErrors[cutFirstIndex:cutEndIndex]

                        for key in error_prev_list:
                            error_prev_list[key] = 0

                        # Get the new errors for that time
                        for error in groupErrors:
                            if (error.wholeStr[ERROR_DATA_CUT_INDEX:] in error_prev_list):
                                error_prev_list[error.wholeStr[ERROR_DATA_CUT_INDEX:]] = 1
                            else:
                                error_prev_list[error.wholeStr[ERROR_DATA_CUT_INDEX:]] = 1
                                print("Error new:  ", error.wholeStr[ERROR_DATA_CUT_INDEX:])

                        # Get the errors that are gone for that time
                        map_keys = []
                        for key in error_prev_list:
                            if error_prev_list[key] == 0:
                                print("Error gone: ", key)
                                map_keys.append(key)
                        
                        # Remove deleted errors from list.
                        for key in map_keys:
                            error_prev_list.pop(key)

                    else:
                        
                        groupErrors = self.uartData.get_tokens_in_range(starting_time, logLine)
                        cutFirstIndex = 0
                        cutEndIndex = len(groupErrors)

                        # Get the first index for the cut 
                        for line in groupErrors:
                            cutFirstIndex += 1
                            if re.search("ADDRESS    DATA", line.wholeStr) != None:
                                break

                        # Get the last index of the cut
                        for index in range(len(groupErrors) - 1, -1, -1):
                            if re.search("0x[0-9a-fA-F]+:  [0-9a-fA-F]+", groupErrors[index].wholeStr) != None:
                                break
                            else:
                                cutEndIndex -= 1
                        
                        # Set group errors
                        groupErrors = groupErrors[cutFirstIndex:cutEndIndex]
                        print("Spike Error Count:  ", len(groupErrors))
                        
                        if display_spike_error:
                            print(groupErrors)
                            
                    # Set old error count to new error count.
                    error_cnt = new_error_cnt
                    




    '''
    Create groups of tokens of errors in order to summarize results.
    '''
    def test_sort_finalize(self):

        # Groups of lists of tokens of errors to collect.
        self.timeOutErrorList = []
        self.memoryErrorList = []
        self.otherErrorList = []

        # Keep track if last line was an error or not
        errorsFoundFlag = False

        # Keep track of error type
        errorType = ErrorType.NO_ERR

        # Keep track of the time of last error with a BistLine container object
        firstErrorTime = BistLine(0, NONE_STR ,NONE_STR)
        
        # Start by going through the uart data. If a line doesn't have correct data, record it.
        for index in range(len(self.uartData.uart_data_tokens)):

            # We are looking for unmatched data, data that does not exactly match the header or statistics data
            if ((not errorsFoundFlag) and (self.uartData.uart_data_tokens[index].lineType != UNMATCHED_STR)):
                continue

            # We found errors. Identify, and set flag high.
            elif ((not errorsFoundFlag) and (self.uartData.uart_data_tokens[index].lineType == UNMATCHED_STR)):
                
                errorsFoundFlag = True

                # Save the time of this first-time error
                firstErrorTime.day  = self.uartData.uart_data_tokens[index].day
                firstErrorTime.hour = self.uartData.uart_data_tokens[index].hour
                firstErrorTime.min  = self.uartData.uart_data_tokens[index].min
                firstErrorTime.sec  = self.uartData.uart_data_tokens[index].sec

                # Every time errors occur in memory, the string "error" or "ERROR" is found in the token.
                # re.search returns None if string is not found.
                if (re.search(ERROR_STR, self.uartData.uart_data_tokens[index].wholeStr) or 
                    re.search(ERROR_LOWERC_STR, self.uartData.uart_data_tokens[index].wholeStr)):

                    errorType = ErrorType.MEM_ERR
                    continue

                # The logs will have a string occuring 20 seconds before this uart string with the word "timeout"
                # if the error is related to a timeout.
                beforeErrorTime = BistLine(0, NONE_STR, NONE_STR)
                beforeErrorTime.day  = firstErrorTime.day
                beforeErrorTime.hour = firstErrorTime.hour
                beforeErrorTime.min  = firstErrorTime.min
                beforeErrorTime.sec  = firstErrorTime.sec
                beforeErrorTime.goBack20Seconds()
                listRecentDataLogs = self.logData.get_tokens_in_range(beforeErrorTime, firstErrorTime)

                for index in range(len(listRecentDataLogs)):
                    if (re.search(TIMEOUT_STR, listRecentDataLogs[index].wholeStr)):
                        errorType = ErrorType.TIMEOUT_ERR
                
                if (errorType == ErrorType.TIMEOUT_ERR):
                    continue
                
                # SPIKE Errors  
                # if(self.uartData.uart_data_tokens[index].lineType == DATA_MATCHED_STR):
                #     data_tokens = re.split(" ", self.uartData.uart_data_tokens[index])
                #     error_count = data_tokens[len(data_tokens)-1]
                #     if(error_count > MAX_ERROR_COUNT):
                #         errorType = ErrorType.SPIKE_ERR
                #         continue
                # Otherwise, this error is likely due to bizarre behavior. Save it as such and move on.
                errorType = ErrorType.OTHER_ERR
                continue

            # Currently looking at errors. Do nothing.
            elif ((errorsFoundFlag) and (self.uartData.uart_data_tokens[index].lineType == UNMATCHED_STR)):
                continue

            # Done looking at errors. Lower the flag, save the group of errors and move on.
            elif ((errorsFoundFlag) and (self.uartData.uart_data_tokens[index].lineType != UNMATCHED_STR)):

                errorsFoundFlag = False

                groupErrors = self.uartData.get_tokens_in_range(firstErrorTime, self.uartData.uart_data_tokens[index])

                # Sort the errors
                if (errorType == ErrorType.MEM_ERR):
                    self.memoryErrorList.append(groupErrors)
                elif (errorType == ErrorType.TIMEOUT_ERR):
                    self.timeOutErrorList.append(groupErrors)
                elif (errorType == ErrorType.OTHER_ERR):
                    self.otherErrorList.append(groupErrors)
                elif (errorType == ErrorType.SPIKE_ERR):
                    self.spikeErrorList.append(groupErrors)
                
                # Reset the error type
                errorType = ErrorType.NO_ERR
                continue

        # See if we've reached the end of file while errors have happened, then sort/save and move on.
        if (errorsFoundFlag):

            errorsFoundFlag = False

            groupErrors = self.uartData.get_tokens_in_range(firstErrorTime, self.uartData.uart_data_tokens[index])

            # Sort the errors
            if (errorType == ErrorType.MEM_ERR):
                self.memoryErrorList.append(groupErrors)
            elif (errorType == ErrorType.TIMEOUT_ERR):
                self.timeOutErrorList.append(groupErrors)
            elif (errorType == ErrorType.OTHER_ERR):
                self.otherErrorList.append(groupErrors)
            
            
            # Reset the error type
            errorType = ErrorType.NO_ERR


    # Print out test results
    def test_summarize(self, no_output = False):

        # Print out summary statement
        print(SUMMARY_STR.format(len(self.memoryErrorList), len(self.timeOutErrorList), len(self.otherErrorList)))

        if not no_output:

            # # Print out sections of memory errors
            # for index in range(len(self.memoryErrorList)):
            #     print(MEM_ERR_HEADER_STR.format(index, self.memoryErrorList[0][0].fileName))
            #     for errIndex in range(len(self.memoryErrorList[index])):
            #         print(self.memoryErrorList[index][errIndex])

            # # Print out sections of timeout errors
            # for index in range(len(self.timeOutErrorList)):
            #     print(TIMEOUT_ERR_HEADER_STR.format(index, self.timeOutErrorList[0][0].fileName))
            #     for errIndex in range(len(self.timeOutErrorList[index])):
            #         print(self.timeOutErrorList[index][errIndex])

            # # Print out sections of other errors
            # for index in range(len(self.otherErrorList)):
            #     print(OTHER_ERR_HEADER_STR.format(index, self.otherErrorList[0][0].fileName))
            #     for errIndex in range(len(self.otherErrorList[index])):
            #         print(self.otherErrorList[index][errIndex])

            # Print out sections of spike errors
            for index in range(len(self.spikeErrorList)):
                print(SPIKE_ERR_HEADER_STR.format(index, self.spikeErrorList[0][0].fileName))
                for errIndex in range(len(self.spikeErrorList[index])):
                    print(self.spikeErrorList[index][errIndex])

            # Print out summary statement
        print(SUMMARY_STR.format(len(self.memoryErrorList), len(self.timeOutErrorList), len(self.otherErrorList)))
        print(END_OF_TEST_STR)

# class DataLog:

#     def create_pickle_from_text(textfilename, print_parse: bool = False, )

# class DataLogSet:

#     def __init__(self, filenames, textfile : bool = True, print_parse : bool = True):
#         """
#         Initialize the object from a text file or pickle file
#         """

#         self.filename_log_dict = {}

#         # Iterate over all of the filenames in the list
#         for filename in filenames:
#             if textfile:
#                 log = 

def main():

    parser = argparse.ArgumentParser(description="Parse Litex Log files")

    # parser.add_argument("--uart-filenames", metavar="filename",  type=str, nargs='+', help="UART output to process")
    parser.add_argument("--log-filenames",         type=str,    nargs='+',        help="Log output to help process")
    parser.add_argument("--uart-filenames",        type=str,    nargs='+',        help="Log output to help process")
    parser.add_argument("--skip-uart-lines",       type=int,    default=0,        help="Number of uart lines to skip")
    parser.add_argument("--no-output",             action="store_true",           help="No uart output")
    parser.add_argument("--log-summary",           action="store_true",           help="Print analysis (for now)")
    parser.add_argument("--dynamic-error-display", action="store_true",           help="List the errors" )
    parser.add_argument("--spike_error_display",   action="store_true",           help="Display Spike Errors")

    args = parser.parse_args()

    fileDict = {args.log_filenames[i]: args.uart_filenames[i] for i in range(len(args.log_filenames))}
    #print(fileDict)

    for log_filename, uart_filename in fileDict.items():

        # Check if data is created as a local variable
        if 'data' in locals():
            # If it is, make another Datalog object
            moreData = DataLog(log_filename, uart_filename, args.skip_uart_lines)

            # and concatenate the lists to original data object
            data.uartData.uart_data_tokens = data.uartData.uart_data_tokens + moreData.uartData.uart_data_tokens
            data.logData.log_data_tokens = data.logData.log_data_tokens + moreData.logData.log_data_tokens
            pass

        else:
            # Else make the variable 'data'
            data = DataLog(log_filename, uart_filename, args.skip_uart_lines)

    # Find out if we are using continuous or noncontinuous data scripts
    continuous_err_display = False
    noncontinuous_err_display = False
    for index in range(len(args.log_filenames)):
        print(args.log_filenames[index])
        print("IDLE" in args.log_filenames[index])
        if "IDLE" in args.log_filenames[index]:
            noncontinuous_err_display = True
        elif "CONTINUOUS" in args.log_filenames[index]:
            continuous_err_display = True
    
    # Check that we aren't using both
    if(args.dynamic_error_display and continuous_err_display and noncontinuous_err_display):
        print("Cannot run dynamic errors with both continuous and noncontinuous currently")
        return
    
    # Run the parser on either continuous or noncontinuous data scripts.
    if((args.dynamic_error_display or args.spike_error_display) and noncontinuous_err_display):
        data.display_dynamic_errors_idle(args.dynamic_error_display, args.spike_error_display)
    elif((args.dynamic_error_display or args.spike_error_display) and continuous_err_display):
        data.display_dynamic_errors_continuous(args.dynamic_error_display, args.spike_error_display)

    # Find and sort the errors
    data.test_sort_finalize()

    # Summarize number of errors and print all if needed.
    data.test_summarize(args.no_output)


if __name__ == "__main__":
	main()




















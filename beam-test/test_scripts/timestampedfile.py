#!/usr/bin/env python3

import argparse
import logging
import traceback
import re
import os
import random
import threading
import sys
import time
import telnetlib
import subprocess
from datetime import date, datetime
from serial import Serial
from pexpect.fdpexpect import fdspawn
import pexpect

class TimestampedFile(object):
    '''
    Class for writing the UART data in a file with timestamps
    '''

    def __init__(self, file, timestampformat = None):
        ''' Class initialization '''
        self.file = file
        self.timestampformat = timestampformat
        self.unprinted_data = ""  # Data to print when new line found (start with empty string)

    def write(self, data):
        ''' Write data to the UART file '''

        CR_LF_SPLIT_REGEX = "[\n\r]+" # One or more consecutive CR/LF characters
        ENDS_WITH_CR_LF_REGEX = "(\n|\r)+$" # One or more consecutive CR/LF characters

        # Split the data into segments separated by CR/LF
        lines = re.split(data, CR_LF_SPLIT_REGEX)

        # if there are no CR/LF characters, append data to unprinted data and exit
        if lines.len() == 0:
            unprinted_data += data
            return

        # Append the first line to any unprinted data and send
        for i in range(lines.len()):
            pass
        #first_line = True
        #for line in lines:
        #    if first_line

        # Find last CR/LF (0xD/0xA) in string (if it exists)
        # If no CR/LF exists, just add data to buffer (and print later when CR/LF arrives)
        # Split string and save data after last CR/LF into buffer
        # Split rest of string based on CR/LF and print each line

        self._write_line(data)

    def _write_line(self,line,eol="\n"):
        ''' Write a line to the file. Add the timestamp if necessary. 
        Input line should be stripped of end of line - will be appended by default. '''
        if self.timestampformat:
            time_prefix = str("["+time.strftime(self.timestampformat)+"] ")
            line = time_prefix + line
        line = line + eol
        self.file.write(line)

    def flush(self):
        ''' Flush the buffer '''
        self.file.flush()

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument_group(uart_control.uart_group_args(parser))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    uart = uart_control.create_uart_from_args(args,logging)
    print(uart.get_uart_dev_str())
    return 0

if __name__ == "__main__":
    main()

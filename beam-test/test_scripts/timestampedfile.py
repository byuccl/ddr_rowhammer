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

        for c in data:
            if c == '\n' or c == '\r':
                self._write_line(self.unprinted_data)
                self.unprinted_data = ""
            else:
                self.unprinted_data += c
        return

    def _write_line(self,line,eol="\n"):
        ''' Write a line to the file. Add the timestamp if necessary. 
        Input line should be stripped of end of line - will be appended by default. '''
        if self.timestampformat:
            time_prefix = str("["+time.strftime(self.timestampformat)+"] ")
            line = time_prefix + line
        line = line + eol
        #print("writing:"+line,end="")
        self.file.write(line)

    def flush(self):
        ''' Flush the buffer '''
        self.file.flush()

def main():

    test_data = [
        "This line has no new line in it",
        "A minor line\n",
        "\n",
        "This is the first line\n",
        "Test1  \n  Test 2   \n  This is a test 3  too",
        "Test1  \n  Test 2   \n  This is a test 3  too",
        "",
        "\nThis is a testn\nMore of a test\n  "
    ]

    TIME_STRING_FORMAT = "%Y-%m-%d %H:%M:%S"

    tsf = TimestampedFile( sys.stdout, timestampformat = TIME_STRING_FORMAT)

    for line in test_data:
        tsf.write(line)
    return 0

if __name__ == "__main__":
    main()

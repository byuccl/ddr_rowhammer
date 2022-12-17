#!/usr/bin/env python3

import argparse
import traceback
import logging
import re
import os
import random
import threading
import sys
import time
from datetime import date, datetime
from serial import Serial

from timestampedfile import TimestampedFile

from pexpect.fdpexpect import fdspawn
import pexpect

# Constants ----------------------------------------------------------------------------------------

class serial_expect():
    '''
    '''
    FDSPAWN_TIMEOUT = 5
    DEFAULT_EXPECT_TIMEOUT = 5

    def __init__(self, 
        serial_fd,
        logging,
        pexpect_stdout = None,   # File handle for output of uart
        timestampformat = None,  # Timestamp specification to go on output (if desired)
        ):

        if pexpect_stdout:
            self.logfile = TimestampedFile(pexpect_stdout, timestampformat = timestampformat)
        else:
            self.logfile = None
        self.serial_fd = serial_fd
        self.logging = logging

    def create_uart_spawn(self):
        ''' Create Serial spawn object for pexpect. If this function is successful,
        the self.serial_fdspawn member is not None. Otherwise, None'''

        try:
            self.serial_fdspawn = fdspawn(self.serial_fd, encoding="utf-8", logfile=self.logfile, timeout=serial_expect.FDSPAWN_TIMEOUT)
        except pexpect.exceptions.TIMEOUT as error:
            #self.logging._error("TTY Timeout:"+str(error)+")")
            self.logging.error("TTY Timeout:"+str(error)+")")
            self.serial_fdspawn = None
        except Exception as error:
            #self.logging._error("Unexpected exception connecting to uart"+str(error))
            self.logging.error("Unexpected exception connecting to uart"+str(error))
            self.serial_fdspawn = None
        return self.serial_fdspawn

    def sendline(self,line):
        ''' Send line over fdspawn handle '''
        if not self.serial_fdspawn:
            #self.logging._error("sendline call without active fdspan")
            self.logging.error("sendline call without active fdspan")
            return False
        try:
            self.serial_fdspawn.sendline(line)
        except Exception as error:
            #self.logging.error("sendline error:"+str(error)+"\n"+traceback.format_exc())
            self.logging.error("sendline error:"+str(error)+"\n"+traceback.format_exc())
            return False
        return True

    def get_expect_str(self):
        ''' Return the last string received with expect '''
        if not self.serial_fdspawn:
            self.logging.error("no active fdspan")
            return None
        return self.serial_fdspawn.match.group(0)

    def expect(self,pattern,timeout=DEFAULT_EXPECT_TIMEOUT):
        ''' Perform the "expect" command and catch any errors. '''
        self.timeout_error = False
        self.EOF_error = False
        self.unicode_error = False
        self.error = False
        
        ''' Expext fdspawn handle '''
        if not self.serial_fdspawn:
            self.logging.error("expect call without active fdspan")
            return None
        try:
            result = self.serial_fdspawn.expect(pattern=pattern, timeout=timeout)
        except pexpect.exceptions.TIMEOUT:
            self.timeout_error = True
            self.logging.error(f"expect timeout (delay {timeout}s)")
            return None
        except pexpect.exceptions.EOF:
            self.EOF_error = True
            self.logging.error(f"UART EOF with pattern:"+str(pattern))
            return None
        except UnicodeDecodeError:
            self.logging.error("expect unicode error")
            self.unicode_error = True
            return None
        except Exception as error:
            self.logging.error("expect error:"+str(error))
            self.error = True
            return None
        return result

    def has_error(self):
        ''' Determines whether any error had occured on the last call to 'expect' '''
        #if self.timeout or self.EOF or self.unicode_error or self.error:
        #if self.EOF or self.unicode_error or self.error or self.timeout_error:
        #    return True
        return False


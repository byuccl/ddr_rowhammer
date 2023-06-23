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

sys.path.insert(0, '../../../yinstruments/yinstruments')
#from usb_finder import find_dev_file_usb_bus
from usb_finder import find_dev_file_ttyUSB,USBFindError 

from timestampedfile import TimestampedFile

class uart_control():
    '''
    Class for controlling the UART interface
    '''

    # Netbooter constants
    #DEFAULT_USB_PROG_PHYS_PORT = "1-4.1"
    DEFAULT_USB_PROG_PHYS_PORT = "1-4.4.1"
    #DEFAULT_USB_UART_PHYS_PORT = "1-4.2"
    DEFAULT_USB_UART_PHYS_PORT = "1-4.4.2"
    DEFAULT_USB_UART_PHYS_IF = 0
    DEFAULT_SERIAL_BAUDRATE = 115200
    FDSPAWN_TIMEOUT = 5
    MAX_TTY_FIND_ATTEMPTS = 5
    TTY_SEARCH_DELAY = 2
    DEFAULT_EXPECT_TIMEOUT = 5
    LOGGER_TEXT_PREFIX = "UART:"

    def __init__(self, 
        usb_uart_phys_port:str,
        usb_uart_phys_if:int,
        uart_stdout = None,
        logging = None,
        litex_baudrate = DEFAULT_SERIAL_BAUDRATE,
        timestampformat = None):

        self.usb_uart_phys_port = usb_uart_phys_port
        self.usb_uart_phys_if = usb_uart_phys_if
        self.logging = logging
        self.serial_fd = None
        self.litex_baudrate = litex_baudrate
        self.timeout = False
        self.serial_dev = None      # String of currently opened Serial device

        if uart_stdout:
            self.logfile = TimestampedFile(uart_stdout, timestampformat = timestampformat)
        else:
            self.logfile = None

    def _info(self, str):
        ''' Send an 'info' message to the logger. '''
        if self.logging:
            self.logging.info(uart_control.LOGGER_TEXT_PREFIX+str)

    def _error(self, str):
        ''' Send an 'error' message to the logger. '''
        if self.logging:
            self.logging.error(uart_control.LOGGER_TEXT_PREFIX+str)

    def get_uart_dev_str(self):
        ''' Return the /dev/ttyUSBx device string of the UART '''
        # This will interface 0 on this port
        USB_UART_INTERFACE = 0
        #print(self.usb_uart_phys_port,USB_UART_INTERFACE, uart_control.DEFAULT_USB_PROG_PHYS_PORT )
        tty_find_attempt = 1
        tty = None
        while tty_find_attempt < uart_control.MAX_TTY_FIND_ATTEMPTS and not tty:
            time.sleep(uart_control.TTY_SEARCH_DELAY)
            self._info(f"Searching for ttyUSB device (Attempt {tty_find_attempt}) for port "+self.usb_uart_phys_port+" IF "+self.usb_uart_phys_if)
            try:
                tty = find_dev_file_ttyUSB(self.usb_uart_phys_port, self.usb_uart_phys_if)
            except (USBFindError) as error:
                # Ignore this for now
                pass
                tty_find_attempt += 1

        if not tty:
            self._error("Cannot find serial device:"+str(error))
            return None
        self._info("Found tty device:"+str(tty))
        return str(tty)
    
    def create_uart_serial(self):
        ''' Create Serial object for uart '''
        self.serial_dev = self.get_uart_dev_str()
        self.serial_fdspawn = None # Clear any reference to a spawn object
        if not self.serial_dev:
            return
        try:
            self.serial_fd = Serial(self.serial_dev, baudrate=self.litex_baudrate)
        except (Exception) as error:
            self._error("Failed to open:"+str(self.serial_dev)+" ("+str(error)+")")
            return None
        self._info("Serial port "+self.serial_dev+" open")
        return self.serial_fd

    def close_uart_serial(self):
        ''' Close serial port'''
        self._info("Serial port "+self.serial_dev+" closed")
        self.serial_dev = None
        self.serial_fd.close()
        self.serial_fd = None
        self.serial_fdspawn = None

    def create_uart_spawn(self):
        ''' Create Serial spawn object for pexpect'''
        if not self.create_uart_serial():
            # Error message would have already been printed
            self.serial_fdspawn = None
        try:
            self.serial_fdspawn = fdspawn(self.serial_fd, encoding="utf-8", logfile=self.logfile, timeout=uart_control.FDSPAWN_TIMEOUT)
        except pexpect.exceptions.TIMEOUT as error:
            self._error("TTY Timeout:"+str(error)+")")
            self.serial_fdspawn = None
        except Exception as error:
            self._error("Unexpected exception connecting to uart"+str(error))
            self.serial_fdspawn = None
        return self.serial_fdspawn

    def sendline(self,line):
        ''' Send line over fdspawn handle '''
        if not self.serial_fdspawn:
            self._error("sendline call without active fdspan")
            return False
        try:
            self.serial_fdspawn.sendline(line)
        except Exception as error:
            self._error("sendline error:"+str(error))
            return False
        return True

    def get_expect_str(self):
        ''' Return the last string received with expect '''
        if not self.serial_fdspawn:
            self._error("no active fdspan")
            return None
        return self.serial_fdspawn.match.group(0)

    def expect(self,pattern,timeout=DEFAULT_EXPECT_TIMEOUT):
        ''' Perform the "expect" command and catch any errors. '''
        self.timeout = False
        self.EOF = False
        self.unicode_error = False
        self.error = False
        
        ''' Expext fdspawn handle '''
        if not self.serial_fdspawn:
            self._error("expect call without active fdspan")
            return None
        try:
            result = self.serial_fdspawn.expect(pattern=pattern, timeout=timeout)
        except pexpect.exceptions.TIMEOUT:
            self.timeout = True
            self._error(f"expect timeout (delay {timeout}s)")
            return None
        except pexpect.exceptions.EOF:
            self.EOF = True
            self._error(f"UART EOF with pattern:"+str(pattern))
            return None
        except UnicodeDecodeError:
            self._error("expect unicode error")
            self.unicode_error = True
            return None
        except Exception as error:
            self._error("expect error:"+str(error))
            self.error = True
            return None
        return result

    def has_error(self):
        ''' Determines whether any error had occured on the last call to 'expect' '''
        if self.timeout or self.EOF or self.unicode_error or self.error:
            return True
        return False

    def has_unicode_error(self):
        ''' Determines whether a unicode error occured on the last call to 'expect' '''
        if self.unicode_error:
            return True
        return False

    def has_uart_error(self):
        ''' Determines whether a non-unicode error occured on the last call to 'expect' '''
        if self.timeout or self.EOF or self.error:
            return True
        return False

    def uart_group_args(parser):
        ''' Static function for creating UART argument group '''
        jcm_arg_group = parser.add_argument_group("UART")
        jcm_arg_group.add_argument("--usb_uart_phys_port", help="USB Physical port for UART", 
            type=str, default = uart_control.DEFAULT_USB_UART_PHYS_PORT)
        jcm_arg_group.add_argument("--usb_uart_phys_if", help="USB Physical interface for UART", 
            type=str, default = uart_control.DEFAULT_USB_UART_PHYS_IF)
        jcm_arg_group.add_argument("--uart_litex_baudrate", help="Baud rate for litex UART", 
            type=int, default = uart_control.DEFAULT_SERIAL_BAUDRATE)

    def create_uart_from_args(args, logging):
        ''' Static function for creating UART argument group '''
        #print(args.usb_uart_phys_port)
        uart = uart_control(args.usb_uart_phys_port, logging = logging, litex_baudrate=args.uart_litex_baudrate)
        return uart


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

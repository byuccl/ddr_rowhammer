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

class TimestampedFile(object):
    '''
    Class for writing a file with timestamps
    '''
    def __init__(self, file, timestampformat = None):
        self.file = file
        self.timestampformat = timestampformat

    def write(self, data):
        line = data
        if self.timestampformat:
            time_prefix = str("["+time.strftime(self.stdout_timeprefix)+"] ")
            line = time_prefix + data
        return self.file.write(line)

    def flush(self):
        self.file.flush()

class uart_control():
    '''
    Class for controlling the UART interface
    '''

    # Netbooter constants
    DEFAULT_USB_PROG_PHYS_PORT = "1-4.1"
    DEFAULT_USB_UART_PHYS_PORT = "1-4.2"
    DEFAULT_SERIAL_BAUDRATE = 115200
    FDSPAWN_TIMEOUT = 5
    MAX_TTY_FIND_ATTEMPTS = 5
    TTY_SEARCH_DELAY = 2
    
    def __init__(self, 
        usb_uart_phys_port:str,
        uart_stdout = None,
        logging = None,
        litex_baudrate = DEFAULT_SERIAL_BAUDRATE):

        self.usb_uart_phys_port = usb_uart_phys_port
        self.logging = logging
        self.serial_fd = None
        self.litex_baudrate = litex_baudrate
        if uart_stdout:
            self.logfile = TimestampedFile(uart_stdout)
        else:
            self.logfile = None

    def _info(self, str):
        ''' Send an 'info' message to the logger. '''
        if self.logging:
            self.logging.info("UART:"+str)

    def _error(self, str):
        ''' Send an 'error' message to the logger. '''
        if self.logging:
            self.logging.error("UART:"+str)

    def get_uart_dev_str(self):
        ''' Return the /dev/ttyUSBx device string of the UART '''
        # This will interface 0 on this port
        USB_UART_INTERFACE = 0
        #print(self.usb_uart_phys_port,USB_UART_INTERFACE, uart_control.DEFAULT_USB_PROG_PHYS_PORT )
        tty_find_attempt = 1
        tty = None
        while tty_find_attempt < uart_control.MAX_TTY_FIND_ATTEMPTS and not tty:
            time.sleep(uart_control.TTY_SEARCH_DELAY)
            self._info(f"Searching for ttyUSB device (Attempt {tty_find_attempt})")
            try:
                tty = find_dev_file_ttyUSB(self.usb_uart_phys_port, USB_UART_INTERFACE)
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
        serial_dev = self.get_uart_dev_str()
        if not serial_dev:
            return
        try:
            self._info("Attempting to open serial port:"+serial_dev)
            self.serial_fd = Serial(serial_dev, baudrate=self.litex_baudrate)
        except (Exception) as error:
            self._error("Failed to open:"+str(serial_dev)+" ("+str(error)+")")
            return None
        return self.serial_fd

    def create_uart_spawn(self):
        ''' Create Serial spawn object for pexpect'''
        if not self.create_uart_serial():
            # Error message would have already been printed
            return

        try:
            self.serial_fdspawn = fdspawn(self.serial_fd, encoding="utf-8", logfile=self.logfile, timeout=uart_control.FDSPAWN_TIMEOUT)
        except pexpect.exceptions.TIMEOUT as error:
            self._error("TTY Timeout:"+str(error)+")")
            self.serial_fdspawn = None
        except Exception as error:
            self._error("Unexpected exception connecting to uart"+str(error))
            self.serial_fdspawn = None
        return self.serial_fdspawn

    def uart_group_args(parser):
        ''' Static function for creating UART argument group '''
        jcm_arg_group = parser.add_argument_group("UART")
        jcm_arg_group.add_argument("--usb_uart_phys_port", help="USB Physical port for UART", 
            type=str, default = uart_control.DEFAULT_USB_UART_PHYS_PORT)
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

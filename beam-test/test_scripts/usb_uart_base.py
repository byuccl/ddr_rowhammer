#!/usr/bin/env python3

import argparse
import logging
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
from pathlib import Path

sys.path.insert(0, '../../../yinstruments/yinstruments')
#from usb_finder import find_dev_file_usb_bus
from usb_finder import find_dev_file_ttyUSB,USBFindError 

from timestampedfile import TimestampedFile

class usb_uart_base():
    '''
    Base class for USB-based UART interfaces. This class contains methods for managing usb UART
    device environments in a dynamic environment (i.e., frequent opening/closing, errors, etc.)
    The UART device represented by this class is tied to a specific usb physical port and not a
    device name. The device name may change as the object is closed and reopened. The object remains
    alive whether or not the serial port is open. 
    
    Performs the following functions:
    - Determine the device name based on the USB port (get_uart_dev_str)
    - Provides multi-attempt method for opening the serial port (to account for delays after powering board)
    - Provides a custom logging prefix for UART specific messages (with prefix)
      (this logger is for major UART messages like opening/closing, errors, etc. not for actual UART data)
    '''

    # UART constants
    TTY_SEARCH_DELAY = 10

    def __init__(self, 
        usb_uart_phys_port:str,
        baud_rate,
        test_logger = None,
        logger_prefix = "UART",
        timeout = 10,
        # TODO below
        uart_stdout = None,
        timestampformat = None):

        self.usb_uart_phys_port = usb_uart_phys_port
        self.baudrate = baud_rate
        if not test_logger:
            # Create an empty logger
            self.logging = test_logger()
        else:
            self.logging = test_logger(test_logger, logger_prefix)
        # String of currently opened Serial device. It is None when the
        # serial port is closed.  
        self.serial_dev = None      
        # Actual file handle of Serial device. It is None when the port is closed.
        self.serial_fd = None
        # timeout for reads and writes
        self.timeout = timeout


        # TODO below
        self.timeout = False
        if uart_stdout:
            self.logfile = TimestampedFile(uart_stdout, timestampformat = timestampformat)
        else:
            self.logfile = None

    def get_uart_dev_str(self, interface, max_tty_find_attempts = 5):
        ''' Returns the /dev/ttyUSBx device string of the UART '''
        tty_find_attempt = 1
        tty = None
        while tty_find_attempt < max_tty_find_attempts and not tty:
            time.sleep(usb_uart_base.TTY_SEARCH_DELAY)
            self._info(f"Searching for ttyUSB device (Attempt {tty_find_attempt})")
            try:
                tty = find_dev_file_ttyUSB(self.usb_uart_phys_port, interface)
            except (USBFindError) as error:
                # Ignore this for now
                tty_find_attempt += 1

        if not tty:
            self._error("Cannot find serial device:"+str(error))
            return None
        self._info("Found tty device:"+str(tty))
        return str(tty)
    
    def create_uart_serial(self):
        ''' Creates Serial object for uart '''
        self.serial_dev = self.get_uart_dev_str()
        if not self.serial_dev:
            return
        try:
            self.serial_fd = Serial(self.serial_dev, baudrate=self.baudrate, timout=self.timeout)
        except (Exception) as error:
            # SerialException if device cannot be found or properly configured
            # ValueError if values are incorrect
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

    # TODO below



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


    #### Static methods
    def ls_usb_uart():
        ''' Lists all of the /dev/ttyUSB devices in the system. '''
        tty_usb = []
        for f in Path("/dev").iterdir():
            if re.match("/dev/tty" + "USB" + "\d+", str(f)):
                tty_usb.append(f)
        return tty_usb

    def list_usb_uart_ports():
        tty_usbs = usb_uart_base.ls_usb_uart()
        for f in tty_usbs:
            p = subprocess.run(
                ["udevadm", "info", "-q", "path", "-n", str(f)], stdout=subprocess.PIPE
            )
            print(f,p.stdout.decode())

    def get_uart_phys_port_arg_name(base_str:str):
        ''' Generate the phys_port argument string name for the uart. '''
        return f"--{base_str}_uart_phys_port"

    def get_uart_baud_arg_name(base_str:str):
        ''' Generate the baudrate argument string name for the uart. '''
        return f"--{base_str}_uart_baudrate"

    def uart_group_args(parser,base_str:str):
        ''' Static function for creating an argument group for given UART.
        A base string is needed for the arguments (make unique for multiple UARTs) '''
        argument_group_name = f"{base_str}_uart"
        uart_arg_group = parser.add_argument_group(argument_group_name)
        uart_arg_group.add_argument(usb_uart_base.get_uart_phys_port_arg_name(base_str), 
            help="Physical port for UART", type=str)
        uart_arg_group.add_argument(usb_uart_base.get_uart_baud_arg_name(base_str), 
            help="Baud rate for UART", type=int)

    def create_uart_from_args(args, base_str:str, logging):
        ''' Static function for creating uart object from arguments '''
        args_dict = vars(args)

        # Get the physical port argument
        phys_port_arg = usb_uart_base.get_uart_phys_port_arg_name(base_str)
        if phys_port_arg in args_dict:
            phys_port = args_dict[phys_port_arg]
        else:
            return None
        # Get the baud rate argument
        baud_arg = usb_uart_base.get_uart_baud_arg_name(base_str)
        if baud_arg in args_dict:
            baud = args_dict[phys_port_arg]
        else:
            return None

        uart = usb_uart_base(phys_port_arg, baud, test_logger = logging)
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

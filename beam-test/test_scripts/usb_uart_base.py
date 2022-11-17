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
from test_logger import test_logger

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
      Manages the state of the open or closed serial port
    - Provides a custom logging prefix for UART specific messages (with prefix)
      (this logger is for major UART messages like opening/closing, errors, etc. not for actual UART data)
    '''

    # UART constants
    TTY_SEARCH_DELAY = 2
    MAX_FIND_TTY_ATTEMPTS = 5

    def __init__(self, 
        usb_uart_phys_port:str,     # USB UART port string (i.e. "1-4.2")
        usb_uart_phys_if,           # USB interface on that port (0-4)
        baud_rate,
        logger = None,
        logger_prefix = "UART",
        timeout = 10,
        # TODO below
        uart_stdout = None,
        timestampformat = None):

        self.usb_uart_phys_port = usb_uart_phys_port
        self.usb_uart_phys_if = usb_uart_phys_if
        self.baudrate = baud_rate
        if not logger:
            # Create an empty logger
            self.logging = test_logger()
        else:
            self.logging = test_logger(logger, logger_prefix)
        # String of currently opened Serial device. It is None when the
        # serial port is closed.  
        self.serial_dev = None      
        # Actual file handle of Serial device. It is None when the port is closed.
        self.serial_fd = None
        # timeout for reads and writes
        self.timeout = int(timeout)


        # TODO below
        #self.timeout = False
        if uart_stdout:
            self.logfile = TimestampedFile(uart_stdout, timestampformat = timestampformat)
        else:
            self.logfile = None

    def get_uart_dev_str(self, max_tty_find_attempts = MAX_FIND_TTY_ATTEMPTS):
        ''' Returns the /dev/ttyUSBx device string of the UART '''
        tty_find_attempt = 1
        tty = None
        while tty_find_attempt < max_tty_find_attempts and not tty:
            # Add a sleep for subsequent attemps
            if tty_find_attempt > 1:
                time.sleep(usb_uart_base.TTY_SEARCH_DELAY)
            self.logging._info(f"Searching for ttyUSB device (Attempt {tty_find_attempt}) for port '{self.usb_uart_phys_port}' IF '{self.usb_uart_phys_if}'")
            try:
                tty = find_dev_file_ttyUSB(self.usb_uart_phys_port, self.usb_uart_phys_if)
            except (USBFindError) as error:
                # Ignore this for now
                tty_find_attempt += 1

        if not tty:
            self.logging._error("Cannot find serial device:"+str(error))
            return None
        self.logging._info("Found tty device:"+str(tty))
        return str(tty)
    
    def create_uart_serial(self):
        ''' Creates Serial object for uart '''
        self.serial_dev = self.get_uart_dev_str()
        self.logging._info("Attempting to open:"+str(self.serial_dev)+" at baud "+str(self.baudrate))

        if not self.serial_dev:
            return
        try:
            self.serial_fd = Serial(self.serial_dev, baudrate=self.baudrate, timeout=self.timeout)
        except (Exception) as error:
            # SerialException if device cannot be found or properly configured
            # ValueError if values are incorrect
            self.logging._error("Failed to open:"+str(self.serial_dev)+" ("+str(type(error))+":"+str(error)+")")
            return None
        self.logging._info("Serial port "+self.serial_dev+" open")
        return self.serial_fd

    def close_uart_serial(self):
        ''' Close serial port'''
        self.logging._info("Serial port "+self.serial_dev+" closed")
        self.serial_dev = None
        self.serial_fd.close()
        self.serial_fd = None

    # TODO below



    def has_error(self):
        ''' Determines whether any error had occured on the last call to 'expect' '''
        #if self.timeout or self.EOF or self.unicode_error or self.error:
        if self.EOF or self.unicode_error or self.error:
            return True
        return False

    def has_unicode_error(self):
        ''' Determines whether a unicode error occured on the last call to 'expect' '''
        if self.unicode_error:
            return True
        return False

    def has_uart_error(self):
        ''' Determines whether a non-unicode error occured on the last call to 'expect' '''
        #if self.timeout or self.EOF or self.error:
        if self.EOF or self.error:
            return True
        return False


    #### Static methods
    def ls_usb_uart():
        ''' Static method. Creates a list of all of the /dev/ttyUSBx devices in the system. '''
        tty_usb = []
        for f in Path("/dev").iterdir():
            if re.match("/dev/tty" + "USB" + "\d+", str(f)):
                tty_usb.append(f)
        return tty_usb

    def usb_uart_dict():
        ''' Creates a dictionary between USB uarts and their port/if interfaces '''
        dict = {}
        for dev in usb_uart_base.ls_usb_uart():
            dict[dev] = usb_uart_base.get_port_if(dev)
        return dict

    def ls_usb_port_if():
        ''' Prints the usb ports and their IFs '''
        usb_d =  usb_uart_base.usb_uart_dict()
        for usb_dev in usb_d.keys():
            usb_r = usb_d[usb_dev]
            print(str(usb_dev)+" "+str(usb_r[0])+" "+str(usb_r[1]))

    def get_port_if(dev):
        ''' Returns the port string and interface number as a tuple based on a given device string. 
        Example strings:
            /devices/pci0000:00/0000:00:14.0/usb1/1-10/1-10.1/1-10.1:1.1/ttyUSB3/tty/ttyUSB3    
                port=1-10.1 IF = 1
            /devices/pci0000:00/0000:00:14.0/usb1/1-4/1-4.2/1-4.2:1.0/ttyUSB2/tty/ttyUSB2
                port=1-4.2  IF = 0
            /dev/ttyUSB1 /devices/pci0000:00/0000:00:14.0/usb1/1-4/1-4.1/1-4.1.4/1-4.1.4:1.1/ttyUSB1/tty/ttyUSB1
                port=1-4.1.4  IF = 1
        '''
        # Get the long devices string based on the /dev string
        p = subprocess.run(
            ["udevadm", "info", "-q", "path", "-n", str(dev)], stdout=subprocess.PIPE
        )

        match_str =  "/devices/.*?/.*?/usb\d+/.*/(.*?):(\d+)\.(\d+)/ttyUSB\d+/tty/ttyUSB\d+$"
        result = p.stdout.decode()
        #print(result)
        m = re.match(match_str, result)
        if m:
            #print(m.group(0))
            # Port ID is group 1
            port = m.group(1)
            #print(m.group(1))
            #print(m.group(2))
            # IF is group 3
            port_if = int(m.group(3))
            #print(m.group(3))
            return (port, port_if)
        else:
            #print("no match")
            return None

    def get_uart_phys_port_arg_name(base_str:str):
        ''' Generate the phys_port argument string name for the uart. '''
        return f"{base_str}_phys_port"

    def get_uart_phys_if_arg_name(base_str:str):
        ''' Generate the physical interface argument string name for the uart. '''
        return f"{base_str}_phys_if"

    def get_uart_baud_arg_name(base_str:str):
        ''' Generate the baudrate argument string name for the uart. '''
        return f"{base_str}_baudrate"

    def uart_group_args(parser,base_str:str, default_phys_port = None, default_phys_if = None, default_baud = None):
        ''' Static function for creating an argument group for given UART.
        A base string is needed for the arguments (make unique for multiple UARTs).
        Default can optionally be provided when creating these arguments.
        '''
        argument_group_name = f"{base_str}_uart"
        uart_arg_group = parser.add_argument_group(argument_group_name)
        # Add argument for physical USB port
        arg = uart_arg_group.add_argument("--"+usb_uart_base.get_uart_phys_port_arg_name(base_str), 
            help="Physical port for UART", type=str, required = True)
        if default_phys_port:
            arg.default=default_phys_port
            arg.required=False
        # Add argument for physical IF number
        arg = uart_arg_group.add_argument("--"+usb_uart_base.get_uart_phys_if_arg_name(base_str), 
            help="Physical IF for UART", type=str, required = True)
        if default_phys_if:
            arg.default=default_phys_if
            arg.required=False
        # Add argument for baud rate
        arg = uart_arg_group.add_argument("--"+usb_uart_base.get_uart_baud_arg_name(base_str), 
            help="Baud rate for UART", type=int, required = True)
        if default_baud:
            arg.default=default_baud
            arg.required=False

    def create_uart_from_args(args, base_str:str, logging, logger_prefix=None):
        ''' Static function for creating uart object from arguments '''
        args_dict = vars(args)
        #print(args_dict)
        # Get the physical port argument
        phys_port_arg = usb_uart_base.get_uart_phys_port_arg_name(base_str)
        #print(phys_port_arg)
        if phys_port_arg in args_dict:
            phys_port = args_dict[phys_port_arg]
            #print(phys_port)
        else:
            #print("No Phys Port")
            return None

        phys_if_arg = usb_uart_base.get_uart_phys_if_arg_name(base_str)
        if phys_if_arg in args_dict:
            phys_if = args_dict[phys_if_arg]
            #print(phys_port)
        else:
            #print("No Phys Port")
            return None

        # Get the baud rate argument
        baud_arg = usb_uart_base.get_uart_baud_arg_name(base_str)
        if baud_arg in args_dict:
            baud = args_dict[baud_arg]
        else:
            return None

        uart = usb_uart_base(phys_port, phys_if, baud, logger = logging, logger_prefix=logger_prefix)
        return uart


def main():

    parser = argparse.ArgumentParser()
    #parser.add_argument_group(uart_control.uart_group_args(parser))
    parser.add_argument("--list_usb_uart", help="List all the USB UART devices and their physical ports/IF", action='store_true')
    args = parser.parse_args()

    if args.list_usb_uart:
        devs = usb_uart_base.ls_usb_uart()
        print("USB UART Devices:")
        for dev in devs:
            print("\t"+str(dev)+":",end="")
            sys.stdout.flush()
            r = usb_uart_base.get_port_if(dev)
            if r:
                print(f"Port={r[0]} IF={r[1]}")
            else:
                print("No Match")

        #print("Ports:")
        #ports = usb_uart_base.list_usb_uart_ports()
        #for port in ports:
        #    print("\t"+port)
    #logging.basicConfig(level=logging.INFO)
    #uart = uart_control.create_uart_from_args(args,logging)
    #print(uart.get_uart_dev_str())
    return 0

if __name__ == "__main__":
    main()

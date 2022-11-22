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
from usb_uart_base import usb_uart_base

from timestampedfile import TimestampedFile

from pexpect.fdpexpect import fdspawn
import pexpect

# Constants ----------------------------------------------------------------------------------------

class usb_uart_expect(usb_uart_base):
    '''
    Provides pexpect functionality on a usb uart channel
    '''
    FDSPAWN_TIMEOUT = 5
    DEFAULT_EXPECT_TIMEOUT = 5

    def __init__(self, 
        usb_uart_phys_port:str,
        usb_uart_phys_if:int,
        baud_rate,
        pexpect_stdout = None,   # File handle for output of uart
        timestampformat = None,  # Timestamp specification to go on output (if desired)
        logger = None,           # Higher level logger for general messages
        logger_prefix = "UART",
        ):

        # Build base usb uart
        usb_uart_base.__init__(self, usb_uart_phys_port, usb_uart_phys_if, baud_rate, 
            logger = logger, logger_prefix = logger_prefix)
        #self.debug = False

        if pexpect_stdout:
            self.logfile = TimestampedFile(pexpect_stdout, timestampformat = timestampformat)
        else:
            self.logfile = None

    def create_uart_spawn(self):
        ''' Create Serial spawn object for pexpect. If this function is successful,
        the self.serial_fdspawn member is not None. Otherwise, None'''
        if not self.create_uart_serial():
            # Error message would have already been printed
            self.serial_fdspawn = None
        try:
            self.serial_fdspawn = fdspawn(self.serial_fd, encoding="utf-8", logfile=self.logfile, timeout=usb_uart_expect.FDSPAWN_TIMEOUT)
        except pexpect.exceptions.TIMEOUT as error:
            self.logging._error("TTY Timeout:"+str(error)+")")
            self.serial_fdspawn = None
        except Exception as error:
            self.logging._error("Unexpected exception connecting to uart"+str(error))
            self.serial_fdspawn = None
        return self.serial_fdspawn

    def sendline(self,line):
        ''' Send line over fdspawn handle '''
        if not self.serial_fdspawn:
            self.logging._error("sendline call without active fdspan")
            return False
        try:
            self.serial_fdspawn.sendline(line)
        except Exception as error:
            self.logging._error("sendline error:"+str(error)+"\n"+traceback.format_exc())
            return False
        return True

    def get_expect_str(self):
        ''' Return the last string received with expect '''
        if not self.serial_fdspawn:
            self.logging._error("no active fdspan")
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
            self.logging._error("expect call without active fdspan")
            return None
        try:
            result = self.serial_fdspawn.expect(pattern=pattern, timeout=timeout)
        except pexpect.exceptions.TIMEOUT:
            self.timeout_error = True
            self.logging._error(f"expect timeout (delay {timeout}s)")
            return None
        except pexpect.exceptions.EOF:
            self.EOF_error = True
            self.logging._error(f"UART EOF with pattern:"+str(pattern))
            return None
        except UnicodeDecodeError:
            self.logging._error("expect unicode error")
            self.unicode_error = True
            return None
        except Exception as error:
            self.logging._error("expect error:"+str(error))
            self.error = True
            return None
        return result

def create_usbuartexpect_from_args(args, base_str:str, logging, pexpect_stdout, 
    timestampformat, logger_prefix="UART"):
    
    uart_args = usb_uart_base.get_uart_args(args,base_str)

    uart = usb_uart_expect(uart_args[0], uart_args[1], uart_args[2], 
        pexpect_stdout = pexpect_stdout, timestampformat = timestampformat, 
        logger = logging, logger_prefix=logger_prefix)
    return uart

def main():

    # ls /dev/serial/by-id/

    parser = argparse.ArgumentParser()
    uart_basename = "uart"
    uartbone_args = usb_uart_base.uart_group_args(parser,uart_basename, 
        default_phys_port="1-4.1", default_phys_if=0, default_baud = 115200)
    parser.add_argument("--read", help="Hex address of read value from uart")
    parser.add_argument("--write", help="Hex address of read value from uart and Value to write", nargs=2)
    parser.add_argument("--ident", help="Read identification string", action='store_true')

    args = parser.parse_args()

    usb_uart_base.ls_usb_port_if()

    logging.basicConfig(level=logging.INFO)
    logging.info("Starting")
    usb_uartbone = usb_uart_bone.create_uartbone_from_args(args, uart_basename, logging)
    if not usb_uartbone:
        print("Error creating object")
        return 1
    # Find device
    uart_fd = usb_uartbone.create_uart_serial()
    if not uart_fd:
        logging.error("Failed to open uart")
        return 1
    if args.read:
        val = usb_uartbone.read(int(args.read,16), length=1)
        for i in val:
            print(f"0x{i:x}")
        print(val)
    if args.write:
        wargs = args.write
        address = int(wargs[0],16)
        data = int(wargs[1],16)
        val = usb_uartbone.write(address, data)
    if args.ident:
        ident_str = usb_uartbone.read_ident()
        print(ident_str)

    # 0xf0001800 (start of id - read bytes until null)
    # 0xf0000800 - reset register (write a 1 to reset the processor)
    return 0

if __name__ == "__main__":
    main()

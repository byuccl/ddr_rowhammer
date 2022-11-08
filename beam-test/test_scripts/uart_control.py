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

sys.path.insert(0, '../../../yinstruments/yinstruments')
#from usb_finder import find_dev_file_usb_bus
from usb_finder import find_dev_file_ttyUSB,USBFindError 

class uart_control():
    '''
    '''

    # Netbooter constants
    DEFAULT_USB_PROG_PHYS_PORT = "1-4.1"
    DEFAULT_USB_UART_PHYS_PORT = "1-4.2"

    def __init__(self, 
        usb_uart_phys_port:str,
        status_logging = None):

        self.usb_uart_phys_port = usb_uart_phys_port
        self.status_logging = status_logging

    def get_uart_dev_str(self):
        # Return the /dev/ttyUSBx device string of the UART
        # This will interface 0 on this port
        USB_UART_INTERFACE = 0
        #print(self.usb_uart_phys_port,USB_UART_INTERFACE, uart_control.DEFAULT_USB_PROG_PHYS_PORT )
        try:
            tty = find_dev_file_ttyUSB(self.usb_uart_phys_port, USB_UART_INTERFACE)
        except (USBFindError) as error:
            self.status_logging.error("Cannot find serial device:"+str(error))
            return None
        return tty

    def uart_group_args(parser):
        ''' Static function for creating UART argument group '''
        jcm_arg_group = parser.add_argument_group("UART")
        jcm_arg_group.add_argument("--usb_uart_phys_port", help="USB Physical port for UART", 
            type=str, default = uart_control.DEFAULT_USB_UART_PHYS_PORT)

    def create_uart_from_args(args, logging):
        ''' Static function for creating UART argument group '''
        #print(args.usb_uart_phys_port)
        uart = uart_control(args.usb_uart_phys_port, status_logging = logging)
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

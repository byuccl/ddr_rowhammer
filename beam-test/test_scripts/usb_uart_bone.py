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
import usb_uart_base

# Constants ----------------------------------------------------------------------------------------

CMD_WRITE_BURST_INCR  = 0x01
CMD_READ_BURST_INCR   = 0x02
CMD_WRITE_BURST_FIXED = 0x03
CMD_READ_BURST_FIXED  = 0x04


class usb_uart_bone(usb_uart_base):
    '''
    Provides usb uart "etherbone" functionality without having to use the server.

    Much of this code was copied from the LiteX CommUART module in the comm_uart.py file
    '''

    def __init__(self, 
        usb_uart_phys_port:str,
        baud_rate,
        test_logger = None,
        logger_prefix = "UARTBONE",
        ):

        usb_uart_base.__init__(self, usb_uart_phys_port, baud_rate, 
            test_loger = test_logger, logger_prefix = logger_prefix)

    '''
    def __init__(self, port, baudrate=115200, csr_csv=None, debug=False):
        CSRBuilder.__init__(self, comm=self, csr_csv=csr_csv)
        self.port     = serial.serial_for_url(port, baudrate)
        self.baudrate = str(baudrate)
        self.debug    = debug
    '''
    
    def open(self):
        if hasattr(self, "port"):
            return
        self.port.open()

    def close(self):
        if not hasattr(self, "port"):
            return
        self.port.close()
        del self.port

    def _read(self, length):
        r = bytes()
        while len(r) < length:
            r += self.port.read(length - len(r))
        return r

    def _write(self, data):
        remaining = len(data)
        pos = 0
        while remaining:
            written = self.port.write(data[pos:])
            remaining -= written
            pos += written

    def _flush(self):
        if self.port.inWaiting() > 0:
            self.port.read(self.port.inWaiting())

    def read(self, addr, length=None, burst="incr"):
        self._flush()
        data       = []
        length_int = 1 if length is None else length
        cmd        = {
            "incr" : CMD_READ_BURST_INCR,
            "fixed": CMD_READ_BURST_FIXED,
        }[burst]
        self._write([cmd, length_int])
        self._write(list((addr//4).to_bytes(4, byteorder="big")))
        for i in range(length_int):
            value = int.from_bytes(self._read(4), "big")
            if self.debug:
                print("read 0x{:08x} @ 0x{:08x}".format(value, addr + 4*i))
            if length is None:
                return value
            data.append(value)
        return data

    def write(self, addr, data, burst="incr"):
        self._flush()
        data   = data if isinstance(data, list) else [data]
        length = len(data)
        offset = 0
        while length:
            size = min(length, 8)
            cmd = {
                "incr" : CMD_WRITE_BURST_INCR,
                "fixed": CMD_WRITE_BURST_FIXED,
            }[burst]
            self._write([cmd, size])
            self._write(list(((addr//4 + offset).to_bytes(4, byteorder="big"))))
            for i, value in enumerate(data[offset:offset+size]):
                self._write(list(value.to_bytes(4, byteorder="big")))
                if self.debug:
                    print("write 0x{:08x} @ 0x{:08x}".format(value, addr + offset, 4*i))
            offset += size
            length -= size

    #### Static methods

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

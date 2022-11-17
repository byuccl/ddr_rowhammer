#!/usr/bin/env python3

import argparse
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
        usb_uart_phys_if:int,
        baud_rate,
        logger = None,
        logger_prefix = "UARTBONE",
        ):

        # Build base usb uart
        usb_uart_base.__init__(self, usb_uart_phys_port, usb_uart_phys_if, baud_rate, 
            logger = logger, logger_prefix = logger_prefix)
        self.debug = False

    '''
    def __init__(self, port, baudrate=115200, csr_csv=None, debug=False):
        CSRBuilder.__init__(self, comm=self, csr_csv=csr_csv)
        self.port     = serial.serial_for_url(port, baudrate)
        self.baudrate = str(baudrate)
        self.debug    = debug
    '''
    
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
    '''


    def _read(self, length):
        r = bytes()
        while len(r) < length:
            r += self.serial_fd.read(length - len(r))
        return r

    def _write(self, data):
        remaining = len(data)
        pos = 0
        while remaining:
            written = self.serial_fd.write(data[pos:])
            remaining -= written
            pos += written

    def _flush(self):
        if self.serial_fd.inWaiting() > 0:
            self.serial_fd.read(self.serial_fd.inWaiting())

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

    def read_ident(self, addr=0xf0001800):
        MAX_CHARS = 256
        char_addr = addr
        ident_str = ""
        while char_addr < addr + MAX_CHARS * 4:
            val = self.read(char_addr)
            #print(val)
            if val == 0:
                break
            new_char = chr(val)
            char_addr += 4
            ident_str += new_char

        return ident_str

    def create_uartbone_from_args(args, base_str:str, logging, logger_prefix="UARTBONE"):
        uart_args = usb_uart_base.get_uart_args(args,base_str)

        uart = usb_uart_bone(uart_args[0], uart_args[1], uart_args[2], logger = logging, logger_prefix=logger_prefix)
        return uart

def main():

    # ls /dev/serial/by-id/

    parser = argparse.ArgumentParser()
    uart_basename = "uartbone"
    uartbone_args = usb_uart_base.uart_group_args(parser,uart_basename, 
        default_phys_port="1-4.1", default_phys_if=0, default_baud = 115200)
    parser.add_argument("--read", help="Hex address of read value from uartbone")
    parser.add_argument("--write", help="Hex address of read value from uartbone and Value to write", nargs=2)
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
    
    return 0

if __name__ == "__main__":
    main()

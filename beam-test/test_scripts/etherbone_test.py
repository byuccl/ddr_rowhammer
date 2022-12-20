#!/usr/bin/env python

import os
import pty
import threading
import argparse
import subprocess
import shutil
import logging
import sys
from serial import Serial
from serial_expect import serial_expect
import time
from netbooter_control import netbooter_control

from pathlib import Path
from datetime import datetime

from rowhammer_tester.scripts.utils import RemoteClient, litex_server, read_ident

def main():

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--address", help="Address of operation", type=str, default="0x40000000")
    #parser.add_argument("--read", help="Perform a read operation", action='store_true')
    parser.add_argument("--write", help="Write operation", type=str)
    parser.add_argument("--num", help="Number of successive values", type=int, default=1)
    args = parser.parse_args()

    wb = RemoteClient()
    wb.open()
    print("Board info:", read_ident(wb))

    address = int(args.address,16)
    for addr in range(address,address+args.num*4,4):
        temp = wb.read(addr)
        print(f"address 0x{addr:08X} = 0x{temp:08X}")

    if args.write:
        value = int(args.write,16)
        for addr in range(address,address+args.num*4,4):
            print(f"writing 0x{value:08X} to address 0x{addr:08X}")
            wb.write(addr, value)
        for addr in range(address,address+args.num*4,4):
            temp = wb.read(addr)
            print(f"address 0x{addr:08X} = 0x{temp:08X}")

    wb.close()

if __name__ == "__main__":
    main()


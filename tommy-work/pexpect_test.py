#!/usr/bin/env python3

from serial import Serial
from pexpect.fdpexpect import fdspawn
import sys
import time
import re

try:
    # This will start a terminal once a board from litex-boards
    # is already built and loaded.

    # # Create, Send output to generated test.txt file
    # fout = open('test.txt','wb')
    # c = pexpect.spawn('litex_term /dev/ttyUSB1')
    # c.logfile = fout

    # Send output to sys.stdout
    fd = Serial(r"/dev/ttyUSB0", baudrate=115200)

    c = fdspawn(fd, encoding="utf-8", logfile=sys.stdout)

    # Send initial newline to trigger 'litex>' prompt when connecting to running instance.
    c.sendline("\n")

    # Run help command when string 'litex>' displays in opened terminal
    c.expect(pattern="\[92;1mlitex\W\[0m> ")
    c.sendline("help")

    # flip csr register that injects single errors to high
    # c.expect(pattern='\[92;1mlitex\W\[0m> ')
    # c.sendline('mem_write 0xf0003810 0x02 4')

    # flip csr register that injects single errors to low'r
    result1 = c.expect(R"Starting SDRAM BIST with burst_length=\d+ and addr_mode=\d+")
    print("result1:",type(result1), result1)
    result2 = c.expect(R"\S+ *")
    print("result2:", result2)
    print(c.match)
    result3 = c.expect(R"\d+")
    print("result3:", result3)
    print(c.match)

    # Terminate sdram_bist.
    time.sleep(5)
    c.send("\n")
finally:
    c.send("\n")
    fd.close()
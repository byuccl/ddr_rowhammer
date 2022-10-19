#!/usr/bin/env python3

from unittest import result
from wsgiref.util import shift_path_info

import pexpect
from serial import Serial
from pexpect.fdpexpect import fdspawn
from datetime import datetime
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

    
    fd = Serial(r"/dev/ttyUSB1", baudrate=115200)

    # Send output to sys.stdout
    c = fdspawn(fd, encoding="utf-8", logfile=sys.stdout)

    # # Send output to generated test.txt file
    # fout = open('test.txt', 'wb')
    # c = fdspawn(fd, logfile=fout)

    # Send initial newline to trigger 'litex>' prompt when connecting to running instance.
    c.sendline("\n")

    # Run help command when string 'litex>' displays in opened terminal
    c.expect(pattern="\[92;1mlitex\W\[0m> ")
    c.sendline("help")

    # flip csr register that injects single errors to high
    c.expect(R'\[92;1mlitex\W\[0m> ')
    c.sendline('mem_write 0xf0003810 0x02 4')

    c.expect(pattern="\[92;1mlitex\W\[0m> ")

    print("Start attributes")
    # print(dir(c.match))
    print(c.match.groups())
    print("End attributes")
    c.sendline("sdram_bist 0x1000 0")

    # flip csr register that injects single errors to low'r
    # result1 = c.expect(R"Starting SDRAM BIST with burst_length=\d+ and addr_mode=\d+")
    # print("result1:",type(result1), result1)
    # result2 = c.expect(R"\S+ *")
    # print("result2:", result2)
    # print(c.match)
    # result3 = c.expect(R"\d+")
    # print("result3:", result3)
    # print(c.match)

    # For comparing error counts
    old_error_cnt = 0
    old_sec_cnt = 0
    old_ded_cnt = 0
    new_error_cnt = 0
    new_sec_cnt = 0
    new_ded_cnt = 0

    MAX_ERROR_GROWTH = 40000000
    MAX_ERROR_CNT = 0xFFFFFFFF

    while True:

        try: 
            
            # 'timeout=None' will make 'expect()' run indefinitely until match is found
            match_index = c.expect(["WR-BW\(MiB/s\) RD-BW\(MiB/s\)  TESTED\(MiB\)     ERRORS        SEC        DED", # Title
                                        "\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*"],                  # Reg Expression matching 6 arguments
                                        timeout=30)

            # c.match object returns true if any match is found
            if c.match:

                # If title prints, print time to the side
                if match_index == 0:
                    pass
                    print("                                  ", 
                    "                                        ", 
                    "\033[ATime: ", datetime.now().time())

                # If stats print, compare them to the previous stats
                elif match_index == 1:
                    result_str = str(c.match.group(0)).split()

                    new_error_cnt = int(result_str[3])
                    new_sec_cnt = int(result_str[4])
                    new_ded_cnt = int(result_str[5])

                    # Compare previous counts: counts should not max out nor grow too fast
                    errors_growth_too_fast = ((new_error_cnt >= old_error_cnt + MAX_ERROR_GROWTH) or 
                        (new_sec_cnt >= old_sec_cnt + MAX_ERROR_GROWTH) or 
                        (new_ded_cnt >= old_ded_cnt + MAX_ERROR_GROWTH))
                    errors_max_out = (new_error_cnt >= MAX_ERROR_CNT or 
                        new_sec_cnt >= MAX_ERROR_CNT or
                        new_ded_cnt >= MAX_ERROR_CNT)

                    if (errors_growth_too_fast or errors_max_out):
                        print("Errors growing too fast" if errors_growth_too_fast else "")
                        print("Error max out" if errors_max_out else "")

                        # Turn off error injector for now
                        c.sendline("\n")
                        time.sleep(0.1)
                        c.expect(pattern="\[92;1mlitex\W\[0m> ")
                        c.sendline('mem_write 0xf0003810 0x00 4')
                        c.expect(pattern="\[92;1mlitex\W\[0m> ")
                        c.sendline("sdram_bist 0x1000 0")
                        
                    else:

                        old_error_cnt = new_error_cnt
                        old_sec_cnt = new_sec_cnt
                        old_ded_cnt = new_ded_cnt
                    


        # Respawn if timeout exception is thrown
        except pexpect.exceptions.TIMEOUT:
            print("Timout exception occured, respawning...")
            c = fdspawn(fd, encoding="utf-8", logfile=sys.stdout)
            c.sendline("\n")
            c.expect(pattern="\[92;1mlitex\W\[0m> ")
            c.sendline('mem_write 0xf0003810 0x02 4')
            c.expect(pattern="\[92;1mlitex\W\[0m> ")
            c.sendline("sdram_bist 0x1000 0")

    # Terminate sdram_bist.
    time.sleep(5)
    c.send("\n")
finally:
    c.send("\n")
    fd.close()

#!/usr/bin/env python3

from distutils.log import error
from socket import timeout
from unittest import result
from wsgiref.util import shift_path_info

import pexpect
from serial import Serial
from pexpect.fdpexpect import fdspawn
from datetime import datetime
import sys
import time
import re

# Function determining if board is still plugged in
MAX_FILE_NUM = 51
BOARD_NOT_PLUGGED_IN = -1

def confirm_board_plugged_in():
    # output_str = pexpect.run("ls /dev/ttyUSB" + str(0), encoding="utf-8", logfile=sys.stdout)
    # print(output_str)
    # if ("cannot access '/dev/ttyUSB" + str(0) + "': No such file or directory" in output_str):
    #     return False
    for i in range(MAX_FILE_NUM):
        output_str = pexpect.run("ls /dev/ttyUSB" + str(i), encoding="utf-8", logfile=sys.stdout)
        print(output_str)
        if not ("cannot access '/dev/ttyUSB" + str(i) + "': No such file or directory" in output_str):
            return True
    return False

# When starting terminal, ttyUSB0 isn't used, but ttyUSB1 or with a higher number.
def find_num_file():
    for i in range(1, MAX_FILE_NUM):
        output_str = pexpect.run("ls /dev/ttyUSB" + str(i), encoding="utf-8", logfile=sys.stdout)
        if not ("cannot access '/dev/ttyUSB" + str(i) + "': No such file or directory" in output_str):
            return i
    return BOARD_NOT_PLUGGED_IN

def configure_board_from_scratch(build_script = False):
    iterate_till_board_plugged_in = True
    while (iterate_till_board_plugged_in):
        while not (confirm_board_plugged_in()):
            pass
        print("Board plugged in, proceeding")
        if not build_script:
            pexpect.run("python3 litex-boards/litex_boards/targets/digilent_arty.py --load", encoding="utf-8", logfile=sys.stdout, timeout=None)
        else:
            pexpect.run("python3 litex-boards/litex_boards/targets/digilent_arty.py --build --load", encoding="utf-8", logfile=sys.stdout, timeout=None)
        if (find_num_file() == BOARD_NOT_PLUGGED_IN):
            continue
        iterate_till_board_plugged_in = False


old_error_cnt = 0
old_sec_cnt = 0
old_ded_cnt = 0
new_error_cnt = 0
new_sec_cnt = 0
new_ded_cnt = 0

cnt_error_max = 0
timeout_error_max = 0

MAX_ERROR_GROWTH = 40000000
MAX_ERROR_CNT = 0xFFFFFFFF
MAX_REPEAT_ERROR = 10



configure_board_from_scratch(build_script=False)

serial_str = r"/dev/ttyUSB" + str(find_num_file())
fd = Serial(serial_str, baudrate=115200)
c = fdspawn(fd, encoding="utf-8", logfile=sys.stdout)
c.sendline("\n")
c.expect(pattern="^.*litex[^>]*> ") # \[92;1mlitex\W\[0m> 

# Error injector
# c.sendline('mem_write 0xf0003810 0x02 4')
# c.expect(pattern="^.*litex[^>]*> ")

c.sendline("sdram_bist 0x2000 0")

while True:

    try: 

        if (cnt_error_max >= MAX_REPEAT_ERROR or timeout_error_max >= MAX_REPEAT_ERROR):
            configure_board_from_scratch()

            serial_str = r"/dev/ttyUSB" + str(find_num_file())
            fd = Serial(serial_str, baudrate=115200)
            c = fdspawn(fd, encoding="utf-8", logfile=sys.stdout)
            c.sendline("\n")
            c.expect(pattern="^.*litex[^>]*> ")
            c.sendline("sdram_bist 0x2000 0")

            cnt_error_max = 0
            timeout_error_max = 0

        
        # 'timeout=None' will make 'expect()' run indefinitely until match is found
        match_index = c.expect(["WR-BW\(MiB/s\) RD-BW\(MiB/s\)  TESTED\(MiB\)     ERRORS        SEC        DED", # Title
                                    "\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*"],                  # Reg Expression matching 6 arguments
                                    timeout=30)

        # c.match object returns true if any match is found
        if c.match:

            # If title prints, print time to the side
            if match_index == 0:
                print("                                  ", 
                "                                        ", 
                "\033[ATime: ", datetime.now().time())

            # If stats print, compare them to the previous stats
            elif match_index == 1:

                # c.match.group[0] contains the 'matched' part of the string.
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
                    cnt_error_max += 1

                    # Turn off error injector for now
                    # c.sendline("\n")
                    # time.sleep(0.1)
                    # c.expect(pattern="^.*litex[^>]*> ")
                    # c.sendline('mem_write 0xf0003810 0x00 4')
                    # c.expect(pattern="^.*litex[^>]*> ")
                    # c.sendline("sdram_bist 0x1000 0")
                    fd.close()
                    fd.open()
                    c = fdspawn(fd, encoding="utf-8", logfile=sys.stdout)
                    c.sendline("\n")
                    c.expect(pattern="^.*litex[^>]*> ")
                    c.sendline("sdram_bist 0x1000 0")

                    old_error_cnt = 0
                    old_sec_cnt = 0
                    old_ded_cnt = 0
                    new_error_cnt = 0
                    new_sec_cnt = 0
                    new_ded_cnt = 0
                    
                else:
                    timeout_error_max = 0
                    cnt_error_max = 0
                    old_error_cnt = new_error_cnt
                    old_sec_cnt = new_sec_cnt
                    old_ded_cnt = new_ded_cnt
                


    # Respawn if timeout exception is thrown
    except pexpect.exceptions.TIMEOUT:
        timeout_error_max += 1
        print("Timout exception occured, respawning...")
        # fd = Serial(r"/dev/ttyUSB1", baudrate=115200)
        fd.close()
        fd.open()
        c = fdspawn(fd, encoding="utf-8", logfile=sys.stdout)
        c.sendline("\n")
        c.expect(pattern="^.*litex[^>]*> ")
        c.sendline("sdram_bist 0x1000 0")

    # EOF exception will occur if board is unplugged
    except pexpect.exceptions.EOF:
        configure_board_from_scratch()
        serial_str = r"/dev/ttyUSB" + str(find_num_file())
        fd = Serial(serial_str, baudrate=115200)
        c = fdspawn(fd, encoding="utf-8", logfile=sys.stdout)
        c.sendline("\n")
        c.expect(pattern="^.*litex[^>]*> ")
        c.sendline("sdram_bist 0x2000 0")
        cnt_error_max = 0
        timeout_error_max = 0


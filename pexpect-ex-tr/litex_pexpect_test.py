#!/usr/bin/env python3

from distutils.log import error
import pexpect
import sys
import time

# # Create, Send output to generated test.txt file 
# fout = open('test.txt','wb')
# c = pexpect.spawn('litex_term /dev/ttyUSB1')
# c.logfile = fout

# Send output to sys.stdout
c = pexpect.spawn('litex_term /dev/ttyUSB1', encoding='utf-8')
c.logfile = sys.stdout

# Run help command when string 'litex>' displays in opened terminal
c.expect(pattern='\[92;1mlitex\W\[0m> ')
c.sendline('help')

# flip csr register that injects single errors to high
c.expect(pattern='\[92;1mlitex\W\[0m> ')
c.sendline('mem_write 0xf0003810 0x02 4')

# Run sdram_bist. 
c.expect(pattern='\[92;1mlitex\W\[0m> ')
c.sendline('sdram_bist 0x1000 0')


while(True):
    # error_index == 0, no errors
    # error_index >= 1, error_index <=3, 1 error type detected
    # error_index >= 4, error_index <=6, 2 error types detected 
    # error_index == 7, all three error types detected
    error_index = c.expect(['\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*0\s\s*0\s\s*0',              # No errors
                            '\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*[1-9]\d*\s\s*0\s\s*0',          # Errors != 0 
                            '\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*0\s\s*[1-9]\d*\s\s*0',          # SEC Errors != 0
                            '\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*0\s\s*0\s\s*[1-9]\d*',          # DED Errors != 0
                            '\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*[1-9]\d*\s\s*[1-9]\d*\s\s*0',      # Error and SEC Errors != 0
                            '\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*[1-9]\d*\s\s*0\s\s*[1-9]\d*',      # Error and DED Errors != 0
                            '\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*0\s\s*[1-9]\d*\s\s*[1-9]\d*',      # SEC and DED Errors != 0
                            '\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*[1-9]\d*\s\s*[1-9]\d*\s\s*[1-9]\d*']) # All three errors != 0

    

    if (error_index == 0):
        pass
    elif(error_index >= 1 and error_index <= 7):
        print("Errors detected")

        # sdram_bist function terminates when any input is entered.
        c.send('\n')
        c.expect(pattern='\[92;1mlitex\W\[0m> ')
        time.sleep(0.5)
        c.expect(pattern='\[92;1mlitex\W\[0m> ')

        # flip csr register that injects single errors to low
        c.sendline('mem_write 0xf0003810 0x00 4')
        c.expect(pattern='\[92;1mlitex\W\[0m> ')
        c.sendline('sdram_bist 4 0')
    else:
        print("No matching case, index: " + str(error_index))


















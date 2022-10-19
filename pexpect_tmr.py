#!/usr/bin/env python3

from mimetypes import init
from multiprocessing.spawn import old_main_modules
from nis import match
# from this import d
from unittest import result
import pexpect
import argparse
import telnetlib
import logging
import traceback
import cffi
import paramiko
from paramiko import SSHClient, SSHException, AutoAddPolicy, \
                    BadHostKeyException, AuthenticationException, buffered_pipe
import socket

from pkg_resources import require
# from asyncio.timeouts import timeout
from serial import Serial
from pexpect.fdpexpect import fdspawn
from datetime import date, datetime

import sys
import time
import re
import os
import numpy as np
import random

# print_fout = open('times_4.txt', 'w+')

MAX_FILE_NUM = 10

TIMEOUT_NETBOOTER = 3.0
SLEEPTIME_NETBOOTER = 1
LITEX_BAUDRATE = 115200

WAIT_TEXT_TIMEOUT = 15 # 15 seconds
WAIT_FOR_BOARD_BOOTUP = 40 # 40 seconds
RUN_JCM_TIMEOUT = 30 # 30 seconds
SDRAM_CAL_TIMEOUT = 5 # 5 seconds
SDRAM_INIT_TIMEOUT = 5 # 5 seconds
TERMINAL_REBOOT_CMD_TIMEOUT = 10 # 10 seconds
BOARD_REPOWER_TIMEOUT = 30 # 30 seconds
BOARD_REPROGRAM_TIMEOUT = 10 # 10 seconds
RESET_LITEX_TIMEOUT = 10 # 10 seconds
FAULT_TIMER_MAX = 1 # 2 second fault injections


MAX_NUM_INC_FAULT_READS = 20
AUTO_NUM_ERRORS = 1
STARTING_FILE_NUM = -1
MEM_INDEX = 2
ERROR_MSG_INDEX = 3
SEC_MSG_INDEX = 4
DED_MSG_INDEX = 5
MAX_LINES_CODE_MAX_OUT_ERROR =120
MAX_NUM_TIMES_BOOT_UP = 5
MAX_MIB_TO_READ = 0x1000
MAX_ALIVE_CNT = 30
MAX_BEGINNING_LINES_FOR_ERRORS = 10

MAX_ERROR_CNT_CYCLES = 30
MAX_PAUSE_ERROR_CNT_CYCLES = 10

PLUG_IN_DELAY = 10
MAX_ERROR_CNT = 0xFFFFFFFF

CORRECTION_FAULT_INJECTION_COMMAND = "~/jcm_apps/jcm_fault_inject.elf --part {fpga} -c 20000000 --jtag --frad_file {frads} --readback_file {design}.rb --target_frame {frame} --target_word {word} --target_bit {bit}"
FAULT_INJECTION_COMMAND = "~/jcm_apps/jcm_random_fault_inject.elf --part {fpga} -c 20000000 --jtag --frad_file {frads} --seed {seed} --readback_file ~/jcm_apps/jcm_readback.rb"
CONFIGURATION_COMMAND = "~/jcm_apps/jcm_config.elf --part {part} -c 20000000 --jtag --config_file {bitstream}"
JCM_IP_ADDRESS = "169.254.132.152"
PART = "xc7a200t"
BITFILE = "./digilent_nexys_video.bit"
FRADS = "~/jcm_apps/a200t.frad"
JCM_LOGIN_LOOPS = 10
JCM_TIMEOUT_IN_SECONDS = 15
NUC_SEED = None
DESIGN = "digilent_nexys_video"

print_jcm_fout = open('jcm_times_16.txt', 'w')


class jcm_control:

    def close_jcm(new_client):
        new_client.close()
        print("SSH closed")

# Logs into the jcm using paramiko. 
# Returns a SSHClient object
    def login_to_jcm(ip_addr:str):
        print("Logging in to JCM, Time: ", file=print_jcm_fout)
        while(1):
            try:
                new_client = SSHClient()
                new_client.load_system_host_keys()
                new_client.set_missing_host_key_policy(AutoAddPolicy())
                print("Connecting to JCM over SSH...", file=print_jcm_fout)
                new_client.connect(ip_addr, username='root', password='chrec', timeout=None)
                print("SSH successful!", file=print_jcm_fout)
                break
            except (BadHostKeyException, AuthenticationException,
                SSHException, socket.error, buffered_pipe.PipeTimeout, socket.timeout) as error:
                print(error, file=print_jcm_fout)
                new_client.close()
        return new_client


# Configure the FPGA using jcm_config.elf
    def configure_fpga(ssh_client):
        print("Sending config command to JCM, Time: ", datetime.now().time(), file=print_jcm_fout)

        config_command = CONFIGURATION_COMMAND.format(part=PART, bitstream=BITFILE)
        print(config_command, file=print_jcm_fout)

        for i in range(JCM_LOGIN_LOOPS):
            try:
                print("Running config command, Time: ", datetime.now().time(), file=print_jcm_fout)
                stdin, stdout, stderr = ssh_client.exec_command(config_command,timeout=JCM_TIMEOUT_IN_SECONDS)
                break
            except SSHException as error:
                print(error, file=print_jcm_fout)
                logging.info("SSHException: Timeout occured or request was rejected opening channel to JCM. Retrying command.")
                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] SSHException: Timeout occured or request was rejected opening channel to JCM. Retrying command.")
                ssh_client = jcm_control.login_to_jcm(JCM_IP_ADDRESS)

        while not stdout.channel.exit_status_ready():
            try:
                line = stdout.readline()
                if (not line.isspace()) and line != '':
                    print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] : ", line, file=print_jcm_fout)
                if (not line.isspace()) and line != '':
                    line = "[{}] ".format(time.strftime("%Y-%m-%d %H:%M:%S")) + line
                    print(line, file=print_jcm_fout)

                    if "Success" in line:
                        print("Configured Successfully!", file=print_jcm_fout)
                        break

                    if "[root@arch" in line:
                        print("ERROR in configure_fpga", file=print_jcm_fout)
                        break
            
            except(buffered_pipe.PipeTimeout, socket.timeout) as error:
                print("ERROR in fonfigure_fpga", file=print_jcm_fout)
                print(error, file=print_jcm_fout)
                return 1
        return 0

    def inject_fault(ssh_client):
        '''
        Injects a fault
        '''

        global frame_to_correct
        global word_to_correct
        global bit_to_correct
        global location_to_correct
        
        print(time.strftime("%Y-%m-%d %H:%M:%S"),"Injecting Location", file=print_jcm_fout)

        if NUC_SEED is None:
            jcm_seed = str(np.uint32(time.time() * 1000))
        else:
            jcm_seed = random.randint(0, 4000000000)

        command = FAULT_INJECTION_COMMAND.format(fpga = PART, frads = FRADS,seed=jcm_seed)

        print("Before", file=print_jcm_fout)
        for i in range(JCM_LOGIN_LOOPS):
            try:
                stdin, stdout, stderr = ssh_client.exec_command(command, timeout = JCM_TIMEOUT_IN_SECONDS)
                break
            except SSHException as error:
                print(error, file=print_jcm_fout)
                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] SSHException: Timeout occured or request was rejected opening channel to JCM. Retrying exec_command.")
                

        print("After", file=print_jcm_fout)
        
        line = ""
        keep_reading = True

        time_start = time.time()
        while keep_reading:
            cur_time = time.time()
            if (cur_time - time_start > 30):
                print("Restarting script", file=print_jcm_fout)
                os.execv(sys.executable, ['python3'] + sys.argv) # Restarts the program
            
            line = stdout.readline()
            if (not line.isspace()) and line != '':
                print(time.strftime("%Y-%m-%d %H:%M:%S"),   " : ", line, file=print_jcm_fout)
                line = "[{}] ".format(time.strftime("%Y-%m-%d %H:%M:%S")) + line
                if "Failed!" in line:
                    return 1
                if "Injecting Frame" in line:
                    search_string = "Frame (0x[0-9A-F]{8})"
                    m = re.search(search_string, line)
                    if m:
                        frame_to_correct = m.group(1)
                    search_string = "word ([0-9]+ )"
                    m = re.search(search_string, line)
                    if m:
                        word_to_correct = m.group(1)
                    search_string = "bit ([0-9]+)"
                    m = re.search(search_string, line)
                    if m:
                        bit_to_correct = m.group(1)

                    location_to_correct = frame_to_correct + ' ' + word_to_correct + bit_to_correct
                    # write_to_log("Injected location " + location_to_correct, jcm_log)
                    
                if "Fault Injection Succeeded!" in line:
                    line = "[{}] ".format(time.strftime("%Y-%m-%d %H:%M:%S")) + "Fault Injected!\n"
                    print("Fault injection succeeded!", file=print_jcm_fout)
                    keep_reading = False


    def correct_fault(ssh_client):
        '''
        Injects a fault to correct it
        '''
        global frame_to_correct
        global word_to_correct
        global bit_to_correct
        global location_to_correct
        global CORRECTION_FAULT_INJECTION_COMMAND
        global DESIGN
        global FAULT_INJECTION_ENABLED

        location = location_to_correct[2:]
        location = location.split()
        inject_address = hex(int(location[0],16))
        inject_word = int(location[1])
        inject_bit = int(location[2])

        command = CORRECTION_FAULT_INJECTION_COMMAND.format(fpga = PART, frads = FRADS, design = DESIGN, frame = inject_address, word = inject_word, bit = inject_bit)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        line = ""
        time_start = time.time()
        keep_reading = True
        while keep_reading:
            
            if not FAULT_INJECTION_ENABLED:
                return 1
            
            cur_time = time.time()
            if (cur_time-time_start >30):
                os.execv(sys.executable, ['python3'] + sys.argv) # Restarts the program
            line = stdout.readline()
            if (not line.isspace()) and line != '':
                print(time.strftime("%Y-%m-%d %H:%M:%S"), " : ", line, file=print_jcm_fout)
                line = "[{}] ".format(time.strftime("%Y-%m-%d %H:%M:%S")) + line
                if "Failed!" in line:
                    return 1
                if "Fault Injection Succeeded!" in line:
                    line = "[{}] ".format(time.strftime("%Y-%m-%d %H:%M:%S")) + "Fault Corrected!\n"
                    print("Fault correction succeeded!", file=print_jcm_fout)
                    keep_reading = False





# Commands spawned with pexpect
class board_control:

    # dev port (i.e. /dev/ttyUSBX) the FPGA is connected to
    def __init__(self, netbooter_port, netbooter_ip):
        self.netbooter_port = netbooter_port
        self.netbooter_ip = netbooter_ip
        self.fout = open('test.txt','wb')
        self.bist_started = False

    # Returns number above 0 if ttyUSB files found, otherwise -1
    def confirm_board_plugged_in(self):
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Confirming board plugged in")
        max_num = STARTING_FILE_NUM
        for i in range(0, MAX_FILE_NUM):
            output_str = pexpect.run("ls /dev/ttyUSB" + str(i), encoding="utf-8", logfile=sys.stdout)
            # output_str = pexpect.run("ls /dev/ttyUSB" + str(i), logfile=self.fout)
            # print(output_str)
            if not ("cannot access '/dev/ttyUSB" + str(i) + "': No such file or directory" in output_str and (i > max_num)):
                max_num = i
        self.file_num = max_num
        if (max_num > 0):
            print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Board plugged in, using /dev/ttyUSB{max_int}.".format(max_int=max_num))
            logging.info("Board plugged in, using /dev/ttyUSB%d", max_num)
        else:
            print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Board not plugged in.")
            logging.info("Board not plugged in")
        return max_num

    # # Runs the fault injector script, makes sure its running
    # def run_jcm_fault_injector(self):
    #     self.jcm_child = pexpect.spawn('python ../../fault_scripts/fault_injection.py --design digilent_nexys_video --dev 3 --ip_address 169.254.132.152')
    #     print("Attempting to start JCM, time: ", datetime.now().time())
    #     self.jcm_child.expect("Before")
    #     while (True):
    #         try:
    #             print("Expecting \"After\"")
    #             self.jcm_child.expect("After", timeout = RUN_JCM_TIMEOUT)
    #             break
    #         except Exception as e:
    #             print(e)
    #             print("Retrying, time: ", datetime.now().time())
    #             self.jcm_child.close(True)
    #             print("Closed")
    #             self.jcm_child = pexpect.spawn('python ../../fault_scripts/fault_injection.py --design digilent_nexys_video --dev 3 --ip_address 169.254.132.152')
    #             print("On retrying JCM")
    #             self.jcm_child.expect("Before")
    #             print("Expecting \"After\"")
    #     print("JCM running successfully!")

    def start_jcm(self):
        global FAULT_INJECTION_ENABLED
   
        # signal.signal(signal.SIGINT, signal_handler)
        
        # Make jcm client object for fault injection
        self.jcm_client = jcm_control.login_to_jcm(JCM_IP_ADDRESS)

        # First run with fault injector is read by run_jcm_fault_injector
        self.first_run = True
        pass

    # Used for after a timeout occurs, attempt to get rid of the double timeout
    def correct_jcm_fault(self):
        jcm_control.correct_fault(self.jcm_client)

    def run_jcm_fault_injector(self):
        pass

        global FAULT_INJECTION_ENABLED
    
        FAULT_INJECTION_ENABLED = True

        # serial_monitor = threading.Thread(target=monitor_serial, args=(fpga_serial,))
        
        # configure_fpga(jcm_client)
        
        # serial_monitor.start()
        
        if (FAULT_INJECTION_ENABLED and self.first_run):
            jcm_control.inject_fault(self.jcm_client)
            self.first_run = False
        elif FAULT_INJECTION_ENABLED:
            jcm_control.correct_fault(self.jcm_client)
            jcm_control.inject_fault(self.jcm_client)
            
        else:
            # if not serial_monitor.is_alive():
            #     return 1
            time.sleep(1)
            print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Not error injecting")
            logging.info("Not error injecting")

    # Stop running jcm
    def stop_jcm(self):
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Stopping JCM.")
        logging.info("Stopping JCM")
        # self.jcm_child.close(True)
        jcm_control.close_jcm(self.jcm_client)

    def load_bitstream_jcm(self):
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Loading bistream with JCM.")
        logging.info("Configuring JCM")
        jcm_control.configure_fpga(self.jcm_client)
   
    # Return true if terminal has started, else return false
    # TODO: Add timeout argument
    def start_terminal(self):
        serial_str = r"/dev/ttyUSB" +  str(self.file_num)
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Attempting to start LiteX with ", serial_str)
        self.fd = Serial(serial_str, baudrate = LITEX_BAUDRATE)
        while(1):

            try:
                # if hasattr(self, 'c'):
                #     self.check_if_alive()
                self.c = fdspawn(self.fd, encoding="utf-8", logfile=sys.stdout, timeout=BOARD_REPROGRAM_TIMEOUT)
                # self.c = fdspawn(self.fd, logfile=self.fout, timeout=BOARD_REPROGRAM_TIMEOUT)
                # Send newline character to get starting litex terminal output
                self.c.sendline("\n")
                self.c.expect(pattern="^.*litex[^>]*> ", timeout=BOARD_REPOWER_TIMEOUT)
                return True

            except pexpect.exceptions.TIMEOUT:
                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Timout occured with ", serial_str, ", retrying.")
                logging.info("Timout occured with ", serial_str, ", retrying.")
                dev_file_num = self.confirm_board_plugged_in()
                if (dev_file_num < 0):
                    print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Board not powered on!")
                    logging.info("Board not powered on!")
                    return False

                self.file_num = dev_file_num 
                try:
                    self.c.sendline("\n")
                    self.c.expect(pattern="^.*litex[^>]*> ", timeout=BOARD_REPOWER_TIMEOUT)
                    return True
                except pexpect.exceptions.TIMEOUT:
                    print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Terminal not started")
                    logging.info("Terminal not started")
                    return False

                except Exception:
                    print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] ", Exception)
                    logging.info(Exception)
                    return False

            except UnicodeDecodeError:
                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] UnicodeDecodeError, retrying")

        # except Exception:
        #     logging.error(traceback.format_exc())
        #     print(Exception, " Time: ", datetime.now().time())
        #     logging.info(Exception)
        #     return False

        # This has occured when fdspawn uses a bad file descriptor
        # except OSError:
        #     print(OSError)
        #     return False

        # except Exception:
        #     print(Exception)
        #     return False

    # def check_if_alive(self):
    #     alive_cnt = 0
        
    #     # Check every second up to max alloted time
    #     while not self.c.isalive():
    #         time.sleep(1)
    #         alive_cnt += 1
    #         self.fd.close()
    #         self.fd.open()
    #         if (not self.c.isalive()) and alive_cnt >= MAX_ALIVE_CNT:
    #             return False
    #     return True



    # Run after starting the litex terminal
    # Attribute:
        # bist_started: Tells 'main()' that the bist has just started.
        # It is used to see if errors have begun to accumulate from the beginning
        # of the bist. It is set to false after an errorless first cycle or after
        # a number of consecutive cycles where errors have been counting.
    def run_bist(self, mem_burst_length, addr_mode):
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Running Bist command.")
        cmd_str = "sdram_bist " + str(mem_burst_length) + " " + str(addr_mode)
        self.c.sendline(cmd_str)
        self.bist_started = True

    # Issue letter to quit bist
    def quit_bist(self):
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Quitting Bist.")
        try:
            self.c.sendline("\n")
            self.c.expect(pattern="^.*litex[^>]*> ")
            return True
        except:
            return False

    # Command for initializing and recalibrating DRAM
    def dram_delay_register_scrub_cmd(self):
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Running sdram_delay_scrub command.")
        logging.debug("Running dram delay register scrub command")
        try:
            self.c.sendline("sdram_delay_scrub")
            self.c.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)
            return True
        except:
            return False

    def dram_mode_register_scrub_cmd(self):
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Running sdram_delay_scrub command.")
        logging.debug("Running dram mode register scrub command")
        try:
            self.c.sendline("sdram_mr_scrub")
            self.c.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)
            return True
        except:
            return False

    # Command for calibrating the DRAM
    def dram_calibrate(self):
        logging.debug("Running dram calibrate command")
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Running sdram calibrate command.")
        try:
            self.c.sendline("sdram_cal")
            self.c.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_CAL_TIMEOUT)
            return True
        except:
            return False

    # Command for initializing and recalibrating DRAM
    def dram_init_and_calibrate(self):
        logging.debug("Running dram init and calibrate command")
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Running sdram init command.")
        try:
            self.c.sendline("sdram_init")
            self.c.expect(pattern="^.*litex[^>]*> ", timeout=SDRAM_INIT_TIMEOUT)
            return True
        except:
            return False


    def reset_litex(self):
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Attempting to reset Litex")
        logging.debug("Resetting Litex")
        try:
            # Force child to close
            self.c.sendline("reboot")
            self.fd.close()
            self.fd.open()
            # serial_str = r"/dev/ttyUSB" +  str(self.file_num)
            # self.fd = Serial(serial_str, baudrate = LITEX_BAUDRATE)
            self.c = fdspawn(self.fd, encoding="utf-8", logfile=sys.stdout, timeout=BOARD_REPROGRAM_TIMEOUT)
            # self.c = fdspawn(self.fd, logfile=self.fout, timeout=BOARD_REPROGRAM_TIMEOUT)
            self.c.expect(pattern="^.*litex[^>]*> ", timeout=BOARD_REPROGRAM_TIMEOUT)
            return True

        except pexpect.exceptions.TIMEOUT:
            print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Timeout occured resetting Litex")
            return False

        except Exception: 
            print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Other exception while resetting Litex")
            logging.info("Other exception while resetting Litex, traceback:")
            return False
    
    
    # Reset SoC experiments
    def reset_litex_sdcard(self):
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Attempting to reset Litex")
        try:
            # Force child to close
            self.fd.close()
            self.c.close(timeout=RESET_LITEX_TIMEOUT)
            serial_str = r"/dev/ttyUSB" +  str(self.file_num)
            self.fd = Serial(serial_str, baudrate = LITEX_BAUDRATE)
            self.c = fdspawn(self.fd, encoding="utf-8", logfile=sys.stdout, timeout=BOARD_REPROGRAM_TIMEOUT)
            # self.c = fdspawn(self.fd, logfile=self.fout, timeout=BOARD_REPROGRAM_TIMEOUT)
            self.c.expect(pattern="^.*litex[^>]*> ", timeout=TERMINAL_REBOOT_CMD_TIMEOUT)
            return True

        except pexpect.exceptions.TIMEOUT:
            print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Timeout occured resetting Litex.")
            return False

        except Exception: 
            print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Other exception while resetting Litex")
            logging.info("Other exception while resetting Litex, traceback:")
            logging.error(traceback.format_exc())
            return False

    # Reinit SoC with a 'reboot' command
    def reset_dram(self):
        
        try:
            self.c.sendline("reboot")
            self.fd.close()
            self.fd.open()
            self.c = fdspawn(self.fd, encoding="utf-8", logfile=sys.stdout, timeout=BOARD_REPROGRAM_TIMEOUT)
            # self.c = fdspawn(self.fd, logfile=self.fout, timeout=BOARD_REPROGRAM_TIMEOUT)
            self.c.expect(pattern="^.*litex[^>]*> ", timeout=TERMINAL_REBOOT_CMD_TIMEOUT)
            return True
        except pexpect.exceptions.TIMEOUT or pexpect.exceptions.EOF:
            return False


    # Reload board with bitstream
    def reset_board(self):
        self.stop_jcm()
        self.fd.close()
        self.start_jcm()
        self.load_bitstream_jcm()
        # Find which dev ports exist (i.e. /dev/ttyUSBX)
        
        if not self.start_terminal():
            return False
        return True
    
    # Turn board off, then on again
    # Before powering off at any time, turn off the jcm
    def repower_board(self):
    
        # Stop JCM
        self.stop_jcm()

        teln = telnetlib.Telnet(self.netbooter_ip, None, timeout=TIMEOUT_NETBOOTER)

        # Turn off
        s = teln.read_some()
        time.sleep(SLEEPTIME_NETBOOTER)

        s = ("pset " + str(self.netbooter_port) + " 0").encode("ascii") + b"\r\n\r\n"
        teln.write(s)
        time.sleep(SLEEPTIME_NETBOOTER)

        # Turn back on
        s = ("pset " + str(self.netbooter_port) + " 1").encode("ascii") + b"\r\n\r\n"
        teln.write(s)
        time.sleep(SLEEPTIME_NETBOOTER)
        teln.close()



def main():
    logging.basicConfig(filename="times_16.txt", level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S', format='%(asctime)s %(levelname)-8s %(message)s')

    print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Starting test")
    logging.info("Starting test")

    new_error_cnt = 0
    new_sec_cnt = 0
    new_ded_cnt = 0
    old_error_cnt = 0
    old_sec_cnt = 0
    old_ded_cnt = 0
    loop_var = 0
    cnt_error_max = 0
    degree_of_max_error = 0
    board_boot_up = 0
    dram_errors_flag = 0
    fault_injector_timer = 0
    mem_error_timer = 0
    pause_error_timer = 0
    getting_correct_input = True
    errors_currently_counting = False
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--netbooter-port", help="netbooter outlet number that the FPGA is connected to", default=1, required=False)
    parser.add_argument("--netbooter-ip", help="Ip address to connect to netbooter", default="169.254.131.160", required=False)
    parser.add_argument("--mem-burst-length", help="Bist memory burst length", default=0x2000, required=False)
    parser.add_argument("--addr-mode", help="Address mode, how Bist should read and write memory: 0=fixed, 1=linear, 2=random", default=1, required=False)
    args = parser.parse_args()

    boardcontroller = board_control(args.netbooter_port, args.netbooter_ip)
    jcmcontroller = jcm_control()

    print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Start of test")
    logging.info("Start of test")

    while True:
        # Make sure board is plugged in
        while (boardcontroller.confirm_board_plugged_in() < 0) and (board_boot_up < MAX_NUM_TIMES_BOOT_UP):
            print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Waiting for board to be plugged in")
            logging.info("Waiting for board to be plugged in")
            #print("Waiting for board to be plugged in, time: ", datetime.now().time(), "\n", file=print_fout)
            board_boot_up += 1
            time.sleep(PLUG_IN_DELAY)
            pass

        # If the board isn't plugged in, give up
        if (board_boot_up >= MAX_NUM_TIMES_BOOT_UP):
            break
        else :
            board_boot_up = 0

        # # Start JCM after 40 seconds (takes about 25 for the board to boot up)
        # time.sleep(WAIT_FOR_BOARD_BOOTUP)

        # New function: Load bitstream onto the board
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Logging into JCM")
        boardcontroller.start_jcm()
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Loading bitstream.")
        boardcontroller.load_bitstream_jcm()
        fault_injector_timer = FAULT_TIMER_MAX
        
        # If terminal didn't start, repower board
        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Starting LiteX")
        if not boardcontroller.start_terminal():
            print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] LiteX not starting, repowering board.")
            logging.info("LiteX not starting, repowering board.")
            boardcontroller.repower_board()
            continue

        # # Error read injector
        # if loop_var == 0:
        #     loop_var += 1
        #     boardcontroller.c.sendline('mem_write 0xf0003810 0x02 4')
        #     boardcontroller.c.expect(pattern="^.*litex[^>]*> ")

        # Send command to run bist
        boardcontroller.run_bist(args.mem_burst_length, args.addr_mode)

        while True:
            
            try: 

                print("Fault injector") ############################################################3

                if (fault_injector_timer <= 0):
                    # Inject error first, then expect data
                    boardcontroller.run_jcm_fault_injector()
                    fault_injector_timer = FAULT_TIMER_MAX
                    print("Ran fault injector") ############################################################3
                else:
                    fault_injector_timer -= 1
                    print("No run fault injector") ############################################################3

                print("After injector") ############################################################3

                # 'timeout=None' will make 'expect()' run indefinitely until match is found, for now timeout occurs in 30 seconds
                match_index = boardcontroller.c.expect(["WR-BW\(MiB/s\) RD-BW\(MiB/s\)  TESTED\(MiB\)     ERRORS        SEC        DED", # Title
                              "\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*\s\s*\d\d*"],                  # Reg Expression matching 6 arguments
                              timeout=WAIT_TEXT_TIMEOUT)

                print("expecter") ############################################################3
                
                # c.match object returns true if any match is found
                if boardcontroller.c.match:
                    # If title prints, print time to the side
                    if match_index == 0:
                        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] ")
                        logging.info("Time Stamp")
                        fault_injector_timer += 1
                        if (getting_correct_input):
                            getting_correct_input = False
                        else:
                            print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Not getting correct output")
                            logging.info("Not getting correct output")
                            boardcontroller.quit_bist()
                            if not boardcontroller.reset_litex():
                                logging.info("Failed closing, reopening Litex, configuring board.")
                                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Failed closing, reopening Litex, configuring board.")
                                if not boardcontroller.reset_board():

                                    # If board is to be repowered, break second loop to go back 
                                    # to beginning init sequence. (Dev port may change)
                                    print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Resetting Litex unsuccessful, repowering board.")
                                    logging.info("Resetting Litex unsuccessful, repowering board.")
                                    boardcontroller.repower_board()
                                    break

                            boardcontroller.run_bist(args.mem_burst_length, args.addr_mode)
                            getting_correct_input = True

                    # If stats print, compare them to the previous stats
                    elif match_index == 1: 

                        getting_correct_input = True
                        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] ")

                        # c.match.group[0] contains the 'matched' part of the string.
                        # Take this, split string between the spaces
                        result_str = str(boardcontroller.c.match.group(0)).split()

                        # Get error counts from matched string 
                        memory_read = int(result_str[MEM_INDEX])
                        new_error_cnt = int(result_str[ERROR_MSG_INDEX])
                        new_sec_cnt = int(result_str[SEC_MSG_INDEX])
                        # new_ded_cnt = int(result_str[DED_MSG_INDEX
                        ded_string = result_str[DED_MSG_INDEX]
                        ded_string_int = "0"
                        if (ded_string.find('\'', 0) == -1):
                            ded_string_int = ded_string
                        else :
                            ded_string_int = ded_string[:ded_string.find('\'', 0):]
                        new_ded_cnt = int(ded_string_int)


                        # ERROR CHECKING

                        # If new errors appear, set an errors flag and start to cycle through
                        # recovery methods
                        if (new_error_cnt > 0 or new_sec_cnt > 0 or new_ded_cnt > 0):

                            # Set the flag, let user know program has detected errors
                            if (dram_errors_flag == 0):
                                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Errors detected")
                                logging.info("Errors detected")
                                dram_errors_flag = 1

                            # Boolean to detect if errors have maxed out
                            errors_max_out = (new_error_cnt >= MAX_ERROR_CNT or 
                            new_sec_cnt >= MAX_ERROR_CNT or
                            new_ded_cnt >= MAX_ERROR_CNT)

                            # First, if errors max out, start recovery cycle
                            if (errors_max_out):
                                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Error max out" if errors_max_out else "")
                                logging.info("Error max out")
                                mem_error_timer = 0
                                pause_error_timer = 0
                                cnt_error_max += 1

                            # Also start recovery cycle if after a long period of counting errors, they do not stop.
                            elif ((old_error_cnt < new_error_cnt) or (old_sec_cnt < new_sec_cnt) or (old_ded_cnt < new_ded_cnt)):

                                # Reset number of cycles to run bist
                                if (errors_currently_counting == False):
                                    errors_currently_counting = True
                                    mem_error_timer = 0
                                    pause_error_timer = 0

                                mem_error_timer += 1
                                
                                

                            # Come here if errors no longer incrementing. Wait a few cycles if errors stop after a bit.
                            # See if they truly stop incrementing, then restart bist.
                            else:
                                # Reset number of cycles to run bist
                                if (errors_currently_counting == True):
                                    errors_currently_counting = False
                                    mem_error_timer = 0
                                    pause_error_timer = 0

                                pause_error_timer += 1
                                
                            # Go through recovery cycle if Bist has paused too long or errors have been incrementing for too long
                            if ((pause_error_timer >= MAX_PAUSE_ERROR_CNT_CYCLES) or (mem_error_timer >= MAX_ERROR_CNT_CYCLES)):
                                mem_error_timer = 0
                                pause_error_timer = 0
                                cnt_error_max += 1
                        
                        # If no errors detected, reset recovery cycle and timers
                        else:
                            mem_error_timer = 0
                            pause_error_timer = 0
                            degree_of_max_error = 0
                            dram_errors_flag = 0

                        old_error_cnt = new_error_cnt
                        old_sec_cnt = new_sec_cnt
                        old_ded_cnt = new_ded_cnt


                        # Errors occur, recalibrate DRAM. Happens again right after, reinit dram,
                        # then if it keeps happening, progressivly go down: reset dram, reload bitstream, then
                        # repower board.
                        if (cnt_error_max > 0):

                            # Keep track of which action to take.
                            # If an instance occurs where errors max out, but not as fast, 
                            # this variable will be set to zero.
                            degree_of_max_error += 1
                            
                            # Stop bist running before doing anything.
                            boardcontroller.quit_bist()

                            # First restart bist
                            if (degree_of_max_error == 1):
                                # Do nothing, just restart bist
                                pass

                            # Next scrub delay registers
                            elif (degree_of_max_error == 2):
                                boardcontroller.dram_delay_register_scrub_cmd()

                            # Next scrub mode registers 
                            elif (degree_of_max_error == 3):
                                boardcontroller.dram_mode_register_scrub_cmd()

                            # Next recalibrate DRAM
                            elif (degree_of_max_error == 4):
                                boardcontroller.dram_calibrate()

                            # Next init and recalibrate DRAM
                            elif (degree_of_max_error == 5):
                                boardcontroller.dram_init_and_calibrate()

                            # Next restart Litex and processor
                            elif (degree_of_max_error == 6):
                                boardcontroller.reset_litex()

                            # Next reconfigure board
                            elif (degree_of_max_error == 7):
                                boardcontroller.reset_board()
                                fault_injector_timer = FAULT_TIMER_MAX

                            # Finally repower board
                            elif (degree_of_max_error >= 8):
                                boardcontroller.repower_board()
                                break
                            
                            # # Turn off error injector
                            # boardcontroller.c.sendline('mem_write 0xf0003810 0x00 4')
                            # boardcontroller.c.expect(pattern="^.*litex[^>]*> ")
                            
                            # Once all is said and done (except for a repower_board event),
                            # restart and run the bist
                            cnt_error_max = 0
                            boardcontroller.run_bist(args.mem_burst_length, args.addr_mode)
                
                    
                    elif match_index == 2:
                        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] String output not expected")
                        logging.info("String output not expected")
                        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] String sent to be matched: ", boardcontroller.c.match.string)
                        logging.info("String sent to be matched: ", boardcontroller.c.match.string)
                        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] String matched: ", boardcontroller.c.match.group(0))
                        logging.info("String matched: ", boardcontroller.c.match.group(0))

                else:

                    print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] No match found")

            # Respawn if timeout exception is thrown
            except pexpect.exceptions.TIMEOUT:

                # Correct fault before doing anything
                boardcontroller.correct_jcm_fault()

                # logging.error(traceback.format_exc())
                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Timeout occured. Attempting to close, reopen Litex.")
                logging.info("Timeout occured. Attempting to close, reopen Litex.")
                if not boardcontroller.quit_bist() and not boardcontroller.reset_litex():
                    logging.info("Failed closing, reopening Litex, configuring board.")
                    print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Failed closing, reopening Litex, configuring board.")
                    if not boardcontroller.reset_board():

                        # If board is to be repowered, break second loop to go back 
                        # to beginning init sequence. (Dev port may change)
                        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Resetting Litex unsuccessful, repowering board.")
                        logging.info("Resetting Litex unsuccessful, repowering board.")
                        boardcontroller.repower_board()
                        break

                boardcontroller.run_bist(args.mem_burst_length, args.addr_mode)

            # EOF exception will occur if board is unplugged
            except pexpect.exceptions.EOF:
                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] End Of File Exception occured. Repowering board.")
                logging.info("End Of File Exception occured.")
                boardcontroller.repower_board()
                break

            except UnicodeDecodeError:
                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] UnicodeDecodeError, retrying.")
                logging.info("UnicodeDecodeError, retrying")
                continue

            except Exception:
                # logging.info("Other Exception occured, traceback: ")
                # logging.error(traceback.format_exc())
                logging.info("Unknown Exception occured")
                logging.info("Resetting Litex. \nTime: ", datetime.now().time())
                print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Other Exception occured, resetting Litex.")
                if not boardcontroller.reset_litex():
                    if not boardcontroller.reset_board():

                        # If board is to be repowered, break second loop to go back 
                        # to beginning init sequence. (Dev port may change)
                        print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Resetting Litex unsuccessful, repowering board.")
                        logging.info("Resetting Litex unsuccessful, repowering board.")
                        boardcontroller.repower_board()
                        break

                boardcontroller.run_bist(args.mem_burst_length, args.addr_mode)



    # If code reaches here, board is not plugged in, give up.
    print("[", time.strftime("%Y-%m-%d %H:%M:%S"), "] Board not plugged in, giving up.")
    logging.info("Board not plugged in, giving up.")



if __name__ == "__main__":
    main()

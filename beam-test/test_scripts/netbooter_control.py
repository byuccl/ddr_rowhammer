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

class netbooter_control():
    '''
    Provides basic control of netbooter operation.

    netbooter_ip_addr: IP address of netbooter (string)
    logging: The logger used for netbooter messages

    Netbooter commands:

Escape character is '^]'.

Synaccess Inc. Telnet V6.2
>
>help
ip     Sets static IP "ip x.x.x.x"
gw      Sets gateway IP
mask    Sets mask
dhcp v  Sets IP to static/DHCP(0/1)
emailsend Sends a test mail
hp      Sets HTTP port#
tp      Sets TELNET port#
help
ipsrc   Sets filtered source IP "ipsrc x.x.x.x"
login
logout
mac     Shows Mac address
nwset   Resets nw interface
nwshow  Shows network Status
lc      Outlet ON/OFF loop control. See Help in web
ping    Pings a host
pset n v  Sets outlet #n to v(0 or 1)
gpset n v Sets outlet group #n to v(0 or 1)
ps v    Sets all outlets to v(0 or 1)
pshow   Shows outlet status
reset   Resets to defaults
rb n    Reboots outlet #n
grb n   Reboots outlet group #n
sysshow Shows Sys info
time
ver     Shows version
web v   Sets Web access ON/OFF(1/0)
>    

    '''

    # Netbooter constants
    TIMEOUT_NETBOOTER = 3.0
    NETBOOTER_LOGGING_PREFIX = "NETBOOTER:"
    SLEEPTIME_NETBOOTER = 1 # Time between creating connected instance of Telnet,
                        # turning board off, then on again.
    DEFAULT_NETBOOTER_IP = "169.254.131.160"
    SYNACCESS_PROMPT = b'\r\n>'
    # The time to delay after issuing a command
    NETBOOTER_COMMAND_DELAY = 0.1


    def __init__(self, 
        netbooter_ip_addr:str = DEFAULT_NETBOOTER_IP, 
        logging = None):
        self.netbooter_ip_addr = netbooter_ip_addr
        self.logging = logging
        # Reference to open telnet object. 'None' if it is closed.
        self.teln = None

    def _info(self, str):
        ''' Send an 'info' message to the logger. '''
        if self.logging:
            self.logging.info(self.NETBOOTER_LOGGING_PREFIX+str)

    def _error(self, str):
        ''' Send an 'error' message to the logger. '''
        if self.logging:
            self.logging.error(self.NETBOOTER_LOGGING_PREFIX+str)


    def ping_netbooter(self):
        command = ['ping', "-c", '1', self.netbooter_ip_addr]
        sys.stdout.flush()
        return subprocess.call(command) == 0

    def open_telnet(self):
        ''' Open the telnet connection to the netbooter.
             return True if it opened correctly, False otherwise
        '''
        # Check to see if the telnet is already open
        if self.teln:
            return True
        # If it is not open, attempt to open it
        try:
            self.teln = telnetlib.Telnet(self.netbooter_ip_addr, timeout=self.TIMEOUT_NETBOOTER)
        except (Exception) as error:
            self._error("Error opening telnet"+str(error))
            self.teln = None
            return False
        return True

    def open_telnet_attempts(self, attempts=1, sleep = 1):
        ''' Multiple attempts to open telnet. '''
        # Attempt command multile times
        for attempt in range(attempts):
            self._info(f"Attempt {(attempt+1)} to open telnet port")
            if self.open_telnet():
                return True
            time.sleep(sleep)
        return False

    def wait_for_prompt(self,timeout=5):
        ''' Waits until the telnet prompt shows up.
        Returns data that was received if prompt was found, None otherwise.
        '''
        # Check to see if the telnet is open
        if self.teln == None:
            return None
        try:
            result = self.teln.read_until(self.SYNACCESS_PROMPT,timeout=timeout)
        except EOFError:
            return None
        result_str = result.decode("utf-8")            
        #print(result,result_str)
        if self.SYNACCESS_PROMPT.decode("utf-8") in result_str:
            # Always wait after doing a read
            time.sleep(netbooter_control.NETBOOTER_COMMAND_DELAY)
            return result_str
        return None

    def close_telnet(self):
        ''' Close telnet connection '''
        if self.teln:
            self.teln.close()
        self.teln = None

    def write_telnet(self, write_str:str):
        ''' write telnet connection '''
        if not self.teln:
            return False
        try:
            self.teln.write(write_str)
        except Exception as error: # EOFException?
            self._error("Error Writing to telnet "+str(error))
            return False
        # Add delay after command
        time.sleep(netbooter_control.NETBOOTER_COMMAND_DELAY)
        return True

    def read_telnet(self):
        ''' write telnet connection '''
        if not self.teln:
            return False

        try:
            result = self.teln.read_some()
        except (Exception) as error:
            # try again (close?)
            #print("Did not read_some")
            return None

        return result

    def _generate_control_string(self,command):
        ''' Generate a control string for a command '''
        s = command.encode("ascii") + b"\r\n"
        return s


    def _control_string(self,power_port,turn_on):
        ''' Generate a control string for the port/function '''
        if turn_on:
            power_state = "1"
        else:
            power_state = "0"
        s = ("pset " + str(power_port) + " " + power_state).encode("ascii") + b"\r\n\r\n"
        return s

    def control_port(self, power_port, turn_on = True, cycle=False, sleep=1, attempts = 5):
        '''
        Perform actual command to the port.
        '''
        if not turn_on:
            new_state = "Off"
            inverted_state = "On"
        else:
            new_state = "On"
            inverted_state = "Off"

        # Attempt command multile times
        for attempt in range(attempts):
            self._info(f"Attempt {(attempt+1)} to set port {power_port} with cycle={cycle}")

            # Open telnet
            #if not self.telnet_open:
            if not self.teln:
                if not self.open_telnet():
                    # Try again
                    continue
            # Opened: wait a bit before communicating
            time.sleep(sleep)

            # Read netbooter port to clear buffer
            try:
                self.teln.read_some()
            except (Exception) as error:
                # try again (close?)
                #print("Did not read_some")
                continue
            time.sleep(sleep)

            if cycle:
                s = ("pset " + str(power_port) + " 0").encode("ascii") + b"\r\n\r\n"
                # Do the opposite of what is wanted (for cycle)
                if not self.write_telnet(self._control_string(power_port, not turn_on)):
                    # Failed write, continue to try again
                    ##print("Failed write cycle")
                    continue
                self._info("Setting port "+str(power_port)+" to "+inverted_state)
                time.sleep(sleep)

            control_string = self._control_string(power_port, turn_on)
            if not self.write_telnet(control_string):
                # Failed write, continue to try again
                #print("Failed write")
                continue
            self._info(str("Setting port "+str(power_port)+" to "+new_state))
            time.sleep(sleep)

            # Close telnet
            self.close_telnet()
            # This succeeded
            return True

        # failed all attempts
        return False

    def send_command(self, command, open_attempts = 3):
        ''' Issues a command and returns the resulting data from the command.
        This function assumes that the telnet is closed and will perform
        an open at the start and a close at the end.

        returns None if there was a problem executing the command.
        returns a byte array of the result if the command was successful.
        '''

        # Open telnet
        if not self.open_telnet_attempts():
            return None

        # Make sure you get a prompt
        result = self.wait_for_prompt()
        if not result:
            return None
        #print("prompt:",result)        

        # Issue pshow command
        command = self._generate_control_string("pshow")
        #print(command)
        result = self.write_telnet(command)
        if not result:
            print("No result")
            return None

        # Read netbooter result
        show_result = self.wait_for_prompt()
        '''
        if show_result:
            print("Result:")
            print(show_result)
        else:
            print("Timed out")
        '''
        return show_result

    def _get_pshow_result(self):
        ''' Performs the 'pshow' command to determine the state of each port.
        Returns a dictionary object containing all of the port information.
        '''
        command = ("pshow").encode("ascii") + b"\r\n"
        result = self.send_command(self, command)
        return result

    def pshow(self):
        ''' Prints the results from the pshow command. '''
        result = self._get_pshow_result()
        #print(result)
        pshow_dict = self.parse_show_str(result)
        for i in pshow_dict.keys():
            port = pshow_dict[i]
            print(f"{int(i):2d}:{port[1]:<10} {port[2]}")
        #print(pshow_dict)
        return 

    def parse_show_str(self,pshow_result):
        ''' Function for parsing and representing the results from a pshow command. 

pshow


Port | Name       |Status| Reservation
   1 |  CTRLNexys |   ON |
   2 |    CTRLJCM |   ON |
   3 |   DDRNexys |   ON |
   4 |     DDRJCM |   ON |
   5 |       DDR4 |   ON |

>
        '''
        # convert byte array into a string
        print(pshow_result)
        #pshow_str = pshow_result.decode("utf-8")
        pshow_str = pshow_result
        header = False
        pshow_dict = {}
        for line in pshow_str.splitlines():
            #print(line)
            # Skip empty lines
            if line == "":
                continue
            if not header:
                # Wait until the Port header line arrives
                if "Port" in line:
                    #print("Header found")
                    header = True
            else:
                # Parsing acutal ports
                #print("l:",line)
                fields = line.split("|")
                #print(fields)
                if len(fields) < 4:
                    #print("too small",fields)
                    # Done with the fields, exit
                    break
                    #continue
                # clean up white space in each line
                port_num = fields[0].strip()
                port_name = fields[1].strip()
                port_status = fields[2].strip()
                port = (port_num, port_name, port_status)
                pshow_dict[port_num] = port
                #print(port_num,port_name,port_status)
        return pshow_dict

    def turn_on_port(self, power_port, cycle=False):
        ''' Turn netbooter port on '''
        return self.control_port(power_port, True, cycle)

    def turn_off_port(self, power_port, cycle=False):
        ''' Turn netbooter port off '''
        return self.control_port(power_port, False, cycle)

    def netbooter_group_args(parser):
        ''' Static function for creating netbooter argument group '''
        jcm_arg_group = parser.add_argument_group("NETBOOTER")
        jcm_arg_group.add_argument("--netbooter_ip", help="Netbooter IP Address", 
            default = netbooter_control.DEFAULT_NETBOOTER_IP, required=False)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument_group(netbooter_control.netbooter_group_args(parser))
    parser.add_argument("--on", help="Turn on port", type=int)
    parser.add_argument("--off", help="Turn off port", type=int)
    parser.add_argument("--cycle", help="Cycle port", type=int)
    parser.add_argument("--show", help="Show status of ports", action='store_true')

    args = parser.parse_args()

    # create jcm objecT
    logging.basicConfig(level=logging.INFO)
    netbooter = netbooter_control(logging=logging)

    # Ping netbooter
    if not netbooter.ping_netbooter():
        print("Failed netbooter ping")
        return 1

    cycle = False
    if args.cycle:
        cycle = True

    if args.on:
        port = args.on
        netbooter.turn_on_port(port,cycle)

    if args.off:
        port = args.off
        netbooter.turn_off_port(port,cycle)

    if args.show:
        netbooter.pshow()

if __name__ == "__main__":
    main()

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
    '''

    # Netbooter constants
    TIMEOUT_NETBOOTER = 3.0
    NETBOOTER_LOGGING_PREFIX = "NETBOOTER:"
    SLEEPTIME_NETBOOTER = 1 # Time between creating connected instance of Telnet,
                        # turning board off, then on again.
    DEFAULT_NETBOOTER_IP = "169.254.131.160"

    def __init__(self, 
        netbooter_ip_addr:str = DEFAULT_NETBOOTER_IP, 
        logging = None):
        self.netbooter_ip_addr = netbooter_ip_addr
        self.logging = logging
        self.telnet_open = False

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
        #print("command",command)
        sys.stdout.flush()
        return subprocess.call(command) == 0

    def open_telnet(self):

        ''' Open the telnet connection to the netbooter '''
        try:
            self.teln = telnetlib.Telnet(self.netbooter_ip_addr, timeout=self.TIMEOUT_NETBOOTER)
        except (Exception) as error:
            self._error("Error opening telnet"+str(error))
            self.teln = None
            return False

        self.telnet_open = True
        return True

    def close_telnet(self):
        ''' Close telnet connection '''
        if self.teln:
            self.teln.close()
        self.telnet_open = False

    def write_telnet(self, write_str:str):
        ''' write telnet connection '''
        if not self.teln:
            return False
        try:
            self.teln.write(write_str)
        except Exception as error: # EOFException?
            self._error("Error Writing to telnet "+str(error))
            return False
        return True

    def _control_string(self,power_port,turn_on):
        ''' Generate a control string for the port/function '''
        if turn_on:
            power_state = "1"
        else:
            power_state = "0"
        s = ("pset " + str(power_port) + " " + power_state).encode("ascii") + b"\r\n\r\n"
        return s

    def control_port(self, power_port, turn_on = True, cycle=False):

        if not turn_on:
            new_state = "Off"
            inverted_state = "On"
        else:
            new_state = "On"
            inverted_state = "Off"

        # Attempt command multile times
        CONTROL_PORT_ATTEMPTS = 5
        for attempt in range(CONTROL_PORT_ATTEMPTS):
            self._info(f"Attempt {(attempt+1)} to set port {power_port} with cycle={cycle}")

            # Open telnet
            if not self.telnet_open:
                if not self.open_telnet():
                    # Try again
                    continue
            # Opened: wait a bit before communicating
            time.sleep(1)

            # Read netbooter port to clear buffer
            try:
                self.teln.read_some()
            except (Exception) as error:
                # try again (close?)
                #print("Did not read_some")
                continue
            time.sleep(self.SLEEPTIME_NETBOOTER)

            if cycle:
                s = ("pset " + str(power_port) + " 0").encode("ascii") + b"\r\n\r\n"
                # Do the opposite of what is wanted (for cycle)
                if not self.write_telnet(self._control_string(power_port, not turn_on)):
                    # Failed write, continue to try again
                    ##print("Failed write cycle")
                    continue
                self._info("Setting port "+str(power_port)+" to "+inverted_state)
                time.sleep(self.SLEEPTIME_NETBOOTER)

            control_string = self._control_string(power_port, turn_on)
            if not self.write_telnet(control_string):
                # Failed write, continue to try again
                #print("Failed write")
                continue
            self._info(str("Setting port "+str(power_port)+" to "+new_state))
            time.sleep(self.SLEEPTIME_NETBOOTER)

            # Close telnet
            self.close_telnet()
            # This succeeded
            return True

        # failed all attempts
        return False


    def turn_on_port(self, power_port):
        ''' Turn netbooter port on '''
        return self.control_port(power_port, True)

    def turn_off_port(self, power_port):
        ''' Turn netbooter port off '''
        return self.control_port(power_port, False)

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

    args = parser.parse_args()

    # create jcm objecT
    logging.basicConfig(level=logging.INFO)
    netbooter = netbooter_control(logging=logging)

    # Ping netbooter
    if not netbooter.ping_netbooter():
        print("Failed netbooter ping")
        return 1

    if args.on:
        port = args.on
        netbooter.turn_on_port(port)

    if args.off:
        port = args.off
        netbooter.turn_off_port(port)

if __name__ == "__main__":
    main()

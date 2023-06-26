#!/usr/bin/env python3

import argparse
import logging
import socket
import traceback
import re
import os
import random
import threading
import sys
import time
import telnetlib
import subprocess
from pdu.netbooter import Netbooter
from pdu.lindy import Lindy



STANDARD_TELNET_PORT = 23
NETBOOTER_LOGGING_PREFIX = "NETBOOTER:"
LINDY_LOGGING_PREFIX = "LINDY:"
DEFAULT_NETBOOTER_IP = "169.254.131.160"
DEFAULT_LINDY_IP = "169.254.132.210"
STARTING_PORT = 1
NUM_NETBOOTER_PORTS = 5
NUM_LINDY_PORTS = 8
DATABOARD_PORT_DEFAULT = 8
NEXYS4DDR_PORT_DEFAULT = 2
NEXYSVIDEO_PORT_DEFAULT = 1
DEFAULT_LINDY_DELAY_SEC = 5





class lindy_control():

#     Provides basic control of lindy operation.

#     lindy_ip_addr: IP address of lindy (string)
#     logging: The logger used for lindy messages

    def __init__(self, 
        lindy_ip_addr:str = DEFAULT_LINDY_IP, 
        logging = None):

        '''Initialize logger and lindy with ip address and telnet standard port'''
        self.logging = logging
        self.lindy_ctrl = Lindy(ip_address = lindy_ip_addr, port = STANDARD_TELNET_PORT)
        self.antmicro_databoard_port = DATABOARD_PORT_DEFAULT
        self.nexys4ddr_port = NEXYS4DDR_PORT_DEFAULT
        self.nexysvideo_port = NEXYSVIDEO_PORT_DEFAULT


    def _info(self, str):

        ''' Send an 'info' message to the logger. '''
        if self.logging:
            self.logging.info(LINDY_LOGGING_PREFIX+str)


    def _error(self, str):

        ''' Send an 'error' message to the logger. '''
        if self.logging:
            self.logging.error(LINDY_LOGGING_PREFIX+str)


    def ping_lindy(self):
        
        '''Check that we can ping ip address of lindy'''
        command = ['ping', "-c", '1', self.lindy_ctrl.ip_address]
        sys.stdout.flush()
        return subprocess.call(command) == 0


    def turn_on_port(self, power_port, cycle=False):

        '''
        Turn on a lindy port, return true if connection succeeded.
        If cycle is high, also do opposite of port request 
        (ex: turn on port, then turn off)
        '''
        self._info("Turning lindy port {port_num} on, cycle: {cycle}, ip addr={addr}".format(port_num = power_port, cycle = cycle, addr = self.lindy_ctrl.ip_address))
        if (power_port < STARTING_PORT or power_port > NUM_LINDY_PORTS):
            self._error("Failed to find lindy port")
            return False
        try:
            self.lindy_ctrl.on(power_port)
        except socket.timeout:
            self._error("Socket timed out connecting to lindy")
            return False
        self._info("Lindy port {port_num} turned on".format(port_num = power_port))

        if cycle:
            try:
                self.lindy_ctrl.off(power_port)
            except socket.timeout:
                self._error("Socket timed out connecting to lindy")
                return False
            self._info("Lindy port {port_num} turned off".format(port_num = power_port))

        return True
        

    def turn_off_port(self, power_port, cycle=False):

        '''
        Turn off a lindy port, return true if connection succeeded
        If cycle is high, also do opposite of port request 
        (ex: turn off port, then turn on)
        '''
        self._info("Turning lindy port {port_num} off, cycle: {cycle}, ip addr={addr}".format(port_num = power_port, cycle = cycle, addr = self.lindy_ctrl.ip_address))
        if (power_port < STARTING_PORT or power_port > NUM_LINDY_PORTS):
            self._error("Failed to find lindy port")
            return False
        try:
            self.lindy_ctrl.off(power_port)
        except socket.timeout:
            self._error("Socket timed out connecting to lindy")
            return False
        self._info("Lindy port {port_num} turned off".format(port_num = power_port))

        if cycle:
            try:
                self.lindy_ctrl.on(power_port)
            except socket.timeout:
                self._error("Socket timed out connecting to lindy")
                return False
            self._info("Lindy port {port_num} turned on".format(port_num = power_port))
        return True
    

    def pshow(self):

        '''Print organized string showing status of ports'''
        print(self.lindy_ctrl.get_status())


    def lindy_group_args(parser):

        ''' Static function for creating lindy argument group '''
        jcm_arg_group = parser.add_argument_group("LINDY")
        jcm_arg_group.add_argument("--lindy_ip", help="Lindy IP Address", 
            default = DEFAULT_LINDY_IP, required=False)
        jcm_arg_group.add_argument("--lindy_delay_sec", help="Delay for lindy to start (takes longer on some ports)",
            default = DEFAULT_LINDY_DELAY_SEC, type=int, required=False)



class netbooter_control():

#     Provides basic control of netbooter operation.

#     netbooter_ip_addr: IP address of netbooter (string)
#     logging: The logger used for netbooter messages

    def __init__(self, 
        netbooter_ip_addr:str = DEFAULT_NETBOOTER_IP, 
        logging = None):

        '''Initialize logger and netbooter with ip address and telnet standard port'''
        self.logging = logging
        self.netbooter_ctrl = Netbooter(ip_address = netbooter_ip_addr, port = STANDARD_TELNET_PORT)
        self.antmicro_databoard_port = DATABOARD_PORT_DEFAULT
        self.nexys4ddr_port = NEXYS4DDR_PORT_DEFAULT
        self.nexysvideo_port = NEXYSVIDEO_PORT_DEFAULT


    def _info(self, str):

        ''' Send an 'info' message to the logger. '''
        if self.logging:
            self.logging.info(NETBOOTER_LOGGING_PREFIX+str)


    def _error(self, str):

        ''' Send an 'error' message to the logger. '''
        if self.logging:
            self.logging.error(NETBOOTER_LOGGING_PREFIX+str)


    def ping_netbooter(self):
        
        '''Check that we can ping ip address of netbooter'''
        command = ['ping', "-c", '1', self.netbooter_ctrl.ip_address]
        sys.stdout.flush()
        return subprocess.call(command) == 0


    def turn_on_port(self, power_port, cycle=False):

        '''
        Turn on a netbooter port, return true if connection succeeded.
        If cycle is high, also do opposite of port request 
        (ex: turn on port, then turn off)
        '''
        self._info("Turning netbooter port {port_num} on, cycle: {cycle}".format(port_num = power_port, cycle = cycle))
        if (power_port < STARTING_PORT or power_port > NUM_NETBOOTER_PORTS):
            self._error("Failed to find netbooter port")
            return False
        try:
            self.netbooter_ctrl.on(power_port)
        except socket.timeout:
            self._error("Socket timed out connecting to netbooter")
            return False
        self._info("Netbooter port {port_num} turned on".format(port_num = power_port))

        if cycle:
            try:
                self.netbooter_ctrl.off(power_port)
            except socket.timeout:
                self._error("Socket timed out connecting to netbooter")
                return False
            self._info("Netbooter port {port_num} turned off".format(port_num = power_port))

        return True
        

    def turn_off_port(self, power_port, cycle=False):

        '''
        Turn off a netbooter port, return true if connection succeeded
        If cycle is high, also do opposite of port request 
        (ex: turn off port, then turn on)
        '''
        self._info("Turning netbooter port {port_num} off, cycle: {cycle}".format(port_num = power_port, cycle = cycle))
        if (power_port < STARTING_PORT or power_port > NUM_NETBOOTER_PORTS):
            self._error("Failed to find netbooter port")
            return False
        try:
            self.netbooter_ctrl.off(power_port)
        except socket.timeout:
            self._error("Socket timed out connecting to netbooter")
            return False
        self._info("Netbooter port {port_num} turned off".format(port_num = power_port))

        if cycle:
            try:
                self.netbooter_ctrl.on(power_port)
            except socket.timeout:
                self._error("Socket timed out connecting to netbooter")
                return False
            self._info("Netbooter port {port_num} turned on".format(port_num = power_port))
        return True
    

    def pshow(self):

        '''Print organized string showing status of ports'''
        print(self.netbooter_ctrl.get_status())


    def netbooter_group_args(parser):

        ''' Static function for creating netbooter argument group '''
        jcm_arg_group = parser.add_argument_group("NETBOOTER")
        jcm_arg_group.add_argument("--netbooter_ip", help="Netbooter IP Address", 
            default = DEFAULT_NETBOOTER_IP, required=False)




def main():

    parser = argparse.ArgumentParser()
    parser.add_argument_group(netbooter_control.netbooter_group_args(parser))
    parser.add_argument("--on", help="Turn on port", type=int)
    parser.add_argument("--off", help="Turn off port", type=int)
    parser.add_argument("--cycle", help="Cycle port", action='store_true')
    parser.add_argument("--show", help="Show status of ports", action='store_true')

    args = parser.parse_args()

    # Create netbooter control object
    logging.basicConfig(level=logging.INFO)
    netbooter = netbooter_control(netbooter_ip_addr=args.netbooter_ip, logging=logging)

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

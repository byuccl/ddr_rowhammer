#!/usr/bin/env python3

import argparse
import logging
from datetime import date, datetime
from serial import Serial

class test_logger():
    '''
    Base class for logging functions that add a prefix to the log message
    (to distinguish one log message from another)
    '''

    def __init__(self, logger, prefix:str):
        ''' Constructor. It is possible to create an empty logger. In this case, don't log'''
        self.logging = logger
        self.prefix = prefix

    def _create_str(self, strg):
        ''' Append the logger prefix to the string. '''
        return str(self.prefix+":"+strg)

    def _info(self, strg):
        ''' Send an 'info' message to the logger. '''
        if self.logging:
            self.logging.info(self._create_str(strg))

    def _error(self, strg):
        ''' Send an 'error' message to the logger. '''
        if self.logging:
            self.logging.error(self._create_str(strg))


def main():
    logging.basicConfig(level=logging.INFO)
    l = test_logger(logging,"TEST")
    l._error("Error test")
    l._info("Info test")
    return 0

if __name__ == "__main__":
    main()

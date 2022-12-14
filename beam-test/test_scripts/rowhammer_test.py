#!/usr/bin/env python3

    # we are li
import time
import random
import argparse
import sys

from datetime import datetime

from rowhammer_tester.scripts.utils import RemoteClient, litex_server, hw_memset, hw_memtest, get_litedram_settings, read_ident

DEFAULT_PATTERN = 0xa5a5a5a5

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument('--srv', action='store_true')
    parser.add_argument('--dbg', action='store_true')
    parser.add_argument('--pattern', help="Pattern to use (hex, i.e., 0xFFFFFFFF)", type=str)
    parser.add_argument('--continuous', action='store_true')
    parser.add_argument('--iterations', type=int)
    #parser.add_argument('--test-modules', action='store_true')
    #parser.add_argument('--test-memory', action='store_true')
    args = parser.parse_args()

    #if args.srv:
    #    litex_server()

    wb = RemoteClient()
    wb.open()
    print("Board info:", read_ident(wb))

    mem_base = wb.mems.main_ram.base
    mem_range = wb.mems.main_ram.size  # bytes

    # we are limited to multiples of DMA data width
    settings = get_litedram_settings()
    dma_data_width = settings.phy.dfi_databits * settings.phy.nphases
    nbytes = dma_data_width // 8

    # pattern
    p = DEFAULT_PATTERN
    if args.pattern:
        p = int(args.pattern,16)
    print(f"Pattern=0x{p:08X}")

    # Set pattern
    print("Writing pattern")
    hw_memset(wb, 0x0, mem_range, [p], args.dbg)

    print("Starting read test")

    if args.continuous:
        iterations = sys.maxsize
    elif args.iterations:
        iterations = args.iterations
    else:
        iterations = 10

    for i in range(iterations):
        errors = hw_memtest(wb, 0x0, mem_range, [p], args.dbg)
        if len(errors) > 0:
            print('!!! Failed pattern: {:08x} !!!'.format(p))
            for e in errors:
                print(
                    'Failed: 0x{:08x} == 0x{:08x}'.format(
                        mem_base + e.offset * nbytes, wb.read(mem_base + e.offset * nbytes)))
                print('  data     = 0x{:x}'.format(e.data))
                print('  expected = 0x{:x}'.format(e.expected))
        else:
            print("Test pattern OK!")

    wb.close()

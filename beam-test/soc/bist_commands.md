# New BIST Commands for BIST Core

This document summarizes the commands for the BIST core.
_Provide a link to the forked repo with the BIST core changes and BIOS changes_.

## sdram_bist_info

This command tells user what the DRAM controller data width is in bits and the Address width in bits. 
Every instance of the LiteDDR controller may have a different data and address bit widths.
There are no arguments for this command.

Example for Nexys Video board with the DDR3:
```
litex> sdram_bist_info

Bist port address width: 25
Bist port data width: 128
```
This indicates that each controller read or write involves 128 bits (16 bytes).
The actual DDR device is 16 bits but the controller abstracts this away.
There are 25 address bits where each address is 16 bytes for a total memory size of 2<sup>25</sup> x 16 = 512 MB. 


## sdram_bist_pat

## sdram_bist_writer

## sdram_bist_reader

## sdram_bist

Put all the output examples here

Note that for this command you cant 'stop' the continuous BIST by hitting enter.

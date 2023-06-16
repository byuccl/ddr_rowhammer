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
There are 25 address bits where each address is 16 bytes for a total memory size of 2<sup>25</sup> x 2<sup>4</sup> = 2<sup>29</sup> = 512 MB. 


## sdram_bist_pat

This command sets the data pattern used for data writing and data reading.
For writes, this pattern indicates the value written to the DRAM.
For reads, this pattern indicates the value expected within the DRAM.
The command is invoked as follows: ```sdram_bist_pat <pattern>```.
There is no output for this command
The pattern is a 32-bit value entered as text hexidecimal with the leading `0x`.
Since the data width of most controllers is greater that 32-bits, the pattern will be replicated and concatenated to fill the entire DRAM controller data width.
For example, if the pattern is set to `0xa5a5a5a5` and the data width is 128-bits, then the 32-bit value will be replicated 4 times to get the full 128 bits or,
```
0xa5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5
```

Example:
```
litex> sdram_bist_pat 0xa5a5a5a5
```

## sdram_bist_writer

This command writes the previously set 'pattern' into the controller at the beginning controller address and for the given number of additional elements.
The command is invoked as follows: ```sdram_bist_writer <beginning address> <length>```.
The 'beginning address' is the first _controller_ address to write to and it is input as a hexidecimal or integer number (use the '0x' qualifier to specify a hexidecimal number).
The 'length' is the number of writes to perform **plus 1**. 
This parameter can be either hexidemcimal or integer.
The following command will write the previously set pattern to controller addresses 0x0-0x1ffffff.
```
litex> sdram_bist_writer 0x0 0x1ffffff

Put output below
```


## sdram_bist_reader

This command performs a read starting at the beginning address and for the given number of additional elements. 
The command will compare the value at each location against the previously defined pattern.
If there are errors, this command will report the errors to the console output.
The command is invoked as follows: ```sdram_bist_reader <beginning address> <length>```.
The 'beginning address' is the first _controller_ address to read from and it is input as a hexidecimal or integer number (use the '0x' qualifier to specify a hexidecimal number).
The 'length' is the number of writes to perform **plus 1**. 
This parameter can be either hexidemcimal or integer.

The following command will read the memory from addresses 0x0-0x1ffffff with no errors
```
litex> sdram_bist_reader 0x0 0x1ffffff

Put output below
```

The following command will read the memory from addresses 0xf-0x13 with errors
```
litex> sdram_bist_reader 0xf 0x4

Put output below
```




## sdram_bist

Put all the output examples here

Note that for this command you cant 'stop' the continuous BIST by hitting enter.

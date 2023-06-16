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

The number of bytes for each board is as follows:
  * Nexys4ddr: 8 bytes (64 bits)
  * Nexys Video: 16 bytes (128 bits)
  * AntMicro DRAM Tester: 64 bytes (512 bits)
  
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
The command is invoked as follows: ```sdram_bist_reader <beginning address> <length> [max errors]```.
The 'beginning address' is the first _controller_ address to read from and it is input as a hexidecimal or integer number (use the '0x' qualifier to specify a hexidecimal number).
The 'length' is the number of writes to perform **plus 1**. 
The 'max errors' is an optional argument that specifies the maximum number of errors to print. The default is 0 meaning there is not a maximum number of errors to print and all errors should be printed.
This parameter can be either hexidemcimal or integer.

The following command will read the memory from addresses 0x0-0x1ffffff with no errors
```
litex> sdram_bist_reader 0x0 0x1ffffff

Put output below
```

**Explain what the different columns of the read output are**

The following command will read the memory from addresses 0xf-0x13 with errors
```
litex> sdram_bist_reader 0xf 0x4

Put output below
```

## sdram_bist

This command performs _continuous_ write/read BIST tests on the DRAM.
This command implements the BIST test as a continuous set of atomic BIST operations until the command is stopped by pressing any key from the command line.
An atomic operation involves a write command to some number of addresses followed by a read of the same number of addresses.
The number of addresses is specified in the command line.
After performing an atomic BIST operation, a message is printed to the screen and another atomic operation is performed as specified by the command line arguments.

The command is invoked as follows: `sdram_bist <address> <length> [delay] [addr_mode] [write_mode] [max errors]`
  * The required 'address' parameter specifies the starting address for this BIST command.
  * The required 'length' parameter specifies the number of DRAM addresses to test. The actual size of address is controller specific (see `sdram_bist_info` to determine this size). 
  * The optional 'delay' parameter indicates the delay in seconds between the ending of writing/reading. The default is zero
  * The optional 'addr_mode' parameter specifies how the address is incremented after completing an atomic BIST operation (default 1)
     * 0: Run the BIST over a constant range of address. This means that _all_ BIST atomic operations occur at the same address range.
     * 1: Increment the address. This means that after each BIST atomic operation, the address register will be incremented and the next BIST operation will occur at the next address following the last BIST atomic operation. Note that with this mode, the address register will roll over back to zero if the maximum address has been reached.
  * The optional `write_mode` parameter determines how writes occur for subsequent atomic operations  (Default: 1)
     * 0: write-once-read-always mode. For 'addr_mode' 0, this will write to the constant range once and all subsequent atomic operations will be read only. For 'addr_mode' 1, this will write a value to each atomic operation until the address rolls over back to zero. At that point, no more writes will occur and the BIST will only read for each atomic operation
     * 1:  for write-read-always mode. For this mode, an atomic operation performs a write and then a read. 
  * The optional `max errors` parameter determines the maximum number of errors to print out. The default is 0 (i.e., print all errors).



Put all the output examples here


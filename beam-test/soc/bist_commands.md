# New BIST Commands for BIST Core

This document summarizes the commands for the BIST core.
_Provide a link to the forked repo with the BIST core changes and BIOS changes_.

## sdram_bist_info

This command tells the user what the DRAM controller data width is in bits and the Address width in bits. 
Every instance of the LiteDDR controller may have a different data and address bit widths.
There are no arguments for this command.

Example for Nexys Video board with the DDR3:
```
litex> sdram_bist_info

Bist port address width: 25
Bist port data width: 128

litex>
```

This indicates that each controller read or write involves 128 bits (16 bytes).
The actual DDR device is 16 bits but the controller abstracts this away.
There are 25 address bits where each address is 16 bytes for a total memory size of 2<sup>25</sup> x 2<sup>4</sup> = 2<sup>29</sup> = 512 MB. 

The number of bytes for each board is as follows:
  * Nexys4ddr: 8 bytes (64 bits)
  * Nexys Video: 16 bytes (128 bits)
  * AntMicro DRAM Tester: 64 bytes (512 bits)

Example for Antmicro Datacenter board with DDR4 RDIMM:
```
litex> sdram_bist_info   

Bist port address width: 28
Bist port data width: 512

litex>
```
  
## sdram_bist_pat

This command sets the data pattern used for data writing and data reading.
For writes, this pattern indicates the value written to the DRAM.
For reads, this pattern indicates the value expected within the DRAM.
The command is invoked as follows: ```sdram_bist_pat <pattern>```.
The pattern is a 32-bit value entered as text hexidecimal with the leading `0x`.
Since the data width of most controllers is greater that 32-bits, the pattern will be replicated and concatenated to fill the entire DRAM controller data width.
For example, if the pattern is set to `0xa5a5a5a5` and the data width is 128-bits, then the 32-bit value will be replicated 4 times to fill the full 128 bits. Ex:
```
0xa5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5
```

The output for this command is the entire pattern set with this command.

Example with the Nexys Video board:
```
litex> sdram_bist_pat 0xa5a5a5a5

Pattern set to: a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5

litex>
```


Example with the Antmicro Datacenter board:
```
litex> sdram_bist_pat 0xa5a5a5a5

Pattern set to: a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 

litex> 
```

## sdram_bist_writer

This command writes the previously set 'pattern' into the controller at the beginning controller address and for the given number of additional elements.
The command is invoked as follows: ```sdram_bist_writer <beginning address> <length>```.
The 'beginning address' is the first _controller_ address to write to and it is input as a hexidecimal or integer number (use the '0x' qualifier to specify a hexidecimal number).
The 'length' is the number of writes to perform **plus 1**. 
This parameter can be either hexidemcimal or integer.
The following command will write the previously set pattern to controller addresses 0x0-0x1ffffff. 
This example is with the Nexys Video board.
```
litex> sdram_bist_writer 0x0 0x1ffffff
DRAM controller has address width 25, data width 128 in bits
Writing from address 0 to address 1ffffff ...Done
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
    39422426            0     33554432            0             1293                0   0x0000000-0x1ffffff          0
Finishing state machine ...Done

litex>
```

**Description of relevant columns**
* **WRITE TICKS** is the number of clock cycles taken to write to all the specified addresses.
* **TOTAL WRITES** is the total number of controller transactions writing to the DRAM that have taken place, one per address.
* **WR-SPEED** takes the above 'WRITE TICKS' and 'TOTAL WRITES' and calculates the average speed of the writes in MiB/s.
* **ADDRESSES TESTED** lists a range of all the addresses written to.
* **ERRORS** is the number of errors encountered. (Always 0 for the sdram_bist_writer command, could be nonzero when reading and checking data from the bist.)

Example with the Antmicro Datacenter board:
```
litex> sdram_bist_writer 0x0 0xfffffff
DRAM controller has address width 28, data width 512 in bits
Writing from address 0 to address fffffff ...Done
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
   308980425            0    268435456            0             5282                0   0x0000000-0xfffffff          0
Finishing state machine ...Done

litex> 
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

The following command will read the memory from addresses 0x0-0x1ffffff with no errors.
This example is with the Nexys Video board.
```
litex> sdram_bist_reader 0x0 0x1ffffff
DRAM controller has address width 25, data width 128 in bits
Reading from address 0 to address 1ffffff
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
           0     38772028            0     33554432                0             1315   0x0000000-0x1ffffff          0
Finishing state machine ...Done

litex>
```

**Description of Relevant Columns**

* **READ TICKS** is the number of clock cycles taken to read all the specified addresses. 
* **TOTAL READS** is the total number of controller transactions reading from the DRAM that have taken place, one per address.
* **RD-SPEED** takes the above 'READ TICKS' and 'TOTAL READS' and calculates the average speed of the reads in MiB/s.
* **ADDRESSES TESTED** lists a range of all the addresses written to.
* **ERRORS** is the number of errors encountered. 

The following command will read the memory from addresses 0xf-0x13 with errors
```
litex> sdram_bist_reader 0xf 0x4

litex> sdram_bist_reader 0xf 0x4
DRAM controller has address width 25, data width 128 in bits
Reading from address f to address 13

Error address range: 0xf-0x13, Num Errors: 5, Data expected:

a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5

   ADDRESS    DATA
 0x000000f:  a5a5a5a4 a5a5a5a4 a5a5a5a4 a5a5a5a4
 0x0000010:  a5a5a5a4 a5a5a5a4 a5a5a5a4 a5a5a5a4
 0x0000011:  a5a5a5a4 a5a5a5a4 a5a5a5a4 a5a5a5a4
 0x0000012:  a5a5a5a4 a5a5a5a4 a5a5a5a4 a5a5a5a4
 0x0000013:  a5a5a5a4 a5a5a5a4 a5a5a5a4 a5a5a5a4
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
           0           22            0            5                0              345   0x000000f-0x0000013          5
Finishing state machine ...Done

litex>
```

Example with Antmicro Datacenter board and no errors:
```
litex> sdram_bist_reader 0x0 0xfffffff 0
DRAM controller has address width 28, data width 512 in bits
Reading from address 0 to address fffffff
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
           0    303394983            0    268435456                0             5379   0x0000000-0xfffffff          0
Finishing state machine ...Done

litex> 
```

Example with Antmicro Datacenter board and a few errors:
```
litex> sdram_bist_reader 0x0 0xfffffff 0
DRAM controller has address width 28, data width 512 in bits
Reading from address 0 to address fffffff

Error address range: 0x4-0xccccc, Num Errors: 5, Data expected: 

a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 

   ADDRESS    DATA
 0x0000004:  66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 
 0x00000ff:  66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 
 0x0000eee:  66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 
 0x000dddd:  66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 
 0x00ccccc:  66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 66666666 
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
           0    303394988            0    268435456                0             5379   0x0000000-0xfffffff          5
Finishing state machine ...Done

litex>
```

Example with Antmicro Datacenter board with all errors, but only print a few
```
litex> sdram_bist_reader 0x0 0xfffffff 4
DRAM controller has address width 28, data width 512 in bits
Reading from address 0 to address fffffff

Error address range: 0x0-0xfffffff, Num Errors: 268435456, Data expected: 

99999999 99999999 99999999 99999999 99999999 99999999 99999999 99999999 99999999 99999999 99999999 99999999 99999999 99999999 99999999 99999999 

   ADDRESS    DATA
 0x0000000:  a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 
 0x0000001:  a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 
 0x0000002:  a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 
 0x0000003:  a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
           0    303394982            0    268435456                0             5379   0x0000000-0xfffffff  268435456
Finishing state machine ...Done

litex> 
```

## sdram_bist

This command performs _continuous_ write/read BIST tests on the DRAM.
This command implements the BIST test as a continuous set of atomic BIST operations until the command is stopped by pressing any key from the command line.
An atomic operation involves a write command to some number of addresses followed by a read of the same number of addresses.
The number of addresses is specified in the command line.
After performing an atomic BIST operation, a message is printed to the screen and another atomic operation is performed as specified by the command line arguments.

The command is invoked as follows: `sdram_bist <base> <length> [max errors] [addr_mode] [write_mode] [error_break] [delay]`
  * The required 'base' parameter specifies the starting address for this BIST command.
  * The required 'length' parameter specifies the number of DRAM addresses to test. The actual size of address is controller specific (see `sdram_bist_info` to determine this size).
  * The optional `max errors` parameter determines the maximum number of errors to print out. The default is 0 (i.e., print all errors).
  * The optional 'addr_mode' parameter specifies how the address is incremented after completing an atomic BIST operation (default 1)
     * 0: Run the BIST over a constant range of address. This means that _all_ BIST atomic operations occur at the same address range.
     * 1: Increment the address. This means that after each BIST atomic operation, the address register will be incremented and the next BIST operation will occur at the next address following the last BIST atomic operation. Note that with this mode, the address register will roll over back to zero if the maximum address has been reached.
  * The optional `write_mode` parameter determines how writes occur for subsequent atomic operations  (Default: 1)
     * 0: read-always mode. For 'addr_mode' 0, this will write to the constant range once and all subsequent atomic operations will be read only. 
     * 1: write_once_read_always mode. For 'addr_mode' 1, this will write a value to each atomic operation until the address rolls over back to zero. At that point, no more writes will occur and the BIST will only read for each atomic operation
     * 2: write-read-always mode. For this mode, an atomic operation performs a write and then a read.
  * The optional 'error_break' parameter, if set high, will stop the BIST if errors are found. The default value is zero.
  * The optional 'delay' parameter indicates the delay in seconds between the ending of writing/reading. The default is zero.

Example with Nexys Video board with addr_mode = 1 and write_mode = 1 with no errors.
```
litex> sdram_bist 0x0 0x1ffffff 0 1 1 
DRAM controller has address width 25, data width 128 in bits
Starting Bist with length 33554431, address mode 1, wmode 1 at clock frequency 100000000
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
    39422414     38772036     33554432     33554432             1293             1315   0x0000000-0x1ffffff          0
           0     38772028            0     33554432                0             1315   0x0000000-0x1ffffff          0
           0     38771971            0     33554432                0             1315   0x0000000-0x1ffffff          0
           0     38771971            0     33554432                0             1315   0x0000000-0x1ffffff          0
           0     38771984            0     33554432                0             1315   0x0000000-0x1ffffff          0
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          0
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          0
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          0
           0     38771971            0     33554432                0             1315   0x0000000-0x1ffffff          0
           0     38771965            0     33554432                0             1315   0x0000000-0x1ffffff          0
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
           0     38772000            0     33554432                0             1315   0x0000000-0x1ffffff          0
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          0
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          0
           0     38772030            0     33554432                0             1315   0x0000000-0x1ffffff          0

litex> 
```

Example with Nexys Video board with addr_mode = 1 and write_mode = 1 with a few errors.
```
litex> sdram_bist 0x0 0x1ffffff 0 1 0 0
DRAM controller has address width 25, data width 128 in bits
Starting Bist with length 33554431, address mode 1, wmode 0 at clock frequency 100000000
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS

Error address range: 0x0-0x1ffffff, Num Errors: 6, Data expected:

a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5
   ADDRESS    DATA
 0x0000000:         0        0        0        0
 0x0000001:         0        0        0        0
 0x0000002:         0        0        0        0
 0x1fffffd:         0        0        0        0
 0x1fffffe:         0        0        0        0
 0x1ffffff:         0        0        0        0
    39422485     38771967     33554432     33554432             1293             1315   0x0000000-0x1ffffff          6
    39422418     38772036     33554432     33554432             1293             1315   0x0000000-0x1ffffff          6
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38771965            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38771965            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38771966            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38771966            0     33554432                0             1315   0x0000000-0x1ffffff          6
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
           0     38772028            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38771971            0     33554432                0             1315   0x0000000-0x1ffffff          6

litex>
```

**NOTE:** When the BIST reads errors, it will automatically write in the range of addresses where it saw the errors. 
The BIST can be stopped if a user presses a key. Optionally, the BIST can also be stopped by setting the 'error_break' argument high.
When errors are found, a line will print the range of addresses where the errors were found, the number of errors, the data expected, and lastly a column of addresses and data containing the errors. 


Example with Nexys Video board with addr_mode = 1 and write_mode = 1 with limited errors.
```
litex> sdram_bist 0x0 0x1ffffff 4 1 1 
DRAM controller has address width 25, data width 128 in bits
Starting Bist with length 33554431, address mode 1, wmode 1 at clock frequency 100000000
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS

Error address range: 0x0-0x1ffffff, Num Errors: 6, Data expected: 

88888888 88888888 88888888 88888888 

   ADDRESS    DATA
 0x0000000:         0        0        0        0 
 0x0000001:         0        0        0        0 
 0x0000002:         0        0        0        0 
 0x1fffffd:         0        0        0        0 
    39422479     38771967     33554432     33554432             1293             1315   0x0000000-0x1ffffff          6
    39422426     38772030     33554432     33554432             1293             1315   0x0000000-0x1ffffff          6
           0     38772016            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38772029            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38772028            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38771965            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38771971            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38772028            0     33554432                0             1315   0x0000000-0x1ffffff          6
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
           0     38772028            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38772034            0     33554432                0             1315   0x0000000-0x1ffffff          6
           0     38771971            0     33554432                0             1315   0x0000000-0x1ffffff          6

litex>
```

Example with Antmicro Datacenter board, addr_mode = 0 and write_mode = 1
```
litex> sdram_bist 0x0 0xfffffff 0 0 1 0
DRAM controller has address width 28, data width 512 in bits
Starting Bist with length 268435455, address mode 0, wmode 0 at clock frequency 100000000
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
   308980437    303394989    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
           0    303394989            0    268435456                0             5379   0x0000000-0xfffffff          0
           0    303394983            0    268435456                0             5379   0x0000000-0xfffffff          0
           0    303394984            0    268435456                0             5379   0x0000000-0xfffffff          0
           0    303394984            0    268435456                0             5379   0x0000000-0xfffffff          0
           0    303394989            0    268435456                0             5379   0x0000000-0xfffffff          0
           0    303394989            0    268435456                0             5379   0x0000000-0xfffffff          0
           0    303394988            0    268435456                0             5379   0x0000000-0xfffffff          0
           0    303394988            0    268435456                0             5379   0x0000000-0xfffffff          0
           0    303394988            0    268435456                0             5379   0x0000000-0xfffffff          0
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
           0    303394988            0    268435456                0             5379   0x0000000-0xfffffff          0
           0    303394984            0    268435456                0             5379   0x0000000-0xfffffff          0

litex> 
```

Example with Antmicro Datacenter board, addr_mode = 0 and write_mode = 2
```
litex> sdram_bist 0x0 0xfffffff 0 0 2 0
DRAM controller has address width 28, data width 512 in bits
Starting Bist with length 268435455, address mode 0, wmode 1 at clock frequency 100000000
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
   308980376    303394984    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980392    303395033    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980392    303394984    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980386    303394986    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980470    303395025    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980475    303394990    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980453    303394985    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980458    303394985    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980469    303394990    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980408    303395033    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
   308980419    303394991    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980402    303394986    268435456    268435456             5282             5379   0x0000000-0xfffffff          0

litex>
```

Example with Antmicro Datacenter board, addr_mode = 1 and write_mode = 1
```
litex> sdram_bist 0x0 0xfffffff 0 1 1 0
DRAM controller has address width 28, data width 512 in bits
Starting Bist with length 268435455, address mode 1, wmode 0 at clock frequency 100000000
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
   308980442    303394984    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
           0    303394989            0    268435456                0             5379   0x0000000-0xfffffff          0
           0    303394983            0    268435456                0             5379   0x0000000-0xfffffff          0
           0    303394983            0    268435456                0             5379   0x0000000-0xfffffff          0

litex> 
litex> sdram_bist 0x0 0x0ffffff 0 1 1 0
DRAM controller has address width 28, data width 512 in bits
Starting Bist with length 16777215, address mode 1, wmode 0 at clock frequency 100000000
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
    19311304     18962185     16777216     16777216             5282             5379   0x0000000-0x0ffffff          0
    19311337     18962184     16777216     16777216             5282             5379   0x1000000-0x1ffffff          0
    19311354     18962180     16777216     16777216             5282             5379   0x2000000-0x2ffffff          0
    19311297     18962232     16777216     16777216             5282             5379   0x3000000-0x3ffffff          0
    19311337     18962186     16777216     16777216             5282             5379   0x4000000-0x4ffffff          0
    19311316     18962185     16777216     16777216             5282             5379   0x5000000-0x5ffffff          0
    19311348     18962186     16777216     16777216             5282             5379   0x6000000-0x6ffffff          0
    19311286     18962231     16777216     16777216             5282             5379   0x7000000-0x7ffffff          0
    19311332     18962180     16777216     16777216             5282             5379   0x8000000-0x8ffffff          0
    19311310     18962185     16777216     16777216             5282             5379   0x9000000-0x9ffffff          0
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
    19311343     18962185     16777216     16777216             5282             5379   0xa000000-0xaffffff          0
    19311282     18962227     16777216     16777216             5282             5379   0xb000000-0xbffffff          0
    19311342     18962184     16777216     16777216             5282             5379   0xc000000-0xcffffff          0
    19311326     18962184     16777216     16777216             5282             5379   0xd000000-0xdffffff          0
    19311305     18962180     16777216     16777216             5282             5379   0xe000000-0xeffffff          0
    19311276     18962233     16777216     16777216             5282             5379   0xf000000-0xfffffff          0
           0     18962231            0     16777216                0             5379   0x0000000-0x0ffffff          0
           0     18962184            0     16777216                0             5379   0x1000000-0x1ffffff          0
           0     18962182            0     16777216                0             5379   0x2000000-0x2ffffff          0
           0     18962182            0     16777216                0             5379   0x3000000-0x3ffffff          0
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
           0     18962182            0     16777216                0             5379   0x4000000-0x4ffffff          0
           0     18962179            0     16777216                0             5379   0x5000000-0x5ffffff          0
           0     18962231            0     16777216                0             5379   0x6000000-0x6ffffff          0
           0     18962182            0     16777216                0             5379   0x7000000-0x7ffffff          0
           0     18962179            0     16777216                0             5379   0x8000000-0x8ffffff          0

litex> 
```

Example with Antmicro Datacenter board, addr_mode = 1 and write_mode = 2
```
litex> sdram_bist 0x0 0xfffffff 0 1 2 0
DRAM controller has address width 28, data width 512 in bits
Starting Bist with length 268435455, address mode 1, wmode 1 at clock frequency 100000000
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
   308980464    303394990    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980469    303394986    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980469    303394984    268435456    268435456             5282             5379   0x0000000-0xfffffff          0
   308980419    303395033    268435456    268435456             5282             5379   0x0000000-0xfffffff          0

litex> 
litex> sdram_bist 0x0 0x0ffffff 0 1 2 0
DRAM controller has address width 28, data width 512 in bits
Starting Bist with length 16777215, address mode 1, wmode 1 at clock frequency 100000000
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
    19311249     18962226     16777216     16777216             5282             5379   0x0000000-0x0ffffff          0
    19311270     18962231     16777216     16777216             5282             5379   0x1000000-0x1ffffff          0
    19311331     18962185     16777216     16777216             5282             5379   0x2000000-0x2ffffff          0
    19311304     18962181     16777216     16777216             5282             5379   0x3000000-0x3ffffff          0
    19311342     18962184     16777216     16777216             5282             5379   0x4000000-0x4ffffff          0
    19311260     18962227     16777216     16777216             5282             5379   0x5000000-0x5ffffff          0
    19311354     18962232     16777216     16777216             5282             5379   0x6000000-0x6ffffff          0
    19311321     18962184     16777216     16777216             5282             5379   0x7000000-0x7ffffff          0
    19311348     18962184     16777216     16777216             5282             5379   0x8000000-0x8ffffff          0
    19311292     18962227     16777216     16777216             5282             5379   0x9000000-0x9ffffff          0
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
    19311283     18962231     16777216     16777216             5282             5379   0xa000000-0xaffffff          0
    19311332     18962185     16777216     16777216             5282             5379   0xb000000-0xbffffff          0
    19311310     18962185     16777216     16777216             5282             5379   0xc000000-0xcffffff          0
    19311287     18962229     16777216     16777216             5282             5379   0xd000000-0xdffffff          0
    19311286     18962231     16777216     16777216             5282             5379   0xe000000-0xeffffff          0
    19311326     18962185     16777216     16777216             5282             5379   0xf000000-0xfffffff          0
    19311310     18962185     16777216     16777216             5282             5379   0x0000000-0x0ffffff          0
    19311249     18962233     16777216     16777216             5282             5379   0x1000000-0x1ffffff          0
    19311310     18962228     16777216     16777216             5282             5379   0x2000000-0x2ffffff          0
    19311348     18962184     16777216     16777216             5282             5379   0x3000000-0x3ffffff          0
 WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
    19311347     18962186     16777216     16777216             5282             5379   0x4000000-0x4ffffff          0

litex>
```

# Rowhammer Tests with the Nexys4ddr, Nexys Video, Antmicro fpga boards

This file summarizes the rowhammer experiments.

Here is a [link to the wiki page](https://github.com/byuccl/ddr_rowhammer/wiki/Instructions-to-Setup-the-rowhammer-tester) on the ddr_rowhammer repository that explains how to set up our rowhammer project.
Also, here is a [link to the fork](https://github.com/byuccl/rowhammer-tester/) which the instructions show how to install.

The goal of this experiment was to find bits on the DRAM modules that are vulnerable to the rowhammer effect.

## Row Hammer Attack Summary

To decrease the cost-per-bit of memory, DRAM cells over time have been placed closer together in the same area and have decreased in size. 
Unfortunately, cells are more likely to experience disturbance or interference from outside neighbouring cell operations. 
Particularly, the voltage stored in a cell may decrease or increase as a result of neighbouring cell accesses, so much so that the intended bit value in the cell flips.
The Row Hammer effect refers to any pattern or technique of cell accesses which results in this effect, where multiple accesses on a row of cells in the DRAM is referred to as a "row hammer event". 

## Our Method of Row Hammer Attack

The Antmicro "rowhammer-tester" is a project written in the migen HDL that takes advantage of the [Litex SoC](https://github.com/enjoy-digital/litex) and its [DRAM controller LiteDRAM](https://github.com/enjoy-digital/litedram) to use the row hammer effect on the DRAM of an fpga. 
It first fills the DRAM device with data of a certain pattern, hammers rows with data of a certain pattern, and then reads the entire memory for errors. 

To run the rowhammer tester, we followed their instructions for creating the project and the bitstream. 
[Here are instructions for the arty board.](https://github.com/antmicro/rowhammer-tester/blob/main/docs/source/arty.md) 
Generally they are the same for each board we test, but with different names for the ```TARGET``` makefile variable.

The command we used mainly is this: 

```
python hw_rowhammer.py --read_count 10e6 --pattern all_0 --all-rows --start-row 0 --nrows 8192 --bank 0 --log-dir <directory to place log> --no-refresh
```

The arguments are as follows:
* ```--read_count```: The number of reads in one rowhammer test.
  Antmicro says the following about this argument: "The number of reads in one pass is divided equally between hammered rows.
  If a user specifies ```--read_count 1000```, then each row will be hammered 500 times.
* ```--pattern```: An argument specifying the pattern that the memory will initially be filled with.
  The input ```all_0``` means the memory will initially fill with 0's before each rowhammer attack.
  A list of possible options for this argument [are here.](https://github.com/antmicro/rowhammer-tester/blob/main/docs/source/usage.md#patterns)
* ```--all-rows```: Specifies a certain rowhammer attack mode in which all row pairs in a specified range will be hammered.
  For this mode, the range is specified with the arguments ```--start-row``` and ```--nrows```.
  The default distance between rows is 1, so the following command ```python hw_rowhammer.py --all-rows --start-row 0 --nrows 5``` will hammer row pairs (0, 2), (1, 3), and (2, 4).
  This distance, and the distance between hammered rows can be adjusted.
  The command ```python hw_rowhammer.py --all-rows --start-row 10 --nrows 16 --row-jump 2 --row-distance 3``` will hammer row pairs (10, 13) and (12, 15).
  More attack modes are described [here.](https://github.com/antmicro/rowhammer-tester/blob/main/docs/source/usage.md#attack-modes)
* ```--bank```: The bank that is being attacked.
  By default, this is 0, but can be changed with this flag.
* ```--log-dir```: The directory where the ```error_summary.json``` file will be placed after the rowhammer tests.
  If not specified, no json file will be created.
* ```--no-refresh```: Disables refresh for the entire attack, in between memory initialization and mamory checks.
  It isn't disabled for a certain amount of time.

For a list of all the arguments and their functions provided by Antmicro, see [this document here.](https://github.com/antmicro/rowhammer-tester/blob/main/docs/source/usage.md#hammering)

The terminal output of the tester looks like this:

```
Preparing ...
WARNING: only single word patterns supported, using: 0x00000000

Filling memory with data ...
Progress: [========================================] 33554432 / 33554432 

Verifying written memory ...
Progress: [========================================] 33554432 / 33554432 (Errors: 0) 
OK

Disabling refresh ...

Running Rowhammer attacks ...
read_count: 10000000
  Iter 1 / 1 Rows = (8686, 8688), Count = 10.00M / 10.00M  

Reenabling refresh ...

Verifying attacked memory ...
Progress: [========================================] 33554432 / 33554432 (Errors: 1627) 

Bit-flips for row   513: 1
Bit-flips for row   517: 1
Bit-flips for row   522: 1
Bit-flips for row   539: 1
Bit-flips for row   543: 1
Bit-flips for row   548: 1


<Continues for a while>


Bit-flips for row 32712: 1
Bit-flips for row 32724: 1
Bit-flips for row 32736: 1
Bit-flips for row 32759: 1
Bit-flips for row 32767: 1

Preparing ...
WARNING: only single word patterns supported, using: 0x00000000

Filling memory with data ...
Progress: [========================================] 33554432 / 33554432 

Verifying written memory ...
Progress: [========================================] 33554432 / 33554432 (Errors: 0) 
OK

Disabling refresh ...

Running Rowhammer attacks ...
read_count: 10000000
  Iter 1 / 1 Rows = (8687, 8689), Count = 10.00M / 10.00M  

Reenabling refresh ...

Verifying attacked memory ...
```



Pairs of rows
What are the parameters that can be changed in a test?
* Number of times that the attacked row was accessed (read_count)
How long does it take to perform a test?


When we first started running the [rowhammer tester](https://github.com/antmicro/rowhammer-tester), we had to modify the output file to also include the bank as it included errors from all banks grouped together in rows, no way of telling which error belonged to which bank although we knew the row number.

### Timing

For the antmicro DDR4 non-irradiated board, the row hammer test took about 30 - 40 seconds for each pair (with about 380 - 640 errors each test).
For the antmicro DDR4 irradiated board, the rowhammer test took about 60 - 75 seconds for each pair (with about 950 - 1220 errors each test). 

### Output Organization

After running the rowhammer tester, a map is dumped into a json file which contains all the numbers of bits that flipped from the tested rowhammer effect. It is generated by checking all the bits against the written data. It is organized as follows:

1. The map holds only one key, the number of reads (10e6 if performing 10e6 reads on the rows being hammered), which points to a map with a first key "read count" (which points again to the number of reads) and keys to data from all the rowhammer experiments of attacking row pairs as "pair\_{}\_{}", where each number in this key represents a row being attacked.
2. Each key "pair\_{}\_{}" points to another map that first has two keys "hammer\_row\_1" and "hammer\_row\_2" (which both point to the number id of the rows being hammered) and second has the "errors_in_row" key that holds the data of all the bits that have flipped.
3. We had to reorganize the "errors_in_row" key as only the row, column, and bit numbers were being output, and not the bank.
   Our changes were made in rowhammer.py. Look for the sections of code with '###################################################'.
   The "errors_in_rows" key points to a map with bank numbers as each key. Each bank number points to a corresponding row map with row numbers as each key. Likewise, each row number points to a map with column numbers as each key. And lastly, each column number points to a list holding all the bitnumbers that have flipped during the test.

An example log from the nexys4ddr scripts is a json file with the following:


```
{
    "10000000": {
        "read_count": 10000000,
        "pair_0_2": {
            "hammer_row_1": 0,
            "hammer_row_2": 2,
            "errors_in_rows": {
                "0": {
                    "1": {
                        "48": [
                            116
                        ],
                        "64": [
                            24
                        ],
                        "192": [
                            98
                        ],
                        "232": [
                            102
                        ],
                        "264": [
                            112
                        ],
                        "328": [
                            78
                        ],
                        "344": [
                            24
                        ],
                        "360": [
                            115
                        ],
                        "376": [
                            6,
                            126
                        ],
                        "464": [
                            77
                        ],
                        "488": [
                            13
                        ],
                        "496": [
                            118
                        ],
                        "672": [
                            20,
                            111
                        ],
                        "736": [
                            44
                        ],
                        "904": [
                            4
                        ],
                        "960": [
                            62
                        ],
                        "1000": [
                            7
                        ]
                    },
                    "3": {
                        "416": [
                            87
                        ],
                        "464": [
                            125
                        ],
                        "552": [
                            93
                        ]
                    },
                    "201": {
                        "128": [
                            84
                        ]
                    },
                    "283": {
                        "528": [
                            88
                        ]
                    },
                    "366": {
                        "152": [





<Continues for a while>





                    "31899": {
                        "408": [
                            23
                        ]
                    },
                    "32035": {
                        "736": [
                            72
                        ]
                    },
                    "32069": {
                        "800": [
                            25
                        ]
                    },
                    "32247": {
                        "192": [
                            90
                        ]
                    }
                }
            }
        },
        "pair_1_3": {
            "hammer_row_1": 1,
            "hammer_row_2": 3,
            "errors_in_rows": {
                "0": {
                    "2": {
                        "256": [
                            52
                        ],
                        "592": [
                            34
                        ],
                        "656": [
                            107
                        ],
                        "696": [
                            53
                        ],
                        "760": [
                            125
                        ],
                        "768": [
                            40
                        ]
                    },
                    "4": {
                        "112": [
                            70
                        ],
                        "144": [
                            60
                        ],
                        "160": [
                            18,
                            114
                        ],
                        "168": [
                            107
                        ],
                        "232": [
                            93,
                            122
                        ],
```



The command we've been using disables the refresher, writing with pattern all 0's. These are the tests I've found so far, I believe there are more on the NUC. 

* Irradiated Nexys4ddr (#57): We have rowhammer data up to the entire bank 0 for the nexys4ddr. These are on Tyler's computer.
* Irradiated Nexys Video (BYU-ARTIX-020): We have rowhammer data up to row 12182 out of 32768 rows. These are on Tyler's computer.
* Irradiated antmicro datacenter (ddr #10): We ran the rowhammer test on this (Mem 1). The generated logs are on Rami's computer, the test was stopped at row 18143 due to the flooding, and the logs were sent to Taylor. We also ran a test on Mem 2 that reached 24486 rows, it is on Rami's computer and also on Tyler's.


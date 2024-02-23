This file summarizes all of the memory experiments we have completed.
This provides an overview of the purpose of the experiment, indicates the specific boards used in the test, a brief summary of what we have learned, and links to the actual data and analysis.

In this file, provide a summary of the various experiments that we have done from the start.
For each experiment provide the following:
* Provide a brief description of the goal of the experiemtn
* Indicate which board/memory was used for the experiment and what subset of the memory was tested
* Provide a small snippet of what the output file looks like
* Indicate where the data is currently located

# Experiment #1: December 2022 Radiation Test (Los Alamos)

The goal of this experiment was to determine the defects that occur with the DRAM from radiation.
We tested with the nexys video and antmicro datacenter boards.
The results of our experiment are summarized [here](https://github.com/byuccl/ddr_rowhammer/tree/tr-ddrh-mjw/radiation_results#radiation-experiment-feedback) and the data from the bist we ran during this test is [here](https://github.com/byuccl/ddr_rowhammer/releases/tag/lansce_Dec2022).

**TODO**: Indicate which specific boards were used for this part. Add a picture?

TODO: expand description

# Experiment #2: July 2023 ChipIR Radiation Test

The goal of this experiment was to determine the defects that occur with the DRAM from radiation, specifically if the number of errors increase as a result of the rowhammer effect and lower refresh rate, and if these errors correlate. 
We targeted the Nexys4DDR, Nexys Video, and antmicro datacenter boards.
The data from the bist we ran during this test is [here](https://github.com/byuccl/ddr_rowhammer/releases/tag/untagged-dae17d4e2af2286aa6d6). The sets of data we parsed and documented are on [this branch of the ddr_rowhammer repository.](https://github.com/byuccl/ddr_rowhammer/tree/radiation2023/radiation2023)

The summaries of the parsed data is under the radiation branch. In radiation2023 directory, you can find DDR2, DDR3, and DDR4 parse logs directories. In each one of those directories, you can find summaries about the errors, their types and some description about them under detailed summaries. The parsing script is also found under the same branch (radiation2023) and its called radiation_2023_parser.py

**TODO**: Indicate which specific boards and memory modules were used for this part. Add a picture?

TODO: expand description

# Board Experiments:

Here is a description of all the experiments we've done with each board.

## Refresh tests (Nexys4ddr, Nexys Video, Antmicro)

The goal of this experiment was to find bits easily flipped when writing to the memory, setting a specified refresh rate, waiting some time, and then checking the errors. 
We have used this on our Nexys4ddr (DDR2), Nexys Video (DDR3), and Antmicro (DDR4) boards. We created scripts called [refresh_plotter_nexys4ddr.py](https://github.com/byuccl/ddr_rowhammer/blob/refresh_change/beam-test/test_scripts/refresh_plotter_nexys4ddr.py), [refresh_plotter.py](https://github.com/byuccl/ddr_rowhammer/blob/refresh_change/beam-test/test_scripts/refresh_plotter.py) (for the nexys video board), and [refresh_plotter_antmicro.py](https://github.com/byuccl/ddr_rowhammer/blob/refresh_change/beam-test/test_scripts/refresh_plotter_antmicro.py) to run the BIST automatically and save the logs in a directory. 


**Part 1**

**TODO** Add board numbers (all six)

At first we ran the BIST on all of the boards: nexys4dr irradiated and non-irradiated, nexys video irradiated and non-irradiated, and antmicro datacenter irradiated and non-irradiated.
These were all run with a limit to the number of errors displayed (first we did 1,000, and then switched to 10,000 errors). Each test wrote and checked both data types (0's and 1's) for every bit.
We have the graphs from our presentation from these logs which show the comparison of the error count with the nexys4ddr and antmicro datacenter board from these.
Most of these have graphs showing the wait-time (time between writing data and checking it) and total errors, as at the time we changed the wait-time many times for comparison. The logs are stored in the following places:

* Non-irradiated Nexys4DDR: Data from refresh rates 7.8 us doubled till 1.00 ms, limit displaying 1000 errors (looks like it wasn't exceeded for these refresh rates) at many wait times, then data from refresh rates 2.00 ms doubled till 8 seconds, limit 10,000 errors at many wait times, then data from refresh rates 16 sec to 34.956 min, limit displaying 1000 errors: 
All these tests are stored on Tyler's computer.
* Irradiated Nexys4DDR: Data from refresh rates 7.8 us doubled till 512 ms, limit 10,000 errors at many wait times: All of these are stored on Tyler's computer.
* Non-irradiated Nexys Video: We also ran the bist on this board, I'm still looking for it but it is on the NUC.
* Irradiated Nexys Video: Data from refresh rates 7.8 us doubled till 32 ms, limit 1,000 errors at many wait times: All of these are on the NUC.
* Non-irradiated Antmicro Datacenter Board: Data from refresh rates 7.8us doubled till 32 ms, limit 10,000 errors at many wait times: these are on Tyler's computer.
* Irradiated Antmicro Datacenter Board: Data from refresh rates 7.8us doubled till 32 ms, limit 10,000 errors at many wait times: these are on the NUC.

**TODO**: Please summarze the size of the data files for these experiments.

**TODO**: Is there a way to compress the data and provide a release? Please experiment with ways of archving this data.


**Part 2**

We started doing these again, this time *recording* all the errors (waiting 5 min between the writing and the checking). 
The purpose of recording the actual errors is so that we can characterize and coralate the specific bits with row hammer testing.

**TODO** Add board numbers and explain why some boards are not being tested.

* We have data for refresh rates from 7.8us doubled till 512 ms for the irradiated nexys4ddr, as well as one time letting it sit for two hours with refresh disabled; these are on Tyler's computer.
* We have data for refresh rates from 7.8us doubled till 256ms for the irradiated nexys video board, as well as one time letting it sit for 24 hours with refresh disabled; these are on Tyler's computer.
* We have data for refresh rates from 7.8us doubled till 16ms (I believe, definitely found data up to 8ms) for the non-irradiated antmicro datacenter board as it appears; these logs are on the NUC.
* We have data for refresh rates from 7.8us doubled till 4.00 ms for the irradiated antmicro datacenter board currently; we stopped this test to run the rowhammer tester on it; the logs with the refresh tests for this board are on Tyler's computer. 

The output for the antmicro datacenter board testing 1's and testing 0's looks like this:

```
[2023-12-02 18:01:20] sdram_refresh_set 50048
[2023-12-02 18:01:20] sdram_refresh_set 50048
[2023-12-02 18:01:20] [92;1mlitex[0m> sdram_bist_pat 0xffffffff
[2023-12-02 18:01:20] sdram_bist_pat 0xffffffff
[2023-12-02 18:01:20] Pattern set to: ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:01:20] [92;1mlitex[0m> sdram_bist_writer 0x0 0xfffffff
[2023-12-02 18:01:20] sdram_bist_writer 0x0 0xfffffff
[2023-12-02 18:01:20] DRAM controller has address width 28, data width 512 in bits
[2023-12-02 18:01:23] Writing from address 0 to address fffffff ...Done
[2023-12-02 18:01:23]  WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
[2023-12-02 18:01:23]    291550789            0    268435456            0             5597                0   0x0000000-0xfffffff          0
[2023-12-02 18:01:23] [92;1mlitex[0m> sdram_refresh_set 782
[2023-12-02 18:01:23] sdram_refresh_set 782
[2023-12-02 18:01:23] [92;1mlitex[0m> sdram_bist_reader 0x0 0xfffffff 0
[2023-12-02 18:01:23] sdram_bist_reader 0x0 0xfffffff 0
[2023-12-02 18:01:23] DRAM controller has address width 28, data width 512 in bits
[2023-12-02 18:01:23] Reading from address 0 to address fffffff
[2023-12-02 18:01:26] Error address range: 0x5ac-0xfe56c20, Num Errors: 36488, Data expected: 
[2023-12-02 18:01:26] ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:01:26]    ADDRESS    DATA
[2023-12-02 18:01:26]  0x00005ac:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff fffdffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:01:26]  0x00027e2:  fffffeff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:01:26]  0x0002d5d:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff fffffff7 ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:01:26]  0x0004c8f:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff fffffdff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:01:27]  0x000552b:  ffffffff ffffffff ffffefff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:01:27]  0x00059c9:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff bfffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:01:27]  0x00068b1:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffdf ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:01:27]  0x0007626:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff fffffbff ffffffff ffffffff ffffffff


<Continues for a while>


[2023-12-02 18:09:52]  0xf7fe0cc:  fffffff7 ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:52]  0xf7fec87:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff fffffff7 ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:52]  0xf814f7c:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff fffffdff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:52]  0xf835fe4:  ffffffff fffffeff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:52]  0xf849938:  ffffffff ffffffff ffffffff ffffffff fffeffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:52]  0xf851b6a:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff fffffffe ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:52]  0xf979b78:  feffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:52]  0xf9adac6:  ffffffff ffffffff ffffffff ffffffff fffffffe ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:52]  0xf9df509:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffff7fff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:52]  0xfa2455e:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff fffffff7 ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:52]  0xfa55bbc:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff fffffff7 ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:52]  0xfa899d9:  ffffffff ffffffff ffffffff ffffffff fffff7ff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:53]  0xfd7a2ac:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff feffffff ffffffff ffffffff ffffffff ffffffff ffffffff 
[2023-12-02 18:09:53]  0xfe56c20:  ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff fffffff7 ffffffff 
[2023-12-02 18:09:53]  WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
[2023-12-02 18:09:53]            0    303394989            0    268435456                0             5379   0x0000000-0xfffffff      36488
[2023-12-02 18:09:53] [92;1mlitex[0m> sdram_refresh_set 50048
[2023-12-02 18:09:53] sdram_refresh_set 50048
[2023-12-02 18:09:53] [92;1mlitex[0m> sdram_bist_pat 0x00000000
[2023-12-02 18:09:53] sdram_bist_pat 0x00000000
[2023-12-02 18:09:53] Pattern set to:        0        0        0        0        0        0        0        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:09:53] [92;1mlitex[0m> sdram_bist_writer 0x0 0xfffffff
[2023-12-02 18:09:53] sdram_bist_writer 0x0 0xfffffff
[2023-12-02 18:09:53] DRAM controller has address width 28, data width 512 in bits
[2023-12-02 18:09:56] Writing from address 0 to address fffffff ...Done
[2023-12-02 18:09:56]  WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
[2023-12-02 18:09:56]    291550729            0    268435456            0             5597                0   0x0000000-0xfffffff          0
[2023-12-02 18:09:56] [92;1mlitex[0m> sdram_refresh_set 782
[2023-12-02 18:09:56] sdram_refresh_set 782
[2023-12-02 18:09:56] [92;1mlitex[0m> sdram_bist_reader 0x0 0xfffffff 0
[2023-12-02 18:09:56] sdram_bist_reader 0x0 0xfffffff 0
[2023-12-02 18:09:56] DRAM controller has address width 28, data width 512 in bits
[2023-12-02 18:09:56] Reading from address 0 to address fffffff
[2023-12-02 18:09:59] Error address range: 0x3566-0xfcfd950, Num Errors: 15686, Data expected: 
[2023-12-02 18:09:59]        0        0        0        0        0        0        0        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:09:59]    ADDRESS    DATA
[2023-12-02 18:09:59]  0x0003566:         0        0    80000        0        0        0        0        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:09:59]  0x00053fb:         0        0 80000000        0        0        0        0        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:09:59]  0x000bfd7:         0        0        0        0        0        0        0        0        0        0        0        0        0        0    80000        0 
[2023-12-02 18:09:59]  0x0010e56:         0        0        0        0        0        0      800        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:09:59]  0x00127f4:         0        0    80000        0        0        0        0        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:09:59]  0x00146ec:         0        0   100000        0        0        0        0        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:09:59]  0x00155d7:         0        0        0        0        0        0       80        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:09:59]  0x0018c59:         0        0        0        0        0        0   800000        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:09:59]  0x002276c:         0        0        4        0        0        0        0        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:09:59]  0x002634e:         0        0        0        0        0        0       80        0        0        0        0        0        0        0        0        0


<Continues for a while>


[2023-12-02 18:13:39]  0xf2aadcb:         0        0        0        0        0        0      800        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:13:39]  0xf2effc6:         0        0     8000        0        0        0        0        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:13:39]  0xf4ac1e1:         0        0        0        0        0        0        0        0        0        0    20000        0        0        0        0        0 
[2023-12-02 18:13:39]  0xf4e78f5:         0        0        0        0        0        0        0        0        0        0        4        0        0        0        0        0 
[2023-12-02 18:13:39]  0xf506dd8:         0        0        0        0        0        0  1000000        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:13:39]  0xf65b576:         0        0        0        0        0        0     4000        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:13:39]  0xf7090ff:         0        0        0        0        0        0        0        0        0        0        4        0        0        0        0        0 
[2023-12-02 18:13:40]  0xf762bca:         0        0        0        0        0        0        0        0        0        0        8        0        0        0        0        0 
[2023-12-02 18:13:40]  0xf8439d9:         0        0        0        0        0        0    80000        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:13:40]  0xf9b7d64:         0        0 20000000        0        0        0        0        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:13:40]  0xfac18d1:         0        0        0        0        0        0        0        0        0        0      100        0        0        0        0        0 
[2023-12-02 18:13:40]  0xfcfd950:         0        0        1        0        0        0        0        0        0        0        0        0        0        0        0        0 
[2023-12-02 18:13:40]  WRITE TICKS   READ TICKS TOTAL WRITES  TOTAL READS  WR-SPEED(MiB/s)  RD-SPEED(MiB/s)      ADDRESSES TESTED     ERRORS
[2023-12-02 18:13:40]            0    303394983            0    268435456                0             5379   0x0000000-0xfffffff      15686
```

## Rowhammer tests (Nexys4ddr, Nexys Video, Antmicro)

The goal of this experiment was to find bits on both boards vulnerable to the rowhammer effect. When we first started running the [rowhammer tester](https://github.com/antmicro/rowhammer-tester), we had to modify the output file to also include the bank as it included errors from all banks grouped together in rows, no way of telling which error belonged to which bank although we knew the row number. The command we've been using disables the refresher, writing with pattern all 0's. These are the tests I've found so far, I believe there are more on the NUC. 

* Irradiated Nexys4ddr: We have rowhammer data up to the entire bank 0 for the nexys4ddr. These are on Tyler's computer.
* Irradiated Nexys Video: We have rowhammer data up to row 12182 out of 32768 rows. These are on Tyler's computer.
* Irradiated antmicro datacenter: We are currently running the rowhammer on this (Mem 1). The generated logs are on Rami's computer. We also ran a test on Mem 2 that reached 24486 rows, it is on Rami's computer and also on Tyler's. 

The json script is organized via read_count, pair of rows attacked, and in errors_in_rows we have bank number, row number, column number, and a list of all bits that flipped in the column. An example log from the nexys4ddr scripts is a json file with the following:

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









## Logs for comparison

 - Scripts ([Nexys4ddr executable](https://github.com/byuccl/ddr_rowhammer/blob/refresh_change/beam-test/test_scripts/getAllErrorBitsFromRW_nexys4ddr.py), [Nexys Video executable](https://github.com/byuccl/ddr_rowhammer/blob/refresh_change/beam-test/test_scripts/getAllErrorBitsFromRW_nexys_video.py)) were made to compare the data between the BIST and the rowhammer tester. Currently, we have run these for the rowhammer data we have for the nexys4ddr and nexys video boards.




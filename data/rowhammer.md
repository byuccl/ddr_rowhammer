# Rowhammer Tests

This file summarizes the rowhammer experiments.

Here is a [link to the wiki page](https://github.com/byuccl/ddr_rowhammer/wiki/Instructions-to-Setup-the-rowhammer-tester) on the ddr_rowhammer repository that explains how to set up our rowhammer project.
Also, here is a [link to the fork](https://github.com/byuccl/rowhammer-tester/) which the instructions show how to install.

## Rowhammer tests (Nexys4ddr, Nexys Video, Antmicro)

The goal of this experiment was to find bits on the DRAM modules that are vulnerable to the rowhammer effect.

**Provide a summary of what rowhammer is**

**Provide a summary of the big picture of what a rowhammer test does**

Pairs of rows
What are the parameters that can be changed in a test?
* Number of times that the attacked row was accessed (read_count)
How long does it take to perform a test?


When we first started running the [rowhammer tester](https://github.com/antmicro/rowhammer-tester), we had to modify the output file to also include the bank as it included errors from all banks grouped together in rows, no way of telling which error belonged to which bank although we knew the row number.
The command we've been using disables the refresher, writing with pattern all 0's. These are the tests I've found so far, I believe there are more on the NUC. 

* Irradiated Nexys4ddr (#57): We have rowhammer data up to the entire bank 0 for the nexys4ddr. These are on Tyler's computer.
* Irradiated Nexys Video (BYU-ARTIX-020): We have rowhammer data up to row 12182 out of 32768 rows. These are on Tyler's computer.
* Irradiated antmicro datacenter (ddr #10): We ran the rowhammer test on this (Mem 1). The generated logs are on Rami's computer, the test was stopped at row 18143 due to the flooding, and the logs were sent to Taylor. We also ran a test on Mem 2 that reached 24486 rows, it is on Rami's computer and also on Tyler's. 

The json script is organized via read_count, pair of rows attacked, and in errors_in_rows we have bank number, row number, column number, and a list of all bits that flipped in the column. An example log from the nexys4ddr scripts is a json file with the following:
**Provide more detail on these parameters and results**

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


## Refresh tests (Nexys4ddr, Nexys Video, Antmicro)

The goal of this experiment was to find bits easily flipped when writing to the memory, setting a specified refresh rate, waiting some time, and then checking the errors. 
We have used this on our Nexys4ddr (DDR2), Nexys Video (DDR3), and Antmicro (DDR4) boards. We created scripts called [refresh_plotter_nexys4ddr.py](https://github.com/byuccl/ddr_rowhammer/blob/refresh_change/beam-test/test_scripts/refresh_plotter_nexys4ddr.py), [refresh_plotter.py](https://github.com/byuccl/ddr_rowhammer/blob/refresh_change/beam-test/test_scripts/refresh_plotter.py) (for the nexys video board), and [refresh_plotter_antmicro.py](https://github.com/byuccl/ddr_rowhammer/blob/refresh_change/beam-test/test_scripts/refresh_plotter_antmicro.py) to run the BIST automatically and save the logs in a directory. 


**Part 1**

**TODO** Add board numbers (all six) --> Added

At first we ran the BIST on all of the boards: nexys4dr irradiated and non-irradiated, nexys video irradiated and non-irradiated, and antmicro datacenter irradiated and non-irradiated.
These were all run with a limit to the number of errors displayed (first we did 1,000, and then switched to 10,000 errors). Each test wrote and checked both data types (0's and 1's) for every bit.
We have the graphs from our presentation from these logs which show the comparison of the error count with the nexys4ddr and antmicro datacenter board from these.
Most of these have graphs showing the wait-time (time between writing data and checking it) and total errors, as at the time we changed the wait-time many times for comparison. The logs are stored in the following places:

* Non-irradiated Nexys4DDR (DDR): Data from refresh rates 7.8 us doubled till 1.00 ms, limit displaying 1000 errors (looks like it wasn't exceeded for these refresh rates) at many wait times, then data from refresh rates 2.00 ms doubled till 8 seconds, limit 10,000 errors at many wait times, then data from refresh rates 16 sec to 34.956 min, limit displaying 1000 errors: 
All these tests are stored on Tyler's computer.
* Irradiated Nexys4DDR (#57): Data from refresh rates 7.8 us doubled till 512 ms, limit 10,000 errors at many wait times: All of these are stored on Tyler's computer.
* Non-irradiated Nexys Video (BYU-Artix7-007): We also ran the bist on this board, I'm still looking for it but it is on the NUC.
* Irradiated Nexys Video (BYU-Artix-020): Data from refresh rates 7.8 us doubled till 32 ms, limit 1,000 errors at many wait times: All of these are on the NUC.
* Non-irradiated Antmicro Datacenter Board (linux-SOC #8): Data from refresh rates 7.8us doubled till 32 ms, limit 10,000 errors at many wait times: these are on Tyler's computer.
* Irradiated Antmicro Datacenter (ddr #10): Data from refresh rates 7.8us doubled till 32 ms, limit 10,000 errors at many wait times: these are on the NUC.




**TODO**: Is there a way to compress the data and provide a release? Please experiment with ways of archiving this data.
* Rami: We can compress the data and push it to github in a release, and we can also put it on a hard-drive so that we can have it in 2 places just in case. 



**Part 2**

We started doing these again, this time *recording* all the errors (waiting 5 min between the writing and the checking). 
The purpose of recording the actual errors is so that we can characterize and correlate the specific bits with row hammer testing.

**TODO**: Please summarize the size of the data files for these experiments.
* For the non-irradiated antmicro board, there are 3 files of data: log file (9.5 GB), Writing Ones Errors (474.2 MB) and Writing Zeros Errors (3.0 GB)

**TODO** Add board numbers and explain why some boards are not being tested.

* We have data for refresh rates from 7.8us doubled till 512 ms for the irradiated nexys4ddr (#57), as well as one time letting it sit for two hours with refresh disabled; these are on Tyler's computer.
* We have data for refresh rates from 7.8us doubled till 256ms for the irradiated nexys video board (BYU-ARTIX-020), as well as one time letting it sit for 24 hours with refresh disabled; these are on Tyler's computer.
* We have data for refresh rates from 7.8us doubled till 16ms (I believe, definitely found data up to 8ms) for the non-irradiated antmicro datacenter board (linux-SOC #8 Mem 2) as it appears; these logs are on the NUC.
* We have data for refresh rates from 7.8us doubled till 4.00 ms for the irradiated antmicro datacenter board currently (ddr #10 Mem-1); we stopped this test to run the rowhammer tester on it; the logs with the refresh tests for this board are on Tyler's computer. 

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



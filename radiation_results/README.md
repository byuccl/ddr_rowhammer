# Radiation Experiment Feedback

Obtain summary of feedback for CTRL radiation experiment for the LANSCE 2022 DDR controller experiment.

## Obtain Raw Beam Logs

All data associated with the beam test is found at the beam test [release](../releases/tag/lansce_Dec2022).
The raw datafile is named [dec20.zip](../releases/download/lansce_Dec2022/dec20.zip) within the release.
Copy this file to the `./radiation_results` directory (where this file exists) and unzip it.
Unzipping these files will create a `tmp` directory that contains all of the extracted log files.


### To run:

Run ```make nontmr``` to obtain events for all non-tmr tests at once output in a text file.

Run ```make tmr``` to obtain events for all tmr tests at once output in a text file.



For events from an individual nontmr test, run ```make nontmr_(day, two digits)_(hour, two digits)_(minute, two digits)```, and for an individual tmr test, run ```make nontmr_(day, two digits)_(hour, two digits)_(minute, two digits)```

For example, to obtain the events of the tmr test on day 20, hour 8, starting at minute 5, run ```make tmr_20_08_05```


# Controller Tests

This is the test run on the NexysVideo board (using DDR3) to test the relilabiliyt of the controller (not the DRAM).
We tested two designs: TMR and non-TMR.
Unlike the Linux test completed last year with the VexRisc processor, this test is a bare betal test in which the processor does _not_ use the DDR for any of its execution.
As such failures in the DDR should not cause the processor to fail.
The goal of this test is to understand actual DDR interface failures without having to deal with failures in the processor (for the linux test failures in the DDR would cause the processor to fail).

**Organization of the DDR Memory**
The DDR3 part on this board uses a single 512 MiByte part (2^29 bytes).
The DDR controller organizes transactions as 16 bytes (2^4) (see below) so each addressable region of the memory from the BIST perspective is 2^(29-4) = 2^25 or 25 bits.
These 25 bits are organized as follows:
* The least significant seven bits are the column address ([6:0] for BIST or [10:4] for processor)
* The next three bits are the bank address ([9:7] for BIST or [13:11] for processor)
* The next 15 bits are the row address ([24:10] for BIST or [28:14] for processor)

This design was a basic VexRiscv system for the NexysVideo board with the addition of the DDR and BIST module.
The software in this design would start the BIST reading to find DRAM errors.
The software would continuously read the BIST registers and report on errors from the BIST module register counts.

The non-tmr controller test logs are named `CTRL_ddr_11_28_December_xx_2022_hh_mm_ss_xxx.log`.
The tmr controller test logs are named `CTRL_ddr_11_28_tmr_December_xx_2022_hh_mm_ss_xxx.log`.

The core used for this test is based on Dr. Scott Lloyd's system that is a modification of the original DDR BIST system.

After bootup, the processor initialiates DDR testing with the following two commands:
```
sdram_bist_pat 165
sdram_bist 8192 1 0 2
```
After executing these commands, the user interface is not used unless there is a problem with the BIST behavior.
The first command, `sdram_bist_pat`, specifies the 'byte' value that is read and written for testing.
In this case, the test uses 165 or 0xA5 as the test pattern.
The second command, `sdram_bist`, start the BIST.
The output of the processor after executing this command is:
```
Starting SDRAM BIST with length=8192, addr_mode=1, data_mode=0 wmode=2
```

The _first_ parameter specifies the number of bytes to transfer for individual reads and writes (note: this is different from the default DDR BIST system in which the address parameter specifies the number of DRAM transactions to complete for each read and write).
For this command, the value 8192 (2^13) bytes are read and written at a time.
For this board, there is a 16-bit (2 byte) data interface resulting in 32-bits (4 bytes) transferred each clock cycle (double data rate).
The DDR is running at a clock 4x of the system clock.
For every system clock, there are 2 bytes per clock edge x 2 clock edges per clock cycle x 4 DDR clocks per system clock = 16 bytes (128 bits) per transaction.
The 8192 bytes are thus broken up into 8192/16 = 512 transactions.
The system clock rate is 100 MHz (10 ns/clock) resulting in 512 x 10ns = 5.12 us per transaction.
Note that this command parameter approach is different than the default BIST system and unique to Dr. Lloyd's implementation.

The _second_ parameter, 1, is the address mode and controls how addresses are changed during the test.
'0' is fixed, meaning keep the address the same, '1' is increment address by one, and '2' specifies to use a random address.
The incrementing address mode is used for this experiment.
Note that the "address" here refers to the address of a block of 16 bytes (i.e., a single transaction).
When the address is incrementing by 1, it is actually incrementing by 16.
Note that the core will just roll over back to zero when the maximum address is reached.

The _third_ parameter, 0, is the data mode.
'0' indicates that the data is fixed (i.e., the pattern given with the `sdram_bist_pat`), '1' is data increment mode, and '2' is random mode.

The _fourth_ parameter, 2, is the write mode.
A '0' indicates that no writing will occur (only BIST reads).
A '1' indicates that the BIST should write once and continuosly read after that.
In mode '2' indicates that the BIST should write and then do a read back and forth.
In this mode, it writes the pattern data to all of the addresses in a single burst (specified by the burst length).
It then performs multiple burst writes until the entire memory has been written.
Next, it reads the entire memory one transaction at a time and compares the read data against the expected data.
If there is a mismatch between the expected value and the read value then an error counter is incremented.

Notes on the software:
* Writes 8196 bytes to the first address (512 transactions or 5.12 us)
* Waits for 100 ms (Dr. Lloyd indicates this delay is necessary to avoid some sort of deadlock that is not understood)
* Reads 8196 bytes at this first address (performs the compare in parallel with the read)
* Waits for 100 ms
* Increments the address (by 1 transaction/16 bytes)
* After 10 times in a row, it prints out a message to the UART to summarize the results
* After 8 of these messages, a new header is printed as well
* If there is an error found, a dedicated error message will print for each address in error

Questions for Tyler:
- What is the difference between the ERROR column count and the error messages in the middle of a line? See [this example](tmp/CTRL_ddr_11_28_December_16_2022__19_52_43_UART.log#L2975)
- Help me figure out what is going on [here](tmp/CTRL_ddr_11_28_December_16_2022__21_44_01_UART.log#L444)

## Non-TMR Tests

### Runs with no events

* CTRL_ddr_11_28_December_16_2022__15_57_38_LOG.log
* CTRL_ddr_11_28_December_16_2022__19_34_08_LOG.log
* CTRL_ddr_11_28_December_16_2022__19_51_03_LOG.log
* CTRL_ddr_11_28_December_16_2022__19_52_43_LOG.log

### [CTRL_ddr_11_28_December_16_2022__16_11_53_LOG.log](tmp/CTRL_ddr_11_28_December_16_2022__16_11_53_LOG.log)

<!-- Note the anchor to a heading. Put all words in heading in lower case with a dash where the spaces were -->
* [Speed Event](#bist-speed-error)@ [18:11:06](tmp/CTRL_ddr_11_28_December_16_2022__16_11_53_UART.log#L5597)

### [CTRL_ddr_11_28_December_16_2022__19_52_43_LOG.log](tmp/CTRL_ddr_11_28_December_16_2022__19_52_43_LOG.log)

* [Data Error](#bist-data-error)@[20:55:41](tmp/CTRL_ddr_11_28_December_16_2022__19_52_43_UART.log#L2975)
* [UART Timeout - Repower recovery](#uart-timeout)@[21:29:56](tmp/CTRL_ddr_11_28_December_16_2022__19_52_43_LOG.log#L601)
  * [JCM Hang](#jcm-hang)@[21:30:28](tmp/CTRL_ddr_11_28_December_16_2022__19_52_43_LOG.log#L625)

### [CTRL_ddr_11_28_December_16_2022__21_38_10_LOG.log](tmp/CTRL_ddr_11_28_December_16_2022__21_38_10_LOG.log)

* [UART Timeout Hang](#uart-timeout-hang)@[21:40:29](tmp/CTRL_ddr_11_28_December_16_2022__21_38_10_LOG.log#L84)

### [CTRL_ddr_11_28_December_16_2022__21_44_01_LOG.log](tmp/CTRL_ddr_11_28_December_16_2022__21_44_01_LOG.log)

* [Data Error](#bist-data-error)@[21:49:53](tmp/CTRL_ddr_11_28_December_16_2022__21_44_01_LOG.log#L103) - [recovers](tmp/CTRL_ddr_11_28_December_16_2022__21_44_01_UART.log#341)
* [BIST Printout Error](#bist-printout-error)@[21:52:07](tmp/CTRL_ddr_11_28_December_16_2022__21_44_01_LOG.log#L124) ([UART](tmp/CTRL_ddr_11_28_December_16_2022__21_44_01_UART.log#444))
* [UART Timeout - reset recovery](#uart-timeout)@[21:52:35](tmp/CTRL_ddr_11_28_December_16_2022__21_44_01_LOG.log#L131)
* [UART Timeout - repower recovery](#uart-timeout)@[23:46:55](tmp/CTRL_ddr_11_28_December_16_2022__21_44_01_LOG.log#L730)
  * [JCM Hang](#jcm-hang)@[21:47:17](tmp/CTRL_ddr_11_28_December_16_2022__21_44_01_LOG.log#L754)

### [CTRL_ddr_11_28_December_17_2022__07_36_01_LOG.log](tmp/CTRL_ddr_11_28_December_17_2022__07_36_01_LOG.log)

* [UART Timeout - reset recovery](#uart-timeout)@[08:13:42](tmp/CTRL_ddr_11_28_December_17_2022__07_36_01_LOG.log#L266)
* [UART Timeout - reset recovery](#uart-timeout)@[08:13:42](tmp/CTRL_ddr_11_28_December_17_2022__07_36_01_LOG.log#L297)  

### [CTRL_ddr_11_28_December_17_2022__08_30_27_LOG.log](tmp/CTRL_ddr_11_28_December_17_2022__08_30_27_LOG.log)

* [UART Timeout -reset recovery](#uart-timeout)@[08:46:44](tmp/CTRL_ddr_11_28_December_17_2022__08_30_27_LOG.log#L153)
* [UART Garbled](#uart-garbled)@[09:00:18](tmp/CTRL_ddr_11_28_December_17_2022__08_30_27_LOG.log#L237) - [UART](tmp/CTRL_ddr_11_28_December_17_2022__08_30_27_UART.log#L1477)
  * [rebooted](tmp/CTRL_ddr_11_28_December_17_2022__08_30_27_LOG.log#L245)
* [UART timeout loop](#uart-timeout-loop)@[11:22:58](tmp/CTRL_ddr_11_28_December_17_2022__08_30_27_LOG.log#L1018)

### [CTRL_ddr_11_28_December_17_2022__11_41_08_LOG.log](tmp/CTRL_ddr_11_28_December_17_2022__11_41_08_LOG.log)

* [UART Timeout - repower recovery](#uart-timeout)@[12:28:52](tmp/CTRL_ddr_11_28_December_17_2022__11_41_08_LOG.log#L321)
* [UART Timeout - repower recovery](#uart-timeout)@[12:57:51](tmp/CTRL_ddr_11_28_December_17_2022__11_41_08_LOG.log#L513)
* [UART Timeout - reset recovery](#uart-timeout)@[13:26:14](tmp/CTRL_ddr_11_28_December_17_2022__11_41_08_LOG.log#L702)
* [Data Error](#bist-data-error)@[14:11:35](tmp/CTRL_ddr_11_28_December_17_2022__11_41_08_LOG.log#L950) - [UART 14:11:30](tmp/CTRL_ddr_11_28_December_17_2022__11_41_08_UART.log#7144)
   * Recovers @14:11:35
   * Lots of incorrect data errors even though 
* [UART Timeout - uart connect recovery](#uart-timeout)@[14:16:59](tmp/CTRL_ddr_11_28_December_17_2022__11_41_08_LOG.log#L1017)


### [CTRL_ddr_11_28_December_19_2022__10_32_48_LOG.log](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_LOG.log)

* [Unicode Error - repower recovery](#unicode-error)@[13:51:47](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_LOG.log#L1102) - [uart](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_UART.log#L9297)
  * In this case there was a single unicode error and it looks like the processor was executing random code. The processor was reset but this did not recover. The processor was repowered and it did recover.  
* [UART timeout - reset recovery](#uart-timeout)@[14:23:47](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_LOG.log#L1335)
* [UART timeout - reset recovery](#uart-timeout)@[15:02:01](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_LOG.log#L1546)
* [Unicode Error](#unicode-error)@[15:59:42](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_LOG.log#L1858) - [uart](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_UART.log#L15390).
   * This is a single byte unicode error that was masked as a bist data error (the output was corrupted)
   * This is really a UART error rather than a unicode error
* [BIST Error](#bist-data-error)@[16:14:49](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_LOG.log#L1939) - [uart](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_UART.log#L16091). Recovers at  [16:14:49](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_UART.log#L16793)
   * Logger thinks there are errors (logging bug)
* [UART timeout - reset recovery](#uart-timeout)@[16:52:18](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_LOG.log#L2237)
* [UART timeout - repower recovery](#uart-timeout)@[17:58:43](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_LOG.log#L2593)
* [UART timeout - repower recovery](#uart-timeout)@[17:58:43](tmp/CTRL_ddr_11_28_December_19_2022__10_32_48_LOG.log#L2671)


## TMR Controller Tests


### [CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_LOG.log](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_LOG.log)

* [BIST Error](#bist-data-error)@[16:11:58](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_LOG.log#L260) - [uart](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_UART.log#L1727). Recovers at  [16:11:58](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_UART.log#L2697)
* [UART timeout - reset recovery](#uart-timeout)@[17:35:11](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_LOG.log#L757)
* [BIST Error](#bist-data-error)@[20:44:08](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_LOG.log#L1747) - [uart](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_UART.log#L15374). Recovers at  [20:44:08](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_UART.log#L16624)
* [UART timeout - reset recovery](#uart-timeout)@[05:35:32](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_LOG.log#L4864)
* [BIST bad data lines](#bist-bad-data-lines)@[06:22:36](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_LOG.log#L5121) - [uart](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_UART.log#L43483). **Does not recover**


### [CTRL_ddr_11_28_tmr_December_18_2022__07_15_59_LOG.log](tmp/CTRL_ddr_11_28_tmr_December_18_2022__07_15_59_LOG.log)

No errors

### [CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_LOG.log](tmp/CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_LOG.log)

* [BIST Error](#bist-data-error)@[12:43:27](tmp/CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_LOG.log#L1709) - [uart](tmp/CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_UART.log#L14772). Recovers at  [12:43:27](tmp/CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_UART.log#L16026)
* [UART timeout - reset recovery](#uart-timeout)@[15:48:43](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_LOG.log#L2943)
* [BIST Error](#bist-data-error)@[16:14:27](tmp/CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_LOG.log#L3090) - [uart](tmp/CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_UART.log#L25879). Recovers at  [12:43:27](tmp/CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_UART.log#L26372)
* [BIST Error](#bist-data-error)@[18:48:31](tmp/CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_LOG.log#L4240) - [uart](tmp/CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_UART.log#L33551). Recovers at  [12:43:27](tmp/CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_UART.log#L34401). **This overlaps with previous**

    
### [CTRL_ddr_11_28_tmr_December_18_2022__20_01_01_LOG.log](tmp/CTRL_ddr_11_28_tmr_December_18_2022__20_01_01_LOG.log)

No errors

### [CTRL_ddr_11_28_tmr_December_18_2022__21_03_16_LOG.log](tmp/CTRL_ddr_11_28_tmr_December_18_2022__21_03_16_LOG.log)

There is a note in which we reboot after 50 BIST errrs (i.e., the message that keeps coming). I should have left this the way it was. Not sure this worked.

* [BIST Error](#bist-data-error)@[05:19:38](tmp/CTRL_ddr_11_28_tmr_December_18_2022__21_03_16_LOG.log#L2635) - [uart](tmp/CTRL_ddr_11_28_tmr_December_18_2022__21_03_16_UART.log#L23132). Recovers at  [12:43:27](tmp/CTRL_ddr_11_28_tmr_December_18_2022__21_03_16_LOG.log#L23769).


### [CTRL_ddr_11_28_tmr_December_19_2022__07_57_13_LOG.log](tmp/CTRL_ddr_11_28_tmr_December_19_2022__07_57_13_LOG.log)

no errors

### [CTRL_ddr_11_28_tmr_December_19_2022__08_22_46_LOG.log](tmp/CTRL_ddr_11_28_tmr_December_19_2022__08_22_46_LOG.log)

no errors

### [CTRL_ddr_11_28_tmr_December_19_2022__08_39_03_LOG.log](tmp/CTRL_ddr_11_28_tmr_December_19_2022__08_39_03_LOG.log)

no error

### [CTRL_ddr_11_28_tmr_December_19_2022__18_34_25_LOG.log](tmp/CTRL_ddr_11_28_tmr_December_19_2022__18_34_25_LOG.log)

[Unicode Error - reboot](#unicode-error)@[03:05:36](tmp/CTRL_ddr_11_28_tmr_December_19_2022__18_34_25_LOG.log#L2713) - [uart](tmp/CTRL_ddr_11_28_tmr_December_19_2022__18_34_25_UART.log#L23814)
  * Some odd printing of random characters followed by a reboot
  * [UART timeout - reset recovery](#uart-timeout)@[03:05:36](tmp/CTRL_ddr_11_28_tmr_December_19_2022__18_34_25_LOG.log#L2726)


### [CTRL_ddr_11_28_tmr_December_20_2022__08_05_34_LOG.log](tmp/CTRL_ddr_11_28_tmr_December_20_2022__08_05_34_LOG.log)

  * [UART timeout - reset recovery](#uart-timeout)@[12:31:49](tmp/CTRL_ddr_11_28_tmr_December_20_2022__08_05_34_LOG.log#L1447)

### [CTRL_ddr_11_28_tmr_December_20_2022__17_47_55_LOG.log](radiation_results/tmp/CTRL_ddr_11_28_tmr_December_20_2022__17_47_55_LOG.log)

no error


## Summary 

### General controller test thoughts:

* We didn't get a lot of errors for confidence.
* We seem to get more timout errors for non-TMR over TMR suggesting that the procesor is more reliable in TMR than non-TMR (although the confidence is week). It may be interesting to dig through the timeout errors in TMR to see what is causing the processor to fail.
* The DRAM errors seem not to change suggesting that DRAM errors will occur in either with similar frequency (although the data needs to be computed)
* It is not clear how useful this test is at radiation. We can reproduce this sort of thing all we like with fault injection and may not be worth the effort for radition testing. The Linux ECC board is probably the best for the next radiation test.


* What are we doing with UART unicode errors to try and recover? Are we trying to send UART commands? It is not clear that anything can be done.
* There was a BIST data error that was actually a UART error. Need to adjust the parser to look specifically for uART errors vs. BIST errors. (see [2022-12-19 15:59:41] in UART log)
* There is a reboot continuous loop problem that occurs when reboots fail. Need to check for this and cause a repower/reconfigure. See nontmr_17_08_30, [2022-12-17 08:46:44]
* nontmr_16_21_44 [2022-12-16 21:52:07] LOG - need to figure out what this error is. Review code to understand.
* Need to reboot JCM or do something with the JCM when the JCM fails. See nontmr_16_21_44, [2022-12-16 23:46:55] and nontmr_16_19_52:[2022-12-16 21:29:56]
* The processor code or UART failed resulting bad output during bist (%lu %lu %lu %lu). It looked like everything was working except the output. Resulted in  "BIST:Bad data line" errors indefinitely but did not fix anything. Should have resulted in a soft reset. See tmr_17_15_35 [2022-12-18 06:22:36]

### Test Improvements

* The BIST is currently setup to do a small DDR transfer and then do a long wait before proceeding to thetest. The duty cycle of the DRAM is very low. Need to investiage commands that do larger bursts and figure out how to reduce the delay between the write and the read check.
* Resolve the BIST data error parsing issue ([see BIST data error](#bist-data-error)) for details and an example. This error never leaves the log even though it recovers.
* Resolve the [JCM Hang](#jcm-hang) error by repowering the JCM and trying to reconnect multiple times if a command fails.
* Resolve the [UART Timout Hang](#uart-timeout-hang) error. If you get multiple successive uart timeouts, then reconfigure the board and try again. Perhaps add more time to the timout delay for the UART. This is related to the [UART timeout loop](#uart-timeout-loop) - need a maximum number of timeouts.
* Detect speed errors in the log and just note them (don't do anything).
* BIST errors sometimes generate a lot of LOG messages even afer the DRAM has recovered: [LOG example](tmp/CTRL_ddr_11_28_December_17_2022__11_41_08_LOG.log#L950) and [UART example](tmp/CTRL_ddr_11_28_December_17_2022__11_41_08_UART.log#7144)
* Resolve [BIST bad data lines](#bist-bad-data-lines)@[06:22:36](tmp/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_LOG.log#L5121). Need to reboot processor.
* It looks like we just repowered the board after reset recovery. We should try reconfiguring the board with the JCM inbetween a reset and a repower
* There is a "bad title line" in LOG when the system first boots. Need to fix this.


### Post Analysis

* Figure out fluence of TMR and non TMR
* Count the events we saw and get some cross sections
* Look at BFAT for those TMR timout errors to see why the processor is failing
* UART UARTBONE I ADDR insight (**We need to figure out the code addresses**)
  * The address is read during the "Setup UARTBone State" during initialization. It reads 000012E8 in this state
  * It is read in the "Reset Recovery State" (before and after issuing reset)
    * Before: 1350,1358
    * After: 20028 (reboot), 1F8 (ok), 20 (reboot), 1350 (reboot)

# DDR VexRiscv Tests

In this set of experiments we created a non-TMR VexRISV system with a DDR controller and put the DDR3 device in the beam rather than the FPGA.
The idea is to understand and quantify how the data in the DDR itself fails rather than how the FPGA controller fails as happened in the DDR controller test.
The same FPGA design was used in this test as was used in the non-TMR controller test.
We don't expect any DDR controller failures (although there may be a few upsets within the FPGA fabric).

The logs for these tests are named `DDR_ddr_11_28_December_xx_2022__mm_dd_ss_XXX.log`.

After bootup, the processor initialiates DDR testing with the following two commands:
```
sdram_bist_pat 90
sdram_bist 8192 1 0 1
```
After executing these commands, the user interface is not used unless there is a problem with the BIST behavior.
The test pattern uses 90 or 0x5A.
The BIST is using linearly increasing addresses, a fixed data pattern, and a single write followd by continuous reads.
Continuous reads are performed because we want to identify data failures (athought we should have fixed them - see notes below).


Notes:
* Single error takes lots of messages before repairing. Need to modify script to distinguish between these bursts (and not log everything) and the single bit errors we saw. Seems like a SEFI.

## [DDR_ddr_11_28_December_16__15_52_53_LOG.log](tmp/DDR_ddr_11_28_December_16__15_52_53_LOG.log)

The filename format was changed after this.
No errors

## [DDR_ddr_11_28_December_16_2022__15_57_43_LOG.log](tmp/DDR_ddr_11_28_December_16_2022__15_57_43_LOG.log)

No errors

## [DDR_ddr_11_28_December_16_2022__16_11_57_LOG.log] DDR_ddr_11_28_December_16_2022__16_11_57_LOG.log

No errors

## [DDR_ddr_11_28_December_16_2022__20_12_00_LOG.log]

Didn't fully start, no errors

## [DDR_ddr_11_28_December_16_2022__20_13_55_LOG.log]

Didn't fully start, no errors

## [DDR_ddr_11_28_December_16_2022__20_15_07_LOG.log]

Didn't fully start, no errors

## [DDR_ddr_11_28_December_16_2022__20_18_03_LOG.log]

Didn't fully start, no errors

## [DDR_ddr_11_28_December_16_2022__20_20_57_LOG.log]

Didn't fully start, no errors

## [DDR_ddr_11_28_December_16_2022__20_21_38_LOG.log]

no errors

## [DDR_ddr_11_28_December_16_2022__20_33_44_LOG.log]

* [2022-12-16 22:37:56] ERROR    BIST:ERROR 0x40002100 XOR=0x02020200
  * [2022-12-16 22:41:22] INFO     BIST:Header
* [2022-12-17 01:03:53] ERROR    BIST:ERROR 0x54000008 XOR=0x20202020
  * [2022-12-17 01:05:24] INFO     BIST:Header
* [2022-12-17 06:42:49] ERROR    BIST:ERROR 0x44000810 XOR=0x22202020
  * [2022-12-17 06:46:47] INFO     BIST:Header
* [2022-12-17 06:57:12] ERROR    BIST:ERROR 0x476ef008 XOR=0x01000001
  * [2022-12-17 07:00:19] INFO     BIST:Header
* [2022-12-17 07:20:44] ERROR    UART:expect timeout (delay 15s)
  * Did we manually shut off?


## [DDR_ddr_11_28_December_17_2022__07_53_34_LOG.log]

No errors

## [DDR_ddr_11_28_December_17_2022__08_59_59_LOG.log]

* [2022-12-17 10:56:30] ERROR    BIST:ERROR 0x4f70c700 XOR=0x00000020
  * Single-bit error
* [2022-12-17 11:37:40] ERROR    BIST:ERROR 0x56002908 XOR=0x80008080
  * start of big burst error
  * seems to be repaired by [2022-12-17 16:33:45] (confirmed in UART)
* [2022-12-17 17:02:55] ERROR    BIST:ERROR 0x5c002800 XOR=0x20200020
  * Ends by [2022-12-17 17:06:10] INFO     BIST:Header
* [2022-12-17 17:11:53] ERROR    BIST:ERROR 0x58201800 XOR=0x58983A0E
  * ends by [2022-12-17 17:12:00] INFO     BIST:Header
* [2022-12-17 17:14:25] ERROR    BIST:ERROR 0x4c003800 XOR=0x02000000
  * [2022-12-17 17:17:42] INFO     BIST:Header
* [2022-12-17 17:19:27] ERROR    BIST:ERROR 0x5dbce008 XOR=0x08080808
  * [2022-12-17 17:21:10] INFO     BIST:Header
* [2022-12-17 22:10:43] ERROR    BIST:ERROR 0x58201900 XOR=0x01000000
  * [2022-12-17 22:12:08] INFO     BIST:Header
* [2022-12-17 23:17:49] ERROR    BIST:ERROR 0x4cb21800 XOR=0x25AFA595
  * [2022-12-17 23:17:58] INFO     BIST:Header
* [2022-12-18 00:10:43] ERROR    BIST:ERROR 0x4c000000 XOR=0x00200020
  * [2022-12-18 00:13:50] INFO     BIST:Header

## DDR_ddr_11_28_December_18_2022__07_17_00_LOG.log]

No errors

## [DDR_ddr_11_28_December_18_2022__07_26_53_LOG.log]

* [2022-12-18 18:58:56] ERROR    BIST:ERROR 0x5a003908 XOR=0x00200020
  * [2022-12-18 19:00:36] INFO     BIST:Header
* [2022-12-18 21:03:29] ERROR    BIST:ERROR 0x44001900 XOR=0x04040404
  * [2022-12-18 21:04:57] INFO     BIST:Header
* [2022-12-18 22:58:05] ERROR    BIST:ERROR 0x420dd804 XOR=0x00020002
  * [2022-12-18 23:00:58] INFO     BIST:Header
* [2022-12-19 02:57:25] ERROR    BIST:ERROR 0x46642800 XOR=0x5A5A5EDC
  * [2022-12-19 02:57:36] INFO     BIST:Header
* [2022-12-19 04:27:13] ERROR    BIST:ERROR 0x44002000 XOR=0x20002020
  * [2022-12-19 04:30:09] INFO     BIST:Header

## [DDR_ddr_11_28_December_19_2022__07_57_17_LOG.log]

Did not start, no errors

## [DDR_ddr_11_28_December_19_2022__08_01_25_LOG.log]

* [2022-12-19 08:51:58] ERROR    BIST:ERROR 0x52108ed4 XOR=0x00000008
  * single bit
* [2022-12-19 09:10:26] ERROR    BIST:ERROR 0x4e327800 XOR=0x00000200
  * [2022-12-19 09:12:00] INFO     BIST:Header
* [2022-12-19 12:16:52] ERROR    BIST:ERROR 0x46003000 XOR=0x02000200
  * [2022-12-19 12:19:20] INFO     BIST:Header
* [2022-12-19 15:48:34] ERROR    BIST:ERROR 0x44000900 XOR=0x00000800
  * [2022-12-19 15:50:07] INFO     BIST:Header
* [2022-12-19 16:56:51] ERROR    BIST:ERROR 0x5a240810 XOR=0x00202020
  * [2022-12-19 16:58:14] INFO     BIST:Header
* [2022-12-20 06:38:08] ERROR    BIST:ERROR 0x4a001900 XOR=0x04040404
  * [2022-12-20 06:39:48] INFO     BIST:Header


## [DDR_ddr_11_28_December_20_2022__08_05_40_LOG.log]

* [2022-12-20 11:34:24] ERROR    BIST:ERROR 0x40002100 XOR=0x80808080
  * [2022-12-20 11:36:05] INFO     BIST:Header

## [DDR_ddr_11_28_December_20_2022__17_48_02_LOG.log]

* [2022-12-20 17:52:29] ERROR    BIST:ERROR 0x40001900 XOR=0x01000101
  * [2022-12-20 17:54:06] INFO     BIST:Header

# DDR4 Test

Why do some of the early logs not have UART output? Was this something that was changed?

## [DDR4_December_16__15_54_15.log]

No issues (no uart)

## [DDR4_December_16_2022__15_56_27.log]

No issues (no uart)

## [DDR4_December_16_2022__16_11_59.log]

No issues (no uart)

## [DDR4_December_16_2022__20_36_46.log]


Failure event at [2022-12-17 02:05:33]. 
Nothing is repaired and the logs print out errors until experiment is restarted. 
It looks like this is a single bit upset that was not repaired and thus the errors persist every cycle.
Error occured at address 0x7693c780 (which chip?).

[2022-12-17 02:05:33] INFO     !!! Failed pattern: a5a5a5a5 !!!
[2022-12-17 02:05:33] INFO     Failed: 0x7693c780 == 0xa5a5a5a5
[2022-12-17 02:05:33] INFO       data     = 0xa5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a525a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5
[2022-12-17 02:05:33] INFO       expected = 0xa5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5

In the midst of all this noise there appeared to be another failure.
Unlike the previous error that just repeated once every iteration, this one appers to have lots of errors in a single iteration.
Starting at iteration 31107 with address 0x7539a000 and going until address 0x753fbfc0

[2022-12-17 03:36:14] INFO     Iteration 31107 (0 errors)
[2022-12-17 03:36:46] INFO     !!! Failed pattern: a5a5a5a5 !!!
[2022-12-17 03:36:46] INFO     Failed: 0x7539a000 == 0xa5afa5a5
[2022-12-17 03:36:46] INFO       data     = 0xa5a5a5a5a5aea5a5a5a5a5a5a5afa5a5a5a5a5a5a5afa5a5a5a5a5a5a5afa5a5a5a5a5a5a5afa5a5a5a5a5a5a5afa5a5a5a5a5a5a5afa5a5a5a5a5a5a5afa5a5
[2022-12-17 03:36:46] INFO       expected = 0xa5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5

**Todo** There are likely more errors burried in this report. Need to write a script to find them (i.e., first time an error occurs print it and then ignore it from then out)

## [DDR4_December_17_2022__08_11_11.log]

No errors

## [DDR4_December_17_2022__13_29_09.log]

An error - need to write script to filter out and find all new errors.

[2022-12-17 14:13:43] INFO     Iteration 3304 (0 errors)
[2022-12-17 14:13:44] INFO     !!! Failed pattern: a5a5a5a5 !!!
[2022-12-17 14:13:44] INFO     Failed: 0x63c9a040 == 0xa5a5a5a5
[2022-12-17 14:13:44] INFO       data     = 0xa5a5a5a5a5a525a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5
[2022-12-17 14:13:44] INFO       expected = 0xa5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5


## [DDR4_December_17_2022__15_22_27.log]

No errors

## [DDR4_December_17_2022__16_02_59_LOG.log]

At this point, switched over to the command line and logged the UART (there is a corresponding UART with each log file from this point on).
Note that there are some odd control characters in the UART log.
It looks like there are a bunch of short runs at this point to debug the logging.

No Errors

## [DDR4_December_17_2022__16_08_01_LOG.log]

Short log, no errors

## [DDR4_December_17_2022__16_10_17_LOG.log]

## [DDR4_December_17_2022__16_15_33_LOG.log]

First long overnight run.

It is not clear that this new approach is checking the full memory space of the memory since it is using the processor interface and the smaller memory space.
**TODO**: figure out how much of the memory space this test is actually testing.

## [DDR4_December_18_2022__07_27_34_LOG.log]

Short empty debug run. It looks like there are a bunch of debug runs at this point.

## [DDR4_December_18_2022__07_28_50_LOG.log]

short debug run

## [DDR4_December_18_2022__07_33_18_LOG.log]

short empty debug run

## [DDR4_December_18_2022__07_36_30_LOG.log]

short empty debug run

## [DDR4_December_18_2022__07_37_35_LOG.log]

short empty debug run

## [DDR4_December_18_2022__07_43_15_LOG.log]

short empty debug run

## [DDR4_December_18_2022__07_46_07_LOG.log]

Longer run but no errors.

## [DDR4_December_18_2022__10_49_29_LOG.log]

No errors

## [DDR4_December_18_2022__17_24_45_LOG.log]

Runt run, no data

## [DDR4_December_18_2022__17_28_27_LOG.log]

Overnight run. Some expect errors.
**TODO**: figure out what happened here.

## [DDR4_December_19_2022__07_57_23_LOG.log]

Short run, no errors

## [DDR4_December_19_2022__09_37_41_LOG.log]

No errors

## [DDR4_December_19_2022__18_16_00_LOG.log]

No errors
Error detected at end? **TODO** look at UART

## [DDR4_December_19_2022__19_54_23_LOG.log]

Some memory errors detected. **TODO** Look into

## [DDR4_December_20_2022__08_05_48_LOG.log]

No errors

## [DDR4_December_20_2022__17_48_09_LOG.log]

No errors


# Error Signatures

## Controller Test

### BIST Speed Error

In a speed error, the memory speed reported deviates from the expected value.
Something has happened to the speed calculation (perhaps an upset in the speed conter registers?).
In this example below, the speed recovers through scrubbing.
Need to annotate all of these from Tyler's script.

```
[2022-12-16 18:11:06]          941          940         2371          0
[2022-12-16 18:11:07]          941          940         2845          0
[2022-12-16 18:11:09]          681          760         3207          0
[2022-12-16 18:11:10]          491          600         3479          0
[2022-12-16 18:11:11]          491          600         3752          0
[2022-12-16 18:11:12]          491          600         4024          0
[2022-12-16 18:11:12] WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS
[2022-12-16 18:11:14]          491          600          200          0
[2022-12-16 18:11:15]          721          790          580          0
[2022-12-16 18:11:16]          941          940         1054          0
[2022-12-16 18:11:18]          941          940         1528          0
[2022-12-16 18:11:19]          941          940         2002          0```
```

[example](tmp/CTRL_ddr_11_28_December_16_2022__16_11_53_UART.log#L5597)

### BIST Data Error

Errors occur at a single bit position for multiple addresses.
This is likely due to an upset in the data path of the SDRAM controller.
The error goes away after scrubbing.
Note that the error shows up on the UART first and then shows up on the LOG file next after it parses the UART.

**LOG error:**

```
[2022-12-16 20:55:32] INFO     BIST:Header (ok)
[2022-12-16 20:55:41] ERROR    BIST:Data Errors (633,0,0:633/1)
[2022-12-16 20:55:43] ERROR    BIST:Data Errors (474,0,0:474/2)
[2022-12-16 20:55:44] ERROR    BIST:Data Errors (474,0,0:474/3)
[2022-12-16 20:55:46] ERROR    BIST:Data Errors (474,0,0:474/4)
[2022-12-16 20:55:47] ERROR    BIST:Data Errors (474,0,0:474/5)
[2022-12-16 20:55:49] ERROR    BIST:Data Errors (473,0,0:473/6)
[2022-12-16 20:55:50] ERROR    BIST:Data Errors (474,0,0:474/7)
[2022-12-16 20:55:50] INFO     BIST:Header (err 7)
[2022-12-16 20:56:02] INFO     BIST:Header (ok)
[2022-12-16 20:56:03] ERROR    BIST:Data Errors (862,0,0:862/1)
[2022-12-16 20:56:13] INFO     BIST:Header (err 1)
[2022-12-16 20:56:25] INFO     BIST:Header (ok)
```

**UART error:**
```
[2022-12-16 20:55:32] WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS
[2022-12-16 20:55:33]          941          940          159          0
[2022-12-16 20:55:34] ERRORS (128-bit words): 8
[2022-12-16 20:55:34] error addr: 0x555a4fd8, content: 0xe5a5a5a5, expected: 0xa5a5a5a5
[2022-12-16 20:55:34] error addr: 0x555a5000, content: 0xe5a5a5a5, expected: 0xa5a5a5a5
[2022-12-16 20:55:34] error addr: 0x555a5800, content: 0xe5a5a5a5, expected: 0xa5a5a5a5
[2022-12-16 20:55:34] error addr: 0x555a5dd8, content: 0xe5a5a5a5, expected: 0xa5a5a5a5
[2022-12-16 20:55:34] error addr: 0x555a5f58, content: 0xe5a5a5a5, expected: 0xa5a5a5a5
[2022-12-16 20:55:34] error addr: 0x555a5f98, content: 0xe5a5a5a5, expected: 0xa5a5a5a5
[2022-12-16 20:55:34] error addr: 0x555a5fc8, content: 0xe5a5a5a5, expected: 0xa5a5a5a5
[2022-12-16 20:55:34] error addr: 0x555a5fd8, content: 0xe5a5a5a5, expected: 0xa5a5a5a5
[2022-12-16 20:55:34] ERRORS (32-bit words): 8
[2022-12-16 20:55:34] ERRORS (128-bit words): 7
```

In this example, the error shows up at [20:55:34](tmp/CTRL_ddr_11_28_December_16_2022__19_52_43_UART.log#L2975) in the UART log.
It shows up at [20:55:41](tmp/CTRL_ddr_11_28_December_16_2022__19_52_43_LOG.log#399) in the master log.
The errors go away at time 20:55:41 in the UART log.
The master LOG seems to sporadically detect errors even though the UART log does not have errors.


### BIST Printout Error

This error occurs when there are lots of meaningless BIST errors that occur in the UART in the middle of the BIST.
These messages are not the logging but something wrong with the BIST.
This causes the pexpect to reboot the processor.
[LOG example](tmp/CTRL_ddr_11_28_December_16_2022__21_44_01_LOG.log#L124) - [UART example](tmp/CTRL_ddr_11_28_December_16_2022__21_44_01_UART.log#444)

```
[2022-12-16 21:52:00] ERRORS (128-bit words): -1
[2022-12-16 21:52:00] ERRORS (32-bit words): 0
[2022-12-16 21:52:00] ERRORS (128-bit words): -1
[2022-12-16 21:52:00] ERRORS (32-bit words): 0
[2022-12-16 21:52:00] ERRORS (128-bit words): -1
[2022-12-16 21:52:00] ERRORS (32-bit words): 0
[2022-12-16 21:52:00] ERRORS (128-bit words): -1
[2022-12-16 21:52:00] ERRORS (32-bit words): 0
[2022-12-16 21:52:00] ERRORS (128-bit words): -1
[2022-12-16 21:52:00] ERRORS (32-bit words): 0
[2022-12-16 21:52:00] ERRORS (128-bit words): -1
[2022-12-16 21:52:00] ERRORS (32-bit words): 0
[2022-12-16 21:52:00] ERRORS (128-bit words): -1
[2022-12-16 21:52:00] ERRORS (32-bit words): 0
...
```


### BIST Bad Data Lines

The UART printout on the BIST wigs out and just prints bad data.
The script allows this to go on too long - processor needs rebooting.

```
[2022-12-18 06:20:46] %lu %lu %lu %lu
[2022-12-18 06:20:47] %lu %lu %lu %lu
[2022-12-18 06:20:49] %lu %lu %lu %lu
[2022-12-18 06:20:50] %lu %lu %lu %lu
[2022-12-18 06:20:52] %lu %lu %lu %lu
[2022-12-18 06:20:52] WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS
[2022-12-18 06:20:53] %lu %lu %lu %lu
[2022-12-18 06:20:55] %lu %lu %lu %lu
[2022-12-18 06:20:56] %lu %lu %lu %lu
[2022-12-18 06:20:57] %lu %lu %lu %lu
[2022-12-18 06:20:59] %lu %lu %lu %lu
[2022-12-18 06:21:00] %lu %lu %lu %lu
```


### UART Timeout

This occurs when the pexpect script does not receive a response after some amount of time.
This is likely a result of the processor hanging.
There are several different recovery mechanisms:
  * **Reconnect Recovery**: The USB disconnects and reconnects to see if that fixes the problem. I don't think this recovery mechanism has succeeded.
  * **Reset Recover**: A reset signal is asserted and the processor will try to run again
  * **Repower Recovery**: The reset recovery fails and so the board repowers

### UART Garbled

The UART prints a bunch of junk but it is not labelled as a Unicode error.

[Example](tmp/CTRL_ddr_11_28_December_17_2022__08_30_27_UART.log#L1477)
```
[2022-12-17 09:00:18]                                                                                                                                                           33              900              900            900
[2022-12-17 09:00:18]     [92    paxi     ax: 
[2022-12-17 09:00:18] 	[92i    pax:    [92    paxi     s`s                                             
[2022-12-17 09:00:18] 	                                                             
[2022-12-17 09:00:18] 	                                                             
[2022-12-17 09:00:18] 	                                                             
```

### UART Timeout Hang

This error starts with a simple [UART timeout error](#uart-timeout).
An example of the start of this error can be found [here](tmp/CTRL_ddr_11_28_December_16_2022__21_38_10_LOG.log#L84).
The script attempts to reboot the system so that the UART responds (see [example](tmp/CTRL_ddr_11_28_December_16_2022__21_38_10_UART.log#149) of the reboot in the UART).
The processor seems to reboot properly but the [last message](tmp/CTRL_ddr_11_28_December_16_2022__21_38_10_UART.log#214) is the header before the BIST prints data out.
The system hangs here and is reboot again.
This rebooting occurs over and over until the test fails.
It is likely that the BIST has an error and the FPGA needs to be reconfigured.
It is possible that the timout delay is not long enough but I doubt it.

### UART Timeout Loop

A UART timeout occurs and just loops repeatedly.
The rest of the test is just UART timouts.

### JCM Hang

This fatal error occurs when the JCM does not respond.
The script is written to exit the test when the JCM hangs.
The script should be updated to repower the JCM and try to connect again (for some number of times).
See [this example](tmp/CTRL_ddr_11_28_December_16_2022__19_52_43_LOG.log#L625)

### Unicode Error

This occurs when the UART starts sending bogus data




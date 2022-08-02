# Beam Test

Folder for everything related to the upcoming radiation test in December 2022.

## To Do

- [ ] Hardware Design / Bitfile
  - [ ] TMR version
  - [ ] BSCAN (query locked and other state, remote reset)
  - [ ] Triplicated clocking/MMCM
  - [ ] Support SD cards
- [ ] BIOS Code
- [ ] Test Infrastructure
  - [ ] Netbooter
  - [ ] JCMs
- [ ] Python Control Script

- [ ] Handle timeouts errors.
- [ ] Handle different types of errors.
  - [ ] "ERRORS"
  - [ ] "SEC"
  - [ ] "DED"
  - [ ] Combinations of above.
- [ ] Recovery methods.
  - [ ] Recalibrate.
  - [ ] Reinitialize.
  - [ ] Hardware Reset?
  - [ ] Reboot?
  - [ ] JTAG Reset?
  - [ ] Power Cycle
- [ ] Log errors with timestamps.
- [ ] Detect and handle failure types.
  - [ ] Controller failures.
  - [ ] Processor failures.
<!-- - [ ]  -->

## DDR Test

In this experiment, the DDR is placed in the beam and the FPGA controller is shielded as best we can.
We expect few FPGA/controller issues (we will be scrubbing the FPGA just in case).
We expect most errors (if not all) to occur from the DDR.
The purpose of this test is to measure the cross section of the DRAM memory cells and the various SEFI modes that it experiences.
We also want to experiment with error recovery mechanisms and find ways of recovering DRAM functionality after failure.

Test Procedure
* Power up and Configure the FPGA (SD-CARD config and boot so no additional step is needed
  * Pexpect to check and see if it is booted properly (before issuing more commands)
* Intialize the memory with BIST (including ECC words)
  * Use an "incrementing" pattern so we know what should be in each word
  * Read all the internal DRAM registers/state as a golden copy
* Continuously read the memory through BIST in some block size (1k?)
  * If a memory error has occured in a block:
    * Read the raw data from software from the entire block to find the word(s) that failed (and log it). Do a bitwise compare and print out the address and bits that failed
    * BIST write to the block to repair the memory
    * Continue the BIST reading where we left off
  * If the bist error count is above some threshold, go through some sort of memory congtroller diagnosis and attempt recover
    * try Bist read again to see if this was a temporary issue or bigger issue (move on if the second read is ok)
    * Read mode registers (repair if there was a problem)
    * Do a reinitialization/recalibration of DRAM if updating mode instructions doesn't solve the problem
  * Recalibrate
* If the processor hangs and doesn't respond (PEXPECT)
  * Try a remote reset (PMOD I/O? BSCAN?)
  * Repower

Expected DDR Errors:
* DRAM memory cell errors (will show up as single-bit errors and possibly double-bit errors)
  * BIST engine will report single and double and DRAM error
* Internal DRAM bank machine failures
  * Very large number of errors from the BIST
  
Test Setup
* Disable L2 cache for DRAM (so processor is always reading actual DRAM rather than cached values)


## FPGA Test

In this experiment, the FPGA is placed in the beam and the DRAM is shielded as best we can.
We expect few DRAM errors (although they may occur occasionally from secondaries).
We expect most errors (if not all) to occur from the FPGA processor and memory controller.
In this experiment we want to have both a TMR and non-TMR version of the FPGA circuitry so we can evalaute the improvement in controller/processor reliability using TMR.

The purpose of this test is to measure the cross section of the DRAM memory cells and the various SEFI modes that it experiences.
We also want to experiment with error recovery mechanisms and find ways of recovering DRAM functionality after failure.


## Test

![image](testing_procedures.svg)

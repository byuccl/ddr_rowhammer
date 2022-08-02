# Beam Test

Folder for everything related to the upcoming radiation test in December 2022.

## Notes / To Do

- [ ] Hardware Design
  - [ ] TMR version
  - [ ] BSCAN
- [ ] Develop automated test script.
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
For this test, we want to initialize the memory and just read memory locations continuously.
We would write to memory only when an error has been found (to repair the error).

Test Organization
* Configure the FPGA
* Intialize the memory with BIST (including ECC words)
  * Use an "incrementing" pattern so we know what should be in each word
  * Read all the internal DRAM registers as a golden copy
* Continuously read the memory through BIST in some block size (1k?)
* If a memory error has occured in a block:
  * Read the raw data from software from the entire block to find the word(s) that failed (and log it). Do a bitwise compare and print out the address and bits that failed
  * BIST write to the block to repair the memory
  * Continue the BIST reading where we left off
* If the bist error count is above some threshold, go through some sort of memory congtroller diagnosis and attempt recover
  * try command again
  * Read mode registers
  * Do a reinitialization of DRAM mode values
  * Recalibrate
* If the processor fails (PEXPECT)

Expected DDR Errors:
* DRAM memory cell errors (will show up as single-bit errors and possibly double-bit errors)
  * BIST engine will report single and double and DRAM error
* Internal DRAM bank machine failures
  * Very large number of errors from the BIST
  * Can we run a simple sequence of DFI reads to (read configuration mode registers)?
  
Test Setup
* Can we disable or remove the L2 DRAM cache?


## FPGA Test


## Test

![image](testing_procedures.svg)

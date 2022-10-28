# Scripts



### blinker.py

This was my first Migen script, made using the tutorial [here](https://m-labs.hk/docs/migen-tutorial.pdf). Though parts of this tutorial are outdated, the code works fine. This implements a one-led blinker. In the provided litex-boards repository, the system clock frequency is set to 100e6 Hz. With my counter starting at 30,000,000 and switching the led on and off, the led is on for about 0.3 seconds and off for the same amount of time. I've included lines of code that print out the verilog code in the terminal and generate the bitstream (though the line for generating the bitstream I found from a different tutorial on the migen website.)
	
### MyFirstMigen.py

This is my first original migen script. Each switch turns on the led just above it. When the first five switches are off and the buttons are pressed, one of the first five leds will blink fast (on for 0.12 seconds, off for the same time, with the same system clock frequency as the one above). It is my first attempt to use arrays to get all leds, switches, and buttons to do something on the board. I've commented out lines that can print out the verilog conversion, generate the verilog script and put it in the same directory, and a line that tells vivado to completely generate the bitstream. 
	
### firstMemoryAttempt.py

This is my first attempt to use the Memory module in Migen. To run this, flip on the desired switches for the data (right 8 switches) and the desired switches for the address (left 8 switches). The center button (btnc) writes that data to the address, and turns the leds off. The bottom button (btnd) reads the data from the desired address (again left 8 switches) and outputs the contained data on the right 8 leds. See the tutorial below called 'LiteX-for-Hardware-Engineers' and the Migen user guide for a description of the signals.

### core_sim_usb.py

Programming the DDR2:
- Programming MR:
  - #A2-A0: Burst length (selected as 8 bit)
  - #A3: Burst Type (selected as interleaved)
  - #A6-A4: CAS Latency (between 3-7, currently 5)
  - #This is the delay, in clock cycles, between the Read
  - #command and the availability of the first bit of output data,
  - #depending on the speed grade option being used.
  - #A7: Mode (0 normal, 1 test)
  - #A8: DLL Reset (0 no, 1 yes) Do not reset a second time
  - #A11-A9: Write Recovery, tWR in ns / tCK in ns, round up
- Programming EMR: 
  - #A0: DLL Enable (0 for enable(normal), 1 for disable(text/debug))
  - #A1: Output Drive Strength (0 for full(normal), 1 for reduced)
  - #A5-A3: Posted CAS additive latency (pg 88). After an activate command, 
  - #the operation must wait tRCD (about 15 ns). This adds wait cycles to
  - #accomidate this time if a read/write command is issued before the
  - #end of tRCD.
  - #A6, A2: Fixes ODT resistance or disables it.
  - #A9-A7: OCD operation, 1 1 1 to enable ocd defaults
  - #A10: DQS# enable(0)/disable(1), DQS# acts as the complement of DQS.
  - #A11: RDQS enable(1)/disable(0). This signal acts the same as DQS.
  - #A12: Output enable(0)/disable(1). All outputs (DQ, DQS, DQS#, RDQS, RDQS#)
  - #function normally when they are enabled.
	

### Migen and Litex

[Here is a link to the tutorials section of the Litex wiki page.](https://github.com/enjoy-digital/litex/wiki/Tutorials-Resources) I've found a lot of helpful links from this page that have helped me learn migen and use litex. Here are a few:

[fpga 101 tutorials/labs (conveniently for nexys4ddr!)](https://github.com/litex-hub/fpga_101) This walks through making Migen designs and running SoC's with litex.

[LiteX-for-Hardware-Engineers](https://github.com/enjoy-digital/litex/wiki/LiteX-for-Hardware-Engineers)

### DDR Controllers (Important Links, keep for reference)

[DDR2 SDRAM Data sheet by Micron](https://media-www.micron.com/-/media/client/global/documents/products/data-sheet/dram/ddr2/1gb_ddr2.pdf?rev=854b480189b84d558d466bc18efe270c)

[Pin layout diagram for Nexys4 DDR2 Memory](https://digilent.com/reference/_media/reference/programmable-logic/nexys-4-ddr/nexys-4-ddr_sch.pdf)




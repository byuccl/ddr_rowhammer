# Migen Scripts

Here are some examples of Migen I have used. More to come!

### blinker.py

This was my first Migen script, made using the tutorial [here](https://m-labs.hk/docs/migen-tutorial.pdf). Though parts of this tutorial are outdated, the code works fine. This implements a one-led blinker. In the provided litex-boards repository, the system clock frequency is set to 100e6 Hz. With my counter starting at 30,000,000 and switching the led on and off, the led is on for about 0.3 seconds and off for the same amount of time. I've included lines of code that print out the verilog code in the terminal and generate the bitstream (though the line for generating the bitstream I found from a different tutorial on the migen website.)
	
### MyFirstMigen.py

This is my first original migen script. Each switch turns on the led just above it. When the first five switches are off and the buttons are pressed, one of the first five leds will blink fast (on for 0.12 seconds, off for the same time, with the same system clock frequency as the one above). It is my first attempt to use arrays to get all leds, switches, and buttons to do something on the board. I've commented out lines that can print out the verilog conversion, generate the verilog script and put it in the same directory, and a line that tells vivado to completely generate the bitstream. 
	
### firstMemoryAttempt.py

This is my first original attempt to use the Memory module in Migen. To use this program, flip on the desired switches for the data (right 8 switches) and the desired switches for the address (left 8 switches). The center button (btnc) writes that data to the address, and turns the leds off. The bottom button (btnd) reads the data from the desired address (again left 8 switches) and outputs the contained data on the right 8 leds. See the tutorial below called 'LiteX-for-Hardware-Engineers' and the Migen user guide for a description of the signals, and run the 'memory.py' example in migen/examples for an example of how the verilog is generated.
	

	
[Here is a link to the tutorials section of the Litex wiki page.](https://github.com/enjoy-digital/litex/wiki/Tutorials-Resources) I've found a lot of helpful links from this page that have helped me learn migen and use litex. Here are a few:

[fpga 101 tutorials/labs (conveniently for nexys4ddr!)](https://github.com/litex-hub/fpga_101) This walks through making Migen designs and running SoC's with litex.

[LiteX-for-Hardware-Engineers](https://github.com/enjoy-digital/litex/wiki/LiteX-for-Hardware-Engineers)




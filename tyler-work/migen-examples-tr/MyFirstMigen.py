from migen import *
from migen.fhdl import verilog
from litex_boards.platforms import digilent_nexys4ddr as board

# Switches turn LEDs on permanently or off, buttons blink LEDs.

class BlinkButton(Module):

    def __init__(self, led, btn, sw):
    
        max_blink_time = 12000000
        self.blink_on = Signal()
        
        self.num_clk_cycles = Signal(max=max_blink_time)
        
        led.eq(0)
        self.blink_on.eq(True)
        
        self.sync += [  If(btn,
                            If(self.num_clk_cycles == 0,
                            	 If(self.blink_on == True,
                                    led.eq(btn | sw),
                                    self.num_clk_cycles.eq(max_blink_time),
                                    self.blink_on.eq(False)
                                ) .Else (
                                    led.eq(sw),
                                    self.num_clk_cycles.eq(max_blink_time),
                                    self.blink_on.eq(True)
                                )
                            ) .Else (
                                self.num_clk_cycles.eq(self.num_clk_cycles - 1)
                            )
                        ) .Elif(sw,
                            led.eq(sw)
                        ) .Else (
                            led.eq(0),
                            self.num_clk_cycles.eq(max_blink_time)
                        )
                     ]
                     
if __name__ == "__main__":
    plat = board.Platform()
    user_led = Signal(16)
    user_btn = Signal(5)
    user_sw = Signal(16)
    example = BlinkButton(user_led, user_btn, user_sw)
    
    
    # Prints out the verilog script in the terminal
    # print(verilog.convert(example, ios={user_led, user_sw, user_btn}))
    
    
    # Writes a verilog file called 'myFirst' in the same directory
    # verilog.convert(example, ios={user_led, user_sw, user_btn}).write("myfirst.v")
    
    # This generates resources for building the xdc file
    for i in range(16):
        example.comb += [plat.request("user_led", number = i).eq(user_led[i])]
        example.comb += [user_sw[i].eq(plat.request("user_sw", number = i))]
    
    for j in range(5):
        example.comb += [user_btn[j].eq(plat.request("user_btn", number = j))]
        
    # Generates the bitstream: Creates a directory called 'take1myfirst' and places the
    # entire project inside, calling the project 'myfirst'. This automatically runs 
    # synthesis and implementation, and generates bitstream.
    # plat.build(example, run = True, build_dir="take1myfirst", build_name="myfirst")
    
    
                         
                         
                         
                         
                         
                         
                         
                         
                         
                         
                         
                         
                         
                         
       

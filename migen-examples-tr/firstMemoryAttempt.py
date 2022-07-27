from migen import *
from migen.fhdl import verilog
from litex_boards.platforms import digilent_nexys4ddr as board

platform = board.Platform()

class buttonSwitchMemory(Module):
    def __init__(self, platform, btn, led, sw):
         
        # 8-bit wide 256-entry (8 bits to navigate) memory module 
        # (In verilog, this would be 'reg [7:0] mem[0:255];')
        self.specials.mem = Memory(8, 256)
        memoryAccess = self.mem.get_port(write_capable=True, we_granularity=8)
        
        # Switches 0-7 are the data, switches 8-15 are the address.
        # Set the data and address, and press button 0 to store the data in the address.
        # Set the address, and press button 1 to output the data stored there on the LED's.
        # * 'we' signal gives permission to write data to address when high
        # * 'we_granularity=8' above means 'we' signal is (mem-bits-wide/we_granularity) bits wide
        #   (in this case, 8/8 = 1 bit wide) and gives permission to write data to different sections of 
        #   mem. If we_granularity was 2, then the 'we' signal would be 8/2 = 4 bits wide, and each 
        #   bit of we would give permission to write to 2 bits of mem, where we[0] would give 
        #   permission to write to mem[adr][0:1].
        # * 'write_capable=True' creates a variable dat_w to write data. dat_r always exists to read it.
        # * Another possible argument for get_port is 'has_re' (default false). If set true, this adds a 
        #   signal 're' which enables reads when high.
        # * Another argument is 'clock_domain' which sets the clock of the created 'always' block. 
        #   The default is "sys", the system clock, but this argument can be used to change it.
        self.sync +=  If(btn[0], 
                          memoryAccess.dat_w.eq(sw[0:8]),
                          memoryAccess.adr.eq(sw[8:16]),
                          memoryAccess.we.eq(1),
                          led.eq(0)
                      ).Elif(btn[1],
                          memoryAccess.we.eq(0),
                          memoryAccess.adr.eq(sw[8:16]),
                          led.eq(memoryAccess.dat_r)
                      ).Else(
                          led.eq(led),
                          memoryAccess.we.eq(0),
                          memoryAccess.adr.eq(memoryAccess.adr),
                          memoryAccess.dat_w.eq(memoryAccess.dat_w)
                      )
        
        self.specials += memoryAccess
        
        for i in range(16):
            self.comb += [platform.request("user_led", number = i).eq(led[i])]
            self.comb += [sw[i].eq(platform.request("user_sw", number = i))]
    	
        for j in range(2):
            self.comb += [btn[j].eq(platform.request("user_btn", number = j))]
            
            

btn = Signal(2)
led = Signal(16)
sw = Signal(16)

module = buttonSwitchMemory(platform, btn, led, sw)

platform.build(module)



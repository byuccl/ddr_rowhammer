from migen import *
from migen.fhdl import verilog
from litex_boards.platforms import digilent_nexys4ddr as board

platform = board.Platform()

class buttonSwitchMemory(Module):
    def __init__(self, platform, btn, led, sw):
         
        # 8-bit wide 256-entry (8 bits to navigate) memory module 
        self.specials.mem = Memory(8, 256)
        memoryAccess = self.mem.get_port(write_capable=True, we_granularity=8)
        
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



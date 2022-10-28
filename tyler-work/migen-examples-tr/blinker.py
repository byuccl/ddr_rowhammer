from migen import *
from migen.fhdl import verilog
from litex_boards.platforms import digilent_nexys4ddr as board

# An LED turns on and off.

class Blinker(Module):
    def __init__(self, led, maxperiod):
        counter = Signal(max = maxperiod + 1)
        period = Signal(max = maxperiod + 1)
        self.comb += period.eq(maxperiod)
        self.sync += If(counter == 0,
                         led.eq(~led),
                         counter.eq(period)
                     ) .Else (
                         counter.eq(counter - 1)
                     )

plat = board.Platform()
led = plat.request("user_led")

my_blinker = Blinker(led, 30000000)

# Print verilog in terminal
# print(verilog.convert(my_blinker, ios={led}))

# Generate bitstream, directory: blinker, project name: blinker_migen
# plat.build(my_blinker, run=True, build_dir="blinker", build_name="blinker_migen")


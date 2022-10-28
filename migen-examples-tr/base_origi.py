#!/usr/bin/env python3

from migen import *

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform

from litex_boards.platforms import digilent_nexys4ddr as board

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.uart import UARTWishboneBridge
from litex.soc.cores import dna, xadc
from litex.soc.cores.spi import SPIMaster
from litex.soc.cores.clock import *
from litex.soc.cores import gpio
from litex.soc.interconnect.csr import AutoCSR, CSRStorage
from litex.soc.integration.doc import AutoDoc, ModuleDoc

from ios import Led, Button, Switch

from litedram.gen import LiteDRAMCoreControl
from litedram.modules import MT47H64M16
from litedram.phy import s7ddrphy

from litex.soc.cores.led import LedChaser



# Design -------------------------------------------------------------------------------------------

# Create our platform (fpga interface)
platform = board.Platform()



class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys2x     = ClockDomain()
        self.clock_domains.cd_sys2x_dqs = ClockDomain()
        self.clock_domains.cd_idelay    = ClockDomain()
        self.clock_domains.cd_eth       = ClockDomain()
        self.clock_domains.cd_vga       = ClockDomain()
        # # #

        self.submodules.pll = pll = S7MMCM(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys2x,     2*sys_clk_freq)
        pll.create_clkout(self.cd_sys2x_dqs, 2*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        pll.create_clkout(self.cd_eth,       50e6)
        pll.create_clkout(self.cd_vga,       40e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

class Led(gpio.GPIOOut):
    pass



# Create our soc 
class BaseSoC(SoCMini):

    def __init__(self, platform, **kwargs):
        sys_clk_freq = int(100e6)

        self.submodules.crg = _CRG(platform, sys_clk_freq)

	# SoCMini (No CPU, we are controlling the SoC over UART)
        SoCMini.__init__(self, platform, sys_clk_freq, csr_data_width=32,
            ident="MemoryAttempt", ident_version=True)

        # Leds
        user_leds = Cat(*[platform.request("user_led", i) for i in range(16)])
        self.submodules.leds = Led(user_leds)
        self.add_csr("leds")
        
        # self.submodules.leds = LedChaser(
        #     pads         = self.platform.request_all("user_led"),
        #     sys_clk_freq = sys_clk_freq)
        # self.add_csr("leds")

        # Clock Reset Generation
        ##### self.submodules.crg = CRG(platform.request("clk100"), ~platform.request("cpu_reset"))

        # No CPU, use Serial to control Wishbone bus
        self.submodules.serial_bridge = UARTWishboneBridge(platform.request("serial"), sys_clk_freq)
        self.add_wb_master(self.serial_bridge.wishbone)
       
        # DDR2 
        self.submodules.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype      = "DDR2",
                nphases      = 2,
                sys_clk_freq = sys_clk_freq)
        self.add_csr("ddrphy")
        
        class ControllerDynamicSettings(Module, AutoCSR, AutoDoc, ModuleDoc):
            # Allows to change LiteDRAMControllor behaviour at runtime
           
            def __init__(self):
                self.refresh = CSRStorage(reset=1, description="Enable/disable Refresh commands sending")
        
        self.submodules.controller_settings = ControllerDynamicSettings()
        self.add_csr("controller_settings")
        
        self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = MT47H64M16(sys_clk_freq, "1:2"),
                l2_cache_size = kwargs.get("l2_size", 8192)
        )
        
        self.submodules.ddrctrl = LiteDRAMCoreControl()
        self.add_csr("ddrctrl")

soc = BaseSoC(platform)

# Build --------------------------------------------------------------------------------------------

builder = Builder(soc, output_dir="build", csr_csv="csr.csv")
builder.build(build_name="top")

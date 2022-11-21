from litex_boards.targets.digilent_nexys_video import BaseSoC

from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.interconnect.csr import AutoCSR
from litex.soc.cores.uart import UARTWishboneBridge

from vexriscvdebug import VexRiscVDebug 

class TestSoC(BaseSoC):
    def __init__(
        self,
        toolchain="vivado",
        sys_clk_freq=...,
        with_ethernet=False,
        with_led_chaser=True,  # Changed this default so I can see if the hack worked.
        with_sata=False,
        sata_gen="gen2",
        with_sata_pll_refclk=False,
        vadj="1.2V",
        with_video_terminal=False,
        with_video_framebuffer=False,
        uart_bone="usb_fifo",
        **kwargs
    ):
        super().__init__(
            toolchain,
            sys_clk_freq,
            with_ethernet,
            with_led_chaser,
            with_sata,
            sata_gen,
            with_sata_pll_refclk,
            vadj,
            with_video_terminal,
            with_video_framebuffer,
            **kwargs
        )
        if uart_bone:
            self.add_uartbone(name=uart_bone, baudrate=115200)
        if with_led_chaser:
            self.add_csr("leds")

        # Turn on the PLL DRP
        #soc.crg.pll.expose_drp()
        self.crg.pll.expose_drp()

        # Get signals for my debug module
        locked_signal = self.crg.pll.locked
        iaddr = self.cpu.ibus.adr
        icyc = self.cpu.ibus.cyc
        iclk100 = self.crg.pll.clkin  #  I had to save this in the module - it wasn't saved
        self.submodules.debug = VexRiscVDebug(iclk100, locked_signal, iaddr, icyc)



def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Nexys Video")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--toolchain",              default="vivado",    help="FPGA toolchain (vivado or symbiflow).")
    target_group.add_argument("--build",                  action="store_true", help="Build design.")
    target_group.add_argument("--load",                   action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",           default=100e6,       help="System clock frequency.")
    target_group.add_argument("--with-ethernet",          action="store_true", help="Enable Ethernet support.")
    sdopts = target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",        action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",            action="store_true", help="Enable SDCard support.")
    target_group.add_argument("--with-sata",              action="store_true", help="Enable SATA support (over FMCRAID).")
    target_group.add_argument("--sata-gen",               default="2",         help="SATA Gen.", choices=["1", "2"])
    target_group.add_argument("--with-sata-pll-refclk",   action="store_true", help="Generate SATA RefClk from PLL.")
    target_group.add_argument("--vadj",                   default="1.2V",      help="FMC VADJ value.", choices=["1.2V", "1.8V", "2.5V", "3.3V"])
    target_group.add_argument("--uart_bone",              default="usb_fifo",  help="Add uartbone with given serial device.")
    viopts = target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (HDMI).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (HDMI).")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = TestSoC(
        toolchain              = args.toolchain,
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        with_ethernet          = args.with_ethernet,
        with_sata              = args.with_sata,
        sata_gen               = "gen" + args.sata_gen,
        with_sata_pll_refclk   = args.with_sata_pll_refclk,
        vadj                   = args.vadj,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        uart_bone              = args.uart_bone,
        **soc_core_argdict(args)
    )
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    
    args.csr_csv = "csr.csv"
    builder = Builder(soc, **builder_argdict(args))
    builder_kwargs = vivado_build_argdict(args) if args.toolchain == "vivado" else {}
    if args.build:
        builder.build(**builder_kwargs)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()

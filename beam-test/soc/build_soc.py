import json

from migen import *

from litex_boards.targets.antmicro_datacenter_ddr4_test_board import BaseSoC

from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.interconnect.csr import AutoCSR
from litex.soc.cores.uart import UARTWishboneBridge

from litedram.core.controller import ControllerSettings
from litedram.common import PhySettings, GeomSettings, TimingSettings

from vexriscvdebug import VexRiscVDebug 

class TestSoC(BaseSoC):
    def __init__(
        self, 
        *, 
        sys_clk_freq=int(100e6), 
        iodelay_clk_freq=200e6,
        with_ethernet=False, 
        with_etherbone=False, 
        eth_ip="192.168.1.50", 
        eth_reset_time="10e-3", 
        eth_dynamic_ip=False,
        with_hyperram=False, 
        with_sdcard=False, 
        with_jtagbone=True, 
        uart_bone="usb_fifo",
        with_spi_flash=False,
        with_led_chaser=True, 
        with_video_terminal=False, 
        with_video_framebuffer=False, 
        **kwargs
    ):
        super().__init__(
        sys_clk_freq           = sys_clk_freq, 
        iodelay_clk_freq       = iodelay_clk_freq,
        with_ethernet          = with_ethernet, 
        with_etherbone         = with_etherbone, 
        eth_ip                 = eth_ip, 
        eth_reset_time         = eth_reset_time, 
        eth_dynamic_ip         = eth_dynamic_ip,
        with_hyperram          = with_hyperram, 
        with_sdcard            = with_sdcard, 
        with_jtagbone          = with_jtagbone, 
        with_spi_flash         = with_spi_flash,
        with_led_chaser        = with_led_chaser, 
        with_video_terminal    = with_video_terminal, 
        with_video_framebuffer = with_video_framebuffer, 
        **kwargs
        )
        # if uart_bone:
        #     self.add_uartbone(name=uart_bone, baudrate=115200)
        # if with_led_chaser:
        #     self.add_csr("leds")

        # # Turn on the PLL DRP
        # #self.crg.pll.expose_drp()

        # # Get signals for my debug module
        # locked_signal = self.crg.pll.locked
        # iaddr = self.cpu.ibus.adr
        # icyc = self.cpu.ibus.cyc
        # iclk100 = self.crg.pll.clkin  #  I had to save this in the module - it wasn't saved
        # self.submodules.debug = VexRiscVDebug(iclk100, locked_signal, iaddr, icyc)

# Build --------------------------------------------------------------------------------------------

class LiteDRAMSettingsEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (ControllerSettings, GeomSettings, PhySettings, TimingSettings)):
            ignored = ["self", "refresh_cls"]
            return {k: v for k, v in vars(o).items() if k not in ignored}
        elif isinstance(o, Signal) and isinstance(o.reset, Constant):
            return o.reset
        elif isinstance(o, Constant):
            return o.value
        print('o', end=' = '); __import__('pprint').pprint(o)
        return super().default(o)

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on DDR4 Datacenter Test Board")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",                  action="store_true",    help="Build design")
    target_group.add_argument("--load",                   action="store_true",    help="Load bitstream")
    target_group.add_argument("--flash",                  action="store_true",    help="Flash bitstream")
    target_group.add_argument("--sys-clk-freq",           default=100e6,           help="System clock frequency")
    target_group.add_argument("--iodelay-clk-freq",       default=200e6,          help="IODELAYCTRL frequency")
    ethopts = target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",         action="store_true",    help="Add Ethernet")
    ethopts.add_argument("--with-etherbone",        action="store_true",    help="Add EtherBone")
    target_group.add_argument("--eth-ip",                 default="192.168.1.50", help="Ethernet/Etherbone IP address")
    target_group.add_argument("--eth-dynamic-ip",         action="store_true",    help="Enable dynamic Ethernet IP addresses setting")
    target_group.add_argument("--eth-reset-time",         default="10e-3",        help="Duration of Ethernet PHY reset")
    target_group.add_argument("--with-hyperram",          action="store_true",    help="Add HyperRAM")
    target_group.add_argument("--with-sdcard",            action="store_true",    help="Add SDCard")
    target_group.add_argument("--with-jtagbone",          action="store_true",    help="Add JTAGBone")
    target_group.add_argument("--without_uartbone",       action="store_true",    help="Add UartBone on 2nd serial")
    target_group.add_argument("--with-video-terminal",    action="store_true",    help="Enable Video Terminal (HDMI)")
    target_group.add_argument("--with-video-framebuffer", action="store_true",    help="Enable Video Framebuffer (HDMI)")
    target_group.add_argument("--with-spi-flash",         action="store_true",    help="Enable SPI Flash (MMAPed).")
    target_group.add_argument("--uart_bone",              default="serial",          help="Add uartbone with given serial device.")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = TestSoC(
        sys_clk_freq           = int(float(args.sys_clk_freq)),
        iodelay_clk_freq       = int(float(args.iodelay_clk_freq)),
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        eth_ip                 = args.eth_ip,
        eth_dynamic_ip         = args.eth_dynamic_ip,
        with_hyperram          = args.with_hyperram,
        with_sdcard            = args.with_sdcard,
        with_jtagbone          = args.with_jtagbone,
        uart_bone              = args.uart_bone,
        with_spi_flash         = args.with_spi_flash,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        **soc_core_argdict(args))

    args.csr_csv = "csr.csv"
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build(**vivado_build_argdict(args))
        builder.soc.generate_sdram_phy_py_header(os.path.join(builder.output_dir, "sdram_init.py"))
        # LiteDRAM settings (controller, phy, geom, timing)
        with open(os.path.join(builder.output_dir, 'litedram_settings.json'), 'w') as f:
            json.dump(builder.soc.sdram.controller.settings, f, cls=LiteDRAMSettingsEncoder, indent=4)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))

if __name__ == "__main__":
    main()

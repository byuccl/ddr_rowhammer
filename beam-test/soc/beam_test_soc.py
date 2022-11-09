from litex_boards.targets.digilent_nexys_video import BaseSoC as OriginalSoC

class TestSoC(OriginalSoC):
    def __init__(
        self,
        toolchain="vivado",
        sys_clk_freq=...,
        with_ethernet=False,
        with_led_chaser=False,  # Changed this default so I can see if the hack worked.
        with_sata=False,
        sata_gen="gen2",
        with_sata_pll_refclk=False,
        vadj="1.2V",
        with_video_terminal=False,
        with_video_framebuffer=False,
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

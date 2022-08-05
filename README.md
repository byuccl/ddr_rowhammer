# DDR Rowhammer Project

The overall goal of the DDR project is to develop and verify DDR controllers for FPGAs that provide both reliability and security.
We will work with sponsors and colleagues at other universities to address each of these concerns as follows:

* **Reliability**:
  * Determine the reliability of an open-source soft DDR controller
    * Perform fault injection
    * Identify single-point failures
  * Improve reliability of DDR controller
    * Test/validate ECC support
    * Support Chip ECC modes on boards/systems that provide the connections
    * Provide higher-level SEU recovery or response support
  * Work with U-Pitt on their DDR testbench 
  * Prepare for radiation experiment (BYU and Pitt)
* **Security**:
  * Rowhammer
    * Implement and verify [LiteX ROwHammer Tester](https://litex-rowhammer-tester.readthedocs.io/en/latest/)
    * Perform fault injection on Litex RowHammer tester

## Getting Started

* Learn what you can about DDR and DDR controllers (keep a list of good references that you find useful)
* Read up about DDR Rowhammering and keep a list of good references that you find along the way
* Start to learn how to use the [“migen” programming language](https://m-labs.hk/gateware/migen/). It is based on Python so you will probably need to review Python as you proceed.
* Review and learn about the [LiteX ROwHammer Tester](https://litex-rowhammer-tester.readthedocs.io/en/latest/). Work towards downloading this example on the ZCU104 board and arty-7 boards.
* Start to learn about and understand the [litedram project](https://github.com/enjoy-digital/litedram). You will be asked to change this core and work on this core later in the summer.

## Resources

* https://github.com/enjoy-digital/litex
* https://github.com/enjoy-digital/litex/wiki
* https://github.com/enjoy-digital/litex/wiki/LiteX-for-Hardware-Engineers - essential reading
* https://github.com/enjoy-digital/litedram
* https://antmicro.com/blog/2021/08/open-source-ddr-test-framework-for-rowhammer/
* https://github.com/antmicro/litex-rowhammer-tester/
* https://cfp.openpower.foundation/summit2021/talk/C9Q3GS/ 
* https://github.com/waviousllc/wav-lpddr-hw 
* https://github.com/litex-hub/linux-on-litex-vexriscv
* [LiteX: an open-source SoC builder and library based on Migen Python DSL](https://arxiv.org/pdf/2005.02506.pdf)

## Boards

* [VCU108](https://www.xilinx.com/products/boards-and-kits/ek-u1-vcu108-g.html) $7,194.00
* [VCU118](https://www.xilinx.com/products/boards-and-kits/vcu118.html) $8,394.00
* [Sidewinder-1000](https://www.xilinx.com/products/boards-and-kits/1-o1x8yv.html)
* [Alpha Data PCIe KU3](https://www.alpha-data.com/product/adm-pcie-ku3/)
* [LPDDR4](https://litex-rowhammer-tester.readthedocs.io/en/latest/lpddr4_tb.html)

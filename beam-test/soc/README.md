# SoC Build with ECC

## Quick setup

### Setting up our ECC project

1. Clone this repository 
```git clone https://github.com/tr-rocks/ecc_litex_build```

Note: If the default location of Vivado is not ```/tools/Xilinx/Vivado```, find the directory Vivado is installed, and run the command ```export VIVADO_LOCATION={}/Vivado```, where {} is the location of Vivado.


Here are the makefile commands to use after the Vivado path has been set:
* ```make deps```: This will install litex and all its submoduled repositories in a virtual environment with our forked litex and litedram repositories containing our BIST designs. To use the litex version setup in this virtual environment, run ```source env.sh```.
* ```make build```: This will setup litex and all the submodules as described above and use Litex to generate a bitstream located in build>antmicro_datacenter_ddr4_test_board>gateware. 
* ```make load```: Only to be used after the bitstream has been generated, this will load the bitstream to the board. (Make sure the board is plugged in.)

Things to note about this SoC:
* 0xf0003800 is the ecc_enable register (should be 1 by default, should remain 1 the entire test to enable error correction in ecc reads)
* 0xf0003804 is the ecc_clear register. If this is set high, the sec/ded error counts will clear to 0.
* 0xf0003808 is the ecc_sec_error counter.
* 0xf000380c is the ecc_ded_error counter.

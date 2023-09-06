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

### About our make file:
1. ```make deps``` runs the following commands:
  * ```python3 -m venv $(PYTHON_VENV)``` where ```PYTHON_VENV = .pyenv```
    * The default name of the virtual environment is .pyenv. All Litex-provided repositories and dependencies (meson and ninja) will be installed in this environment.
  * ```curl -fSL# https://static.dev.sifive.com/dev-tools/freedom-tools/v2020.08/$(RISCV_TOOLCHAIN).tar.gz > $(RISCV_TOOLCHAIN).tar.gz``` where ```RISCV_TOOLCHAIN = riscv64-unknown-elf-gcc-10.1.0-2020.08.2-x86_64-linux-ubuntu14```
  * ```tar -xzf $(RISCV_TOOLCHAIN).tar.gz --checkpoint=.10000```
    * The default method and riscv toolchain that the setup script for Litex uses is not what is used here, but instead ```apt install gcc-riscv64-linux-gnu```. However, when using this method and adding the ```--with-sdcard``` argument to our designs, as is needed for this design, we were getting the problem in [Andy's issue](https://github.com/enjoy-digital/litex/issues/1624). Therefore, we instead used the same [toolchain he used](https://static.dev.sifive.com/dev-tools/freedom-tools/v2020.08/riscv64-unknown-elf-gcc-10.1.0-2020.08.2-x86_64-linux-ubuntu14.tar.gz) and extracted it.
  * ```echo 'alias source=. # So vivado and make work together.' > ./env.sh```
    * We use ```.``` to source both the virtual environment and the settings64.sh in Vivado as is shown below. 
    * We created an env.sh file to eventually simplify sourcing both Vivado (settings64.sh) and .pyenv.
  * ```echo '. $(PYTHON_VENV)/bin/activate' >> ./env.sh```
    * Source the python environment with env.sh.
  * ```echo ". $(VIVADO_LOCATION)/$(VIVADO_VERSION)/settings64.sh" >> ./env.sh``` where ```VIVADO_LOCATION = /tools/Xilinx/Vivado``` and ```VIVADO_VERSION ?= $$(ls -d $(VIVADO_LOCATION)/*.* | tr / \\n | tail -n 1)```
    * Source settings64.sh in our Vivado location with env.sh. 
  * ```echo 'export PATH="$$PATH:$$(pwd)/$(RISCV_TOOLCHAIN)/bin"' >> ./env.sh```
    * Place the toolchain within our path.
  * ```git submodule update --init linux-on-litex-vexriscv```
  * ```git submodule update --init --recursive dependencies```
    * Update the submodules to match what the project expects by cloning missing submodules, update the working tree of the submodules.
  * ```. ./env.sh && pip install -r ./requirements.txt```
    * Source the virtual environment and install all litex repositories (each repository listed in requirements.txt. Includes meson and ninja).
  * ```cd dependencies/litex-boards/litex_boards/targets/ && rm antmicro_datacenter_ddr4_test_board.py```
  * ```cd dependencies/litex-boards/litex_boards/platforms/ && rm antmicro_datacenter_ddr4_test_board.py```
  * ```cp ./target/antmicro_datacenter_ddr4_test_board.py dependencies/litex-boards/litex_boards/targets/```
  * ```cp ./platform/antmicro_datacenter_ddr4_test_board.py dependencies/litex-boards/litex_boards/platforms/```
    * For now, we have a board executable separate from the litex-boards repository that these commands replace with the one inside. The Linux-on-litex repository will search for and run the antmicro-datacenter executable found in Litex boards when running make.py. Perhaps in the future, fork our own litex-boards repository. 
2. ```make build``` runs everything above and the following commands:
  * ```. ./env.sh; \```
  * ```cd linux-on-litex-vexriscv && ./make.py --board datacenter --build```
    * Source our virtual environment, navigate into our forked linux-on-litex repository, and run the make.py file for the data center board to generate the bitstream. This will build the bitstream using Vivado, and may take a while.
3. ```make load``` Only should be run after Vivado generates the bitstream. It runs the following commands only:
  * ```. ./env.sh; \```
    ```cd linux-on-litex-vexriscv && ./make.py --board datacenter --load```
    * Again source the virtual environment, navigate into our forked linux-on-litex repository and run the make.py file to load the generated bitstream onto the board. This uses openocd.
4. ```make clean``` runs the following commands:
  * ```git submodule deinit -f linux-on-litex-vexriscv```
  * ```git submodule deinit -f dependencies```
  * ```rm -r .pyenv && rm -r linux-on-litex-vexriscv/build```
    * Unregister all the submodules by removing the entire ```submodule.$name``` section from .git/config together with their work tree. Remove the virtual environment, and lastly remove the build directory created in linux-on-litex (only exists if make.py was run in the linux-on-litex directory).


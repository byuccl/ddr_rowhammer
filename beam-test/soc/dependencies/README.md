# Dependencies

These are required to build the LiteX SoC for the beam test.

## Required

*TO DO: Expand this list as other dependencies are discovered.*

* Utilities
  * python3
  * make
  * meson
  * ninja
* Vivado
* Litex
  * migen
  * litex
    * Custom fork.
  * litedram
    * Custom fork.
  * litex-boards
  * liteeth
  * liteiclink
  * pythondata-cpu-vexriscv
  * pythondata-software-picolibc
  * pythondata-software-compiler_rt
  * GCC RISCV Toolchain
    * https://static.dev.sifive.com/dev-tools/freedom-tools/v2020.12/sdk-utilities-1.0.1-2020.12.1-x86_64-linux-ubuntu14.tar.gz

## Submodules

The following were added as submodules so changes to the upstream project(s) will not easily break this project:

* migen
* litex
* litedram
* litex-boards
* liteeth
* liteiclink
* pythondata-cpu-vexriscv
* pythondata-software-picolibc
* pythondata-software-compiler_rt

## Other

The GCC RISCV Toolchain needs to be downloaded, extracted, and added to the path.

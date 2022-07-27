PACKAGES=libc libcompiler_rt libbase libfatfs liblitespi liblitedram libliteeth liblitesdcard liblitesata bios
PACKAGE_DIRS=/home/rickstr/tr-github/litex_files/litex/litex/soc/software/libc /home/rickstr/tr-github/litex_files/litex/litex/soc/software/libcompiler_rt /home/rickstr/tr-github/litex_files/litex/litex/soc/software/libbase /home/rickstr/tr-github/litex_files/litex/litex/soc/software/libfatfs /home/rickstr/tr-github/litex_files/litex/litex/soc/software/liblitespi /home/rickstr/tr-github/litex_files/litex/litex/soc/software/liblitedram /home/rickstr/tr-github/litex_files/litex/litex/soc/software/libliteeth /home/rickstr/tr-github/litex_files/litex/litex/soc/software/liblitesdcard /home/rickstr/tr-github/litex_files/litex/litex/soc/software/liblitesata /home/rickstr/tr-github/litex_files/litex/litex/soc/software/bios
LIBS=libc libcompiler_rt libbase libfatfs liblitespi liblitedram libliteeth liblitesdcard liblitesata
TRIPLE=riscv64-unknown-elf
CPU=vexriscv
CPUFAMILY=riscv
CPUFLAGS=-march=rv32i2p0_m     -mabi=ilp32 -D__vexriscv__
CPUENDIANNESS=little
CLANG=0
CPU_DIRECTORY=/home/rickstr/tr-github/litex_files/litex/litex/soc/cores/cpu/vexriscv
SOC_DIRECTORY=/home/rickstr/tr-github/litex_files/litex/litex/soc
PICOLIBC_DIRECTORY=/home/rickstr/.local/lib/python3.8/site-packages/pythondata_software_picolibc/data
COMPILER_RT_DIRECTORY=/home/rickstr/.local/lib/python3.8/site-packages/pythondata_software_compiler_rt/data
export BUILDINC_DIRECTORY
BUILDINC_DIRECTORY=/home/rickstr/tr-github/litex_files/build/digilent_arty/software/include
LIBC_DIRECTORY=/home/rickstr/tr-github/litex_files/litex/litex/soc/software/libc
LIBCOMPILER_RT_DIRECTORY=/home/rickstr/tr-github/litex_files/litex/litex/soc/software/libcompiler_rt
LIBBASE_DIRECTORY=/home/rickstr/tr-github/litex_files/litex/litex/soc/software/libbase
LIBFATFS_DIRECTORY=/home/rickstr/tr-github/litex_files/litex/litex/soc/software/libfatfs
LIBLITESPI_DIRECTORY=/home/rickstr/tr-github/litex_files/litex/litex/soc/software/liblitespi
LIBLITEDRAM_DIRECTORY=/home/rickstr/tr-github/litex_files/litex/litex/soc/software/liblitedram
LIBLITEETH_DIRECTORY=/home/rickstr/tr-github/litex_files/litex/litex/soc/software/libliteeth
LIBLITESDCARD_DIRECTORY=/home/rickstr/tr-github/litex_files/litex/litex/soc/software/liblitesdcard
LIBLITESATA_DIRECTORY=/home/rickstr/tr-github/litex_files/litex/litex/soc/software/liblitesata
BIOS_DIRECTORY=/home/rickstr/tr-github/litex_files/litex/litex/soc/software/bios
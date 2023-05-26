# -------------------------------------- #
# NOTES
# -------------------------------------- #

# Pay attention to "; \" in the rules.
# 	This is used frequently with the environment script.
# 	This chains all the commands together into one line.
# 	This allows the commands to use the same shell, so
# 	environment sourced with the script is preserved.

# -------------------------------------- #
# SETTINGS
# -------------------------------------- #

PYTHON_VENV = .pyenv
VIVADO_LOCATION ?= /tools/Xilinx/Vivado
VIVADO_VERSION ?= $$(ls -d $(VIVADO_LOCATION)/*.* | tr / \\n | tail -n 1)
RISCV_TOOLCHAIN = riscv64-unknown-elf-gcc-10.1.0-2020.08.2-x86_64-linux-ubuntu14
PYTHON_FLAGS =
BUILD_TARGET = antmicro_datacenter_ddr4_test_board.py
BUILD_FLAGS =

# -------------------------------------- #
# RULES
# -------------------------------------- #

.PHONY: env.sh build load

# -------------------------------------- #

default:
	@echo No default rule configured.

# -------------------------------------- #

$(PYTHON_VENV):
	@echo ------------------------------------------
	@echo Creating python virtual environment.
	@echo ------------------------------------------
	python3 -m venv $(PYTHON_VENV)
	@echo -------------------DONE-------------------

venv: $(PYTHON_VENV)

# -------------------------------------- #

$(RISCV_TOOLCHAIN):
	@echo ------------------------------------------
	@echo Downloading and extracting RISCV Toolchain
	@echo ------------------------------------------
	sudo apt install gcc-riscv64-linux-gnu
	@echo
	@echo -------------------DONE-------------------

# Easy way to get the toolchain without typing out the whole name.
toolchain: $(RISCV_TOOLCHAIN)

# -------------------------------------- #

env.sh: $(PYTHON_VENV) $(RISCV_TOOLCHAIN)
	@echo ------------------------------------------
	@echo Writing environment configuration to script.
	@echo ------------------------------------------
	echo 'alias source=. # So vivado and make work together.' > ./env.sh
	echo '. $(PYTHON_VENV)/bin/activate' >> ./env.sh
	echo ". $(VIVADO_LOCATION)/$(VIVADO_VERSION)/settings64.sh" >> ./env.sh
	@echo -------------------DONE-------------------

env: env.sh
	@echo To use the environment in your current shell use: '`. env.sh`'

# -------------------------------------- #

$(PYTHON_VENV)/dependencies_installed.txt: | env.sh
	@echo ------------------------------------------
	@echo Installing build dependnecies.
	@echo ------------------------------------------
	git submodule update --init --recursive dependencies
	. ./env.sh && pip install -r ./requirements.txt
	@echo Installed dependencies on $$(date). > $(PYTHON_VENV)/dependencies_installed.txt
	@echo -------------------DONE-------------------

# -------------------------------------- #

move_target_platform:
	cd dependencies/litex-boards/litex_boards/targets/ && rm antmicro_datacenter_ddr4_test_board.py
	cd dependencies/litex-boards/litex_boards/platforms/ && rm antmicro_datacenter_ddr4_test_board.py
	cp ./target/antmicro_datacenter_ddr4_test_board.py dependencies/litex-boards/litex_boards/targets/
	cp ./platform/antmicro_datacenter_ddr4_test_board.py dependencies/litex-boards/litex_boards/platforms/

deps: $(PYTHON_VENV)/dependencies_installed.txt move_target_platform

# -------------------------------------- #

build: deps | env.sh
	@echo ------------------------------------------
	@echo Building SoC.
	@echo ------------------------------------------
	. ./env.sh; \
	python $(PYTHON_FLAGS) ./dependencies/litex-boards/litex_boards/targets/$(BUILD_TARGET) --build $(BUILD_FLAGS)
	@echo -------------------DONE-------------------

# -------------------------------------- #

load: | env.sh
	@echo ------------------------------------------
	@echo Loading Design
	@echo ------------------------------------------
	. ./env.sh; \
	python $(PYTHON_FLAGS) ./dependencies/litex-boards/litex_boards/targets/$(BUILD_TARGET) --load
	@echo -------------------DONE-------------------

clean:
	rm -r .pyenv && rm -r build
	git submodule deinit -f dependencies

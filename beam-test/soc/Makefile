# -------------------------------------- #
# NOTES
# -------------------------------------- #

# Pay attention to "; \" in the rules.
# 	This is used frequently with the environment script.
# 	This chains all the commands together into one line.
# 	This allows the commands to use the same shell, so
# 	environment sourced with the script is preserved.

# TODO: Add some Vivado version discovery logic?
# TODO: Move all the pip-installable dependencies to a requirements.txt file.

# -------------------------------------- #
# SETTINGS
# -------------------------------------- #

PYTHON_VENV = .pyenv
VIVADO_VERSION = 2022.1
RISCV_TOOLCHAIN = riscv64-unknown-elf-gcc-10.1.0-2020.08.2-x86_64-linux-ubuntu14
PYTHON_FLAGS = -m
BUILD_TARGET = litex_boards.targets.digilent_nexys_video
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
	curl -fSL# https://static.dev.sifive.com/dev-tools/freedom-tools/v2020.08/$(RISCV_TOOLCHAIN).tar.gz > $(RISCV_TOOLCHAIN).tar.gz
	tar -xzf $(RISCV_TOOLCHAIN).tar.gz --checkpoint=.10000
	@echo
	rm $(RISCV_TOOLCHAIN).tar.gz
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
	echo '. /tools/Xilinx/Vivado/$(VIVADO_VERSION)/settings64.sh' >> ./env.sh
	echo 'export PATH="$$PATH:$$(pwd)/$(RISCV_TOOLCHAIN)/bin"' >> ./env.sh
	@echo -------------------DONE-------------------

env: env.sh
	@echo To use the environment in your current shell use: '`. env.sh`'

# -------------------------------------- #

$(PYTHON_VENV)/dependencies_installed.txt: | env.sh
	@echo ------------------------------------------
	@echo Installing build dependnecies.
	@echo ------------------------------------------
	git submodule update --init --recursive dependencies
	. ./env.sh; \
	pip install --upgrade pip meson ninja; \
	pip install -e dependencies/migen; \
	pip install -e dependencies/litex; \
	pip install -e dependencies/litex-boards; \
	pip install -e dependencies/litedram; \
	pip install -e dependencies/liteeth; \
	pip install -e dependencies/liteiclink; \
	pip install -e dependencies/pythondata-cpu-vexriscv; \
	pip install -e dependencies/pythondata-software-picolibc; \
	pip install -e dependencies/pythondata-software-compiler_rt
	@echo Installed dependencies on $$(date). > $(PYTHON_VENV)/dependencies_installed.txt
	@echo -------------------DONE-------------------

deps: $(PYTHON_VENV)/dependencies_installed.txt

# -------------------------------------- #

build: deps | env.sh
	@echo ------------------------------------------
	@echo Building SoC.
	@echo ------------------------------------------
	. ./env.sh; \
	python $(PYTHON_FLAGS) $(BUILD_TARGET) --build $(BUILD_FLAGS)
	@echo -------------------DONE-------------------

# -------------------------------------- #

load: | env.sh
	@echo ------------------------------------------
	@echo Loading Design
	@echo ------------------------------------------
	. ./env.sh; \
	python $(PYTHON_FLAGS) $(BUILD_TARGET) --load
	@echo -------------------DONE-------------------

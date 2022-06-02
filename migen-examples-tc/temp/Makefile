# Check OS.
ifeq ($(OS),Windows_NT)
DETECTED_OS := Windows
else
DETECTED_OS := $(shell uname)
endif

PYTHON := python3

# Creating a default rule so make with no arguments will not do anything.
default:
	@echo No default make rule exists.
	@echo DETECTED_OS: $(DETECTED_OS).

# Activate the pyenv, optionally creating it first.
.PHONY: env
env: litex-rowhammer-tester/Makefile
	@echo Activating rowhammer_tester venv.
	$(MAKE) -C litex-rowhammer-tester env

.PHONY: rowhammer-setup
rowhammer-setup: litex-rowhammer-tester/Makefile
	@echo Running initial setup.
	sudo apt update
	sudo apt install git build-essential autoconf cmake flex bison libftdi-dev libjson-c-dev libevent-dev libtinfo-dev uml-utilities python3 python3-venv python3-wheel python3-pip protobuf-compiler libcairo2 -y
	pip install ninja
	$(MAKE) -C litex-rowhammer-tester deps

.PHONY: openocd-setup
openocd-setup: openocd/
	# sudo apt update
	# sudo apt install libtool libusb-1.0-0-dev pkg-config -y
	cd openocd; ./bootstrap; ./configure --enable-ftdi
	$(MAKE) -C openocd -j `nproc`
	sudo $(MAKE) -C openocd install

# TODO: Rule to source vivado?
# TODO: Rule to activate python env(s).
# TODO: Rule to do setup and install?
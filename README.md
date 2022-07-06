# Nexys Video

Learning LiteX with the Nexys Video.

## Notes

### Setup
* Created python venv (.pyenv).
* `git submodule add --branch master https://github.com/enjoy-digital/litex`
* `git submodule update --init`
* `python litex/litex_setup.py --init --install --config=standard --gcc=riscv`
* `pip install meson ninja`
* `cp riscv64-unknown-elf-gcc-10.1.0-2020.08.2-x86_64-linux-ubuntu14/* .pyenv/`

### Design Flow
* 
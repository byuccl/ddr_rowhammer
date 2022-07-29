#!/usr/bin/env python3

from serial import Serial
from pexpect.fdpexpect import fdspawn
import sys, time, re


class Litexpect(fdspawn):
    """Wrapper for interacting with a LiteX prompt over serial via Pexpect."""

    # LiteX's "litex> " prompt with control characters.
    LITEX_PROMPT = "\[92;1mlitex\W\[0m> "

    def __init__(
        self,
        serial_port: str,
        baudrate: int,
        serial_options: dict = dict(),
        *args,
        **kwargs,
    ):
        """Create Litexpect instance.
        Parameters
        ----------
        serial_port : str,
            Passed to Serial for opening connection to board.
        baudrate : int,
            Passed to Serial for opening connection to board.
        serial_options : dict,
            Additional keyword arguments to Serial.
        *args
            Passed through to fdspawn superclass constructor.
        **kwargs
            Passed through to fdspawn superclass constructor.
        """
        # Open serial port.
        self.fd = file_descriptor = Serial(serial_port, baudrate=baudrate)
        # Spawn pexpect instance from file descriptor.
        super().__init__(file_descriptor, encoding="utf-8", *args, **kwargs)
        # Send initial newline to trigger 'litex>' prompt.
        # This helps when connecting to a running instance.
        self.sendline("\n")

    def __enter__(self):
        """Setup when used as context manager."""
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        """Cleanup when used as context manager."""
        # Send a newline to terminate BIST in case it is still running.
        self.sendline("\n")
        return super().__exit__(exc_type, exc_value, traceback)

    def send_command(self, command: str):
        """Sends a command to the LiteX prompt.
        Parameters
        ----------
        command : str
            Command string to send to LiteX.
        """
        self.expect(pattern=self.LITEX_PROMPT)
        self.sendline(command)

    def set_fault_injection(self, enabled: bool):
        """Sets fault injection for BIST.
        Parameters
        ----------
        enabled : bool
            Enables fault injection when True.
        """
        state = "0x02" if enabled else "0x00"
        self.send_command(f"mem_write 0xf0003810 {state} 4")

    def start_bist(self, burst_length: int, mode: int = 0):
        # TODO: Create docstring.
        self.send_command(f"sdram_bist {burst_length:x} {mode}")


# -------------------------------------- #

# TODO: Finish this?
def test_burst_length(c: Litexpect, max_burst, max_iterations=30):
    for i in range(1, max_iterations):
        failed_lengths = set()
        for burst_length in range(1, max_burst):
            # Skip known failures.
            if burst_length in failed_lengths:
                continue
            # Start BIST with burst_length.
            c.start_bist(burst_length, 0)
            # Capture BIST message.
            c.expect(R"Starting SDRAM BIST with burst_length=\d+ and addr_mode=\d+")
            # Capture BIST headers.
            # Run BIST for i iterations.
            for _ in range(i):
                c.expect
            # Extract error counts.
            # if errors
            #   Log that bust_length failed at i iterations.


def main():
    serial_port = R"/dev/ttyUSB0"
    baudrate = 115200

    # Open serial connection to bard.
    with Litexpect(serial_port, baudrate=baudrate) as c:
        c.logfile = sys.stdout

        c.start_bist(0x1000)
        c.expect(R"Starting SDRAM BIST with burst_length=\d+ and addr_mode=\d+")

        result2 = c.expect(R"( *(\S+))+")
        print("result2:", result2)
        results: re.Match = c.match
        print(results)
        print(results.groupdict())
        
        result3 = c.expect(R"\d+")
        print("result3:", result3)
        print(c.match)

        # Terminate sdram_bist.
        time.sleep(5)
        c.send("\n")


if __name__ == "__main__":
    main()

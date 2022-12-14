<!-- 
username:wirthlin
token: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 
-->


# DDR Rowhammer scripts

## jcm_session.py

* Configuration example:
`python3 jcm_session.py --jcm_ip 169.254.132.152 --jcm_part xc7a200t --bitfile /root/newtobetmred_tmr.bit --jcm_clock 30_000_000`

`python3 jcm_session.py --jcm_ip 169.254.132.152 --jcm_part xc7a200t --bitfile /root/newtobetmred_tmr.bit --jcm_clock 30_000_000 --jcm_file temp.txt`

## netbooter.py

`python3 netbooter_control.py --off 2`

## usb_uart_bone.py

Prints all of the USB uarts in the system and their IDs:

`python3 usb_uart_bone.py`


## ddrctrl_experiment.py

`python3 ddrctrl_experiment.py --jcm_part xc7a200t --bitstream /root/newtobetmred_tmr.bit`

`python3 ddrctrl_experiment.py --jcm_part xc7a200t --bitstream /root/newtobetmred_tmr.bit --log_dir ./tmp --jcm_clock 30_000_000`

`python3 ddrctrl_experiment.py --jcm_part xc7a200t --bitstream /root/newtobetmred_tmr.bit --log_dir ./tmp --jcm_clock 30_000_000 --frads_file xc7a200t_frad.txt`

`python3 ddrctrl_experiment.py --jcm_part xc7a200t --bitstream /root/newtobetmred_tmr.bit --log_dir ./tmp --jcm_clock 30_000_000 --frads_file xc7a200t_frad.txt --fault_injection -uart_bone_ident 0xf0001800`

No Beam (fault injection)

`python3 ddrctrl_experiment.py --jcm_part xc7a200t --bitstream /root/ddr_11_28.bit --log_dir ./tmp --jcm_clock 30_000_000 --frads_file xc7a200t_frad.txt --fault_injection 2 --uart_bone_ident 0xf0002000 --jcm_ip 169.254.132.152 --jcm_netbooter_port 1 --nexys_netbooter_port 2 --usb_uart_phys_port 1-4.4.2 --uartbone_phys_port 1-4.4.1`

Beam (no fault injection)

`python3 ddrctrl_experiment.py --jcm_part xc7a200t --bitstream /root/ddr_11_28.bit --log_dir ./tmp --jcm_clock 30_000_000 --frads_file xc7a200t_frad.txt --fault_injection 0 --uart_bone_ident 0xf0002000 --jcm_ip 169.254.132.152 --jcm_netbooter_port 1 --nexys_netbooter_port 2 --usb_uart_phys_port 1-4.4.2 --uartbone_phys_port 1-4.4.1`

To Do:
  * Catch uartbone timeouts (instead of hanging)

## ddrdata_experiment.py

* With JCM (assume already configured)

`python3 ddrdata_experiment.py --log_dir ./tmp --bitstream /root/ddr_11_28.bit --jcm_clock 30_000_000 --jcm_netbooter_port 4 --nexys_netbooter_port 3 --jcm_ip 169.254.132.151 --uart_phys_port 1-4.4.4.1`

uart bone (prog): 1-4.4.3

Fault Injection (in another window)

`python3 usb_uart_bone.py ---uartbone_phys_port xx --uartbone_phys_if xx --uartbone_baudrate 115200 -read xx`


# Error Logs

Types of errors:

* UART Timout
  * Back to back timout error (two back to back terminal errors)
    * First timeout (in middle of script)
    * second timeout (after trying to reconnect to the terminal for terminal recovery state)
    * Response: Unrecoverable post mortum
  * terminal recovery (actually recovers from the terminal recovery state)
* Data error
  * Recoverable data error (less than 8 consecutive data errors, scrubber fixes them)
  * A few BIST data errors, one good execution, and a few more bist errors and then they go away?
* Unicode error
  * Recoverable after rerunning BIST
* Mixed errors
  * First a data error and then a UART timeout
  * Unicode errors and then UART timeout
* Odd Errors
  * Get a DDR Data error regularly but there is at least one good execution in the mix that resets the counters. Seems to be a timing error.

To Do:
* Check back to back reconfigures (need a repower?)
* When JCM configuration/scrubbing fails (can't start because something is executing: reboot jcm?)
* USB port rebooting
  * https://github.com/mvp/uhubctl
  * https://github.com/byuccl/yinstruments/blob/main/yinstruments/usb_power.py

* Coding
  * Move to new state machine model (return next state)
  * Move the uart_control to a multi-class organization (test_logger, uart_base, and uart_expect)
  * Trap control C when ending script (clean up nicely)

# Test notes

NUC usb dongle: 169.254.132.50 ("DDR Experiemnt" label). enxa0cec803ae9e
Netbooter IP - 169.254.131.160
USB Ethernet - 169.254.132.50 (netmask 255.255.0.0)

## DDR Data

CTRL jcm (169.254.132.152)
CTRL artix - Artix 19

DATA jcm - 169.254.132.151
DATA artix - Artix 26



```
/dev/ttyUSB0 1-4.4.1 0     # programming port for control DDR
/dev/ttyUSB1 1-4.4.1 1     # uart bone for control DDR
/dev/ttyUSB2 1-4.4.2 0     # general uart for control ddr
/dev/ttyUSB3 1-4.4.3 0     # programming port for data ddr
/dev/ttyUSB4 1-4.4.3 1     # uart bone for data ddr?
/dev/ttyUSB5 1-4.4.4.1 0   # general uart for data ddr
/dev/ttyUSB6 1-4.4.4.3 0   # AntMicro USB (probably programming port)
/dev/ttyUSB7 1-4.4.4.3 1   # AntMicro USB ?
/dev/ttyUSB8 1-4.4.4.3 2   # AntMicro USB ?
/dev/ttyUSB9 1-4.4.4.3 3   # AntMicro USB ?
```


# Rowhammer tester

See Row Hammer Tester [Read the Docs](https://rowhammer-tester.readthedocs.io/en/latest/) 
and [repository](https://github.com/antmicro/rowhammer-tester) for more details.
We are using the **Data Center DRAM Tester** board.
Refer to the 


## Physical Setup:

1. Insert memory into antmicro card
2. Plug power cord into antmicro and into netbooter
3. Plug in uart for antmicro board into usb hub
4. Plug ethernet usb dongle into usb hub
5. Connect ethernet between dongle and board

## Ethernet setup

New Dongle id: enxa0cec875a7f9 (a0:ce:c8:75:a7:f9)
(Note:there is a lost dongle somewhere)


## Software setup

Board IP address: 192.168.100.50

Script:

`beam_bist.py`

Issues:
* Can't seem to connect to the USB terminal

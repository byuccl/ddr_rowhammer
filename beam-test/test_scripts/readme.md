
### BIST Experiment setup

Physical port and interface for boards, as well as current netbooter ports:
Nexys4ddr:                  Physical port: 1-4.4     Interface: 1     Netbooter port: 2
Nexys Video:                Physical port: 1-4.2     Interface: 0     Netbooter port: 3
Antmicro Datacenter board:  Physical port: 1-4.1     Interface: 2     Netbooter port: 1

First, clone the ddr_rowhammer repository and yinstruments repository.
Then navigate inside the ddr_rowhammer directory, and checkout the beam-test-changed-bist branch. 

```
git clone https://github.com/byuccl/ddr_rowhammer/
git clone https://github.com/byuccl/yinstruments/
cd ddr_rowhammer
git checkout beam-test-changed-bist
```

Then navigate into the directories beam_test/soc/, and run `make deps`. [This is a link to documentation on our makefile.](https://github.com/byuccl/ddr_rowhammer/wiki/Instructions-to-setup-our-BIST-designs)

```
cd beam-test/soc
make deps
```

Finally, sourced the file 'env.sh', install dependencies for the pexpect scripts, set the repository 'yinstruments' to the path, and navigated into the test_scripts directory where the scripts can now be run.

```
source env.sh
pip install pexpect paramiko pyudev
export PYTHONPATH=$PYTHONPATH:$PWD/../../../yinstruments/yinstruments
cd ../test_scripts/
```

### Commands

Here are the commands that run the continuous version of the BIST:

**Antmicro datacenter board**:

Continuous mode:
```
python3 ddrcontinuous_experiment.py --lindy_delay_sec 10 --test_name testexperiment --usb_uart_phys_port 1-4.4 --usb_uart_phys_if 2 --lindy_ip 169.254.132.210 --board_lindy_port 8 --no_uart_bone --continuous --test_board_name databoard --test_prefix EXAMPLE_DDR4_CONTINUOUS
```

Noncontinuous mode:
```
python3 ddrcontinuous_experiment.py --lindy_delay_sec 10 --test_name testexperiment --usb_uart_phys_port 1-4.4 --usb_uart_phys_if 2 --lindy_ip 169.254.132.210 --board_lindy_port 8 --no_uart_bone --test_board_name databoard --noncontinuous_bist_delay 300 --test_prefix EXAMPLE_DDR4_NONCONTINUOUS
```

**Nexys video board**:

Continuous mode:
```
python3 ddrcontinuous_experiment.py --test_name testexperiment --usb_uart_phys_port 1-4.2 --usb_uart_phys_if 0 --lindy_ip 169.254.132.210 --board_lindy_port 2 --uartbone_phys_port 1-4.1 --uartbone_phys_if 0 --uart_bone_ident 0xf0002000 --continuous --test_board_name nexys_video --test_prefix EXAMPLE_DDR3_CONTINUOUS
```

Noncontinuous mode:
```
python3 ddrcontinuous_experiment.py --test_name testexperiment --usb_uart_phys_port 1-4.2 --usb_uart_phys_if 0 --lindy_ip 169.254.132.210 --board_lindy_port 2 --uartbone_phys_port 1-4.1 --uartbone_phys_if 0 --uart_bone_ident 0xf0002000 --noncontinuous_bist_delay 300 --test_board_name nexys_video --test_prefix EXAMPLE_DDR3_NONCONTINUOUS 
```

**Nexys4ddr board**:

Continuous mode:
```
python3 ddrcontinuous_experiment.py --test_name testexperiment --usb_uart_phys_port 1-4.3 --usb_uart_phys_if 1 --lindy_ip 169.254.132.210 --board_lindy_port 2 --no_uart_bone --continuous --test_board_name nexys4ddr --test_prefix EXAMPLE_DDR2_CONTINUOUS
```

Noncontinuous mode:
```
python3 ddrcontinuous_experiment.py --test_name testexperiment --usb_uart_phys_port 1-4.3 --usb_uart_phys_if 1 --lindy_ip 169.254.132.210 --board_lindy_port 2 --no_uart_bone --noncontinuous_bist_delay 300 --test_board_name nexys4ddr --test_prefix EXAMPLE_DDR2_NONCONTINUOUS
```

Notes:
Nexys4ddr board 

Previous documentation:

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

Beam (no fault injection) wo/TMR

`python3 ddrctrl_experiment.py --jcm_part xc7a200t --bitstream /root/ddr_11_28.bit --log_dir ./lansce2022 --jcm_clock 30_000_000 --frads_file xc7a200t_frad.txt --fault_injection 0 --uart_bone_ident 0xf0002000 --jcm_ip 169.254.132.152 --jcm_netbooter_port 1 --nexys_netbooter_port 2 --usb_uart_phys_port 1-4.4.2 --uartbone_phys_port 1-4.4.1`

Beam (no fault injection) w/TMR

`python3 ddrctrl_experiment.py --jcm_part xc7a200t --bitstream /root/ddr_11_28_tmr.bit --log_dir ./lansce2022 --jcm_clock 30_000_000 --frads_file xc7a200t_frad.txt --fault_injection 0 --uart_bone_ident 0xf0002000 --jcm_ip 169.254.132.152 --jcm_netbooter_port 1 --nexys_netbooter_port 2 --usb_uart_phys_port 1-4.4.2 --uartbone_phys_port 1-4.4.1`


To Do:
  * Catch uartbone timeouts (instead of hanging)

## ddrdata_experiment.py

* With JCM (assume already configured)

`python3 ddrdata_experiment.py --log_dir ./ --bitstream /root/ddr_11_28.bit --jcm_clock 30_000_000 --jcm_netbooter_port 4 --nexys_netbooter_port 3 --jcm_ip 169.254.132.151 --uart_phys_port 1-4.4.4.1`


* With scrubbing

```
python3 ddrdata_experiment.py --log_dir ./lansce2022 --bitstream /root/ddr_11_28.bit --jcm_clock 30_000_000 --jcm_netbooter_port 4 --nexys_netbooter_port 3 --jcm_ip 169.254.132.151 --uart_phys_port 1-4.4.4.1 --enable_scrubbing --frads_file xc7a200t_frad.txt
```

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
* FIgure out why uartbone is hanging. Is there a recovery mechanism?
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
/dev/ttyUSB0 1-4.4.1 0     # programmiWed 14 Dec 2022 05:03:52 PM MST
ng port for control DDR
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


SEtting time after connecting internet:

shrec@nuc4:~/ddr/ddr_mjw/ddr_rowhammer/beam-test/test_scripts$ timedatectl set-ntp off
shrec@nuc4:~/ddr/ddr_mjw/ddr_rowhammer/beam-test/test_scripts$ timedatectl set-ntp on


See Row Hammer Tester [Read the Docs](https://rowhammer-tester.readthedocs.io/en/latest/) 
and [repository](https://github.com/antmicro/rowhammer-tester) for more details.
We are using the **Data Center DRAM Tester** board.
Refer to the [Network Notes](https://github.com/byuccl/ddr_rowhammer/tree/main/beam-test/network_notes) for setting up the network.


## Physical Setup:

1. Insert memory into antmicro card
2. Plug power cord into antmicro and into netbooter
3. Plug in uart for antmicro board into usb hub
4. Plug ethernet usb dongle into usb hub
5. Connect ethernet between dongle and board

## Ethernet setup

New Dongle id: enxa0cec875a7f9 (a0:ce:c8:75:a7:f9)
(Note:there is a lost dongle somewhere)

Associate the device with the name 'fpga0'

```
sudo ip link property add dev enxa0cec875a7f9 altname fpga0
sudo netplan apply
```

Make sure it was setup properly
```
ip link show
```

Set the IP address of the board.
```
sudo ip addr add 192.168.100.2/24 dev fpga0
```

Bring the interface "UP" (it may be up as seen in the previous command)

```
sudo ip link set fpga0 up
```


## Software setup



For the **server window** (go to rowhammer_tester/scripts):

```
source ~/ddr/rowhammer/rowhammer-tester/venv/bin/activate
export TARGET=ddr4_datacenter_test_board
```


```
export TARGET=ddr4_datacenter_test_board
```

Turn on the rowhammer board:

```
python3 ~/ddr/ddr_mjw/ddr_rowhammer/beam-test/test_scripts/netbooter_control.py  --on 5
```


In the rowhammer_tester/scripts directory:
```
cd ~/ddr/rowhammer/rowhammer-tester/rowhammer_tester/scripts
litex_server --udp --udp-ip 192.168.100.50 --udp-port 1234
```
Wait for a bit to see if it connects properly. If tit does not exit then all is well.

Board IP address: 192.168.100.50

For the **client window**:

It looks like you need to run the bios console once to get the memory intialized and calibrated.

```
source ~/ddr/rowhammer/rowhammer-tester/venv/bin/activate
export TARGET=ddr4_datacenter_test_board
cd ~/ddr/rowhammer/rowhammer-tester/rowhammer_tester/scripts
```

`python3 ~/ddr/rowhammer/rowhammer-tester/rowhammer_tester/scripts/bios_console.py`: Connects to the litex system through the Etherbone

Or run rowhammer test in beam test directory

```
python3 rowhammer_test.py --log_dir ./lansce2022/ --continuous
```
Issues:
* Can't seem to connect to the USB terminal

For the **runtime window**:

```
source ~/ddr/rowhammer/rowhammer-tester/venv/bin/activate
export TARGET=ddr4_datacenter_test_board
cd ~/ddr/ddr_mjw/ddr_rowhammer/beam-test/test_scripts
python3 rowhammer_test.py --log_dir ./lansce2022/ --continuous
```

# Notes

Beam counter is 60 seconds ahead of this NUC time.

## 12/16/2022:

Runs: 
* Started all three experiments at 16_11_57
* Accidentally Ctrl-C DDR controller experiment and had to restart (19_34_08)
* Stopped DDR CTRL again to move process onto a screen (named DDRCTRL). Started again at 19_51_03. This was accidently killed when existing screen with Ctrl-k (instead of Ctrl-a d)
* Started DDR CTRL again again at 19_52_43 (screen DDRCTRL)
* Stopped DDR data to (1) move it to a screen and (2) turn on JCM scrubbing. DDRDATA. Started again a few times for debugging (ignore incomplete versions). Some had read data. The long one is 20_33_44. Couldn't get JCM scrubbing working and moved on.
* Stopped rowhammer to add screen and simplify log. Restarted with screen ROWHAMMER at 20_36_46
* DDRCTRL crashed at 9:39 pm. Restarted. Need to review and figure out what happened. Something goofy happened when I tried to restart it. Restarted again.

* Run TMR CTRL DDR through the night (see if any errors in the morning)
* 

## 12/17/2022:

* Arrival:
  * DDRCTRL crashed (same JCM problem as yesterday)
    * Added a check to see if the JCM is scrubbing before trying to configure. Addressed in log starting at 08_30_27
    * It turns out we have been running the non-TMR bitstream since the start. Will continue with non-TMR for the day and run TMR for the rest of the test starting tonight
    * Got into an infinite loop trying to recover. Restarted manually at about 11:41 am
    * Started TMR around 3:36 pm (for rest of test?)
  * ROWHAMMER
    * Errors show the base address but do not show the bit (expected and read are the same)
      * Need to see if I can figure out how to get the actual bad data
    * The memory can completely fail.
      * Need to provide an automated way to recover (need to reinitialize the memory)
      * Perhaps modify the script to just run the bios code and run memtest manually
  * DDRDATA
    * It looks like there was a major error that cause a lot of problems but it seemed to have recovered. I don't think there is anything to change for this (as long as it recovers)
    * There was a UART timeout delay. Scrubbing not enabled properly.
      * Need to respond to UART timeout delays with a reboot of the system (until scrubbing can be fixed)
    * Changed code to repower when the UART timesout (starting with 08_59_59 log)

## 12/18/2022:

  * DDRCTRL
    * It looks like there was some cyclic error mode. Need to go back and review and possibly address in the script
    * 8:00 pm: some sort of cyclic data error. Need to find a way to detect these and reboot.
      * Added a test that will repower board after 50 BIST error messages. Not sure how to detect this BIST error bug.
  * DDRDATA
    * There are some block errors. Script seems ok
  * DDRROWHAMMER
    * Created stand alone script
    * Change number of enters to =0 for mem_cmp

## 12/19/2022:

  * DDRCTRL
    * Need to review logs for counts
    * Didn't seem to reboot with BIST errors. Changed the logic and will try again
    * Need to incorporate the netbooter pshow command
    * For the 21_03_16 log, I am getting bist errors when BIST errors are not occuring (see 05:19:38 line 2635 in the log file). There is an error, but the UART does not suggest an error. At 8:39 AM I started a new run to provide more information on why these errors keep coming (when there are no errors in the UART log). Watch for BIST errors throughout day.
    * Run the non-TMR for a while to get more data (some logs are hung up)
  * DDRDATA
    * Just getting a very few big BIST error blocks. Not much to do here but to just collect more data.
  * ROWHAMMER
    * Debuggging code to process memory errors and issue a mem_write to fix errors
    * Need to play with rowhammer experiments in the beam
  * Lattice
    * Need to automatically reboot lattice board as part of script

## 12/20/2022:

  * DDRCTRL
    * Very little activity. One reboot, no bist errors
    * Keep running TMR until completed
  * DDRDATA
    * Several big burst data events, otherwise quite
    * Keep running for rest of test
  * ROWHAMMER
    * Two single-bit errors found
    * Keep running for rest of test

Evening:
  * Clean up data room and take all stuff out

## 12/21/2022:



  * Cleanup
    1. Close beam shutter
    2. Gracefully stop all experiments (remove power)
    3. Backup all log data
    4. Shut down NUCs and start packing NUCs / control room cables and materials
    5. Open beam area

### Backup data

DDR Backups
```
cd ~/ddr/beam_data/ddr
mkdir ./tmp
scp -rp shrec@99.99.99.12:~/ddr/ddr_mjw/ddr_rowhammer/beam-test/test_scripts/lansce2022/* ./tmp
zip ddr_dec20.zip ./tmp/*
rm -rf ~/ddr/beam_data/ddr/tmp
```

Processor Backups

password:radiation
```
cd ~/ddr/beam_data/proc
mkdir ./tmp
scp -rp shrec@99.99.99.30:~/aew/scripts/rad_test_logs/* ./tmp
zip -r proc_dec20.zip ./tmp/*
rm -rf ~/ddr/beam_data/proc/tmp
```

VexLinux Backups

password:radiation
```
cd ~/ddr/beam_data/vexlinux
mkdir tmp_152
mkdir tmp_153
scp -rp shrec@99.99.99.30:~/VexLinuxTMR/JCM_repo/fault_injection/radiation_test/RT_logs_153/* ./tmp_153
scp -rp shrec@99.99.99.30:~/VexLinuxTMR/JCM_repo/fault_injection/radiation_test/RT_logs_152/* ./tmp_152
zip -r vex_dec20.zip ./tmp_152 ./tmp_153
rm -rf ~/ddr/beam_data/vexlinux/tmp_152
rm -rf ~/ddr/beam_data/vexlinux/tmp_153
```

Lattice Backups

password:chrec
```
cd ~/ddr/beam_data/lattice
mkdir tmp
# this takes a long time
scp -rp chrec@99.99.99.33:~/lattice_rad_test/rad_test_logs/* ./tmp
# this takes a long time too
scp -rp chrec@99.99.99.33:~/lattice_rad_test/changers* ./tmp
zip lattice_dec20.zip ./tmp/*
rm -rf ~/ddr/beam_data/lattice/tmp
```

Zcu102 Backups

password:chrec
```
cd ~/ddr/beam_data/zcu102
mkdir tmp
scp -rp chrec@99.99.99.33:~/pcap_scrubbing/radTest/logs_2022/2022_12_* ./tmp
zip -r zcu102_dec20.zip ./tmp/*
rm -rf ~/ddr/beam_data/zcu102/tmp
```

# Post test follow up
  * DDRCTRL
    * Review logs to identify various failure modes
    * Parse logs to obtain cross sections of various failure modes
    * Try to correlate failures with CRAM upsets and generate a sensitive CRAM upset list
    * Run extensive fault injection on TMR and non-TMR to understand failure modes and continue instrumentation of system (what is happening when the processor fails?)
      * Understand frozen hangs better (where is the code and what is the processor doing?)
    * Run BFAT on beam results
      * Through sensitive CRAM upset list
      * All CRAM bits (to see what BFAT things will happen to each one)
    * There seemed to be a ssh key issue when went to the beam. Try to replicate this and mitigate against this.
    * Archive with a zip file the DDR designs
    * Methods for improving speed of TMR (document how to create TMR)
  * DDRDATA
    * Figure out how to get scrubbing to work
    * Parsing scripts
    * Dig through failures manually to figure out what is going on
  * ROWHAMMER
    * Parse data and try to get a cross section of the memory
      * Figure out how the module works in terms of memory addressing
      * FIgure out which module the failures occured in
    * Play around more with the rohammering and propose a rowhammering beam test
    * Future: Larger beam so we can hit more memories.
  * Andy's work
  * ZCU 102 work
  * Lattice
    * Review logs to figure out why test is so sensitive
    * Clean up scrubber/mask file work
  * Misc
    * Commit and merge all scripts
    * Start to generalize scripts and libraries
    * Measure cross section of 7 series CRAM and compare with ICE/ICE-II
    * Compute cross section of Lattice
    * Experiment with uartbone. Why does it fail and can we recover it when it does fail?
  * Future work
    * Create Litex Linux using Antmicro board and ECC
  

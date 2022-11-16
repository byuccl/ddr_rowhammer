

# DDR Rowhammer scripts

## jcm_session.py

`python3 jcm_session.py --jcm_ip 169.254.132.152 --jcm_part xc7a200t --bitfile /root/newtobetmred_tmr.bit --jcm_clock 30_000_000`

`python3 jcm_session.py --jcm_ip 169.254.132.152 --jcm_part xc7a200t --bitfile /root/newtobetmred_tmr.bit --jcm_clock 30_000_000 --jcm_file temp.txt`

## netbooter.py

`python3 netbooter_control.py --off 2`

## ddr_experiment.py

`python3 ddr_experiment.py --jcm_part xc7a200t --bitstream /root/newtobetmred_tmr.bit`

`python3 ddr_experiment.py --jcm_part xc7a200t --bitstream /root/newtobetmred_tmr.bit --log_dir ./tmp --jcm_clock 30_000_000`

`python3 ddr_experiment.py --jcm_part xc7a200t --bitstream /root/newtobetmred_tmr.bit --log_dir ./tmp --jcm_clock 30_000_000 --frads_file xc7a200t_frad.txt`

`python3 ddr_experiment.py --jcm_part xc7a200t --bitstream /root/newtobetmred_tmr.bit --log_dir ./tmp --jcm_clock 30_000_000 --frads_file xc7a200t_frad.txt --fault_injection`

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

To Do:
* Check back to back reconfigures (need a repower?)
* When JCM configuration/scrubbing fails (can't start because something is executing: reboot jcm?)
* USB port rebooting
  * https://github.com/mvp/uhubctl
  * https://github.com/byuccl/yinstruments/blob/main/yinstruments/usb_power.py
  
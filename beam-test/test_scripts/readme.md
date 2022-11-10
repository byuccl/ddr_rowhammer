

# DDR Rowhammer scripts

## jcm_session.py

`python3 jcm_session.py --jcm_ip 169.254.132.152 --jcm_part xc7a200t --bitfile /root/newtobetmred_tmr.bit --jcm_clock 30_000_000`

`python3 jcm_session.py --jcm_ip 169.254.132.152 --jcm_part xc7a200t --bitfile /root/newtobetmred_tmr.bit --jcm_clock 30_000_000 --jcm_file temp.txt`

## netbooter.py

`python3 netbooter_control.py --off 2`

## ddr_experiment.py

`python3 ddr_experiment.py --jcm_part xc7a200t --bitstream /root/newtobetmred_tmr.bit`

`python3 ddr_experiment.py --jcm_part xc7a200t --bitstream /root/newtobetmred_tmr.bit --log_dir ./tmp --jcm_clock 30_000_000`


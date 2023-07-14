# Radiation Result Summary

This experiment ran with the DDR2, DDR3, and DDR4 chips on the nexys4ddr board, nexys video board, and the antmicro datacenter board respectively. We tried two types of experiments listed below:

1. Continuous experiment: With the chip placed under the radiation beam, we ran a BIST continuously reading and checking the entire memory. When errors occured, our BIST also wrote contintuously to the entire memory.
2. Idle experiment: With the chip placed under the radiation beam, we ran a BIST that periodically read the DRAM memory (set to 5 minutes), regardless if errors occured from the reading. 

After some of the first experiments, the scripts have been slightly modified and improved for better results and data. (For example, the DRAM controller at times appeared to output a continuous array of faulty data. To fix this, we added a periodic reset of the SoC when this occured.)

## Running the Parser

There are three parts to the parser:
1. The parser shows, in the order they occured, the error addresses and data as they happen dynamically, as well as the error count and date/time of the errors appearing.
2. The parser then shows a list of all the error addresses that appeared and lists them in order of which occured the most.
3. There is a regular expression for every expected line of data. Any line that does not match any one of the regular expressions will be displayed at the end.

To run the parser, place all the data logs in this directory.

An example to run the parser with the experiment on June 29, 2023 on 20:07:18:
```
python3 radiation_2023_parser.py --log_filename DDR2_IDLE_testexperiment_June_29_2023__20_07_18_LOG.log --uart_filename DDR2_IDLE_testexperiment_June_29_2023__20_07_18_UART.log --with_all_err_freq_cnts
```

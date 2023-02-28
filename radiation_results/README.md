# Radiation Experiment Feedback

Obtain summary of feedback for CTRL radiation experiment for the LANSCE 2022 DDR controller experiment.

## Obtain Raw Beam Logs

All data associated with the beam test is found at the beam test [release](../releases/tag/lansce_Dec2022).
The raw datafile is named [dec20.zip](../releases/download/lansce_Dec2022/dec20.zip) within the release.
Copy this file to the `./radiation_results` directory (where this file exists) and unzip it.
Unzipping these files will create a `tmp` directory that contains all of the extracted log files.


### To run:

Run ```make nontmr``` to obtain events for all non-tmr tests at once output in a text file.

Run ```make tmr``` to obtain events for all tmr tests at once output in a text file.



For events from an individual nontmr test, run ```make nontmr_(day, two digits)_(hour, two digits)_(minute, two digits)```, and for an individual tmr test, run ```make nontmr_(day, two digits)_(hour, two digits)_(minute, two digits)```

For example, to obtain the events of the tmr test on day 20, hour 8, starting at minute 5, run ```make tmr_20_08_05```

## Non-TMR Tests

^ File ^ Notes ^
| ---- | ----- |
| nontmr_16_15_52 | No events |
| nontmr_16_15_57 | No events |
| nontmr_16_16_11 | 2 speed events |     
| nontmr_16_19_34 | No events |     
| nontmr_16_19_51 | No events |     
| nontmr_16_19_52 | Repairable memory event at 20:55:34 (note 1, 2) |     
| nontmr_16_21_38 | Reboot problem (note 3) |
| nontmr_16_21_44 | note 1,4,2  |       
| nontmr_17_07_36 | |     
| nontmr_19_10_32 | |
| nontmr_16_15_52 | |     
| nontmr_17_08_30 | |


| nontmr_17_11_41 | |

Notes:
1. There was only one memory error in the system but the log reported multiple, periodic errors. This appears to be a bug in the main log (i.e., only one error, not multiple).
2. At the end of this run, we had a UART timeout. The script tried to repower and configure the board but it failed to configure and quit (script should try to reconfigure multiple times, maybe repower JCM?)
3. In this run it looks like it started out ok and had a few good BIST runs. Early in the run we had a UART timeout and tried recovering multiple ways (reset). It looked like the BIST was recovering but the script kept resetting as it didn't recognize a proper start. It appears that this run was cancelled manually (no log end message).
4. Different error message (BIST vs. software?)

appears that the script never was able to get the system running properly. The script kept resetting the processor causing it to start over 


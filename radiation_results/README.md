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
| nontmr_16_21_44 | note 1,4,2 |       
| nontmr_17_07_36 | 2 Uartbone reset events (note 5) |     
| nontmr_17_08_30 | 1 Uartbone reset event (note 5), Reboot problem (note 3), Unreadable characters at 09:00:18 (note 6), 2 speed events |
| nontmr_17_11_41 | Repairable memory event at 14:11:30 (note 1), 1 Uartbone reset event (note 5), 2 Netbooter resets (note 9), 1 timeout event at 14:17:02 (note 7), 1 speed event |
| nontmr_19_10_32 | Repairable memory event at 16:14:45 (note 10), 3 Uartbone reset events (note 5), 1 Netbooter reset (note 8), 3 speed events, Others (note 11) | 

| tmr_17_15_35 | 2 Repairable memory events at 16:11:51, 20:44:01 (note 1), 2 Uartbone resets (note 5), Others (note 12) |
| tmr_18_07_15 | No events |
| tmr_18_07_26 | 3 Repairable memory events at 12:43:22, 16:14:23, 18:48:48 (note 1), 1 Uartbone reset event (note 5) |
| tmr_18_20_01 | No events |
| tmr_18_21_03 | 1 Repairable memory event at 05:19:34 (note 1) |
| tmr_19_07_57 | No events |
| tmr_19_08_22 | No events |
| tmr_19_08_39 | No events |
| tmr_19_18_34 | 3 speed events, Other (note 13) |
| tmr_20_08_05 | 1 UARTbone reset event (note 5) |
| tmr_20_17_47 | No events |

Notes:
1. There was only one memory error in the system but the log reported multiple, periodic errors. This appears to be a bug in the main log (i.e., only one error, not multiple).
2. At the end of this run, we had a UART timeout. The script tried to repower and configure the board but it failed to configure and quit (script should try to reconfigure multiple times, maybe repower JCM?)
3. In this run it looks like it started out ok and had a few good BIST runs. Early in the run we had a UART timeout and tried recovering multiple ways (reset). It looked like the BIST was recovering but the script kept resetting as it didn't recognize a proper start, and the script never was able to get the system running properly. The script kept resetting the processor causing it to start over. It appears that this run was cancelled manually (no log end message).
4. Different error message (BIST vs. software?)
5. One or more UART timeouts occured where the ttyUSB device was closed and reopened, and a timeout reoccured. A UART bone reset was issued, and the BIST restarted successfully.
6. In this run, unknown characters were being printed out. After 15 seconds, the ttyUSB device was closed and reopened, after which unknown characters were still being printed out. After trying to recover in a few ways, the board was eventually repowered, and the JCM was reconfigured.
7. A UART timeout occured, but unlike other UART hangs, the bist simply recovered after the ttyUSB device was closed and reopened.
8. One or more UART timeouts occured, and the BIST did not recover after reopening the ttyUSB device nor after issuing a UART bone reset. The Netbooter repowered the board, and the JCM was reconfigured.
9. In this run, the Netbooter repowered the board on two different occasions, both related to note 8. However, on one of these occurances, it appears that Litex almost recovered after a UART bone reset, as the text for a partial reboot can be seen. The program still froze at this point for 10 seconds, after which the board was repowered. 
10. In this run, a variation of the problem in note 1 occured (in which the log file reported false multiple, periodic errors after only one occured). This time, however, random lines from the BIST output were also being recorded in the log file.
11. In this run, a few events of strange behavior occured. The first one occured at 13:51:48. The program started outputting null characters in multiples and in long lines. After the maximum of 10 bad data lines were recorded, the ttyUSB device reopened, and null characters still printed out. The Netbooter repowered the board after the BIST did not properly restart. The second occured at 18:05:30, where BIST numbers printed out in strange places. Again, after a few attempts to recover the BIST, the Netbooter repowered the board.
12. In this run, beginning at 06:20:46 and ending at 07:13:47 (the end of the test), the BIST stopped outputting numerical values for the statistics and started outputting '%lu' in their place, even though the title strings remained the same. Our attempts to recover from this did not work, as after 10 lines of bad data were output, a newline character was input and the bist restarted with outputting a title string marked as the first header. Thus, a cycle of restarting the BIST unsuccessfully occured until the end of the test.
13. In this run, a long line of 1's printed out at 03:05:36, along with three big numbers, each 825307441. The log recorded 5 unicode errors. Reopening the ttyUSB device did not stop this behavior, and the BIST eventually was restarted after a UART bone reset was issued. 






# Radiation Experiment Feedback

Obtain summary of feedback for CTRL radiation experiment.

## Non-TMR Tests

^ File ^ Notes ^
| ---- | ----- |
| nontmr_16_15_52 | No events |
| nontmr_16_15_57 | No events |

### To run:

Run ```make nontmr``` to obtain events for all non-tmr tests at once output in a text file.

Run ```make tmr``` to obtain events for all tmr tests at once output in a text file.



For events from an individual nontmr test, run ```make nontmr_(day, two digits)_(hour, two digits)_(minute, two digits)```, and for an individual tmr test, run ```make nontmr_(day, two digits)_(hour, two digits)_(minute, two digits)```

For example, to obtain the events of the tmr test on day 20, hour 8, starting at minute 5, run ```make tmr_20_08_05```


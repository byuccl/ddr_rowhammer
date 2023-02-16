# Radiation Experiment Feedback

Obtain summary of feedback for CTRL radiation experiment.

### To run:

Run ```make nontmr``` to obtain events for all non-tmr tests at once.

Run ```make tmr``` to obtain events for all tmr tests at once.



For events from an individual nontmr test, run ```make nontmr_(day, two digits)_(hour, two digits)_(minute, two digits)```, and for an individual tmr test, run ```make nontmr_(day, two digits)_(hour, two digits)_(minute, two digits)```

For example, to obtain the events of the tmr test on day 20, hour 8, starting at minute 5, run ```make tmr_20_08_05```


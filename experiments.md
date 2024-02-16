In this file, provide a summary of the various experiments that we have done from the start.
For each experiment provide the following:
* Provide a brief description of the goal of the experiemtn
* Indicate which board/memory was used for the experiment and what subset of the memory was tested
* Provide a small snippet of what the output file looks like
* Indicate where the data is currently located

# Experiment #1: December 2022 Radiation Test (Los Alamos)

# Experiment #2: July 2023 Radiation Test (Europe)

# Board Experiments since then:

Here is a description of all the experiments we've done with each board.

## Refresh tests (Nexys4ddr, Nexys Video, Antmicro)

* The goal of this experiment was to find bits easily flipped when writing to the memory, setting a specified refresh rate, waiting some time, and then checking the errors.

## Rowhammer tests (Nexys4ddr, Nexys Video, Antmicro)

* Tho goal of this experiment was to find bits on both boards vulnerable to the rowhammer effect.

## Logs for comparison

 - Scripts ([Nexys4ddr executable](https://github.com/byuccl/ddr_rowhammer/blob/refresh_change/beam-test/test_scripts/getAllErrorBitsFromRW_nexys4ddr.py), [Nexys Video executable](https://github.com/byuccl/ddr_rowhammer/blob/refresh_change/beam-test/test_scripts/getAllErrorBitsFromRW_nexys_video.py)) were made to compare the data between the BIST and the rowhammer tester. 

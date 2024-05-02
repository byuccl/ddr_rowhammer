
# Experiment #1: December 2022 Radiation Test (Los Alamos)

The goal of this experiment was to determine the defects that occur with the DRAM from radiation.
We tested with the nexys video and antmicro datacenter boards.
The results of our experiment are summarized [in this README](https://github.com/byuccl/ddr_rowhammer/tree/tr-ddrh-mjw/radiation_results#radiation-experiment-feedback) and the raw data from the bist we ran during this test is [here](https://github.com/byuccl/ddr_rowhammer/releases/tag/lansce_Dec2022). We parsed through the data, and all of our results are found in the [radiation_results](https://github.com/byuccl/ddr_rowhammer/tree/tr-ddrh-mjw/radiation_results) folder, where each log file shows how many errors occured reading memory, 

![image](https://github.com/byuccl/ddr_rowhammer/assets/83432874/7e268e56-8f36-4a1d-9268-0aec8da942a3)

The antmicro datacenter board we used is the one with two labels "Test" and "ddr" (id number 070), not the one labelled "linux soc" (id number 008).

![image](https://github.com/byuccl/ddr_rowhammer/assets/83432874/c2448998-88c5-48fb-887c-543e49521ebf)

The nexys video board we used is the one labelled BYU-ARTIX-026.

# Experiment #2: July 2023 ChipIR Radiation Test

The goal of this experiment was to determine the defects that occur with the DRAM from radiation, specifically if the number of errors increase as a result of the rowhammer effect and lower refresh rate, and if these errors correlate. 
We targeted the Nexys4DDR, Nexys Video, and antmicro datacenter boards.
The data from the bist we ran during this test is [here](https://github.com/byuccl/ddr_rowhammer/releases/tag/untagged-dae17d4e2af2286aa6d6). The sets of data we parsed and documented are on [this branch of the ddr_rowhammer repository.](https://github.com/byuccl/ddr_rowhammer/tree/radiation2023/radiation2023)

The summaries of the parsed data is under the radiation branch. In radiation2023 directory, you can find DDR2, DDR3, and DDR4 parse logs directories. In each one of those directories, you can find summaries about the errors, their types and some description about them under detailed summaries. The parsing script is also found under the same branch (radiation2023) and its called radiation_2023_parser.py

![img_0423](https://github.com/byuccl/ddr_rowhammer/assets/83432874/2eb5fc83-daf6-430a-b530-f36bc2f12a7e)


![IMG_0422](https://github.com/byuccl/ddr_rowhammer/assets/83432874/6e89d89c-8059-4c94-b656-4cd1870ddcc8)


We have labelled the three boards under radiation "Test". This is the Nexys4ddr board (labelled #57), the Nexys Video board (labelled "BYU-ARTIX-020"), and the antmicro datacenter board (labelled "ddr"; the "linux soc" board was for a different experiment not radiating the DDR memory).

TODO: expand description

Logs:
* DDR2 Logs: Fully detailed summaries for Stuck and Soft bits, SEFIs are not fully summarized but they are logged with their time of occurance under DDR2_Results.md
* DDR3 Logs: Detailed summaries for Stuck Bits. Soft errors and SEFIs are logged under DDR3_Results.md
* DDR4 Logs: Errors logged under DDR4_Results.md but not fully summarized

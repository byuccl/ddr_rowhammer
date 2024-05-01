# DDR Data Summary

The purpose of this page is to summarize the data that we have collected for refresh and rowhammer testing.
It also provides links to the raw data files.

## Boards

We are performing the various experiments on three different board types and multiple boards of each type.

* Nexys4DDR (DDR2)
  * Radiated board (has a label '#57')
  * Unradiated board (has a label 'ddr')
* NexysVideo (DDR3)
  * Unradiated board (BYU-Artix7-007)
  * Radiated board (BYU-Artix-020)
* AntMicro (DDR4)
  * Radiated board with a label 'linux-SOC' '#008'
  * Unradiated board with label '#010'
* DDR4 Memories for AntMicro
  * MEMAM: not radiated
  * MEM1: radiated
  * MEM2: unradiated

## Experiments

The experiments used to collect this data are described in detail [here](../experiments.md).

### Rowhammer tests

* Nexys4DDR:
  * completed all of bank #0 on board #57
  * completed all of bank #0 for board 'ddr' (non irradiated)
* NexysVideo:
  * completed all of bank #0 for Radiated board (BYU-Artix-020)
  * still running for Unradiated board (BYU-Artix7-007) (getting close to compelting)
* AntMicro:
  * #010/MEM1: up to row 18143 on bank 0
  * #010/MEM2: all of bank 0
  
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
  * completed all of bank #0 on board #57 (irradiated)
    * 7 files = {4.3 MB, 304 MB, 108.0 MB, 87.8 MB, 536.7 MB, 74.8 MB, 142.4 MB}
    * Compressed all together: 71.8 MB
  * completed all of bank #0 for board 'ddr' (non irradiated)
    * 1 file = 21.4 MB
    * Compressed all together: 1.1 MB
* NexysVideo:
  * completed all of bank #0 for Radiated board (BYU-Artix-020)
    * 15 files = {251.2 MB, 250.0 MB, 383.8 MB, 177.4 MB, 1.0 GB, 199.3 MB, 438.9 MB, 1.1 GB, 291.3 MB, 451.8 MB, 376.9 MB, 482.7 MB, 1.6 GB, 1.6 GB, 1.2 GB, 1.1 GB}
    * Compressed all together: 668.8 MB
  * completed rows 0 - 17771 of bank #0 (BYU-Artix7-007) (currently running)
    * 8 files = {1.4 GB, 9.7 MB, 977.1 MB, 191.8 MB, 109.3 MB, 106.6 MB, 993.0 MB, 1.2 GB}
    * Compressed all together: 351.4 MB
* AntMicro:
  * #010/MEM1: completed rows 0 to row 68550 of bank #0 (currenlty running)
    * 4 files - 5.3 GB, 2.7 GB, 3.4 GB, 290.1 MB
    * Compressed all together: 681.4 MB
  * #010/MEM2: completed all of bank #0
    * 4 files - 3.3 GB, 5.2 GB, 1.2 GB, 86.3 kB
    * Compressed all together: 534.7 MB
  

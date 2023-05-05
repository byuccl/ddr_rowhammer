
# Guide to our DRAM Bist

The commands we have edited / added to the bios and have actively used in our last radiation test are the following:

```
sdram_bist_pat <value>
sdram_bist <length> [<addr_mode>] [<data_mode>] [<write_mode>]
```

Other commands we added to the bios are the following:

```
sdram_gen_handler
sdram_chk_handler
sdram_bitslip_scrub
sdram_bitslip_set <module> <bitslip>
sdram_delay_scrub
sdram_delay_set
sdram_mr_scrub
```

Guide to LiteDRAM:

This is an example of a write, followed by a read, with the native protocol driven by the vexriscv cpu with the Alveo U280 board:

![image](https://user-images.githubusercontent.com/83432874/236324037-058adcdc-b427-431a-8326-fae1d834171f.png)

The native protocol works accordingly:
  1. The address is placed in the cmd.addr signal, and cmd.valid is set high. (In this case, this is a single write to addr = 0x0 and a single read from addr = 0x0400000.)
  - The cmd.we signal, 1 bit wide, controls whether the controller performs a read or write (1 for write, 0 for read)
  - On a burst transaction, for every clock cycle that cmd.ready is high (while setting cmd.valid high), a new address must be placed in cmd.addr. No need to specify anywhere the number of bursts to run. Set cmd.valid low when done adding addresses for the burst read or write. (This includes single reads and writes.)
  - The cmd.last signal is to be set high after running the last command, or set high on the last clock cycle in which both cmd.valid and cmd.ready are high when a write or read burst occurs. 
  - The signal cmd.first is not used.
  2. In all the examples I've seen for a write, wdata.valid is set high immediately after the first cycle both cmd.ready and cmd.valid are high. It is immediately set low once the number of cycles in which wdata.ready is high matches the number of cycles both cmd.ready and cmd.valid were set high. In the examples I've seen for a read, rdata.ready is always set high. 
  - Every cycle in which both wdata.ready and wdata.valid are high, wdata.data must be set to the desired value. 
  - The signal wdata.we is a write-enable mask. Each bit controls a byte in the data to be written. If the dram does not support byte-enabled reading/writing, this signal will do nothing.
  - Every cycle in which both rdata.ready and rdata.valid are high, valid data exists in rdata.valid.
  - The flush signal is only to be set high if a transaction is not taking place. It must be set low during the entire transaction. It is used by the wishbone-to-native converter in which the flush signal is set equal to the inverse of the wishbone's ~cyc signal.
  - The signals wdata.first, wdata.last, rdata.first, and rdata.last are not used.
  
  Note:
  - It appears that LiteDRAM added a 'lock' signal to this protocol; there is a description in crossbar.py on how it is used. As said in the notes, locks (cmd_layout.lock) make sure that, when a master starts a transaction with a given bank (which may include multiple reads/writes), no other bank will be assigned to it during this time. The arbiter (of a bank) considers a given master as a candidate for selection if:
     - given master's command is valid
     - given master addresses the arbiter's bank
     - given master is not locked
       * i.e. it is not during transaction with another bank
       * i.e. no other bank's arbiter granted permission for this master (with
         bank.lock being active)

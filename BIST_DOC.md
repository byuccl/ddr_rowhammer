
# Migen Notes

### LiteDRAM Bist Fifo

Migen, Litex, and LiteDRAM each have their own code to implement their own fifo. The one described here will be the one in litex>soc>interconnect>stream.py, called , as this is the version used in the DMA, used by the LiteDRAM Bist. 

![image](https://user-images.githubusercontent.com/83432874/236911630-1c5172f1-c5f1-447b-9130-3102bfa185e8.png)

This is the fifo running in the DMA reader, connected to the Bist checker that reads from the DRAM and checks the data. 
- The fifo has a sink object and a source object, and data travels from the sink to the source. Both the sink and source contains ```data```, ```ready```, and ```valid``` variables/signals.
- This specific fifo, although not shown, has a depth of 16. 
  - To fill up the fifo, for each clock cycle that sink.ready is high, the correct data must be set in sink.data, and sink.valid must be set high. 
  - To empty the data, for each clock cycle that source.valid is high, source.ready must be set high. 
  - If the fifo reaches the maximum depth, sink.ready will go low until data is used by the source.
  - An example of these being used is in LiteDRAM>frontend>dma.py.

# Guide to our DRAM Bist

The commands we have edited / added to the bios and have actively used in our last radiation test are the following:

```
sdram_bist_pat <value>
sdram_bist <length> [<addr_mode>] [<data_mode>] [<write_mode>]
```

- ```length```: defines the number of bytes to write. 
- ```addr_mode```: defines if the address should remain fixed the entire test (value 0), if the address should increment each time (value 1, starts at zero and increments by one),  or if random address values should be used (value 2).
- ```data_mode```: defines if the data to be written should be a fixed value (value 0), if the data value should increment each time (value 1), or if random data values should be used (value 2).
- ```write_mode```: defines if the bist should only read data (value 0), if the bist should perform one write and then a read (value 1), or if the bist should perform a burst write and then a burst read over and over again (value 2).

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

### Software

The following are CSR registers controlling the Bist via software:

  * sdram_generator.reset: A signal used to reset the state machine.
  * sdram_generator.base: The starting address that the bist should write to.
  * sdram_generator.end: The maximum DRAM address that the Bist should write to
  * sdram_generator.length: The number of DRAM words to write. (A DRAM word in this case is enough bytes to fill one transaction to the DRAM.)
  * sdram_generator.mode: The data mode. The data is created, written and read in the Bist state machine itself, not in software.
  * sdram_generator.start: The signal to start the generator state machine.
  * sdram_generator.done: A register to read. This helps us know if the generator state machine is finished.
  * sdram_generator.ticks: A register to keep track of the number of ticks throughout the burst write.
  * sdram_generator.pattern: A register to control the data pattern to write to the dram if the data mode is 'fixed'.
  * sdram_checker.reset: A signal used to reset the state machine. This also resets the error count.
  * sdram_checker.base: The starting address that the Bist should read from.
  * sdram_checker.end: The maximum DRAM address that the Bist should read from.
  * sdram_checker.length: The number of DRAM words to read.
  * sdram_checker.mode: The data mode. If the mode is fixed, the data is read from a csr register, otherwise it is read from a memory module.
  * sdram_checker.start: The signal to start the checker state machine.
  * sdram_checker.done: A register to read. This helps us know if the checker state machine is finished.
  * sdram_checker.ticks: A register to keep track of the number of ticks throughout the burst write.
  * sdram_checker.errors: A register to read that keeps track of the number of errors counted in the checker state machine.
  * sdram_checker.pattern: A register to control the data pattern to check after reading from the dram if the data mode is 'fixed'.

Our bist ran the following way:

- First, the command ```sdram_bist_pat 165``` was called. In hex, the value of 165 is 0xa5. This value was written to both the sdram_generator.pattern and sdram_checker.pattern CSR registers. It was replicated enough times and concatenated to fill the entire space of the DRAM controller data width.
- Next, the command ```sdram_bist 8192 1 0 2``` was issued.
  - The software first checked that the length of bytes, 8192, was a power of 2. The software also checked the length against a minimum, which was the number of bytes to fill one DRAM controller transaction. (For example, the minimum length allowed when running this program with the nexys video board was 16 bytes: the maximum amount for a one-burst write to the DRAM.) 
  - After the checks, and after the software initialized global error, length, and tick counters to zero, the software enetered a forever-running loop. An ```if``` statement checked on the beginning of each loop if the user inputed any character during execution, and if true, the statement ran a ```break``` command and exited the bist loop.
  - A new loop is entered into which starts the writing and reading. 
    - First, the CSR registers controlling the generator are updated. First, the register sdram_generator.reset is set high, then low, to reset the generator state machine. For the incrementing address mode, sdram_generator.base is first set to zero, sdram_generator.end is set to base + length, and sdram_generator.length is set to the length. The register sdram_generator.mode, the data mode, is set to 0, indicating the data is in a fixed data mode and should be checked by a CSR register. After this, the statement ```cdelay(100)``` is run, which delays the software program.

# Guide to LiteDRAM:

### Native protocol

This is an example of a write, followed by a read, with the native protocol driven by the vexriscv cpu with the Alveo U280 board:

![image](https://user-images.githubusercontent.com/83432874/236324037-058adcdc-b427-431a-8326-fae1d834171f.png)

Here is an example of a burst write with the bist: (The command run was ```sdram_bist 100 0```, where a hundred bursts occured with no random addressing)

![image](https://user-images.githubusercontent.com/83432874/236509942-5c885ffb-70dc-493b-8658-87fe66b89756.png)

Here is an example of a burst read with the bist, occuring a small time after this burst write:

![image](https://user-images.githubusercontent.com/83432874/236510439-30ca8725-f98f-4069-95b9-7778d9213499.png)

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
         
  - In all examples I've seen, with bist and with cpu, the lock signal has been set low.
  

  
## Tools (found in litedram.frontend)



### DMA

This is a class that takes a LiteDRAM port using the native or axi protocol and converts the signals into a smaller, simpler set of signals to be used. It includes a 'fifo' migen module with a default depth of 16. It is used by LiteDRAM's bist.

  - The bist would write 8192 bytes in a burst write, and then read the same amount back, incrementing the error counter every time the data read back did not match the data expected. (The controller would write 32 * 4 bits, 16 bytes, every DRAM controller transaction to the DRAM.)
  - The address mode was set to 1, on incrementing mode. The bist has two address signals, one for the writer and one for the reader. The writer would first start with its address at 0, and increment it by 1 every burst write. The reader would use its own address variable, starting at 
   - Global counter variables keeping track of the error counts and total write length, read length, number of ticks for writing, and number of ticks for reading were set to zero, 





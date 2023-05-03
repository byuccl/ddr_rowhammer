
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

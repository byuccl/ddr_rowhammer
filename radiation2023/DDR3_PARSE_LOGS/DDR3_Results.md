## Nexys Video 

We ran the continuous test 15 times, and the idle test 14 times, all from June 26 to July 2.
This summarizes the notable and/or major events during each script.
The tests will be shown in chronological order. 


### Continuous Test 1 (2023-06-26 16:44:23 - 16:50:40)

No events occurred. BIST ran normally

### IDLE Test 1 (2023-06-26 16:50:46 - 18:16:21)

No events occurred. BIST ran normally

### Continuous Test 2 (2023-06-26 18:18:24 - 2023-06-27 10:44:03)

No events occurred. BIST ran normally 

### IDLE Test 2 (2023-06-27 10:44:07 - 10:49:24)

No events occurred. BIST ran normally

### Continuous Test 3 (2023-06-27 15:55:40 - 15:56:14)

No events occurred. BIST ran normally

### Continuous Test 4 (2023-06-27 16:06:20 - 16:07:12)

No events occurred. BIST ran normally 

### Continuous Test 5 (2023-06-27 16:15:38 - 16:16:02)

No events occurred. BIST ran normally


### Continuous Test 6 (2023-06-27 16:21:18 - 16:23:34)

No events occurred. BIST ran normally

### IDLE Test 3 (2023-06-27 16:23:42 - 16:23:57)

No events occurred. BIST ran normally 

### Continuous Test 7 (2023-06-27 16:26:05 - 16:26:37)

No events occurred. BIST ran normally 

### Continuous Test 8 (2023-6-27 12:05:07 - 21:05:07)

Simulation was stopped 

### Continuous Test 9 (2023-06-27 21:09:34 - 21:09:58)

No events occurred. BIST ran normally

### IDLE Test 4 (2023-06-28 05:40:22 - 2023-06-29 01:46:32)

No events occurred. BIST ran normally 


### IDLE Test 5 (2023-06-29 08:54:59 - 09:54:05)

- At 9:12:9, there were 33554432 errors, and these errors were basically the addresses returning 0s instead of the written pattern. There was a timeout at 9:26:56 after the spike errors. 
  - The first timeout occured at 09:20:51, when a reading command was sent and only partial output came back. However, the UARTBONE was read and showed the BIST to be in the IDLE/beginning state. A UARTBONE reset was issued successfully.
  - The output from the reading command sent at 09:21:09 stopped after 09:21:10. After sending another read command and receiving no output, the UARTBone showed the BIST was in the state of burst reading and counting errors (perhaps stuck in the reading state?).
- The first error that shows bit flips was at 9:37:24 and gone 2 seconds after
- New error showed up at 9:42:27 and was gone a seconds after
- The simulation timed out after that 
  - The reading command was sent, the output partially said "Command not found", and the BIST was in the IDLE/beginning state at the time of the timeout.

- Besides the times when zeros were found, there were 2 bit errors found:
  - 0x0b9b551:  a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a7a5
    - Appeared 9:37:24 - Gone 9:37:26
    - 1/5 error groups
    - Bit error 
  - 0x0852ab4:  a5a5a7a5 a5a5a5a5 a5a5a5a5 a5a5a5a5
    - Appeared 9:42:27 - Gone 9:42:28 (it was gone at the last error group by end of test)
    - 1/5 error groups 
    - Bit error 



### IDLE Test 6 (2023-06-29 10:00:28 - 10:51:13)

- 4096 Errors were found at 10:05:47 and were all gone at 10:05:52 after a following write to the whole memory 
- Between 10:20:55 and 10:21:01, 4104 errors were found and they were gone after a write to the whole memory
- Between 10:26:02 and 10:26:08, 4096 errors were found and they were gone after a write to the whole memory 
- All of the errors were found once so there was no specific pattern found 


### IDLE Test 7 (2023-06-29 10:54:26 - 15:13:20)

- Between 11:39:52 - 11:39:55, there were 33554432 errors and this is because the pattern was messed up. The expected pattern was a5a5a525 a5a5a525 a5a5a525 a5a5a525 which is different to the written pattern a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5
- At 11:39:57, there were 4088 new errors. The expected pattern was still different than the written pattern, however, there were errors that had bit flips. There was a pattern for these errors, they were at address 0x1000000, and every address adding 0x0000400 
- All errors were gone at 11:40:02
- There were 3 timeouts between 11:45:03 - 11:46:13
  - Two ways to reset the BIST failed, and after the third timeout, the board was repowered.
  - The timeout at 11:45:33 occured because one of the reading commands was not recognized (partial output said "Incorrect count"). The BIST was in the IDLE/beginning state.
- There were 4096 new errors at 12:17:45. However, only one error was printed because there was a timeout. There were 5 timeouts between 12:17:45 and 12:41:25
  - At 12:18:15, the output stopped while the reader was in the middle of printing out errors. The BIST was in the state in which a read command had been sent to the controller and the BIST was now waiting for a response. Perhaps it was stuck waiting for a response. Reconnecting to the ttyUSB device and issuing a UARTBone reset both failed, and the board was repowered.
  - At 12:33:59, the output stopped in the middle of burst reading/counting errors, and at the timeout the UARTBone shows the BIST was in the state of burst reading and counting errors. Perhaps the BIST was stuck in this state. Reconnecting to the ttyUSB device and issuing a UARTBone reset both failed (resulted in incomplete rebooting output), and the board was repowered.
- Between 12:51:29 - 12:51:34, there were 8188 new errors that were gone after. The pattern noticed was that the errors showed up every 0x0000400 address
- Between 13:09:34 - 13:09:35, a new error and it was gone as well
- At 13:31:12, there were 2048 errors in addresses 0x20080-0x186077f and these errors were weird. The data read was completely different than the pattern. For example, the data read at address 0x0020080 is: 1547d5d 7f363c05  476fa3f 3f747a0f. All of these errors were gone after a bist write. 
- Similar pattern appeared at 13:36:20 with 1024 errors. For example, the data read at address 0x0000001 is: dcad392 fd75defc 81c04f4c 67c3657f 
These errors were gone after a bist write
- There were 2 timeouts after that. 
  - At 13:47:31, output stopped in the middle of a reading command. The BIST was in the state of burst reading and counting errors. A UARTBOne reset resulted in partial output before timing out again, and the board was repowered.
- At 13:52:44, there were 9204 errors that were normal bit flips compared to the data written. The errors were gone after a bist write.
- There was a timeout at 13:59:12
  - The first argument in the reading command was not recognized (output: "Incorrect beginning_address"). Reconnecting to the ttyUSB device and issuing a UARTBone reset both failed. There was also a UARTBone Timeout that occured here. The BIST was likely in the IDLE state, but we don't know for sure. The board was eventually repowered.
- There were 8204 errors found at 14:19:20, but there were 2 timeouts during the read. All of these errors were gone after the timeout. 
  - The timeout at 14:19:50 occured near the end of the reading command printing out errors. The BIST state variable said it was in the continuous-running BIST mode waiting to display a summary of data. Either the register holding the BIST state was corrupted, or some crazy transition occured from one state to another that wasn't supposed to happen. The board was eventually repowered.
- 4101 errors were found at 14:30:35 and were gone after a bist write
- At time 14:30:42, we got an error at address 0x15925ef which was: a5a5a5a5 a5e5a5a5 a5a5a5a5 a5a5a5a5. This was the only error found until 4105 new errors were found at 15:11:30. Those errors were gone after a bist write but the only error that stayed there was the one at address 0x15925ef. This error stayed there until the end of the test.

- 0x15925ef:  a5a5a5a5 a5e5a5a5 a5a5a5a5 a5a5a5a5
  - Appeared 14:30:35 - Gone 14:54:40
  - Appeared 14:59:41 - Gone 14:59:43
  - Appeared 15:05:10 - Gone 15:06:29
  - Appeared 15:11:36 - Gone 15:13:01 (End of test)
  - 637/649 error groups
  - Stuck bit
### IDLE Test 8 (2023-06-29 15:13:39 - 15:25:52)
- The error from the previous test was still showing up. It was gone at 15:19:13, and it showed back up at time 15:24:14 and stayed there until the end of the test

- 0x15925ef:  a5a5a5a5 a5e5a5a5 a5a5a5a5 a5a5a5a5
  - Appeared 15:18:56 - Gone 15:19:13
  - Appeared 15:24:14 - Gone 15:25:52 (It was gone by the end of the test)
  - 64/64 error groups
  - Stuck bit

### Continuous Test 10 (2023-06-29 15:30:26 - 19:37:45)
- The error at address 0x15925ef showed up at the beginning of the test
- 4089 errors were found at time 15:39:10 and were gone after a bist write but the error at the beginning is still there 
- At 16:15:48, 3410 new errors were found and the original error was gone until it came back at 16:15:54 with all the errors gone after a bist write 
- Starting at 16:34:41, a series of timeouts occur. All of them happen after the bist is closed and restarted. Each time, the BIST recovers after a UARTBOne-issued reset, but times out once the BIST is closed again. The BIST is always in the IDLE/beginning state for each of these timeouts. After 15 of these, the single error disappears for a short time until it comes back, and the bist closes, and a timeout occurs in which the board is repowered. Timeouts no longer occur after this repower.
- 3341 new errors showed up at 17:00:20, and the original error is gone but again, it is found at time 17:01:38 when the other errors were gone after the bist write

- The same thing keeps happening throughout the test, whenever there are a lot of errors, the error at address 0x15925ef is gone but then when the other errors are gone, the error shows up again. 

- At time 17:27:13, there were 33554432 errors with the error at address 0x15925ef gone. The number of errors stayed the same with the errors at the same addresses but with more bit flips. 

- 0x15925ef:  a5a5a5a5 a5e5a5a5 a5a5a5a5 a5a5a5a5
  - Appeared 15:30:42 - Gone 16:15:48
  - Appeared 16:15:54 - Gone 17:00:20
  - Appeared 17:01:38 - Gone 17:05:08
  - Appeared 17:05:31 - Gone 17:07:09 
  - Appeared 17:08:33 - Gone 17:27:13
  - 3615/5022 error groups
  - Stuck bit
### IDLE Test 9 (2023-06-29 19:37:56 - 07:51:52)

- The error at address 0x15925ef was still showing up. It showed up around 75 times during this test. 
- Another error that showed up for a significant number of times is at address 0x15ca824 and the error was: a5a5a5a5 a5ada5a5 a5a5a5a5 a5a5a5a5
- Also, during this test, there were 18 timeouts. 
  - Most of the time, the BIST was in the IDLE state during a timeout. Once, it was stuck in a state displaying errors. Another time, the BIST was stuck waiting for the controller after having sent it a request to read an address while reading errors. Lastly, one other time happened where the BIST was stuck in a state that both read data and counted the errors in a burst read.
- At 20:08:41, 4122 errors were found and had more bit flips at 20:13:46. The parser shows them gone, and shows new errors found but they are the same addresses but with more bit flips
- At 20:18:51, there were 5146 errors, the new errors were weird errors that are not similar to the bit flips seen. For example, the error found at address 0x063aa80 is: 81d0162 9d031673 bc1d82bd ad45bb32. These errors were gone after a bist write at 20:23:57. But similar weird errors showed up at the same time, however, there was a timeout during the read. All these errors were gone at 20:24:05 after a bist write


- There was an error at address 0x171de1e that kept showing up, and then is gone after a bist write 

- The weird errors kept showing up during the test and were gone after some writes. The same time those weird errors were showing up, there were some errors with bit flips showing up as well. 

- At 7:03:06, there were 33554432 errors and they were gone at 7:40:20

- The test finished with 8182 errors

### IDLE Test 10 (2023-06-30 8:19:06 - 17:29:25)
- This is the smoothest test so far, although it ran for 9 hours. It did not have any timeouts at all. 
- This test only had 2 main errors; The error at address 0x15925ef (137 times)and the another error at address 0x05e250e (68 times) which had the following data read: a5ada5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5

- 0x15925ef:  a5a5a5a5 a5e5a5a5 a5a5a5a5 a5a5a5a5
  - Appeared 8:19:22 - Gone 17:29:24 (End of test)
  - 137/137 error groups
  - Stuck bit

- 0x05e250e:  a5ada5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5
  - Appeared 8:19:22 - Gone 9:20:09
  - Appeared 9:55:19 - Gone 10:00:26
  - Appeared 11:10:48 - Gone 11:20:58
  - Appeared 11:31:00 - Gone 11:41:10
  - Appeared 12:06:18 - Gone 12:21:31
  - Appeared 12:41:35 - Gone 12:41:39
  - Appeared 12:51:42 - Gone 13:01:52
  - Appeared 13:26:59 - Gone 13:42:12
  - Appeared 14:02:16 - Gone 14:02:20
  - Appeared 14:17:24 - Gone 14:22:31
  - Appeared 14:32:33 - Gone 14:42:43
  - Appeared 14:52:45 - Gone 16:03:41
  - Appeared 16:08:42 - Gone 16:23:55
  - Appeared 16:28:56 - Gone 16:44:09
  - Appeared 17:29:24 - Gone 17:29:24 (End of test)
  - 68/137 error groups
  - Stuck bit 
### IDLE Test 11 (2023-06-30 17:33:24 - 20:14:15)
- The error at address 0x12925ef hs been found 19 teams during this test, and the error at address 0x05e250e was found 14 times. 
- This test timed out 43 times 
  - In the first timeout, the BIST was starting the reading command and no output came out. The BIST was in the idle state. After the board was repowered, the next one happened 5 min afterwards, the same thing happened: the reading command was sent and no output came out. The BIST was in an error-reading state. The next time, the reader command was started and the BIST was in a writing state. Afterwards, the BIST was stuck in a reading state and timeouts happened over and over again.
- At time 18:09:00, there were 5122 errors and these were the weird errors that have just random values that is no where near the pattern written. These errors were gone at 18:14:12
- This pattern just kept happening the same as some previous tests,teh weird errors show up and then they are gone. But they show up again after some time

- 0x15925ef:  a5a5a5a5 a5e5a5a5 a5a5a5a5 a5a5a5a5
  - Appeared 17:33:38 - Gone 17:53:43
  - Appeared 17:53:49 - Gone 17:58:50
  - Appeared 18:14:12 - Gone 18:34:23
  - Appeared 18:34:31 - Gone 18:39:34
  - Appeared 18:56:07 - Gone 19:27:52
  - Appeared 19:34:10 - Gone 19:39:11 (End of test)
  - 19/29 error groups
  - Stuck bit
- 0x05e250e:  a5ada5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5
  - Appeared 18:14:12 - Gone 18:56:07
  - Appeared 19:07:21 - Gone 19:22:51
  - Appeared 19:39:11 - Gone 19:39:11 (End of test)
  - 14/29 error groups
  - Stuck bit


### IDLE Test 12 (2023-06-30 20:14:57 - 2023-07-01 07:51:28)
- At time 21:07:38, the errors where the data read is random and so different than the pattern written to the DRAM showed up, and during the read of the errors, there was a timeout. 
- At time 5:19:57, there were 16778243 errors and these errors were because the data read from the addresses was just 0s or 1000. These errors were done but they came back at 5:35:19. 
- The error we had before at address 0x15925ef was found 88 times. 
- Error at address 0x05e250e was found 72 times 
- Error at address 0x0e7748f was found 72 times
- Error at address 0x0ea11eb was found 25 times
- Error at address 0x11bb43c was found 12 times 
- There were 25 time outs during this test 
- There were a lot of times where the test timed out while reading the errors. That happened especially during the times when there were the weird errors. 

- 88:  0x15925ef:  a5a5a5a5 a5e5a5a5 a5a5a5a5 a5a5a5a5
  - Appeared 20:15:14 - Gone 20:40:31
  - Appeared 20:55:52 - Gone 21:07:38
  - Appeared 21:07:38 - Gone 21:12:46
  - Appeared 21:12:48 - Gone 21:30:24
  - Appeared 21:40:42 - Gone 22:00:56
  - Appeared 22:01:05 - Gone 22:42:48
  - Appeared 22:49:35 - Gone 22:59:38
  - Appeared 23:09:54 - Gone 0:00:14
  - Appeared 0:12:12 - Gone 1:09:13
  - Appeared 1:24:37 - Gone 1:36:42
  - Appeared 1:49:12 - Gone 1:59:17
  - Appeared 2:09:39 - Gone 2:29:13
  - Appeared 2:44:43 - Gone 2:49:44
  - Appeared 3:10:06 - Gone 3:20:12
  - Appeared 3:32:09 - Gone 4:24:00
  - Appeared 4:39:21 - Gone 5:09:43
  - Appeared 5:09:43 - Gone 5:14:52
  - Appeared 5:47:28 - Gone 6:02:36
  - Appeared 6:07:48 - Gone 6:17:59
  - Appeared 6:17:59 - Gone 6:23:07
  - Appeared 6:28:23 - Gone 6:57:02
  - Appeared 6:57:02 - Gone 7:02:11
  - Appeared 7:08:57 - Gone 7:13:59
  - Appeared 7:29:23 - Gone 7:34:26
  - Appeared 7:51:26 - Gone 7:51:26 (End of test)
  - 88/162 error groups
  - Stuck bit

- 72:  0x05e250e:  a5ada5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5
  - Appeared 20:15:14 - Gone 20:35:29
  - Appeared 20:55:52 - Gone 21:02:37
  - Appeared 21:07:38 - Gone 21:12:46
  - Appeared 21:12:48 - Gone 21:12:54
  - Appeared 21:20:18 - Gone 21:35:30
  - Appeared 21:45:43 - Gone 22:17:31
  - Appeared 22:22:32 - Gone 22:42:48
  - Appeared 1:49:12 - Gone 2:49:44
  - Appeared 3:10:06 - Gone 4:24:00
  - Appeared 4:39:21 - Gone 5:09:43
  - Appeared 5:09:43 - Gone 5:19:57
  - Appeared 5:47:28 - Gone 6:02:36
  - Appeared 6:07:48 - Gone 6:17:59
  - Appeared 6:17:59 - Gone 6:57:02
  - Appeared 6:57:02 - Gone 7:02:11
  - Appeared 7:08:57 - Gone 7:19:07
  - Appeared 7:29:23 - Gone 7:51:26 (End of test)
  - 72/162 error groups
  - Stuck bit
- 72:  0x0e7748f:  a5a5a5a5 a5a5a585 a5a5a5a5 a5a5a5a5
  - Appeared 21:07:38 - Gone 21:12:46
  - Appeared 21:12:48 - Gone 21:20:18

  NOT DONE YET
- 25:  0x0ea11eb:  a5a5a5a5 a5a5a5a5 a5ada5a5 a5a5a5a5
  - 
- 12:  0x11bb43c:  a5a5a5a5 a5a5ada5 a5a5a5a5 a5a5a5a5
  - 

### Continuous Test 11 (2023-07-01 07:54:08 - 07:55:36)
- The error we had before at address 0x15925ef was found 21 times. 
- Error at address 0x05e250e was found 22 times 
- Error at address 0x0e7748f was found 21 times
- There were no timeouts during this test

- 0x05e250e:  a5ada5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5
  - Appeared 7:54:23 - Gone 7:55:36 (End of test)
  - 22/22 error groups
  - Stuck bit

- 0x0e7748f:  a5a5a5a5 a5a5a585 a5a5a5a5 a5a5a5a5
  - Appeared 7:54:23 - Gone 7:55:36 (It was gone at the last error group by the end of the test)
  - 22/22 error groups
  - Stuck bit

- 0x15925ef:  a5a5a5a5 a5e5a5a5 a5a5a5a5 a5a5a5a5
  - Appeared 7:54:23 - Gone 7:55:36 (It was gone at he last error group by the end of the test)
  - 22/22 error groups
  - Stuck bit

### IDLE Test 13 (2023-07-01 07:57:44 - 15:49:34)
- The test timed out 17 times 
- There were some errors that were just some random bits that do not look like the pattern written to the DRAM 
- Besides those errors, the following errors were found: 
    - 0x0e7748f was found 53 times
    - 0x15925ef was found 46 times
    - 0x0a7748f was found 41 times (a5a5a5a5 a5a5ada5 a5a5a5a5 a5a5a5a5)
    - 0x11bb43c was found 41 times 
    - 0x01e250e was found 31 times (a5ada5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5)
    - 0x05e250e was found 14 times 
    - 0x01e2511 was found 11 times (a5ada5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5) and 6 times (0xa52da5a5 a525a5a5 a525a5a5 a525a5a5)
    - 0x11925ef was found 6 times  

- At 13:57:09, 12550 errors were found. It looks like these addresses had a lot of bit flips that made the data read really different than the pattern written. 

- At 14:07:21, something unexpected happened with the test. There was a change in the address width from 25 to 05 and the data width from 118 to 08. This made it read addresses 0-0f. The data expected changed to 05 05 05 05. The number of errors was zero but it showed some errors which somehow were all in address 0x0000000. The same problem did not go away and stayed until 14:42:58. Then it happened to address 0x0000002 and stayed like that until there was a unicode error at 14:53:12 and the whole thing rebooted 

- The test was fine after that until 15:28:57 where we got the errors that are not similar to the pattern written at all 



### Continuous Test 12 (2023-07-01 16:22:26 - 16:22:44)
- Board was not able to connect. Cannot find serial device

### Continuous Test 13 (2023-07-01 16:23:07 - 21:07:26)
- At 16:58:21, the test says that there were 2 errors found but there 4098 errors found. The same thing happened at 17:10:26 where it says that there are 2 errors but there were 2050 errors showing up. 
- At 18:02:13, there were 769 errors found and they were just the random bits errors
- At 18:33:19, there were 310141 errors found between addresses 0x0 and 0x1ffff80, but the number of errors increased to 33554432 errors but it went down to 1 error at 19:11:57 after a timeout at 19:11:55 
- The error at address 0x0e7748f was found 10526 times
- The error at address 0x15925ef was found 1621 times 
- The test had 5 timeouts 


### Continuous Test 14 (2023-07-01 12:26:36 - 2023-07-02 07:59:14)
- Until 0:22:35, there were at most 2 errors showing up. Then at that time, there were 14757 errors found and they were gone 5 seconds later 

- At 0:23:07, there were 258 errors found and these are the errors that are just random bits read that are so different than the pattern. 

- At 0:29:06, there were 33554432 errors found and they stayed there until 0:43:14 as there was a timeout at 0:43:12. The 33554432 were found again at 5:00:32. Between those times, there were mainly 3 errors and there would be 4000 others from time to time. The number of errors went back to 2 at 5:34:40. 
- At 7:08:18, there were 513 errors found and these are the errors that are just random bits read that are so different than the pattern. 
- The following were the most frequent errors during this test: 
        14079 |   0x0e7748f:  a5a5a5a5 a5a5a585 a5a5a5a5 a5a5a5a5
         3921 |   0x1d83bab:  a5a5a5a5 ada5a5a5 a5a5a5a5 a5a5a5a5
         2759 |   0x0ea11eb:  a5a5a5a5 a5a5a5a5 a5ada5a5 a5a5a5a5
          576 |   0x0e7748f:  a5a5a5a5 a585a5a5 a5a5a5a5 a5a5a5a5


### Continuous Test 15 (2023-07-02 08:01:03 - 18:59:58)
- Until 13:00:38, there were mostly the same 2-3 errors found, and there were around 4000 errors found from time to time. At this time, the weird random errors were found. 
- The reason the parser is showing unexpected data printed or timeout occured is because the speed of reading is faster than what the others had

- The following were the most frequent errors during this test: 
        7625 |   0x0e7748f:  a5a5a5a5 a5a5a585 a5a5a5a5 a5a5a5a5
        7399 |   0x0129cb1:  a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a1
        2969 |   0x1ef1d5c:  a5e5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5


### IDLE Test 14 (2023-07-02 19:10:18 - 2023-07-03 08:23:33)
- At 0:48:24, there were 5122 errors that were a mix of just the random bits read which are way different than the pattern written to the DRAM and some bit flips 
- At 02:04:34, there were 33554432 errors found. These errors were just the DRAM returning zeros. For example, address 0x0000004 returned 0 0 0 0. another example is from address 0x000027e, it returned 1000 0 0 0. These errors were gone at 2:11:41 after a write to the DRAM 
- At 04:09:08, there were 1225014 between addresses 0x0 - 0x1ffff83
- The following were the most frequent errors during this test:
            119 |   0x0129cb1:  a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a1
            83 |   0x0769724:  a5a5a5a5 a5a525a5 a5a5a5a5 a5a5a5a5
            12 |   0x022eca3:  a5a5a5a5 a5a5a5a5 85a5a5a5 a5a5a5a5


### Most vulnerable addresses
- 0x0e7748f 
- 0x1d83bab
- 0x0ea11eb
- 0x0129cb1
- 0x1ef1d5c
- 0x15925ef
- 0x05e250e
- 0x12925ef
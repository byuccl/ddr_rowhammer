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
- The first error that shows bit flips was at 9:37:24 and gone 2 seconds after
- New error showed up at 9:42:27 and was gone a seconds after
- The simulation timed out after that 



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
- There were 4096 new errors at 12:17:45. However, only one error was printed because there was a timeout. There were 5 timeouts between 12:17:45 and 12:41:25
- Between 12:51:29 - 12:51:34, there were 8188 new errors that were gone after. The pattern noticed was that the errors showed up every 0x0000400 address
- Between 13:09:34 - 13:09:35, a new error and it was gone as well
- At 13:31:12, there were 2048 errors in addresses 0x20080-0x186077f and these errors were weird. The data read was completely different than the pattern. For example, the data read at address 0x0020080 is: 1547d5d 7f363c05  476fa3f 3f747a0f. All of these errors were gone after a bist write. 
- Similar pattern appeared at 13:36:20 with 1024 errors. For example, the data read at address 0x0000001 is: dcad392 fd75defc 81c04f4c 67c3657f 
These errors were gone after a bist write
- There were 2 timeouts after that. 
- At 13:52:44, there were 9204 errors that were normal bit flips compared to the data written. The errors were gone after a bist write.
- There was a timeout at 13:59:12
- There were 8204 errors found at 14:19:20, but there were 2 timeouts during the read. All of these errors were gone after the timeout. 
- 4101 errors were found at 14:30:35 and were gone after a bist write
- At time 14:30:42, we got an error at address 0x15925ef which was: a5a5a5a5 a5e5a5a5 a5a5a5a5 a5a5a5a5. This was the only error found until 4105 new errors were found at 15:11:30. Those errors were gone after a bist write but the only error that stayed there was the one at address 0x15925ef. This error stayed there until the end of the test 


### IDLE Test 8 (2023-06-29 15:13:39 - 15:25:52)
- The error from the previous test was still showing up. It was gone at 15:19:13, and it showed back up at time 15:24:14 and stayed there until the end of the test


### Continuous Test 10 (2023-06-29 15:30:26 - 19:37:45)
- The error at address 0x15925ef showed up at the beginning of the test
- 4089 errors were found at time 15:39:10 and were gone after a bist write but the error at the beginning is still there 
- At 16:15:48, 3410 new errors were found and the original error was gone until it came back at 16:15:54 with all the errors gone after a bist write 
- 3341 new errors showed up at 17:00:20, and the original error is gone but again, it is found at time 17:01:38 when the other errors were gone after the bist write

- The same thing keeps happening throughout the test, whenever there are a lot of errors, the error at address 0x15925ef is gone but then when the other errors are gone, the error shows up again. 

- At time 17:27:13, there were 33554432 errors with the error at address 0x15925ef gone. The number of errors stayed the same with the errors at the same addresses but with more bit flips. 

### IDLE Test 9 (2023-06-29 19:37:56 - 07:51:52)

- The error at address 0x15925ef was still showing up. It showed up around 75 times during this test. 
- Another error that showed up for a significant number of times is at address 0x15ca824 and the error was: a5a5a5a5 a5ada5a5 a5a5a5a5 a5a5a5a5
- Also, during this test, there were 18 timeouts. 
- At 20:08:41, 4122 errors were found and had more bit flips at 20:13:46. The parser shows them gone, and shows new errors found but they are the same addresses but with more bit flips
- At 20:18:51, there were 5146 errors, the new errors were weird errors that are not similar to the bit flips seen. For example, the error found at address 0x063aa80 is: 81d0162 9d031673 bc1d82bd ad45bb32. These errors were gone after a bist write at 20:23:57. But similar weird errors showed up at the same time, however, there was a timeout during the read. All these errors were gone at 20:24:05 after a bist write


- There was an error at address 0x171de1e that kept showing up, and then is gone after a bist write 

- The weird errors kept showing up during the test and were gone after some writes. The same time those weird errors were showing up, there were some errors with bit flips showing up as well. 

- At 7:03:06, there were 33554432 errors and they were gone at 7:40:20

- The test finished with 8182 errors

### IDLE Test 10 (2023-06-30 8:19:06 - 17:29:25)
- This is the smoothest test so far, although it ran for 9 hours. It did not have any timeouts at all. 
- This test only had 2 main errors; The error at address 0x15925ef (137 times)and the another error at address 0x05e250e (68 times) which had the following data read: a5ada5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5


### IDLE Test 11 (2023-06-30 17:33:24 - 20:14:15)
- The error at address 0x12925ef hs been found 19 teams during this test, and the error at address 0x05e250e was found 14 times. 
- This test timed out 43 times 
- At time 18:09:00, there were 5122 errors and these were the weird errors that have just random values that is no where near the pattern written. These errors were gone at 18:14:12
- This pattern just kept happening the same as some previous tests,teh weird errors show up and then they are gone. But they show up again after some time


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


### Continuous Test 11 (2023-07-01 07:54:08 - 07:55:36)
- The error we had before at address 0x15925ef was found 21 times. 
- Error at address 0x05e250e was found 22 times 
- Error at address 0x0e7748f was found 21 times
- There were no timeouts during this test


### IDLE Test 13 (2023-07-01 07:57:44 - 15:49:34)
- The test timed out 17 times 
-  
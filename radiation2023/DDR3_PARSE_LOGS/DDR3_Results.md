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
- Between 12:51:29 - 12:51:34, there were 8188 new errors that were gone after. 

STILL NOT DONE 

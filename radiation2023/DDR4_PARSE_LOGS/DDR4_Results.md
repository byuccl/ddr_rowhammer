## Antmicro Data Board 

### Idle Test 1 ( 2023-06-26 16:47:09 - 2023-06-26 16:47:37 )

No output from BIST. Appears that ttyUSB device could not be found by software, and script closed in the Terminating State.

### Idle Test 2 ( 2023-06-26 16:48:14 - 2023-06-26 16:48:43 )

No output from BIST. Appears that ttyUSB device could not be found by software, and script closed in the Terminating State.

### Idle Test 3 ( 2023-06-26 16:49:01 - 2023-06-26 18:15:31 )

No events occured. BIST ran normally.

### Idle Test 4 ( 2023-06-27 10:43:21 - 2023-06-27 10:49:08 )

No important events, although at one point it appeared that the BIST restarted because the Litex prompt was not recognized. The USB device was simply closed and reopened.
No errors occured.

### Idle Test 5 ( 2023-06-27 16:22:22 - 2023-06-27 16:22:49 )

No events occured. BIST ran normally.

### Idle Test 6 ( 2023-06-28 05:11:59 - 2023-06-29 01:48:40 )

The program ran from 05:11:59 - 05:17:30 and appeared to stop until 01:08:12 the next day. After that, it ran up till 01:48:40.
No errors occured.

### Idle Test 7 ( 2023-06-29 08:56:03 - 2023-06-29 08:56:30 )

No events occured. BIST ran normally.

### Idle Test 8 ( 2023-06-29 08:57:06 - 2023-06-29 09:41:49 )

Events:
- The first errors were recorded when the reader ran at 09:12:40. There were two that kept occuring at addresses 0x89b13f1 and 0xf8cefcf.
- This test was run with the reader running, and the writer running if errors were present. We had DRAM recovery commands running after every three consecutive reads with errors.
- The number of errors in the beginning ranged from 2 - 6.
- A UART timeout occured after starting the Writer and receiving no input. After simply closing and reopening the ttyUSB device, the writer and reader both successfully ran, and the error count went up to about 4100 errors.
- Another UART timeout occured for the same reason: sending a writer command and receiving no output.
- Four more UART timeouts occured when starting the reader and not receiving matching output. It appeared that the BIST reader was running longer than 30 seconds to print out all the errors, and our pexpect script treated this as a timeout when no litex prompt appeared. After reopening the ttyUSB device and running the reader, the same thing happened, and our scripts repowered the board on the second timeout. The board was repowered after each of these timeouts. 
- The number of errors near the end ranged from 4 - 5.
- At the end of the test, the ttyUSB devices were not found and the pexpect script terminated.

### Idle Test 9 ( 2023-06-29 09:57:29 - 2023-06-29 09:57:48 )

No output from BIST. Appears that ttyUSB device could not be found by software, and script closed in the Terminating State.

### Idle Test 10 ( 2023-06-29 10:00:36 - 2023-06-29 10:00:55 )

No output from BIST. Appears that ttyUSB device could not be found by software, and script closed in the Terminating State.

### Idle Test 11 ( 2023-06-29 10:55:31 - 2023-06-29 11:07:32 )

Events:
- We had the same problem in this test as in Idle Test 8, in that timeouts occured because the BIST reader was running longer than 30 seconts to print out all the errors. Because it took too long, our pexpect scripts treated this like a timeout, and after each UART timeout, the ttyUSB device was reset, and the reader took too long again, thus the board was repwered. 
- The number of errors ranged from 9 - 12.

### Idle Test 12 ( 2023-06-29 19:41:19 - 2023-06-29 19:47:07 )

Events:
- Same problem as previous test. Board kept repowering.
- The number of errors ranged from 19 - 26.

### Idle Test 13 ( 2023-06-29 19:48:35 - 2023-06-29 19:53:14 )

Events:
- Same problem as previous test. Board kept repowering.
- The number of errors ranged from 21 - 24.

### Idle Test 14 ( 2023-06-29 20:05:03 - 2023-06-29 20:05:13 )

No BIST output. Appears to be manually closed.

### Idle Test 15 ( 2023-06-29 20:05:33 - 2023-06-30 07:55:02 )

Events:
- Much smoother test. The UART delay was set to 60 seconds instead of 30. 3 UART timeouts occured after sending a reading/writing command and getting no output. 
- The test runs the writer once. Then the reader runs every five minutes. If there are 5 consecutive errors after the reader runs, the writer runs once before the reader runs again.
- The number of errors ranged from 34 - 2497522.
- Beginning at 03:42:32 and lasting until the end of the test, the entire DRAM address space was recorded as having errors.

### Idle Test 16 ( 2023-06-30 08:19:49 - 2023-06-30 17:29:49 )

Events:
- An End Of File exception occured during BIST execution. The board was repowered. Other than this exception, this test ran very smoothly. 
- The number of errors ranged from 35 - 93. 

### Idle Test 17 ( 2023-06-30 17:33:34 - 2023-06-30 20:12:43 )

Events:
- No timeouts or exceptions during the entire test, very smooth.
- The number of errors ranged from 53 - 4944937.

### Idle Test 18 ( 2023-06-30 20:13:58 - 2023-07-01 07:50:36 )

Events:
- Again, no UART timeouts or exceptions.
- The number of errors ranged from 60 - 7736081.

### Idle Test 19 ( 2023-07-01 07:57:48 - 2023-07-01 15:49:17 )

Events:
- One UART timeout after a reading command was sent, and no output returned. 
- The number of errors ranged from 103 - 12884574.
- Between 08:52:45 and 11:55:32, the read-count doubled while the address-range it read from remained the same.
- Beginning at 13:08:20 and lasting until the end of the test, the entire DRAM address space was recorded as having errors.

### Idle Test 20 ( 2023-07-02 19:10:38 - 2023-07-03 08:19:32 )

Events:
- Two UART timeouts after sending reading commands with no returning output. The board was repowered both times. 
- The number of errors ranged from 132 - 
- Between 23:46:30 until the timeout at time 06:13:57, the entire DRAM address space was recorded as having errors.

### Continuous Test 1 (2023-06-29 11:07:40 - 11:18:21)
- This test did not really run as it kept timing out 


### Continuous Test 2 (2023-06-29 11:18:41 - 11:21:29)
- This test was not that smooth and it did not run for long. There were not that much errors. There were 4 error group so it is hard to conclude if a specific error kept occurring 

### Continuous Test 3 (2023-06-29 12:54:44 - 13:00:38)
- This test timed out 3 times in 6 minutes. We did not really get that much errors from it. We had 8 error groups for this test. 



### Continuous Test 4 (2023-06-29 13:16:51 - 13:48:09)
- The first error was at 13:17:18
- There were 7 timeouts this test 
- At 13:27:39, there were 5605502 errors found and they stayed there until the end of the test which resulted in an error frequency of 60/76 for the addresses that had the problems


### Continuous Test 5 (2023-06-29 13:49:36 - 14:58:07)
- There were 45 timeouts in this test 
- The first error was at 13:50:03
- It is hard to see specific patterns because test kept timing out while reading the errors because the delay was shorter than needed for this board. 
- There were 10 addresses that got the most errors during this test, and these addresses are:
0x0e99007 0x162c7a7 0x2f76f9d 0x3d6effe 0x5cd65dc 0x65a1dec 0x7f0086d 0x88c7f96 0x73fd4b0 0x7d9ef11 




### Continuous Test 6 (2023-06-29 15:13:08 - 19:41:08)
- At this time, there was a change in the reading delay.
- The first error was at 15:13:34
- This test did not have any timeout errors 
- For the first 137 groups, the error count was around 4120, at 16:19:58, the count jumped to around 6166. The error count jumped to around 12300 at group count 324. 
- The highest error frequency was 643/714 


### Continuous Test 7 (2023-07-01 7:54:14 - 7:55:37)
- The first error was at 7:54:41 
- This test did not run for long so we did not get much errors to see a specific pattern. 
- There were no timeouts during this test


### Continuous Test 8 (2023-07-01 16:22:32 - 21:07:21)
- There were no timeouts this test. 
- First error was at 16:22:58
- The number of errors ranged between 77 - 16500
- There were no stuck bits as the largest error frequency was 782/795


### Continuous Test 9 (2023-07-01 21:26:41 - 2023-07-02 07:58:54)
- There were 2 UART timeouts this test
- The first error was at 21:27:00
- The number of errors ranged between 61 - 12400
- I noticed that the error count was getting high then the DRAM would kind of recover and go back to low numbers, but then it jumps back to high numbers
- There were 1213 error groups, the 3 addresses with the highest error frequency were:
    - 0x05eecf5 (1135 times)
        - a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a4a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5
    - 0x06e3abc (1112 times)
        - a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a1a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5
    - 0x0724e9d (1107 times)
        - a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a4a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5 a5a5a5a5



### Continuous Test 10 (2023-07-02 08:01:10 - 19:00:19)
- The fist error was at 08:01:37
- The number of errors ranged between 51 - 168435456
- At 13:07:07, there were 268435456 errors which means that the whole DRAM had errors. The errors stayed there until the end of the test. The DRAM was not able to recover. 
- There were no timeout errors 
- We cannot really conclude which addresses are the most vulnerable because the whole DRAM had errors for a majority of testing time. 


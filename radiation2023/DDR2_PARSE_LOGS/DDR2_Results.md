## Nexys 4 DDR

We ran the continuous test 21 times, and the idle test 25 times, all from June 26 to July 2. 
This summarizes the notable and/or major events during each script. 
The tests will be shown in chronological order.

### Continuous Test 1 ( 2023-06-26 16:45:36 - 2023-06-26 16:51:51 )

No events occured. BIST ran normally.

### Idle Test 1 ( 2023-06-26 16:51:57 - 2023-06-26 17:27:25 )

No events occured. BIST ran normally.

### Continuous Test 2 ( 2023-06-26 18:19:28 - 2023-06-26 18:19:47 )

No output from BIST. Appears that ttyUSB device could not be found by software, and script closed in the Terminating State.

### Continuous Test 3 ( 2023-06-26 18:21:23 - 2023-06-27 10:44:38 )

No events occured. BIST ran normally. 

### Idle Test 2 ( 2023-06-27 10:44:40 - 2023-06-27 10:50:03 )

No events occured. BIST ran normally.

### Continuous Test 4 ( 2023-06-27 16:04:46 - 2023-06-27 16:09:45 )

No events occured. BIST ran normally.

### Continuous Test 5 ( 2023-06-27 16:20:43 - 2023-06-27 16:22:56 )

No events occured. BIST ran normally.

### Idle Test 3 ( 2023-06-27 16:23:02 - 2023-06-27 16:23:24 )

No events occured. BIST ran normally.

### Continuous Test 6 ( 2023-06-27 16:25:36 - 2023-06-27 16:26:34 )

No events occured. BIST ran normally.

### Continuous Test 7 ( 2023-06-27 20:57:33 - 2023-06-27 20:57:52 )

No output from BIST. Appears that ttyUSB device could not be found by software, and script closed in the Terminating State.

### Continuous Test 8 ( 2023-06-27 20:58:31 - 2023-06-27 20:58:49 )

No output from BIST. Appears that ttyUSB device could not be found by software, and script closed in the Terminating State.

### Continuous Test 9 ( 2023-06-27 21:01:23 - 2023-06-27 21:01:41 )

No output from BIST. Appears that ttyUSB device could not be found by software, and script closed in the Terminating State.

### Continuous Test 10 ( 2023-06-27 21:04:25 - 2023-06-27 21:04:51 )

No events occured. BIST ran normally.

### Idle Test 4 ( 2023-06-28 05:07:02 - 2023-06-28 05:07:21 )

No output from BIST. Appears that ttyUSB device could not be found by software, and script closed in the Terminating State.

### Idle Test 5 ( 2023-06-28 05:07:50 - 2023-06-29 01:49:05 )

No events occured. BIST ran normally.

### Idle Test 6 ( 2023-06-29 08:52:49 - 2023-06-29 08:53:10 )

No events occured. BIST ran normally.

### Idle Test 7 ( 2023-06-29 08:54:29 - 2023-06-29 09:56:34 )

Events:
- First error appears at 09:14:54. At this time, our script was detecting errors and rewriting to the memory if errors were found,
  and DRAM recovery commands to clear the mode and delay registers were still implemented.
- First unrecognized character appears at 9:29:59. Up until 9:30:03 (when the board repowered), there are a few times when a space 
  character ' ' outputs as a backwards asterisk '`'.
- Between 9:35:24 - 9:35:26, three errors are found, two of which go away after a following write to the whole memory, but one of 
  which persists up until the end of the test (address 0x0ed5b13). Because of the way we had our scripts set up, our scripts cycled 
  continuously through recovery commands, and as a result became stuck in a neverending cycle of sending BIST recovery commands, 
  rebooting the SoC, and then repowering the board with the Lindy. The error at this same address persisted even after repowering 
  several times.
  Following are the errors found at this time period:
    - 0x01f2bca: a5a5a5a5 a5a525a5
    - 0x0c843e7: a5a585a5 a5a5a5a5
    - 0x0ed5b13: a5a5a5a1 a5a5a5a5
  * **MJW**: Please put the details of each error (address, expected value, received value)
  * **MJW**: Please put the details of stuck bit
- Up from 9:29:59 to the end of the test, even after the board has repowered and continues to repower several times, random letters 
  and characters begin to output in the messages, and portions of messages are scattered in the output.
- There is a bug in which, after leaving a BIST recovery mode, the pexpect script does not find expected data from the writer all the 
  time, and the writer will run 1-3 times until it is successful.

- The following are the errors found during this test with their frequency: 
  - 259: 0x0ed5b13:  a5a5a5a1 a5a5a5a5
  -   2: 0x0c843e7:  a5a585a5 a5a5a5a5
  -   1: 0x078c709:  a5a5a5a5 a525a5a5
  -   1: 0x01f2bca:  a5a5a5a5 a5a525a5


- 0x0ed5b13: a5a5a5a1 a5a5a5a5
  - Appeared at 9:35:24 - 9:56:34 (End of test)
  - 259/262 error groups
  - Stuck bit


- 0x0c843e7: a5a585a5 a5a5a5a5 
  - Appeared at 9:30:0 - Gone 9:30:23
  - Appeared at 9:35:24 - Gone 9:35:27
  - Appeared at 9:35:46 - Gone 9:40:48
  - Appeared at 9:40:59 - Gone 9:41:0
  - Appeared at 9:42:26 - Gone 9:47:29
  - 8/262 error groups 
  - Is it stuck or bit error ?

- 0x078c709: a5a5a5a5 a525a5a5
  - Appeared at 9:14:54 - Gone 9:14:56
  - 1/262 error groups 
  - Bit error 

- 0x01f2bca: a5a5a5a5 a5a525a5
  - Appeared at 9:35:24 - Gone 9:35:27
  - 1/262 error groups
  - Bit error




### Idle Test 8 ( 2023-06-29 09:56:37 - 2023-06-29 09:58:11 )

Events:
- Similar behavior to events of last test. Again, there is only one error read at the same address (address: 0x0ed5b13) without any 
  other errors, and the cycle of sending bist recovery commands and repowering the board went once while the same error persisted.
- Again, unrecognized characters and scattered portions of messages output in random areas.
- Only error found was:
  - 0x0ed5b13: a5a5a5a1 a5a5a5a5 
- There was a reboot at 9:57:32, and the board passed the memTest so it is hard to say that there was a stuck bit 

- 0x0ed5b13: a5a5a5a1 a5a5a5a5
  - Appeared 9:56:58 - Gone 9:58:11 (End of Test)
  - 33/33 error groups
  - Stuck bit 
### Idle Test 9 ( 2023-06-29 09:59:47 - 2023-06-29 10:01:20 )

Events:
- Very similar behavior to Idle Test 8. The same error at address 0x0ed5b13 was output without any other errors, and the cycle of bist 
  recovery commands persisted with unrecognized characters and scattered portions of messages in random places in the output.
- Only error found was:
  - 0x0ed5b13: a5a5a5a1 a5a5a5a5
- There was a reboot at 10:00:42 and the memTest was OK 

- 0x0ed5b13: a5a5a5a1 a5a5a5a5
  - Appeared at 10:00:08 - Gone 10:01:20 (End of test)
  - 33/33 error groups 
  - Stuck bit

### Idle Test 10 ( 2023-06-29 10:01:35 - 2023-06-29 10:02:14 )

Events:
- No change in behavior from Tests 8 and 9.
- Only error found was:
  - 0x0ed5b13: a5a5a5a1 a5a5a5a5
- Test had no timeouts 

- 0x0ed5b13: a5a5a5a1 a5a5a5a5a
  - Appeared at 10:01:56 - Gone 10:02:14 (End of test)
  - 12/12 error groups
  - Stuck bit

### IDLE Test 11 (2023-06-29 10:54:20 - 10:54:56)
- Similar behavior to tests 8-10
- The same error from before is still showing up. The error is:
  - 0x0ed5b13: a5a5a5a1 a5a5a5a5
- There were no timeouts this test

- 0x0ed5b13: a5a5a5a1 a5a5a5a5
  - Appeared at 10:54:40 - 10:54:56 (End of test)
  - 11/11 error groups 
  - Stuck bit
### Idle Test 12 ( 2023-06-29 11:04:12 - 2023-06-29 11:04:47 )

Events: 
- No change in behavior from Tests 8 - 11.
- Error found:
  - 0x0ed5b13: a5a5a5a1 a5a5a5a5
- Test had no timeouts

### Continuous Test 11 ( 2023-06-29 11:08:05 - 2023-06-29 11:08:51 )
- First error was at 11:08:25 
- There were 2 errors this test that were there all the time and did not go away at all. Those 2 errors are: 
  - 0x0df1440 : a5a5a5a5 a5a5a5a7
  - 0x0ed5b13 : a5a5a5a1 a5a5a5a5

- There was a unicode error at 11:08:46 

- 0x0df1440: a5a5a5a5 a5a5a5a7
  - Appeared at 11:08:25 - Gone 11:08:51 (End of test)
  - 26/26 error groups
  - Stuck bit

- 0x0ed5b13: a5a5a5a1 a5a5a5a5
  - Appeared at 11:08:25 - Gone 11:08:51 (End of test)
  - 26/26 group errors
  - Stuck bit 

### Continuous Test 12 ( 2023-06-29 11:19:08 - 2023-06-29 11:21:01 )
- Memory initialization failed because of 1 data error. It does not look like the error was one of teh errors found in the previous test, because this error had to be between addresses 0x40000000 - 0x40200000
- First error group was found at 11:19:28, and they stayed the same until the end of the test. These errors were: 
  - 0x0021998:  a5a5a5e5 a5a5a5a5
  - 0x0df1440:  a5a5a5a5 a5a5a5a7
  - 0x0ed5b13:  a5a5a5a1 a5a5a5a5

- This test did not have any timeouts 

- 0x0021998: a5a5a5e5 a5a5a5a5
  - Appeared at 11:19:28 - Gone 11:21:01 (End of test)
  - 26/26 group errors
  - Stuck bit

- 0x0df1440: a5a5a5a5 a5a5a5a7
  - Appeared at 11:19:28 - Gone 11:21:01 (End of test)
  - 26/26 group errors
  - Stuck bit

- 0x0ed5b13: a5a5a5a1 a5a5a5a5
  - Appeared at 11:19:28 - Gone 11:21:01 (End of test)
  - 26/26 errors
  - Stuck bit

### Continuous Test 13 ( 2023-06-29 12:46:18 - 2023-06-29 12:51:09 )
- This test also failed memory initialization at 12:49:  because of 1 data error, but the fail was at 12:49:42. It had no other memory initialization errors 
- The test had 2 timeouts
- There were 3 errors showing up during this test, but none of them was showing up the whole time. These errors are the same errors from the previous test. The following are the errors with their frequency out of 75:
  - 74: 0x0ed5b13:  a5a5a5a1 a5a5a5a5
  - 71: 0x0df1440:  a5a5a5a5 a5a5a5a7
  - 62: 0x0021998:  a5a5a5e5 a5a5a5a5


- 0x0ed5b13: a5a5a5a1 a5a5a5a5
  - Appeared at 12:46:38 - Gone 12:51:09 (It was actually gone at this time, not because the test ended)
  - 74/75 error groups
  - Stuck bit

- 0x0df1440: a5a5a5a5 a5a5a5a7
  - Appeared 12:46:39 - Gone 12:46:42
  - Appeared 12:46:47 - Gone 12:47:18
  - Appeared 12:47:22 - Gone 12:51:09 (End of test)
  - 71/75 error groups
  - Stuck bit 


- 0x0021998: a5a5a5e5 a5a5a5a5
  - Appeared at 12:46:39 - Gone 12:46:52
  - Appeared at 12:46:42 - Gone 12:50:32
  - Appeared at 12:50:33 - Gone 12:50:44
  - Appeared at 12:50:44 - Gone 12:51:02
  - 62/75 error groups
  - Stuck bits

### Continuous Test 14 ( 2023-06-29 12:51:20 - 2023-06-29 12:53:35 )
- There were 3 timeouts this test 
- There were no memory initialization errors 
- The first error was found at 12:51:40
- There were only 2 errors found this test, these 2 errors are:
  - 77: 0x0ed5b13:  a5a5a5a1 a5a5a5a5
  - 76: 0x0df1440:  a5a5a5a5 a5a5a5a7


- 0x0ed5b13: a5a5a5a1 a5a5a5a5
  - Appeared at 12:51:40 - Gone 12:53:34 (End of test)
  - 77/77 error groups
  - Stuck bit


- 0x0df1440: a5a5a5a5 a5a5a5a7
  - Appeared 12:51:40 - Gone 12:52:28
  - Appeared 12:52:29 - Gone 12:53:34 (End of test)
  - 76/77 error groups
  - Stuck bit

### Continuous Test 15 ( 2023-06-29 12:57:14 - 2023-06-29 13:12:29 )
- The first error was at 12:57:34
- There were 19 unicode errors that led to 19 reboots of the board 
- The test had 532 errors and there were 3 errors showing up, the errors were the following: 
  - 517: 0x0ed5b13:  a5a5a5a1 a5a5a5a5
  - 501: 0x0df1440:  a5a5a5a5 a5a5a5a7
  - 2  : 0x065cdf0:  a5a5a5b5 a5a5a5a5

- 0x0ed5b13: a5a5a5a1 a5a5a5a5 
  - Appeared at 12:57:34 - Gone 13:04:35
  - Appeared at 13:04:37 - Gone 13:04:39
  - Appeared at 13:04:41 - Gone 13:04:49
  - Appeared at 13:04:50 - Gone 13:07:57
  - Appeared at 13:07:57 - Gone 13:08:11
  - Appeared at 13:08:31 - Gone 13:09:21
  - Appeared at 13:09:23 - Gone 13:09:36
  - Appeared at 13:09:38 - Gone 13:10:26
  - Appeared at 13:10:27 - Gone 13:10:53
  - Appeared at 13:10:54 - Gone 13:11:44
  - Appeared at 13:11:46 - Gone 13:12:29 (End of test)
  - 517/532 error groups
  - Stuck bit

- 0x0df1440: a5a5a5a5 a5a5a5a7
  - Appeared 12:57:34 - Gone 13:00:46
  - Appeared 13:00:47 - Gone 13:02:37
  - Appeared 13:03:07 - Gone 13:04:07
  - Appeared 13:04:35 - Gone 13:12:29 (End of test)
  - 501/532 error groups
  - Stuck bit

- 0x065cdf0: a5a5a5b5 a5a5a5a5
  - Appeared 13:11:46 - Gone 13:11:49
  - Appeared 13:11:54 - Gone 13:11:56
  - 2/532 error groups 
  - Bit error
### Continuous Test 16 ( 2023-06-29 13:13:19 - 2023-06-29 19:16:17 )
- The first error was at 13:13:38
- There were 4 timeouts this test 
- At 14:20:38, the data read from the DRAM was just 0s. There were 8388611 errors which were just the DRAM returning 0s. Some addresses were returning other values than 0. For example, address 0x0000116 returned 0 82010000. These error stayed until 16:18:49, as there was a timeout at 16:19:23. The DRAM recovered after that and showed 2 errors.
- At 16:47:53, the whole DRAM went bad as there were 16777216 errors; the whole memory was returning 0s 
- At 16:59:09, the pattern written to the memory was corrupted as it was set to 252525a5 252525a5, there were 221 errors showing up because of that, but the data read from the addresses was corrupted as well. The addresses were (0x5ff - 0x7741ff). For example, address 0x00006ff returned 252525a5 25a5. This kept happening for different addresses as well until a timeout occurred at 17:25:31. The DRAM recovered after that. 
- Besides the errors reading 0s, there were 4 main errors that had a good error frequency. The following errors are:
  - 5124: 0x0df1440:  a5a5a5a5 a5a5a5a7
  - 4839: 0x06d2819:  a5a5a5a5 a5a585a5
  - 2513: 0x0ed5b13:  a5a5a5a1 a5a5a5a5
  - 2424: 0x0a4f004:  a5a5a5a1 a5a5a5a5

### Idle Test 13 ( 2023-06-29 19:16:25 - 2023-06-29 19:16:56 )

Events:
- Three errors output consistently here (addresses 0x0044a67, 0x06d2819, 0x0df1440). After three writes and three reads reading the 
  errors, the pexpect script entered the first DRAM Recovery state, which stopped and restarted the BIST, and one more read happened 
  just before the end of the test.
- The log is saying at the end of the test: Reader successful, Delay for 300 seconds. Was it delaying for this long? Also, at the very
  end of the test, why did it only  print out one error address when the error count was 3? I believe there is some script modification
  and debugging going on here.
  * **MJW**: Lets talk thorugh this. I did make some committs to the code during the test and we can see the commit history. 
- As in Idle test 7, there appears to be a bug in which, after leaving a BIST recovery mode, the pexpect script runs the writer at a 
  maximum of 3 times, as the pexpect script does not find expected data and therefore runs it again.
- Errors found are: 
  - 0x0044a67: a5a5a5a5 a5a5a5b5
    - Appeared 19:16:46 - Gone 19:16:56 (End of test)
    - 4/4 error groups
    - Stuck error
  - 0x06d2819: a5a5a5a5 a5a585a5
    - Appeared 19:16:46 - Gone 19:16:56 (This error was gone at that time, it was not present in the last error group)
    - 3/4 error groups
    - Stuck error
  - 0x0df1440: a5a5a5a5 a5a5a5a7
    - Appeared 19:16:46 - Gone 19:16:56 (This error was gone at that time, it was not present in the last error group)
    - 3/4 error groups
    - Stuck error

### Idle Test 14 ( 2023-06-29 19:26:24 - 2023-06-29 19:47:00 )

Events:
- Same behavior as last test with the same three errors output consistently, although an extra error appeared once at 19:46:58 at address
  0xe58519. A single write occured in the beginning to the entire memory, and 5 reads of the entire memory occured afterwards. The script 
  is modified here to constantly run the reader instead of the writer. After the reads, the pexpect script entered the first DRAM 
  Recovery state, which simply stopped and restarted the BIST, and one more read happened just before the end of the test.
- Again, the log says "Reader successful, Delay for 300 seconds" at the end, and only one of the 3 errors were displayed at the end.
- Errors found are: 
  - 0x0044a67: a5a5a5a5 a5a5a5b5
    - Appeared 19:26:45 - 19:47:0 (End of test)
    - 6/6 error groups 
    - Stuck bit
  - 0x06d2819: a5a5a5a5 a5a585a5
    - Appeared 19:26:45 - Gone 19:47:0 (This error was gone at that time, it was not present in the last error group)
    - 5/6 error groups
    - Stuck bit
  - 0x0df1444: a5a5a5a5 a5a5a5a7
    - Appeared 19:26:45 - Gone 19:47:0 (This error was gone at that time, it was not present in the last error group)
    - 5/6 error groups
    - Stuck bit
  - 0x0e58519: a5e5a5a5 a5a5a5a5 
    - Appeared 19:46:56 - Gone 19:47:0 (This error was gone at that time, it was not present in the last error group)
    - 1/6 error groups
    - Bit error
- There were no timeouts this test 
### Idle Test 15 ( 2023-06-29 19:52:58 - 2023-06-29 19:55:35 )

Events:
- Same behavior as idle test 14 with the same three errors, and the error at address 0xe58519 appeared twice. One write and 5 reads occured,
  and the pexpect script went to the DRAM recovery state, and the BIST stopped and restarted. One more read happened before the end of the test,
  and only one of three errors was output with the same "Reader successful, Delay for 300 seconds" message appearing in the log.
- Errors found are: 
  - 0x0044a67:  a5a5a5a5 a5a5a5b5
    - Appeared 19:53:19 - 19:55:35 (End of test)
    - 6/6 error groups 
    - Stuck bit
  - 0x06d2819:  a5a5a5a5 a5a585a5
    - Appeared 19:53:19 - 19:55:35 (This error was gone at that time, it was not present in the last error group)
    - 5/6 error groups
    - Stuck bit
  - 0x0df1440:  a5a5a5a5 a5a5a5a7
     - Appeared 19:53:19 - 19:55:35 (This error was gone at that time, it was not present in the last error group)
    - 5/6 error groups
    - Stuck bit
  - 0x0e58519:  a5e5a5a5 a5a5a5a5
    - Appeared 19:54:57 - Gone 19:55:35 (This error was gone at that time, it was not present in the last error group)
    - 2/6 error groups
    - Bit error
- There were no timeouts this test 

### Idle Test 16 ( 2023-06-29 20:01:10 - 2023-06-29 20:06:25 )

Events:
- Same behavior as idle test 13 with the same three errors, but instead of the error at address 0xe58519 appearing, a new one appeared at 
  address 0x0928880 twice. This test ran longer with a delay set to 30 seconds instead of 300 seconds between reads, with the pattern occurring 
  of one write followed by five reads followed by a BIST restart. 
- The bug continues after Idle Test 7, where after leaving the BIST recovery mode, the writer writes 1 - 3 times in a row 
  before running the reader. At the start, the writer wrote data to the full DRAM memory (addresses 0x0 - 0x0ffffff), but after some time, 
  it appears that the writer wrote to the addresses 0x0 - 0x517 about 6 times. 
- Errors found are:
  - 0x0044a67:  a5a5a5a5 a5a5a5b5
    - Appeared 20:01:30 - Gone 20:03:45
    - Appeared 20:04:17 - Gone 20:04:17
    - Appeared 20:04:48 - Gone 20:04:48
    - Appeared 20:05:19 - Gone 20:05:19
    - Appeared 20:06:21 - Gone 20:06:25 (End of test)
    - 12/17 error groups 
    - Stuck bit 
  - 0x06d2819:  a5a5a5a5 a5a585a5
    - Appeared 20:01:30 - Gone 20:03:45
    - Appeared 20:03:45 - Gone 20:04:17
    - Appeared 20:04:17 - Gone 20:04:48
    - Appeared 20:04:48 - Gone 20:05:19
    - Appeared 20:05:19 - Gone 20:05:50
    - Appeared 20:05:50 - Gone 20:06:25 (This error was gone at that time, it was not present in the last error group)  
    - 11/17 error groups
    - Stuck bit
  - 0x0df1440:  a5a5a5a5 a5a5a5a7
    - Appeared 20:01:30 - Gone 20:03:45
    - Appeared 20:03:45 - Gone 20:04:17
    - Appeared 20:04:17 - Gone 20:04:48
    - Appeared 20:04:48 - Gone 20:05:19
    - Appeared 20:05:19 - Gone 20:05:50
    - Appeared 20:05:50 - Gone 20:06:25 (This error was gone at that time, it was not present in the last error group)  
    - 11/17 error groups
    - Stuck bit
  - 0x0928880:  a5a5a5a5 a5a5b5a5
    - Appeared 20:05:50 - Gone 20:06:25 (This error was gone at that time, it was not present in the last error group)
    - 2/17 error groups
    - Bit error 
- There were no timeouts this test 


### Idle Test 17 ( 2023-06-29 20:07:18 - 2023-06-30 07:51:27 )

Events:
- The script ran the test in the pattern of Test 15: running the writer once, then the reader 5 times, and if errors occured in all these 5 
  times, the BIST simply closed and restarted. 
- The test ran from 20:07:18 to about 23:33:27 normally, running the reader every 5 minutes. 
  - The error count remained in the single digits during this entire time, with a max error count of 9.
  - A UART timeout occured at 20:23:21, where the reader stopped midway outputting a line of data to summarize the output. The board was repowered.
  - A UART timeout occured at 20:39:34 for the same exact reason as the timeout above. The board was again repowered.
  - A UART timeout occured at 22:06:15. After sending the reading command, no output came out. The board was repowered.
  - A UART timeout occured at 23:17:28. Amidst a few unicode errors, the writer stopped midway outputting a line of data to summarize the output. The board was repowered.  
  - A UART timeout occured at 23:33:27. After sending the reading command, a few lines output, but it appears the reader didn't run. The board was repowered.
- After the board repowered at 23:33:27, bizarre behavior happened up until about 00:02:41, when another UART timeout occured and the board was again repowered.
  - At first, the writer ran once normally, and the reader ran and counted 3 data errors, but while the BIST was displaying errors, the BIST output many more erroneous addresses above the 3 originally recorded. The error count for the next BIST reads climbs up to 268435456, which isn't possible as there are only 16777215 total addresses in the DRAM. There is some register corruption going on here. The data output at these addresses mostly matched what we expected in the beginning, although more than 3 do not. I believe one of the problems is that the register holding the data to match the data read back is going bad here.
  - The pexpect script failed to recognize matching data 579 times. The data that did not match was the number of addresses tested. The range changed from 0x0000000 - 0x0ffffff to 0x10000000-0x10ffffff, although this range of addresses doesn't exist with the DDR2. Our script was missing a return statement if it recognized bad data too many times in a row, thus it continued in a perpetual loop of sending reading commands. At 00:02:42, a UART timeout occured after sending the reading command returned with the response "Command not found". Data in the output started becoming corrupted at 00:02:10. The board was repowered as a result of the timeout.
  - Another UART Timeout immediately occured afterwards, at 00:04:09, after sending the writing command and receiving no output. The board was again repowered. After this, the BIST ran normally, running the reader every 5 minutes. 
    - Eight more UART timeouts occured before the end of the test, all of which resulted in the Lindy repowering the board. One occured while waiting for output from a writing command, and the other seven occured while waiting for output from the reading command. 
  - The error count remained in the single digits during this entire time, with a max error count of 9.

  - Errors found: 
    - 0x01c2c44:  25a5a5a5 a5a5a5a5
    - 0x0605a00:  a5e5a5a5 a5a5a5a5
    - 0x0df1440:  a5a5a5a5 a5a5a5a7
    - 0x01f9c00:  a5e5a5a5 a5a5a5a5
    - 0x0044a67:  a5a5a5a5 a5a5a5b5

### Idle Test 18 ( 2023-06-30 08:18:34 - 2023-06-30 17:32:24 )

Events:
- No UART timeouts occured during the entire test.
- The total number of errors after each read in the entire test remained in the single digits, with the maximum reaching 7.
- The total number of addresses that printed out with data errors was 11. 
- The pexpect script wrote to the entire memory once, then read from it five times. After every five reads, the Bist simply stopped and restarted, and the issue mentioned originally in Idle Test 7 with the writer running three times at minimum again appears here. The cycle of five reads, restarting the bist, and the writer running three times continues until the end of the test.
- Errors found:
  - 0x078ec96:  a5a5a1a5 a5a5a5a5
  - 0x0df1440:  a5a5a5a5 a5a5a5a7
  - 0x03eb11f:  a5e5a5a5 a5a5a5a5
  - 0x0e5564e:  a5a5a5a5 a5e5a5a5
  - 0x0dfa3b7:  a5a5a5a5 a5a5a5b5
  - 0x0240aaa:  a4a5a5a5 a5a5a5a5
  - 0x0adc6a6:  a5a5a5a5 ada5a5a5
  - 0x010b930:  a5a5a5a7 a5a5a5a5
  - 0x08aab56:  a5a5e5a5 a5a5a5a5
  - 0x0680a8a:  a5e5a5a5 a5a5a5a5
  - 0x0a4f004:  a5a5a5a1 a5a5a5a5
### Idle Test 19 ( 2023-06-30 17:33:20 - 2023-06-30 20:11:57 )

Events: 
- Two UART timeouts occured, both from starting the reader and timing out from no output.
- The total number of addresses that printed out with data errors was 23.
- The number of errors ranged from 2 - 9.
- Errors found with their frequency: 
  - 36: 0x078ec96:  a5a5a1a5 a5a5a5a5
  - 36: 0x0df1440:  a5a5a5a5 a5a5a5a7
  - 29: 0x0240aaa:  a4a5a5a5 a5a5a5a5
  - 23: 0x0adc6a6:  a5a5a5a5 ada5a5a5
  - 13: 0x0680a8a:  a5e5a5a5 a5a5a5a5
  -  7: 0x0dfa3b7:  a5a5a5a5 a5a5a5b5
  -  6: 0x0216929:  85a5a5a5 a5a5a5a5
### Idle Test 20 ( 2023-06-30 20:14:09 - 2023-07-01 07:52:49 )

Events:
- 8 UART Timeouts occured: 5 after starting the reader and no data returned, 1 after starting the writer and no data returned, and 2 after starting the reader and getting unicode errors, which led to the Terminal Recovery state that tried to close and reopen the ttyUSB device and send input but failed receiving output.
- At 23:31:14, there were 4194307 errors as the memory was returning 0s instead of the expected data. This kept happening until 2:09:17 as the memory recovered after a timeout at 2:08:41
- The errors that were bitflips are (with their error frequency):
  - 94: 0x078ec96:  a5a5a1a5 a5a5a5a5
  - 93: 0x0df1440:  a5a5a5a5 a5a5a5a7
  - 91: 0x0adc6a6:  a5a5a5a5 ada5a5a5
  - 49: 0x01f5ae8:  a5a5a5a5 a5a5a4a5
  - 43: 0x0240aaa:  a4a5a5a5 a5a5a5a5
  - 38: 0x0504725:  a5a525a5 a5a5a5a5

### Continuous Test 17 (2023-07-01 07:54:00 - 07:55:32)
- There were no timeouts this test 
- The first error was at 7:54:20. 
- There were 4 main errors this test that had a 24/25 error frequency. The errors were the following:
  - 0x078ec96:  a5a5a1a5 a5a5a5a5
  - 0x0adc6a6:  a5a5a5a5 ada5a5a5
  - 0x0df1440:  a5a5a5a5 a5a5a5a7
  - 0x01f5ae8:  a5a5a5a5 a5a5a4a5
### Idle Test 21 ( 2023-07-01 07:57:39 - 2023-07-01 15:49:50 )

Events:
- A smoother test than the previous, but UART timeouts still occured (12 total, all after sending a reading command). 
- More instances of data and register corruption. Instances where address range changed to 0x0-0x0fffff7, address width register changed from 24 to 16, and entire lines from the output were colored green.
- The number of errors ranged from 4 - 16.
- The errors found with a significant error frequency are: 
  - 82: 0x078ec96:  a5a5a1a5 a5a5a5a5
  - 82: 0x0df1440:  a5a5a5a5 a5a5a5a7
  - 80: 0x01f5ae8:  a5a5a5a5 a5a5a4a5
  - 69: 0x036a949:  a5a5a5a5 a5a5e5a5
  - 68: 0x0fe20e2:  a5a4a5a5 a5a5a5a5
  - 50: 0x0c131ad:  85a5a5a5 a5a5a5a5
  - 38: 0x012764f:  a5a5a5a5 a5a5e5a5
  - 38: 0x0a4c9f8:  a5a5a5a5 a525a5a5
  - 28: 0x0b8ec51:  a5a5a5a5 a5a5a5e5
  - 21: 0x0240aaa:  a4a5a5a5 a5a5a5a5
  - 18: 0x0251b5d:  a5a5a5a5 a585a5a5
  - 16: 0x0bb8558:  a5a5a5b5 a5a5a5a5
  - 14: 0x0d04af0:  a5a5a525 a5a5a5a5
  - 14: 0x029fdba:  a5a4a5a5 a5a5a5a5
  - 14: 0x034fe9e:  a5a5a5a5 a5a5a7a5
  - 10: 0x0a88ff3:  a5a4a5a5 a5a5a5a5
### Continuous Test 18 (2023-07-01 16:22:00 - 21:07:16)
- The first error was at 16:22:40
- There were 7 timeouts this test
- The error count range was 8-13 until 19:37:39. At that time, there were 16777215 errors found. The memory recovered at 19:39:19 after a timeout occurred. 
- The following were the errors with a significant error frequency out of 4650 error groups:
  - 4595: 0x078ec96:  a5a5a1a5 a5a5a5a5
  - 4595: 0x0a4c9f8:  a5a5a5a5 a525a5a5
  - 4595: 0x0b8ec51:  a5a5a5a5 a5a5a5e5
  - 4595: 0x0bb8558:  a5a5a5b5 a5a5a5a5
  - 4595: 0x0c131ad:  85a5a5a5 a5a5a5a5
  - 4594: 0x0fe20e2:  a5a4a5a5 a5a5a5a5
  - 4594: 0x01f5ae8:  a5a5a5a5 a5a5a4a5
  - 4574: 0x0df1440:  a5a5a5a5 a5a5a5a7
  - 4519: 0x012764f:  a5a5a5a5 a5a5e5a5
  - 4400: 0x03e13ae:  a5a5e5a5 a5a5a5a5
  - 4049: 0x0dfa3b7:  a5a5a5a5 a5a5a5b5
  - 3525: 0x00ca4f7:  e5a5a5a5 a5a5a5a5
  - 2362: 0x03af07f:  b5a5a5a5 a5a5a5a5
  - 1676: 0x00dcaf0:  a5a5a5a7 a5a5a5a5
  - 1067: 0x0e5564e:  a5a5a5a5 a5e5a5a5


### Continuous Test 19 (2023-07-01 21:26:29 - 2023-07-02 00:25:50)
- The first error was found at 21:26:49
-  There were 2 timeouts this test and 1 unicode error which was at the end of the test 
- Even though there was a good number of repeated dynamic errors, none of the errors were stuck bits as there were times in the test were no errors were found. 
- The following errors were found the most during this test
  - 2165: 0x00ca4f7:  e5a5a5a5 a5a5a5a5
  - 2165: 0x03e13ae:  a5a5e5a5 a5a5a5a5
  - 2165: 0x0a4c9f8:  a5a5a5a5 a525a5a5
  - 2165: 0x0c131ad:  85a5a5a5 a5a5a5a5
  - 2165: 0x0df1440:  a5a5a5a5 a5a5a5a7
  - 2165: 0x0fe20e2:  a5a4a5a5 a5a5a5a5
  - 2160: 0x01f5ae8:  a5a5a5a5 a5a5a4a5
  - 2083: 0x012764f:  a5a5a5a5 a5a5e5a5
  - 1951: 0x076cc63:  a5a5a5a5 85a5a5a5
  - 1808: 0x03af07f:  b5a5a5a5 a5a5a5a5
  - 1795: 0x0dfa3b7:  a5a5a5a5 a5a5a5b5
  - 1465: 0x078ec96:  a5a5a1a5 a5a5a5a5
  - 1465: 0x0b8ec51:  a5a5a5a5 a5a5a5e5
  - 1465: 0x0bb8558:  a5a5a5b5 a5a5a5a5
  -  828: 0x005bac2:  a5a5a5a5 b5a5a5a5
  -  700: 0x058ec96:  a5a5a1a5 a5a5a5a5
  -  700: 0x098ec51:  a5a5a5a5 a5a5a5e5
  -  700: 0x09b8558:  a5a5a5b5 a5a5a5a5


### Continuous Test 20 (2023-07-02 08:00:19 - 08:00:31)
- Test did not run. It was stopped quickly so no errors found 


### Continuous Test 21 (2023-07-02 08:00:43 - 08:00:48)
- Test stopped quickly so no errors found 
### Idle Test 22 ( 2023-07-02 19:00:11 - 2023-07-02 19:00:21 )

No BIST output. Perhaps this test was stopped manually.

### Idle Test 23 ( 2023-07-02 19:00:39 - 2023-07-02 19:00:39 )

No BIST output. Again, perhaps this test was stopped manually.

### Idle Test 24 ( 2023-07-02 19:09:40 - 2023-07-03 06:08:39 )

Events: 
- More random characters in random places within the output. 
- UART timeouts after sending a reading/writing command and receiving no input.
- The number of errors ranged from 15 - 32.
- The errors with a significant error frequency are:
  - 148: 0x0059b09:  a5a5a5b5 a5a5a5a5
  - 148: 0x00e4241:  a5a7a5a5 a5a5a5a5
  - 148: 0x012764f:  a5a5a5a5 a5a5e5a5
  - 147: 0x01f5ae8:  a5a5a5a5 a5a5a4a5
  - 147: 0x0ded024:  a5a5a5b5 a5a5a5a5
  - 147: 0x0df1440:  a5a5a5a5 a5a5a5a7
  - 147: 0x0fe20e2:  a5a4a5a5 a5a5a5a5
  - 146: 0x0bb8558:  a5a5a5b5 a5a5a5a5
  - 143: 0x00ca4f7:  e5a5a5a5 a5a5a5a5
  - 143: 0x010b930:  a5a5a5a7 a5a5a5a5
  - 143: 0x0240aaa:  a4a5a5a5 a5a5a5a5
  - 142: 0x0ccea44:  a5a5a525 a5a5a5a5
  - 141: 0x02913fb:  a5a5a5a5 a4a5a5a5
  - 141: 0x0a4c9f8:  a5a5a5a5 a525a5a5
  - 140: 0x0c131ad:  85a5a5a5 a5a5a5a5
  - 119: 0x0d844e5:  a5a5a5a5 a5a7a5a5
  - 100: 0x0ed0e2d:  a5a5a5a5 25a5a5a5
  -  98: 0x0b6ac1e:  a5a5a5a5 b5a5a5a5
  -  89: 0x058aa3c:  a5a5a5a5 ada5a5a5
  -  85: 0x0e5564e:  a5a5a5a5 a5e5a5a5
  -  83: 0x0afd50a:  e5a5a5a5 a5a5a5a5
  -  77: 0x056a750:  a5a5a5a5 a5a5a5a7
  -  73: 0x084c579:  a5a5a5a5 a5a5e5a5
  -  68: 0x05ac296:  a5a5a5a5 b5a5a5a5
  -  67: 0x0150761:  a5a5e5a5 a5a5a5a5
  -  54: 0x0b30399:  a5a5a5e5 a5a5a5a5
  -  52: 0x076cc63:  a5a5a5a5 85a5a5a5
  -  52: 0x0b8ec51:  a5a5a5a5 a5a5a5e5
  -  39: 0x0991428:  a5a5a5a5 a5a525a5
  -  32: 0x0536d07:  25a5a5a5 a5a5a5a5
  -  27: 0x01cae7e:  a5a5a5a5 85a5a5a5



### Most vulnerable addresses
- 0x0df1440
- 0x01f5ae8
- 0x078ec96
- 0x0240aaa
- 0x012764f
- 0x0fe20e2
- 0x0ed5b13
- 0x0bb8558
- 0x00ca4f7
- 0x010b930
- 0x0c131ad
- 0x0a4c9f8



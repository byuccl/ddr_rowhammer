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
- Up from 9:29:59 to the end of the test, even after the board has repowered and continues to repower several times, random letters 
  and characters begin to output in the messages, and portions of messages are scattered in the output.
- There is a bug in which, after leaving a BIST recovery mode, the writer writes 1 - 3 times in a row before running the reader. This
  seems to happen all throughout this test and other tests in which errors occur.

### Idle Test 8 ( 2023-06-29 09:56:37 - 2023-06-29 09:58:11 )

Events:
- Similar behavior to events of last test. Again, there is only one error read at the same address (address: 0x0ed5b13) without any 
  other errors, and the cycle of sending bist recovery commands and repowering the board went once while the same error persisted.
- Again, unrecognized characters and scattered portions of messages output in random areas.

### Idle Test 9 ( 2023-06-29 09:59:47 - 2023-06-29 10:01:20 )

Events:
- Very similar behavior to Idle Test 8. The same error at address 0x0ed5b13 was output without any other errors, and the cycle of bist 
  recovery commands persisted with unrecognized characters and scattered portions of messages in random places in the output.

### Idle Test 10 ( 2023-06-29 10:01:35 - 2023-06-29 10:02:14 )

Events:
- No change in behavior from Tests 8 and 9.

### Idle Test 11 ( 2023-06-29 11:04:12 - 2023-06-29 11:04:47 )

Events: 
- No change in behavior from Tests 8 - 10.

### Continuous Test 11 ( 2023-06-29 11:08:05 - 2023-06-29 11:08:51 )

### Continuous Test 12 ( 2023-06-29 11:19:08 - 2023-06-29 11:21:01 )

### Continuous Test 13 ( 2023-06-29 12:46:18 - 2023-06-29 12:51:09 )

### Continuous Test 14 ( 2023-06-29 12:51:20 - 2023-06-29 12:53:35 )

### Continuous Test 15 ( 2023-06-29 12:57:14 - 2023-06-29 13:12:29 )

### Continuous Test 16 ( 2023-06-29 13:13:19 - 2023-06-29 19:16:17 )

### Idle Test 12 ( 2023-06-29 19:16:25 - 2023-06-29 19:16:56 )

Events:
- Three errors output consistently here (addresses 0x0044a67, 0x06d2819, 0x0df1440). After three writes and three reads reading the 
  errors, the pexpect script entered the first DRAM Recovery state, which stopped and restarted the BIST, and one more read happened 
  just before the end of the test.
- The log is saying at the end of the test: Reader successful, Delay for 300 seconds. Was it delaying for this long? Also, at the very
  end of the test, why did it only  print out one error address when the error count was 3? I believe there is some script modification
  and debugging going on here.
- As in Idle test 7, there appears to be a bug in which, after leaving a BIST recovery mode, the writer writes 1 - 3 times in a row 
  before running the reader. 

### Idle Test 13 ( 2023-06-29 19:26:24 - 2023-06-29 19:47:00 )

Events:
- Same behavior as last test with the same three errors output consistently, although an extra error appeared once at 19:46:58 at address
  0xe58519. A single write occured in the beginning to the entire memory, and 5 reads of the entire memory occured afterwards. The script 
  is modified here to constantly run the reader instead of the writer. After the reads, the pexpect script entered the first DRAM 
  Recovery state, which simply stopped and restarted the BIST, and one more read happened just before the end of the test.
- Again, the log says "Reader successful, Delay for 300 seconds" at the end, and only one of the 3 errors were displayed at the end.

### Idle Test 14 ( 2023-06-29 19:52:58 - 2023-06-29 19:55:35 )

Events:
- Same behavior as idle test 13 with the same three errors, and the error at address 0xe58519 appeared twice. One write and 5 reads occured,
  and the pexpect script went to the DRAM recovery state, and the BIST stopped and restarted. One more read happened before the end of the test,
  and only one of three errors was output with the same "Reader successful, Delay for 300 seconds" message appearing in the log.

### Idle Test 15 ( 2023-06-29 20:01:10 - 2023-06-29 20:06:25 )

Events:
- Same behavior as idle test 13 with the same three errors, but instead of the error at address 0xe58519 appearing, a new one appeared at 
  address 0x0928880 twice. This test ran longer with a delay set to 30 seconds instead of 300 seconds between reads, with the pattern occuring 
  of one write followed by five reads followed by a BIST restart. 
- The bug continues after Idle Test 7, where after leaving the BIST recovery mode, the writer writes 1 - 3 times in a row 
  before running the reader. At the start, the writer wrote data to the full DRAM memory (addresses 0x0 - 0x0ffffff), but after some time, 
  it appears that the writer wrote to the addresses 0x0 - 0x517 about 6 times. 

### Idle Test 16 ( 2023-06-29 20:07:18 - 2023-06-30 07:51:27 )

Events:
- The script ran the test in the pattern of Test 15: running the writer once, then the reader 5 times, and if errors occured in all these 5 
  times, the BIST simply closed and restarted. 
- The test ran from 20:07:18 to about 23:33:27 with minor incidents: 
  - The error count remained in the single digits during this entire time, with a max error count of 9.
  - A UART timeout occured at 20:23:21, where the reader stopped midway outputting a line of data to summarize the output. The board was repowered.
  - A UART timeout occured at 20:39:34 for the same exact reason as the timeout above. The board was again repowered.
  - A UART timeout occured at 22:06:15. After sending the reading command, no output came out. The board was repowered.
  - A UART timeout occured at 23:17:28. Amidst a few unicode errors, the writer stopped midway outputting a line of data to summarize the output. The board was repowered.  
  - A UART timeout occured at 23:33:27. After sending the reading command, a few lines output, but it appears the reader didn't run. The board was repowered.
- After the board repowered at 23:33:27, bizarre behavior happened up until about 00:02:41, when another UART timeout occured and the board was again repowered.
  - First, after the writer ran once, the reader counted 

### Continuous Test 17 ( 2023-07-01 07:54:00 - 2023-07-01 07:55:32 )







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

### Idle Test 20 (  -  )
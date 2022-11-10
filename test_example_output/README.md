# All errors in tests

In this document I will record all the strange behavior I've noticed so far with the test scripts running the bist and fault injection. 

## Unexpected data

There have been a number of times when unexpected data has output. Here are a few examples 

### UnicodeDecodeExceptions

A number of times, pexpect expected a line of data only to throw a UnicodeDecodeException. This often happens when the code reads data at the beginning of the litex program or after a bist calibrate, init, or reboot command is sent, when data other than bist data is output. I had the code retry to expect the same line after this exception over and over again until the exception stopped occuring. Here is an example.

```
[ 2022-10-26 17:26:21 ]  Starting test
[ 2022-10-26 17:26:21 ]  Confirming board plugged in
/dev/ttyUSB0
/dev/ttyUSB1
/dev/ttyUSB2
/usr/bin/ls: cannot access '/dev/ttyUSB3': No such file or directory
/usr/bin/ls: cannot access '/dev/ttyUSB4': No such file or directory
/usr/bin/ls: cannot access '/dev/ttyUSB5': No such file or directory
/usr/bin/ls: cannot access '/dev/ttyUSB6': No such file or directory
/usr/bin/ls: cannot access '/dev/ttyUSB7': No such file or directory
/usr/bin/ls: cannot access '/dev/ttyUSB8': No such file or directory
/usr/bin/ls: cannot access '/dev/ttyUSB9': No such file or directory
[ 2022-10-26 17:26:23 ]  Board plugged in, using /dev/ttyUSB2.
[ 2022-10-26 17:26:23 ]  Logging in to JCM
[ 2022-10-26 17:26:23 ]  Configuring JCM with new program
[ 2022-10-26 17:26:32 ]  Starting litex with /dev/ttyUSB2
[ 2022-10-26 17:26:32 ]  Expecting Litex Prompt


[ 2022-10-26 17:26:32 ]  Unicode error occured, retrying up to 20x


[ 2022-10-26 17:26:32 ]  Unicode error occured, retrying up to 20x


[ 2022-10-26 17:26:32 ]  Unicode error occured, retrying up to 20x


[ 2022-10-26 17:26:32 ]  Unicode error occured, retrying up to 20x


 m0, b00: |00000000000000000000000000000000| delays: -

  m0, b01: |10000000000000000000000000000000| delays: 02+-02

  m0, b02: |00011111111111111000000000000000| delays: 10+-07

  m0, b03: |00000000000000000001111111111111| delays: 25+-06

  m0, b04: |00000000000000000000000000000000| delays: -

  m0, b05: |00000000000000000000000000000000| delays: -

  m0, b06: |00000000000000000000000000000000| delays: -

  m0, b07: |00000000000000000000000000000000| delays: -

  best: m0, b02 delays: 10+-07

  m1, b00: |00000000000000000000000000000000| delays: -

  m1, b01: |10000000000000000000000000000000| delays: 02+-02

  m1, b02: |00111111111111111000000000000000| delays: 09+-07

  m1, b03: |00000000000000000011111111111111| delays: 25+-07

  m1, b04: |00000000000000000000000000000000| delays: -

  m1, b05: |00000000000000000000000000000000| delays: -

  m1, b06: |00000000000000000000000000000000| delays: -

  m1, b07: |00000000000000000000000000000000| delays: -

  best: m1, b02 delays: 09+-07

Switching SDRAM to hardware control.
```

... and soon afterwards the bist runs normally. 


This example shows multiple UnicodeDecodeExceptions occuring many times a second.

```

[ 2022-10-20 19:37:47 ] 
                                   646          654         2391          0          0          0

[ 2022-10-20 19:37:48 ] 
                                   646          654         2715          0          0          0

[ 2022-10-20 19:37:49 ] 
                 [ 2022-10-20 19:37:50 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:50 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:51 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:51 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:51 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:51 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:52 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:52 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:52 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:52 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:52 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:52 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:53 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:53 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:53 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:53 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:54 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:54 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:54 ] UnicodeDecodeError, retrying.
[ 2022-10-20 19:37:54 ] UnicodeDecodeError, retrying.
```

... and so forth, unitl 20:04:35, when a timeout occured and the board was reconfigured.


In this following test run on October 29, 2022, a UnicodeDecodeException output every second. By the 29th, I had set up the code to reopen litex if necessary if 20 of these occured in a row, else reconfigure. 

```

[ 2022-10-29 06:33:19 ]  
                                   646          654         3029          0          0          0

[ 2022-10-29 06:33:20 ]  
                                   646          654         3353          0          0          0

[ 2022-10-29 06:33:21 ]  
[ 2022-10-29 06:33:22 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:23 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:24 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:25 ]  UnicodeDecodeException whie expecting title or data
        [ 2022-10-29 06:33:26 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:27 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:28 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:29 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:30 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:31 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:32 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:33 ]  UnicodeDecodeException whie expecting title or data
  [ 2022-10-29 06:33:34 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:35 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:36 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:37 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:38 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:39 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:40 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:41 ]  UnicodeDecodeException whie expecting title or data
[ 2022-10-29 06:33:41 ]  Too many UnicodeDecode exceptions
[ 2022-10-29 06:33:41 ]  Correct fault
[ 2022-10-29 06:33:41 ]  Restart litex


[ 2022-10-29 06:33:41 ]  Other exception occured restarting Litex
[ 2022-10-29 06:33:41 ]  <class 'Exception'>
[ 2022-10-29 06:33:41 ]  Configuring JCM with new program
[ 2022-10-29 06:33:49 ]  Starting litex with /dev/ttyUSB2
[ 2022-10-29 06:33:49 ]  Expecting Litex Prompt
```


### Other bizarre data output

Here I have examples of times when bizarre output occured, or nothing at all. These happened rarely.
Here is an example where a timeout occured, a reboot command was sent, and only titles output. 

```

[ 2022-10-17 23:12:06 ] 
         646          654         2310          0          0          0

[ 2022-10-17 23:12:07 ] 
         646          654         2634          0          0          0

[ 2022-10-17 23:12:08 ] 
         646          654         2959          0          0          0

[ 2022-10-17 23:12:09 ] 
         646          654         3283          0          0          0

[ 2022-10-17 23:12:10 ] 
[ 2022-10-17 23:12:25 ] Timeout occured. Attempting to close, reopen Litex.
[ 2022-10-17 23:12:25 ] Attempting to reset Litex
reboot

[1m      / /__/ / __/ -_)>  <[0m

[1m     /____/_/\__/\__/_/|_|[0m

[1m   Build your hardware, easily![0m


 (c) Copyright 2012-2022 Enjoy-Digital

 (c) Copyright 2007-2015 M-Labs


 BIOS built on Oct 13 2022 18:12:25

 
 
 
 ... More output after rebooting Litex
 
 
 

--============= [1mConsole[0m ================--


[92;1mlitex[0m> [ 2022-10-17 23:12:26 ] Running Bist command.
sdram_bist 8192 1
sdram_bist 8192 1

Starting SDRAM BIST with burst_length=8192 and addr_mode=1

WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-17 23:12:26 ] 
WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-17 23:12:39 ] 
WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-17 23:12:52 ] 
WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-17 23:13:04 ] 
WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-17 23:13:17 ] 
WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-17 23:13:30 ] 

```


This output lasted for the rest of the test until I stopped the test at 11:48:00 the following day.


Another time, a timeout occured, the bist restarted, and all the numbers output as %u's. 

```

[ 2022-10-27 05:05:10 ]  

                                   646          654         2965          0          0          0

[ 2022-10-27 05:05:12 ]  

                                   646          654         3289          0          0          0

[ 2022-10-27 05:05:13 ]  

[ 2022-10-27 05:05:28 ]  Time out whie expecting title or data
[ 2022-10-27 05:05:28 ]  Correct fault
[ 2022-10-27 05:05:28 ]  Restart litex




[92;1mlitex[0m> 

[92;1mlitex[0m> 

[92;1mlitex[0m> [ 2022-10-27 05:05:28 ]  Injected first fault
[ 2022-10-27 05:05:28 ]  Starting bist
sdram_bist 8192 1
sdram_bist 8192 1

Starting SDRAM BIST with burst_length=%u and addr_mode=%u

                          WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-27 05:05:28 ]  
                          %u %u %u %u %u %u

                          %u %u %u %u %u %u

                          %u %u %u %u %u %u

                          %u %u %u %u %u %u

                          %u %u %u %u %u %u

                          %u %u %u %u %u %u

                          %u %u %u %u %u %u

                          %u %u %u %u %u %u

                          WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-27 05:05:36 ]  
[ 2022-10-27 05:05:36 ]  Correct fault
[ 2022-10-27 05:05:37 ]  Restart litex




[92;1mlitex[0m> 

[92;1mlitex[0m> 

[92;1mlitex[0m> [ 2022-10-27 05:05:37 ]  Starting bist
sdram_bist 8192 1
sdram_bist 8192 1

Starting SDRAM BIST with burst_length=%u and addr_mode=%u

                          WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-27 05:05:37 ]  




[92;1mlitex[0m> 

[92;1mlitex[0m> 

[92;1mlitex[0m> [ 2022-10-27 05:05:37 ]  Starting bist
sdram_bist 8192 1
[ 2022-10-27 05:05:37 ]  expect title line
sdram_bist 8192 1

Starting SDRAM BIST with burst_length=%u and addr_mode=%u

                          WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-27 05:05:37 ]

```

This lasted until 05:13:05 when a timeout occured and the board reconfigured.

The most recent example of wacky data is here, where %2lu was printed out for several lines until a timeout occured 15 seconds later. The fault was corrected and output for the bist resumed normally.

```

[ 2022-10-30 20:15:14 ]  
                                   646          654         2382          0          0          0

                          WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-30 20:15:15 ]  
[ 2022-10-30 20:15:15 ]  
                                   646          654         2706          0          0          0

[ 2022-10-30 20:15:16 ]  
                                   646          654         3030          0          0          0

[ 2022-10-30 20:15:17 ]  
                                   646 %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
%2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu 
[ 2022-10-30 22:58:10 ]  Time out whie expecting title or data
[ 2022-10-30 22:58:10 ]  Correct fault
[ 2022-10-30 22:58:11 ]  Restart litex


2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu %2lu          654         1629          0          0          0


[92;1mlitex[0m> 

[92;1mlitex[0m> 

[92;1mlitex[0m> [ 2022-10-30 22:58:11 ]  Injected first fault
[ 2022-10-30 22:58:11 ]  Starting bist
sdram_bist 8192 1
sdram_bist 8192 1

Starting SDRAM BIST with burst_length=8192 and addr_mode=1

                          WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-30 22:58:11 ]  
                                   646          654          324          0          0          0

[ 2022-10-30 22:58:12 ]  
                                   646          654          648          0          0          0

[ 2022-10-30 22:58:13 ]  

```


This next test printed out crazy data. A timeout occured over and over again as the expected data could not be found.

```

--============= [1mConsole[0m ================--


[92;1mlitex[0m> [ 2022-10-18 17:07:07 ] Running Bist command.
sdram_bist 8192 1
sdram_bist 8192 1

Starting SDRAM BIST with burst_length=8192 and addr_mode=1

                          WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-18 17:07:07 ] 
                                   646          654          324          0          0          0

[ 2022-10-18 17:07:08 ] 
                                  646u`%,u          654u`%$u`       640u`%$ub                                   646u`e,u
6545`%,=        9735`%,=                                   646u`%$u`         654u`%,u       1217u`%,u                  
6465`%,=          654u`e,u       1621u`e,u                 \00                 646u`%,u          654u`%$u`      9946u`%$
ub                                   646u`e,u          6545`%,=       22705`%,=                                   646u`%
$u`         654u`%,u       2515u`%,u                          WR-*W@MIBGsa 2DEBW(-ib/;)  4ESTED@MIBA     %RROZS@       3
EC        DEDB                                   646u`e,u          6545`%,=       :919=`%,=                             
646u`%$u`         654u`%,u       3243u`%,u                                   6465`%,=          654u`e,u       3568u`e,u
\00                 646u`%,u          654u`%$u`      ;812u`%$ub                                   646u`e,u          6545`
%,=        1205`%,=                                   646u`%$u`         654u`%,u        445u`%,u                      
6465`%,=          654u`e,u        769u`e,u                 \00                 646u`%,u          654u`%$u`      1014u`%
$ub                          WR-BWHMaBOs! 2D%BW(Eij/s)( TESTEDHMaBI     ERRORS@       3EC        DED[ 2022-10-18 17:07:
23 ] Timeout occured. Attempting to close, reopen Litex.
[ 2022-10-18 17:07:23 ] Quitting Bist.




S9:;1mlitexS0-> `CGmeafd`not`fgufdj
SY:31-latexSP-6  Cgmmafd`ngt`fgund
S1:;1elitex{S0-> `CGmeafd`not`fgufd[ 2022-10-18 17:07:23 ] Running Bist command.
sdram_bist 8192 1
%&*;%&*;%&*;%&*;%&*;%&j;%&*;%&*;%&*;%&*;%&*;%&*;%&*;%&*;%&*;%&*;%&*;\00[ 2022-10-18 17:07:39 ] Timeout occured. Attempting to close, reopen Litex.
[ 2022-10-18 17:07:39 ] Quitting Bist.




Ifcorrect burstlefo|`
S1:;1elitex{S0-> `CGmeafd`not`fgufdj
SY:31-latexSP-6  Cgmmafd`ngt`fgund[ 2022-10-18 17:07:39 ] Running Bist command.
sdram_bist 8192 1
%&*;%&*;%&*;%&*;%&*;%&";-&";-&";-&";-&";-&";-&";-&";-&";-&";-&";-&";([ 2022-10-18 17:07:54 ] Timeout occured. Attempting to close, reopen Litex.
[ 2022-10-18 17:07:54 ] Quitting Bist.




Ifcorrect burstdenot`j
SY:31-latexSP-6  Cgmmafd`ngt`fgund
S1:;1elitex{S0-> `CGmeafd`not`fgufd[ 2022-10-18 17:07:54 ] Running Bist command.
sdram_bist 8192 1
%&*;%&*;%&*;%&*;%&*;%&j;%&*;%&*;%&*;%&*;%&*;%&*;%&*;%&*;%&*;%&*;%&*;\00[ 2022-10-18 17:08:09 ] Timeout occured. Attempting to close, reopen Litex.
[ 2022-10-18 17:08:09 ] Quitting Bist.




Ifcorrect burstlefo|`
S1:;1elitex{S0-> `CGmeafd`not`fgufdj
SY:31-latexSP-6  Cgmmafd`ngt`fgund[ 2022-10-18 17:08:09 ] Running Bist command.
sdram_bist 8192 1
%&*;%&*;%&*;%&*;%&*;%&";-&";-&";-&";-&";-&";-&";-&";-&";-&";-&";-&";([ 2022-10-18 17:08:25 ] Timeout occured. Attempting to close, reopen Litex.
[ 2022-10-18 17:08:25 ] Quitting Bist.

```

## Timeouts

A few different kinds of timeout errors have occured.

Often, a timeout will occur, and an attempt made to close and reopen Litex will fail. This is an example from a test on 11/2/2022, running with a TMR design. The test ran normal until a timeout occured at 00:45:49 after fault injection. There was a failed attempt to reopen litex, and the board was reconfigured with the bitstream. 

```

[ 2022-11-02 00:45:33 ] 
                                   646          654         2786          0          0          0

                          WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-11-02 00:45:49 ]  Time out whie expecting title or data
[ 2022-11-02 00:45:49 ]  Correct fault
[ 2022-11-02 00:45:49 ]  Restart litex


[ 2022-11-02 00:45:59 ]  Timeout occured restarting Litex
[ 2022-11-02 00:45:59 ]  Configuring JCM with new program
[ 2022-11-02 00:46:07 ]  Starting litex with /dev/ttyUSB2
[ 2022-11-02 00:46:07 ]  Expecting Litex Prompt
```

Here is one where a fault is corrected and Litex closes and reopens again successfully.

```

[ 2022-10-28 09:45:01 ]  
                                   646          654         1591          0          0          0

[ 2022-10-28 09:45:02 ]  
                                   646          654         1915          0          0          0


[92;1mlitex[0m> [ 2022-10-28 09:45:03 ]  
[ 2022-10-28 09:45:18 ]  Time out whie expecting title or data
[ 2022-10-28 09:45:18 ]  Correct fault
[ 2022-10-28 09:45:18 ]  Restart litex




[92;1mlitex[0m> 

[92;1mlitex[0m> [ 2022-10-28 09:45:18 ]  Injected first fault
[ 2022-10-28 09:45:18 ]  Starting bist
sdram_bist 8192 1
sdram_bist 8192 1

Starting SDRAM BIST with burst_length=8192 and addr_mode=1

                          WR-BW(MiB/s) RD-BW(MiB/s)  TESTED(MiB)     ERRORS        SEC        DED

[ 2022-10-28 09:45:18 ]  
                                   646          654          324          0          0          0

[ 2022-10-28 09:45:19 ]  
                                   646          654          648          0          0          0

```

Often, a UnicodeDecodeException will occur before a timeout as seen in this example:

```

[ 2022-10-31 01:33:55 ]  
                                   646          654         2570          0          0          0

[ 2022-10-31 01:33:56 ]  
                                   646          654         2894          0          0          0

[ 2022-10-31 01:33:58 ]  
                                   646          654         3219          0          0          0

[ 2022-10-31 01:33:59 ]  
[ 2022-10-31 01:34:00 ]  UnicodeDecodeException whie expecting title or data
                          [ 2022-10-31 01:34:15 ]  Time out whie expecting title or data
[ 2022-10-31 01:34:15 ]  Correct fault
[ 2022-10-31 01:34:15 ]  Restart litex


[ 2022-10-31 01:34:15 ]  Other exception occured restarting Litex
[ 2022-10-31 01:34:15 ]  <class 'Exception'>
[ 2022-10-31 01:34:15 ]  Configuring JCM with new program
[ 2022-10-31 01:34:23 ]  Starting litex with /dev/ttyUSB2
[ 2022-10-31 01:34:23 ]  Expecting Litex Prompt

```





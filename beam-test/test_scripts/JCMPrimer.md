# JCM and JTAG Primer

Welcome to the CCL Lab for Dr. Wirthlin’s group! This document is an attempt to get you up to speed as efficiently as possible on the JCM. A lot of work has been done on the JCM/JTAG code and a lot of bugs and snags have been found and overcome. Hopefully this document will help you not make the same mistakes and get started quickly. Take the time to read this completely even if you don’t need everything yet, because chances are you may need some of these things in the future. Feel free to add to it as well. Let’s dive right in.

1. **JTAG**: The acronym stands for Joint Test Action Group (the group that made it). Learn more about JTAG at BYU’s Computing Bootcamp Website:
    
    [JTAG presentation by Caden Ellis](https://docs.google.com/presentation/d/1BK4iDBzpEVbI0DaubN6lMWB-D2COckOeole8y7d5qR0/edit?usp=sharing)

    [High-level Guide to JTAG](https://www.xjtag.com/about-jtag/jtag-high-level-guide/)
       
2. **JCM**: The acronym stands for JTAG Configuration Manager. This is the software that controls the JTAG ports on the board. 
    
    [Old Documentation](https://ccl.byu.edu/wiki/projects/jcm/software)

3. **SMAP**: 

## Setting up your JCM
Your JCM setup consists of the following boards and cables.

### Boards

**AVNET MicroZed Board**: This is a red-colored board that we use as the processor for the JCM. It's got a Zynq-7000 SOC that acts as our processor, and it's also got some memory. You'll notice the large ethernet port on one of the ends. That end of the board essentially has almost all of the important things you'll need to use for the JCM setup. Next to the ethernet port is a micro USB port that we use to power the MicroZed board. Between the ethernet port and the micro USB port, there is a slot underneath the board into which we put a micro SD card with an Arch Linux image as well as all the JCM code. The final thing to note is the two male 100-pin connectors underneath the board. We will use these to connect to our JCM Carrier board.

**BYU JCM Carrier Board**: This is a green-colored board that allows us to connect our processor to an external board through JTAG. These external boards will be described below. You will notice that the JCM Carrier has the female 100-pin connectors on top of the board. A completed setup has the MicroZed board mounted on those connectors. In order to mount the MicroZed board correctly, make sure that the ethernet port on the MicroZed is on the same side of the JCM Carrier as the USB-C port on the JCM Carrier. You will use the USB-C port on the JCM Carrier to power up the board. The only other port of interest on the JCM Carrier is the 12-pin female header on the bottom right of the board when you put the USB-C connector on the right. That 12-pin header is one we will use to connect to an external board with our JTAG ribbon cables.

**External Board**: The final board in our JCM setup is some sort of FPGA board, and this usually ends up being a Xilinx Board. Most often, it will be a Series-7 or an Ultrascale board, but we are starting to interface with the Versal family of boards. These boards are usually powered on by a 12 V cable of some sort, and the only other connection we have to it is the JTAG ribbon cable that comes from the JCM Carrier board. These boards are the ones we test with radiation, so most of the setup we have is to allow us to configure these boards and run tests on them.

### Cables

To fully setup your JCM system, you will end up needing a total of 6 cables:

**USB-C**: We plug this one into the JCM Carrier board to power it up.<br>
**Micro USB**: This one powers up the MicroZed board.<br>
**12V Power Cable**: This one is usually goes into a circular port on our external Xilinx boards and is used to power them up.<br>
**JTAG Ribbon Cable**: This cable has two male 12-pin connectors on each end and connects the JCM Carrier and the external board.

To complete the physical setup, you will need a **USB to Ethernet Cable** of some sort as well as an **ethernet cable**. Use these to connect your local computer to the MicroZed board.

### Final Setup Steps

The picture below shows an example of what your setup should look like after you are done physically putting everything together.

![JCM Setup](images/JCM_Setup.jpg)

After you have physically constructed your JCM system, you just need to let your computer know that you have another network cable that you want to set up.

The following instructions only apply to Ubuntu 20. We will add instructions for other operating systems as we figure them out.

Go to your network settings. You should already have the ethernet cable connected from your computer to the MicroZed. Once it is connected, turn the JCM on, and you should see two connections: one that says **PCI Ethernet** and one that says **USB Ethernet**. The PCI Ethernet is the one your computer uses for internet, so we don't need to mess with that one.

The USB Ethernet is the one that connects you to the MicroZed board. Click on the gear to the right, and we'll put in some additional information that will allow us to connect to the JCM.

When we created the Arch Linux image on the micro SD card, we configured it to have a static IP address of 169.254.132.152 so that we can easily connect to it. Now that you are in the Wired Settings for the USB Ethernet, click on the IPv4 tab on the top and select the "Manual" option for the IPv4 Method.

We now need to tell your computer which static IP address you want the manual IPv4 connection to have. On the first line under "Addresses", put 169.254.132.150 for the Address and put 255.255.255.0 for the Netmask. All you need to do now is click the green "Apply" button at the top right and you should be all set up to connect to the JCM.

**WARNING** - If you have been paying attention to all of these instructions, you have probably noticed that the IP address we put into the Network Settings isn't exactly the same as the static IP address we have configured the JCM to have. This is because the Network Settings only wants you to have the same **subnet** as the IP address you will be using. This means that only the first three numbers in the IP address need to match exactly. We change the fourth number to 150 when we put it into Network Settings so that everything works out. In other words, you didn't read the instructions above wrong, and there isn't a typo. If you do end up putting the exact IP address into Network Settings, your setup will not work, and it may be hard to figure out what is going on.

All of the above is there to say that while we put an address that differs slightly from the actual IP address into Network Settings, we will use the exact IP address when we connect to the JCM.

## Logging into the JCM
We use SSH to log in to the JCM's terminal and run the software. The typical format for logging into something via SSH is as follows:

```
ssh <username>@<ip_address>
```

There are a few options you can use for doing this every time.

Before going over the options, here is just a reminder of some of things we have set for the JCM:<br>
Static IP Address: **169.254.132.152**<br>
Username: **root**<br>
Password: **chrec**

**Option 1**: The first option is to type in the whole IP address each time you want to log into the JCM.

```
ssh root@169.254.132.152
```

If your computer can successfully connect to the JCM, it will prompt you for your password, in which case you simply need to type `chrec` and press Enter. Upon entering the correct password, the prompt on your terminal will change to look like this:

```
[root@arch ~]#
```

**Option 2**: You can accomplish all of the above in an easier way. This option is one used by Josh Hanni to make login much easier. You can modify your .bashrc file on your local computer to include an alias like the one below:

```
alias sshjcm="ssh root@169.254.132.152"
```

After adding this line and sourcing your .bashrc file, you can log into the JCM using whatever alias you have created.
       

## Notes on the General Organization of the Code:
Getting familiar with a big code base and being able to contribute to it is a very valuable skill. Here is some help to get familiar with how everything is organized. 

### Code Origin and GitHub setup
As mentioned before, your MicroZed board has a micro SD card that contains an Arch Linux image with the necessary setup and drivers as well as all the code we run on the JCM. When you login, you will be in your home (~/) directory, which on the JCM is the `/root` directory. In this directory, there is a folder called `git/`. We have cloned the repository with all the JCM code into the `/root/git` folder, and it is typically named `jcm/`

This repository is hosted on GitHub, and it can be found [here](https://github.com/byuccl/JCM). This is a private repository, so you will have to be added by Dr. Wirthlin to have access to it on your personal GitHub account.

There are many branches of this repository, but the one that is usually put onto a JCM is the `appDevel` branch. This is the branch that has our most up-to-date code for our JCM testing. Because it is our most updated branch, there are many times you will need to do a fresh pull of the code onto the JCM.

With the JCM configured and connected to your computer through its static IP address, it will not be able to connect to the internet. It will only be able to connect to your computer through SSH. For this reason, whenever you need to connect to GitHub (whether to pull or push code), you will need to adjust your connection settings to do that. The instructions for doing that as well as changing back are below.

<hr>

#### Connecting to the Internet:

This process seems to always change depending which computer you are on. Here is one way that typically works:

1. Change the JCM connection from Manual to Shared Internet (In Network Settings, IPv4):
2. Log into the JCM.
3. Run `dhcpcd` on board
4. Unplug the ethernet cable from your computer (not just the JCM) 

**At this point, you may need to open and close the connection editors a few times and wait for the IP to change.** You can try `systemctl restart dhcpcd` and run `dhcpcd` again. Another thing you can do is to go to your network settings and switch off and on the USB ethernet port that connects to the board.

5. If you don’t know the IP address at this point, continue with this step. If you do, skip to step 6. On Josh Hanni’s board, the IP address is 10.42.0.133, and the IP address will usually be something similar to that one (the last number will typically be the only different one). The steps for finding out your specific IP address are below:

If you don’t have Screen installed on your device run:

```
sudo apt install screen
```

Connect to the JCM using Screen:

```
sudo screen /dev/ttyUSB0 115200
```

Once you execute that, it will ask for an arch login and password. Type in `root` for the login and `chrec` for the password.

Once you are logged in, find the IP address using `ifconfig`

6. SSH onto the JCM using the new IP address (rather than staying strictly with screen, because screen is really slow).
Now you can do github commands!

#### Changing Back:

1. Change the connection back to manual in settings (In Network Settings, IPv4)
2. Put in the IP address (make sure that the last number is different from the one on the board, otherwise you will have a very tricky bug). 
3. Turn off the JCM to get it back to its static IP.
4. Turn it back on and connect after waiting a few minutes.

*Important*:
Make sure that when you switch your IP address back, you don’t use the same IP address as the board. Just the same subnet. This means just the first 3 numbers are the same. Took me 3 days to figure out that problem. 
(Example: Make the IP address of the connection 169.254.132.150, NOT 169.254.132.152 because that is the IP of the board. Just the first 3 numbers need to match)

Static IP of Board: 169.254.132.152

When you SSH again there may be a warning message. Go ahead and run the command it suggests then try to connect again.

<hr>

You will likely become very used to this process as you work on the JCM, so becoming familiar with connecting to the internet and then changing back to the static IP address will be a useful skill.

Now that you know how to connect to the internet, it will be helpful and time-saving to set up your JCM to connect to GitHub on your profile with an SSH key so that you can very easily push and pull code.

With your JCM connected to the internet, do the following to generate and add an SSH key to the JCM and GitHub:

1. Login to the JCM.
2. Type the following into your terminal, substituting in your GitHub email address:

```
ssh-keygen -t ed25519 -C "your_email@example.com"
```

3. When you're prompted to "Enter a file in which to save the key," press Enter. This accepts the default file location.
4. You will then be prompted to "Enter passphrase" and then "Enter same passphrase again." I typically just press Enter both times so that I don't have to type it in each time I connect to GitHub.
5. You now have an SSH key. To add it to the ssh-agent, you must first start the ssh-agent in the background like so:

```
eval "$(ssh-agent -s)"
```

6. You can then add your SSH key to the ssh-agent by running the following command:

```
ssh-add ~/.ssh/id_ed25519
```

7. Now that you've done that, you can add the SSH public key to your GitHub account. Copy the key to your clipboard.

```
cat ~/.ssh/id_ed25519.pub
# Then select and copy the contents of the id_ed25519.pub file
# displayed in the terminal to your clipboard.
```

8. In the upper-right corner of any GitHub page, click your profile photo, then click **Settings**.
9. In the "Access" section of the sidebar, click **SSH and GPG keys**.
10. Click **New SSH key** or **Add SSH key**.
11. In the "Title" field, add a descriptive label for the new key. I typically put "JCM" or something similar to that.
12. Paste your key into the "Key" field.
13. Click the green **Add SSH key**.
14. If prompted, confirm your GitHub password.

With these steps completed, you should be able to easily push and pull to GitHub from the JCM whenever you need to do that.

All of the steps above are picked and chosen from some GitHub Docs. I'll put the links to them below if you run into any issues with these steps:

[Generate a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

[Add a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)

### Downloading and Installing the Xilinx SDK:
It is essential to download the Xilinx SDK on your work computer if you want to save a lot of compile time by compiling on your work computer (rather than compiling on the JCM directly, which takes way longer). You would then copy the executables over to the JCM. (There are short commands for copying the executables near the end of this document under the helpful .bashrc files section)

For the whole **docker** process, follow these instructions
(You may have to be added to the group):

[Docker Instructions](https://github.com/byuccl/JCM/blob/master/doc/docker/Vivado_2017_1.md)

For just the **SDK**, you have two options:

**If you have Ubuntu 20, please run the following commands before the install process, otherwise Vivado will never finish installing.**

```
sudo apt install libtinfo5
sudo apt install libncurses5
```

**Option 1**: We will download the Vivado installer from the FPGA server (2017.4 in the example). First make sure you can log into the FPGA server. 

```
ssh <username>@fpga.ee.byu.edu
```

Then go to /fpga3/SoftwareInstallers/Vivado/2017.4. Remember this path and then use it to copy the tar file **from** the server **to** your computer, **running the command on your own computer** (not logged into the fpga server; it will throw an error):

```
scp <username>@fpga.ee.byu.edu:<path to file>/Xilinx_Vivado_SDK_2017.4_1216_1.tar.gz ~/Desktop
```

This command will copy the file over to your desktop, but you can feel free to put it wherever you would like it to be on your computer. 

**Option 2**: You can download the Vivado installer directly from the Xilinx Website. Click on [this link](https://www.xilinx.com/support/download.html). Then select "Vivado Archive" under the "Version" label on the left. Then click on "2017.4" on the list that shows up and select the download option that says "Vivado Hlx 2017.4: All OS installer Single-File Download (TAR/GZIP - 16.17 GB)". This will download the same file to your computer that option 1 copies to your desktop.

**The following instructions apply to both options above.**

In your terminal, navigate to the directory you have the new file and unpack it with this command:

```
tar -xvzf Xilinx_Vivado_SDK_2017.4_1216_1.tar.gz
```

Once that is done executing, run:

```
cd Xilinx_Vivado_SDK_2017.4_1.tar.gz
sudo ./xsetup
```

Make sure you use sudo. Then follow these steps once the installer opens:

* "A Newer Version is Available" - Don't select the latest tools - select Continue
* Welcome: Select "Next"
* License Agreement: Agree to all terms, Select Next
* Select Installation to Install: Select Vivado HL Design Edition
* Vivado HL Design Edition
* Design Tools: Select the SDK (not default)
* Devices: Deselect all except: Production Devices->SOC->Zynq-7000
* Installation Options: Deselect all
* Select Destination Directory
* Leave default "/opt/Xilinx", Select Next (confirm making a new directory)
* Click "Install"
      
Wait while the installer completes the full installation. Ignore the dialog box indicating that there are new updates and exit the installation.

The reason you downloaded all of this onto your computer is so that you can cross compile the JCM code. This means that your computer will be able to compile the code as if it had the same compiler as runs on the JCM. In order to instruct your computer to do this, however, you will need the Vivado environment settings to be added to your path. You can do this a few ways, and these will be outlined below.

**Option 1**: Modify the .bashrc file to automatically run the Vivado environment settings when a new shell is created:

```
echo  >> ~/.bashrc
echo "# Set Vivado environment variables" >> ~/.bashrc
echo "source /opt/Xilinx/Vivado/2017.4/settings64.sh" >> ~/.bashrc
echo "source /opt/Xilinx/SDK/2017.4/settings64.sh" >> ~/.bashrc
```

The nice part about this option is that you will never have to worry about running the Vivado environment settings manually since your computer will prepend them to your path every time you open a new terminal. This will make cross compiling for the JCM very convenient, and this is a very good option.

There are a few times that this might cause a few issues for you. If you are working on any other projects where you need to use a newer or different version of Vivado, you may not necessarily always want the 2017.4 SDK’s environment always prepended to your path since you may end up using the wrong version. Another time you may not always want these on your path is if you are using newer versions of CMake for another project. The Vivado SDK 2017.4 makes it so that your machine will be using CMake version 3.3.2, and you may run into complaints from your computer if you have a project where you use a later version.

That being said, those problems aren’t necessarily the biggest hindrances, and they aren’t that hard to circumvent. It is just good to know that those are some of the consequences of using this convenient option.

**Option 2**: Manually run the Vivado environment settings every time you want to compile the code for the JCM on a new terminal:

```
source /opt/Xilinx/Vivado/2017.4/settings64.sh
source /opt/Xilinx/SDK/2017.4/settings64.sh
```

This option seems to trade all of the convenience from option 1 for better control over your PATH variable in your system environment. While it is nice that you will have complete control over when the Vivado environment settings are prepended to your path, it is annoying to have to run both of those commands in your terminal when you want to cross compile.

**Option 3**: This option is, in Josh Hanni’s opinion, the one that gives the same control and is slightly less annoying than option 2. This involves adding an alias to your .bashrc file like the one below:

```
alias jcm_env=“source /opt/Xilinx/Vivado/2017.4/settings64.sh && source /opt/Xilinx/SDK/2017.4/settings64.sh”
```

This will make it so that when you want to compile, just typing “jcm_env” into the terminal will run the Vivado environment settings. While option 1 is definitely the most convenient, this one gives you more control while avoiding typing two long commands before compiling in a new terminal.

Ultimately, it is up to you to determine which option will suit your personal preferences and needs best. If you don’t have any other projects or need for any other Vivado or CMake versions, option 1 will probably be just fine and not mess with anything. Otherwise, the other two options are here to consider. There are likely more options out there, and as we keep building the make system for the JCM, we can hopefully make it more convenient for everyone. Until then, these are what we’ve got.

**NOTE**: To compile the code on your own computer, you need to make sure that “ccache” is installed. If you get an error when running make about ccache, make sure that you run these commands.

```
# Install package
sudo apt install -y ccache

# Update symlinks
sudo /usr/sbin/update-ccache-symlinks

# Prepend ccache into the PATH
echo 'export PATH="/usr/lib/ccache:$PATH"' | tee -a ~/.bashrc

# Source bashrc to test the new PATH
source ~/.bashrc && echo $PATH
```

### 7 Series FPGAs Configuration User Guides:

Here is the very useful link for the [FPGA User’s Guide](https://www.xilinx.com/support/documentation/user_guides/ug470_7Series_Config.pdf).

[Clock Usage Guide](https://www.xilinx.com/support/documentation/user_guides/ug472_7Series_Clocking.pdf)

[Nexys Video Guide](https://reference.digilentinc.com/_media/reference/programmable-logic/nexys-video/nexysvideo_rm.pdf)

### How to Setup VSCode to work with SSH:
Editing code in VSCode is very handy. 
One option is to have all of the code on your main computer, edit it in VSCode, and then copy all of the files to the JCM over SSH. However, this is very slow. 
A better option is to set up VSCode to work over an SSH tunnel, so you can edit the code on the JCM directly while also viewing the code in VSCode. 

This [link](http://linux427.groups.et.byu.net/wiki/doku.php?id=setup_vscode) has good tips for how to do so, as well as setting other things up like SSH keys, under “Setup.”
Setup SSH keys with the JCM, as this will save time with passwords.

With VSCode, it may take several tries to connect to the JCM. Keep trying.

### Setting Up Valgrind:

Valgrind is really good for finding memory leaks and uninitialized variables. 

If you're running Linux and you don't have a copy already, you can get Valgrind from the Valgrind download page. (You don’t have valgrind if you type `valgrind` into the terminal and it doesn’t know what it is). 
Download the tar file and `scp` it over to the JCM. 

Installation should be as simple as decompressing and untarring using bzip2 (XYZ is the version number in the below examples).

```
bzip2 -d valgrind-XYZ.tar.bz2
tar -xf valgrind-XYZ.tar
```

This will create a directory called valgrind-XYZ; change into that directory and run:

```
./configure
make
make install
```

The `make` command took many hours to run on the jcm, so make sure to do this at the end of the day so it can finish by morning. 

Below is an example of running an excutable through valgrind while checking for memory leaks:

```
valgrind --tool=memcheck --leak-check=yes <executable> <args>
```

This will give a good memory check. See more about the commands in the following [link](https://www.cprogramming.com/debugging/valgrind.html).

### Using GDB:
GDB is really good at finding the source of segmentation faults. It should be built into the linux system already. 

Make sure that you are in the directory with the file you would like to test.<br>
Type `gdb` into the terminal to start running the debugger.<br>
Type `file <program>.elf`. <br>
Type `r <args>` to run an executable in the debugger.

For Python, do the same thing but run `gdb python` at the beginning.

[Intense Documentation](https://sourceware.org/gdb/current/onlinedocs/gdb.pdf)

[Cheat Sheet](https://darkdust.net/files/GDB%20Cheat%20Sheet.pdf)

### SWIG:

"SWIG is a software development tool that simplifies the task of interfacing different languages to C and C++ programs." - SWIG Documentation

SWIG can help us create python executables from C++ source code. 

Read more about the documentation of SWIG [here](https://github.com/byuccl/JCM/blob/appDevel/jcm_source/python/swig/README.md)


### Setting Up CI:
As of writing this, we don’t have continuous integration set up. Here are a few ideas of things that would be helpful to make a part of the continuous integration process. 
* C++ Linter and Formatter
* Pylint
* Run “make clean” and “make _jcm.so” in SWIG, which is very picky about correct code
* Run Valgrind on the executables. Will also find uninitialized variables
* Make tests to go along with the executables, with different options and set outputs

### How to Back Up the SD Card:
Add this

### .bashrc’s to Make your Life Easier:

Work Computer .bashrc (Just add the lines below to the end of your .bashrc. Read the notes)

```
################################################################

# Set Vivado environment variables
source /opt/Xilinx/Vivado/2017.4/settings64.sh

# ssh alias for the JCM
alias sshzynq='ssh root@169.254.132.152'

# This will copy all of the jtag executables from your work computer to the JTAG directory 
# on the JCM. HAS TO BE RUN IN THE SAME DIRECTORY AS THE JTAG EXECUTABLES
alias copy_exec_jtag='scp *.elf root@169.254.132.152:/root/git/jcm/jcm_source/base/apps/jtag'

# This will copy all of the executables from your work computer to the apps directory 
# on the JCM. HAS TO BE RUN IN THE SAME DIRECTORY AS THE APPS EXECUTABLES
alias copy_exec_apps='scp *.elf root@169.254.132.152:/root/git/jcm/jcm_source/base/apps/'

##################################################################
```


JCM .bashrc (Just add the lines below to the end of your .bashrc. Read the notes)

```
################################################################

export JCM_HOME="/root/git/jcm/"
export JCM_SRC_PATH="/root/git/jcm/jcm_source/base/"
alias jtag_dir="cd ~/git/jcm/jcm_source/base/apps/jtag"
alias prog="./jcm_jtag_xilinx_read_config_reg.elf --chain '[4 6]' -d 1 --part xc7z020 --prog -c 1000000"
alias prog2="./jcm_jtag_reg.elf --chain '[4 6]' -d 1 -r 0xb --writeword 0 --readir -c 10000000"
alias read_ir="./jcm_jtag_reg.elf --chain '[4 6]' -d 1 -r 9 --swap --readir"
alias jcm_config="./jcm_config.elf --jtag --chain '[4 6]' -d 1 --part xc7z020 --config_file /root/git/jcm/jcm_source/base/bit_files/zed_0.bit -c 1000000"
alias config="./jcm_jtag_xilinx_full_configure.elf --chain '[4 6]' -d 1 --part xc7z020 -f /root/git/jcm/jcm_source/base/bit_files/zed_0.bit -c 10000000"

alias prog_nexys="./jcm_jtag_xilinx_read_config_reg.elf --chain '[6]' -d 0 --part xc7a200t --prog -c 1000000"
alias prog2_nexys="./jcm_jtag_reg.elf --chain '[6]' -d 0 -r 0xb --writeword 0 --readir -c 10000000"
alias read_ir_nexys="./jcm_jtag_reg.elf --chain '[6]' -d 0 -r 9 --swap --readir"
alias jcm_config_nexys="./jcm_config.elf --jtag --chain '[6]' -d 0 --part xc7a200t --config_file /root/git/jcm/jcm_source/base/bit_files/nexys_0.bit -c 1000000"
alias config_nexys="./jcm_jtag_xilinx_full_configure.elf --chain '[6]' -d 0 --part xc7a200t -f /root/git/jcm/jcm_source/base/bit_files/nexys_0.bit -c 10000000"
alias find_clock_nexyx="python3 find_clock_rate.py -r 9 --part xc7a200t -f /root/git/jcm/jcm_source/base/bit_files/nexys_0.bit -d 0"
##################################################################
```

Remember to source your .bashrc after. 

### Super helpful linux commands:
Run this in the jcm_source directory and find every occurrence of ”XilinxConfigInterface” that occurs in a .cpp or .h file, with a recursive check, with the line number.

```
grep --include=\*.{cpp,h} -rnw base -e "XilinxConfigInterface"
```

### List of Executables that have passed Valgrind (can verify):
jcm_jtag_reg.elf<br>
jcm_jtag_raw.elf


### Failed Valgrind:
Everything else

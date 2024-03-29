****************************************************************************************
AimTrak on Unix and Raspberry Pi
****************************************************************************************

Emulators
1 Mame by MameDev.org
1.1 Using python script

A script has been created to setup the files required to have AimTrak run.  This is a python 3.6 script and follows the actions stated in the sections below.
To excute the file do the following;
python aimtrak_setup.py -s

Reboot the machine.  Then with aimtrak guns plugged in;
python aimtrak_setup.py -m <path to mame.ini>

The first run will ask for super permissions to add udev and X11 files.
The second run will ask for the Ultimarc id's if you have more than one AimTrak gun.  It will then place those in the mame.ini file.

If your mame.ini file does not exist run mamedev without a rom listed, then 'Configure Options', last 'Save Configuration'.  Exit then run the script.  Using the command line option -createconfig adds in the lightgun indexes, this script does not account for those existing in the file.

1.2 Udev rule -  65-aimtrak.rules

Create the file 65-aimtrak.rules in /etc/udev/rules.d  You will need super permissions to create and edit the file.  The contents of the file are below.  SUBSYSTEMS starts each entry and all other values need to be on the same line as SUBSYSTEMS.

# Set mode & disable libinput handling to avoid X12 picking up the wrong interfaces/devices.
SUBSYSTEMS=="usb", ATTRS{idVendor}=="d209", ATTRS{idProduct}=="160*", MODE="0666", ENV{ID_INPUT}="", ENV{LIBINPUT_IGNORE_DEVICE}="1"

# For ID_USB_INTERFACE_NUM==2, enable libinput handling.
SUBSYSTEMS=="usb", ATTRS{idVendor}=="d209", ATTRS{idProduct}=="160*", ENV{ID_USB_INTERFACE_NUM}=="02", ENV{ID_INPUT}="1", ENV{LIBINPUT_IGNORE_DEVICE}="0"

1.3 X11 Configuration -  60-aimtrak.conf
Create the file 60-aimtrak.conf in /etc/X11/xorg.conf.d.  You will need super permissions to create and edit the file.  The contents of the file are below

Section "InputClass"
        Identifier "AimTrak Guns"
        MatchDevicePath "/dev/input/event*"
        MatchUSBID "d209:160*"
        Driver "libinput"
        Option "Floating" "yes"
        Option "AutoServerLayout" "no"
EndSection

*NOTE: if xorg.conf.d directory does not exist on your system, the file can be placed in /etc/X11/Xsession.d.

1.4 AimTrak Setup
1.4.1 Single Gun

When editing the mame.ini file please remember if you save in UI it will most likely overwrite the configuration and remove the needed items for the aimtrak to work.  Also the UI can create machine(game) specific ini files located next the mame.ini file that will override the mame.ini file values when the game loads.  If the aimtrak stops working check for the machine specific ini file.  If want to keep the file then the following will need to be changed and added to that file too.

Change these entries to the following:
mouse                1
lightgun             1
offscreen_reload     1
lightgun_device      lightgun

Add the following at the end of the file.
#
# SDL Lightgun indexes
#
lightgun_index1    “Ultimarc Ultimarc”

1.4.2 Multiple AimTrak

Follow the instructions in the AimTrak Setup Guide for changing the id of the Aimtrak guns.

Run the following command on console

xinput

The ouput will be something similar to this
⎡ Virtual core pointer                    	id=2	[master pointer  (3)]
⎜   ↳ Virtual core XTEST pointer              	id=4	[slave  pointer  (2)]
⎜   ↳ Synaptics TM3053-003                    	id=12	[slave  pointer  (2)]
⎜   ↳ TPPS/2 IBM TrackPoint                   	id=13	[slave  pointer  (2)]
⎜   ↳ Ultimarc Ultimarc                       	id=14	[slave  pointer  (2)]
⎣ Virtual core keyboard                   	id=3	[master keyboard (2)]
    ↳ Virtual core XTEST keyboard             	id=5	[slave  keyboard (3)]
    ↳ Power Button                            	id=6	[slave  keyboard (3)]
    ↳ Video Bus                               	id=7	[slave  keyboard (3)]
∼ Ultimarc Ultimarc                       	id=15	[floating slave]
∼ Ultimarc Ultimarc                       	id=16	[floating slave]
∼ Ultimarc Ultimarc                       	id=17	[floating slave]

Change the following in the mame.ini or machine specific ini file.

#
# SDL Lightgun indexes
#
lightgun_index1    14
lightgun_index2    15
lightgun_index3    16
lightgun_index4    17

The numbers will be the id numbers from the output for the different Ultimarc Ultimarc devices

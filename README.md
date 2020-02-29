# rpi-radio
A Python script to play webstream-radio

This is based on

https://www.instructables.com/id/Raspberry-Pi-Radio/

The license is CC BY-NC-SA.

I refactored the original to support:

* radio streams in a separate file
* keyboard controls
* Use button of rotary encoder for channel switch
* Use rotary encoder for volume
* some cleanup

# Installation notes

install raspian buster lite
add the file "ssh" to the boot partition of the sd card
update && upgrade 
install mplayer git
Remove the line

dtparam=audio=on

from /boot/config.txt if it exists.
You don’t have to edit /etc/modules anymore, but need to load the correct device tree file. To do this, you must edit /boot/config.txt and add the following line

DAC FOR RASPBERRY PI 1/DAC+ LIGHT/DAC ZERO/MINIAMP/BEOCREATE/DAC+ DSP
dtoverlay=hifiberry-dac

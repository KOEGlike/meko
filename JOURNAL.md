---
title: "Meko Music Player"
author: "koeg"
description: "A high definition music player with bluetooth support, which has an e paper display and a physical wheel"
created_at: "2025-04-29"
---
## 04.29: chose the soc, and usb uart switchin
- choose the esp32-mini-1u because it has support for bluetooth audio and rust 
- this chip doesn't have an integrated usb controller, so I had to choose a chip for usb to uart
**Total time: 1.5**
## 05.05: added the dac/amp chip, added display connector
- there is little info on high quality dac/amp chips, after many days of research and pain a choose the ES9218P, which is a really nice chip to work with, but the datasheet is a bit lackluster
**Total time: 2h**
- chose a display, added the flex pcb connector for it
**Total time: 2h**
## 05.07: added the hall-effect sensor for the wheel
- I saw a wide where a guy made a high precision scrolling device, and he used a hall-effect sensor, I chose to go down this rout because there is no rotory encoder to ware out 
**Total time: 1h**
## 05.08: power, lil bit
- Copy pasted bms and power path chip from previous project, did some calculations, changed resistor values
**Total time:1h**
## 05.09: power and usb
- Chose a dual output switching regulator, implemented usb to uart chip
**Total time: 1.5h**
## 05.10: audio
- Read the datasheet far more times than i would like to admit
- Some things are not clear 
- implemented the things that I kind understand 
- asked a question on stackexchange
**Total time: 1.5h**
## 05.17: some Chad replied to my question on electronics stackexchange. 
- Someone who has experience with this rare chip, YIPPPEEEEEE
- I will have to use a oscillator, not a crystal, and low noise LDOs instead of switching regulators
- Did some research on mems vs oscillator vs crystal
**Total time: 2h**
## 05.18: implemented to suggestion from stackexchange
- oscillator instead of crystal
- added low noise LDOs
**Total time: 2h**
## 05.22: Added components, choose LDOs
- I switched from a esp32-mini-1u to a esp32-pico-mini-02, for an integrated pcb antenna and a smaller from factor
- Chose the micro SD slot, and added it to to the schematic
- the same chad from electronics stackexchange replied to my other question about power delivery for this chip
- Did a lot of datasheet reading abot LDOs and what to choose, and decided that will try to solder 1mm*1mm packages 
**Total time: 3h**
## 05.23: Power, power, POWER 
- implemented the LDOs
- learned a lot about filters, low-pass, high-pass, etc. Interesting topic 
- again lots of reaiding
**Total time: 4h**
## 05.24: inter chip COM 
- the esp32 has a f#$* up io multiplexer if you want to do multiple things
- the SD card pins and the JTAG pins are the same, so if you use an SD card you cant use JTAG, or vice-versa 
- all of the pins that can output a i2s clock signal are used by uart or the boot pin
- might need to figure something out for using the same pins for different things
- wired up the hall-effect sensor, en and boot pins with the usb-to-uart adapter, some parts of the dac/amp chip
- created a symbol for my display
- read a bunch again
**Total time:5h**

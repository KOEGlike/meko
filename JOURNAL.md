---
title: "Meko V3"
github: "https://github.com/KOEGlike/meko"
description: "A Linux music player with DDR3, a 70Hz e-paper display and a haptic touchpad"
created_at: "2026-07-12"
---

# 2026.07.12: Thinking of what I need to change

_This will be a long journal, because I did a lot of research beforehand_

For V2, I went with an MCU(microcontroller unit) which are low power processors, and can't run normal OSs. This - I found out while developing the firmware - was a really limiting factor, mainly because the embedded RTOS that I was forced to use with this specific MCU(nRF5380), Zephyr.

## Zephyr rant

![zephyr logo](https://cdn.hackclub.com/019f6765-8668-7584-b6df-d85233e2b156/image.png)

The thing to know about Zephyr is that it has literally no docs for any of the built-in drivers, so you have to look at examples(if they even exist) to figure out how the hell the driver works. In theory, Zephyr would be awesome; it is similarly structured to how Linux works, has a bunch of built-in drivers, has standard APIs for similar peripherals, and a bunch of cool stuff, but in reality the lack of docs, the complicated build system, and the unclear runtime errors just make it impossible to actually use.

Thank you for listening to my rant.

## The solution: Linux

![linux logo](https://cdn.hackclub.com/019f6765-df8c-71df-9d94-99a626b2e400/image.png)

I realized that with the features I wanted (Wi-Fi, Bluetooth, BLE, high-quality audio, streaming support, USB DAC functionality), Linux was a must; it has better docs, support for a bunch of ICs that I need, etc. But to run Linux, I need an MPU(microprocessor unit); the main difference between an MPU and MCU is that the MPU has an MMU(memory management unit), which allows the use of external memory - like DDR - which Linux needs to run (doesn't actually, but in reality it's a necessity).

## Choosing an MPU

![SAMA7D65-V/4HB](https://cdn.hackclub.com/019f6768-2877-740e-92f0-70b723a492ab/image.png)

This is the part that I'm still not done with; I'm really torn between the SAMA7 series from Microchip and the STM32MP1 series from STM, both are really awesome chips, the SAMA7 has a really good audio engine and relatively good GPU, and the STM32 is really easy to implement and it also has a pretty good GPU and audio peripheral. I would lean towards the SAMA7, but that is only available in a 0.65mm BGA package, which is really hard to fan out, while the STM32MP1 has a 0.8mm pitch, which is really easy to use. I think the strategy I will go with is to try to route the SAMA7, and if I fail miserably, I will switch to the STM32.

Two articles were really helpful researching this topic: [this one](https://jaycarlson.net/embedded-linux/), and [this one](https://www.thirtythreeforty.net/posts/mastering-embedded-linux-part-1-concepts/)

## 70Hz e-paper

![drawing of display](https://cdn.hackclub.com/019f6764-a657-7f59-a516-7d014b1332f0/image.png)

V2 had a normal e-ink screen, which had a max partial refresh rate of 0.5s, which is really bad, but for a music player it's alright. But I wanted more!!! So I found out about Sharp MIP displays, which give the effect of e-ink - they don't have a backlight, are mostly black and white, and they are really low power - but they have a higher refresh rate and always need to be powered; for example, the display that I chose (LS022B7DH03) has 70Hz.

## RAM

![lpddr3](https://cdn.hackclub.com/019f6767-5722-7828-809c-23a2a2671b86/image.png)

One of the main reasons I didn't go with a SiP(an IC where both the MPU and RAM are in the same package) is because they mostly only package DDR3L or DDR2L, which have significantly higher power consumption than LPDDR2/3. Both of my chosen MPUs support both LPDDR2 and LPDDR3, so I will be most likely going to use LPDDR3, and 512MB of it, because these MPUs would be sooner bottlenecked by their performance than from the amount of RAM, and 512MB seems to be the sweet spot from what I read on forums/articles.

## _Time Spent: 8h_

# 2026.07.15: Making a custom BGA symbol = HELL

So I realized that the SAMA7 doesn't have a premade footprint and symbol :YAYAYAY:

## Footprint

I heard from Cyao that KiCad has some pretty good built-in BGA footprint generators, so I started researching. Turns out it's pretty easy to use; you only need to add a new entry to a YAML file with the specs of your footprint, and boom, you have a 3D model and footprint. I even made a [pull request](https://gitlab.com/kicad/libraries/kicad-footprint-generator/-/merge_requests/2132) to the main repo, so the footprint can be included in the KiCad default library.

![footprint](https://cdn.hackclub.com/019f6759-1979-74bb-8e4a-e8a1b97e00c4/image.png)
![3d model](https://cdn.hackclub.com/019f6759-1d18-708f-9c76-50ef3c12f1f2/image.png)

## Symbol

This is the part that is hell.

First, the [official KiCad symbol generator](https://gitlab.com/kicad/libraries/kicad-library-utils/-/tree/master/symbol-generators?ref_type=heads) doesn't work out of the box; I had to ask Gemini to fix it 💀 Also, the documentation is really hard to find for both the footprint generator and symbol generator. Also, Microchip doesn't provide a clean .csv file that I can easily process; that would be too easy. Instead, they have all their pins listed in an HTML table, with a bunch of row groups and stuff that makes it really hard to parse. I spent like 1.5h getting this fricking script working, but in the end, with the help of Gemini, I had made a script that converts the HTML table into a CSV file that the KiCad symbol generator can use. So now I have a massive monolithic symbol, with all the pins and their alternate functions that I now need to split up into separate units.

![massive symbol](https://cdn.hackclub.com/019f6759-21a5-749a-91b8-43729f18471b/image.png)

## Also, I did some RAM research

I asked around in a bunch of communities for advice on DDR3 learning resources, and I got some really good answers. Turns out bit/byte swapping on LPDDR3 is a bit more complicated, but I still don't fully understand and need to do more research. I hope I don't even need to do this, crossing my fingers!!!

## _Time Spent: 6h_

# 2026.07.16: Split apart the symbol

This was mostly a long monotonous but fun process of looking at the datasheet and organizing the pins into units. I took a bunch of inspiration from Cyao's SBC.

![split up symbol](https://cdn.hackclub.com/019f6f8c-4fbe-7dd1-bb52-e04dcd09edba/image.png)

## _Time Spent: 4h_

# 2026.07.19: Made PMIC symbol and did some research

## PMIC

Microchip recommends two PMICs for the SAMA7, the MCP16501 and MCP16502; the MCP16501 can't do dynamic voltage adjustment, and doesn't let the SAMA7 go up to 1GHz, so the obvious choice was the MCP16502. Luckily Component Search Engine already had a base symbol that I could use as a starting point, but it had the pins arranged based on the footprint, so I just needed to arrange the pins in a way that it made sense. I used a built-in footprint from KiCad, so I didn't have to make that.

![pmic symbol](https://cdn.hackclub.com/019f7bef-e38d-7d60-a8aa-58aecc442bcb/image.png)

## RAM research

I messaged Cyao about where he sourced his RAM when he made his SBC, because I couldn't find LPDDR3 on Mouser/LCSC/DigiKey, and other western sites sold these chips for pretty expensive. Turns out Taobao has some pretty cheap RAM, $5 for 1GB.

Also I learned that GB and Gb are different, GB is a gigabyte and Gb is a gigabit, which is 8 times smaller than a gigabyte. Thanks Cyao!

In the end I landed on a 16Gb chip from Samsung called K4E6E304EC; it's a 174 ball BGA, and is around $7.5. I don't need 2 GB, but you only live once, and it's not that expensive compared to the whole board.

![bottom of ram ic](https://cdn.hackclub.com/019f7bfb-ccc6-7792-9111-293e7c1a0969/c2803256-______.jpg)

I submitted a footprint creation request to Component Search Engine; it should take 1-2 days for them to make it; I will make a custom symbol.

## Thank you again Cyao for all the help!!!!!

## _Time Spent: 4h_

# 2026.07.20: Making RAM symbol and RAM troubles

## Symbol

I realized that I really like making symbols; it's just a really relaxing process, and I can learn a lot about the IC I'm making the symbol for.

Turns out, the pin table in KiCad doesn't have a "visible" field, so I had to use a text editor to mass hide pins, like GND and VCC, so for example I can have one GND pin instead of sixty-seven-thousand.

![ram symbol](https://cdn.hackclub.com/019f84ac-c970-7b97-bbe3-0f5766acd44d/image.png)

But I realized something...

## RAM troubles

The DRAM IC I chose has a 32 bit wide data bus, but my MPU only has a 16 bit wide DRAM controller, hmmmmmmmmmmmmmmmmm

So I dived into the datasheet, now this is where it got really confusing, because the datasheet mentioned x16 multiple times, so I went to the EE Discord to ask what the helly is going on, does this IC support both x16 and x32??

![datasheet talking about x16, and an extra column (c10)](https://cdn.hackclub.com/019f84b4-e9a3-78a5-823f-d685090f87e8/image.png)

The first answer I got told me that I can't use this IC, but then another guy joined the conversation and said that I could use this IC, and they also provided some evidence hmmmmmmmmmmmmmmmmmmm

So I went on a search for an LPDDR3 chip that had a 16 bit wide data bus. But I couldn't find any, they were all 32 bit wide 😮 So my DRAM IC must have support for a 16 bit wide data bus, but I'm still not 100% sure, and still have to do more research.

Also made a stack exchange post, but that didn't get any replies :sob:

## _Time Spent: 4h_

# 2026.07.26: Microchip support saves me

## RAM

So after I did a bunch more research, I asked Microchip's live chat if they had any example of the SAMA7 being used with LPDDR3, and turns out there are examples with x32 memory WOOOOOOOOOOOOOOOOOOO

But I still had a bunch of questions about this example, like do I lose half the capacity, or do I only lose speed, but the live chat support person said that I should create a regular support ticket for these questions, cuz they didn't know. So I did that, and waited eagerly.

A few days later I got a wall of text as a response, which explained everything. I LOVE U BARATH V. FROM MICROCHIP

Turns out almost all x32 LPDDR3 devices (I learned that they call DDR ICs devices from Barath) have an x16 mode, but the datasheets don't make this clear at all, but I also got feedback on the specific DDR device I chose (<3 Microchip) and it has this feature; in x16 you get half the speed but the full capacity of the device.

But turns out that there was another factor that would have halved my capacity, which was that the device I chose was actually two DDR chips put in one package, and required two CS and CKE pins, but the SAMA7 only has one CS and CKE pin for DDR devices, so I could have only used one of the chips in the package. The solution? Use a device that doesn't have two chips inside one package, which means use one with half the capacity, so in the end I will have an 8Gb/1GB DDR device.

Luckily the footprint doesn't change at all; I only have to mark two pins as NC (CS1 and CKE1), and rename CS0 to CS and CKE0 to CKE.

With my newfound knowledge I connected the RAM to the SAMA7:

![DDR with labels](https://cdn.hackclub.com/019fa4c3-a62d-7dfa-be17-d944adf23414/image.png)
![hierarchical sheets of DDR and SAMA7](https://cdn.hackclub.com/019fa4c3-d397-7b00-b78e-523cc5d47cbe/image.png)

## Display

I looked around a bit for displays to see if there were any better options than my current choice, mainly I wanted a larger display, so I could have more room for the PCB, but all the larger MIP panels had a horrible refresh rate, like 15Hz, which was unacceptable compared to the current 70Hz one. So I didn't change anything else.

## PWR

Started looking for a power path, charger and fuel gauge IC; I may have found one from Analog Devices, but I'm still not sure about it.

## _Time Spent: 6h_

# 2026.08.06: Wireless shenanigans and making power IC symbols

## Finding a good wireless IC and datasheet shenanigans

At first I wanted to use the NXP IW611 as a bare IC, but the PCB layout looked painful, and if I want to sell Meko V3 later I have to go through an expensive certification process. So I went looking for modules, and along the way I found the U-Blox Maya-W3, which uses the Infineon CYW55513, which has Bluetooth 6 :yayayayay:

I asked Component Search Engine to make a footprint and symbol for the Maya-W3, but the first time they rejected it for the reason of "The datasheet doesn't have enough info", but it did. So I submitted again, and now they made it in under 24h, yipeee

But as always, the footprints are nice from CSE, but the symbols are crap. So I had to remake that, and I'm glad I did, because I discovered that the Maya-W3 datasheet is also terrible. It lists the max I2S sample rate as 8kHz, which is really bad, like old call quality, and I realized this just at the end of me finishing the symbol, shi. I also looked at the NXP IW611 I2S sample rate, and it also capped out at 8kHz... Then, as my last hope, I checked the datasheet of the Infineon CYW55513 (the chip that the Maya uses), and it listed its max I2S sample rate at 96kHz; this is excellent!!! So in the end I will use the Maya-W3.

Side note: Both the Maya-W3 and CYW55513 datasheets mention SMIF pins, but don't mention at all what they are used for. If you google SMIF it comes up with an Infineon page that says that it's just SPI, and if you check out CYW55513 example designs the SMIF pins are connected to an external flash and PSRAM, so idk if I should connect them, so I reached out to support, but they haven't responded.

![maya-w3 symbol](https://cdn.hackclub.com/019fd843-4a07-7c6e-9934-ca50763a6a7f/image.png)
![maya-w3 cse footprint](https://cdn.hackclub.com/019fd8cb-d08f-7f26-a10d-9289489aa3f8/image.png)

## Finding power ICs

Turns out there aren't any good ICs that all have power path, a fuel-gauge and a battery charger, so I separated the fuel gauge into a separate IC. For the battery charger I chose the BQ25640; it has USB-OTG, USB-PD, voltage monitoring support and a bunch of other cool features. And for the fuel gauge I chose the MAX17260, which is a really simple and good fuel gauge IC, nothing special, it uses a TDFN-14 package. On the other hand the BQ has a really funky TI package, so I asked Snapmagic to make that for me :skull:

I made the symbols for them cuz the premade ones were ass:
![fuel gauge and battery IC symbol](https://cdn.hackclub.com/019fd843-4d5f-702a-a33b-c356d10559ca/image.png)

There are also some shenanigans with the TI BQ IC, cuz it has D- and D+ pins, and the datasheet doesn't mention what to do when you don't want to use them, so I made a support ticket.

## _Time Spent: 7h_

# 2026.08.16: Finished Power

## Mucking around with ESD

For the USB port I just chose a standard 16 pin USB 2.0 connector, nothing fancy. But now I needed some ESD protection.

I checked out the SAMA7D6 example design, and they used an IC that had both ESD and filtering; I have never seen this before, and it seemed pretty cool, so I wanted to use a similar IC. After searching for one of these ICs that was available on LCSC, the one I chose luckily already had a built-in KiCad symbol.

Now came the VBUS and CC pin ESD protection part. While researching I found out that the CC lines can short to VBUS when plugging/unplugging a USB cable. At this time I still thought that my BMS supported USB-PD, and that VBUS can go up to 21V. So I thought that I needed an IC that protected against this, so the CC lines don't get 21V on them. So I did a bunch of research, found a part, made a symbol, downloaded a footprint, etc. Just to realize that first off my BMS could tolerate up to 26V on the CC lines, and second that my BMS didn't support PD, so VBUS would only go up to 5V. So I ditched this complicated IC and just used simple TVS diodes.

![usb schematic](https://cdn.hackclub.com/01a00bb5-bc79-7a59-8e56-d3de287ba85b/image.png)

## Implementing the power ICs

This was mostly just reading the datasheets a bunch.

### BMS

I asked in the TI dev forums regarding the D-/+ pins, and what to do with them if I don't want to use them. They replied and said that I should just leave them unconnected. The rest was pretty easy.

Also the BMS doesn't shut down the battery output until it reaches 2.4V, and by that point, the battery would probably be completely dead and unusable. So I will need to implement a software shutdown when the battery voltage reaches like 3.2V. Luckily the fuel-gauge has a battery voltage readout register, so I can use that. My MPU works down to 3V, so 3.2V should be fine.

### Fuel-Gauge

I learned a lot about fuel-gauges. One of the things I learned is how a Coulomb counter works, and how to choose the sense resistor.

### PMIC

Setting up the switching regulators was pretty easy, just had to read the recommended part values.

The more interesting part is the low-power/high-power/hibernate modes. The SAMA7D6 needs a backup source called VBAT to keep the RAM in self-refresh mode. First I thought that I needed another LDO for this input which is always on, so I again found a part, made a symbol, etc. But then again I realized that my PMIC had an unused LDO, which I could configure via I2C to always be on, except when the PMIC fully shuts down. This way, the device can hibernate while keeping the RAM in self-refresh mode.

![power schematic](https://cdn.hackclub.com/01a00bc3-9d2e-7ea7-bc93-700ef7ba0172/image.png)

## _Time Spent: 6h_

# 2026.08.20: DDR Troubles and Adding Supporting Circuitry

I discovered maybe a problem with my LPDDR RAM and I also continued to add supporting circuitry to the MPU

## DDR

Turns out that the answer that I got from my Microchip support inquiry - regarding using LPDDR3 with half of its data bus - might have been written by AI (thanks Electronics Stack Exchange for pointing this out).

Microchip said that a register of the LPDDR3 memory device which tells you if the device supports x16 is writable, but it's not, it's read only.

So this might mean that the SAMA7 example that uses LPDDR3 might be just plain wrong.

I reached out to Micron if the memory device used in the SAMA example truly supports x16 operation, but they haven't responded yet.

![MR8 read only](https://cdn.hackclub.com/01a020bd-e708-79ed-b440-a28730f384a7/image.png)
_Notice the R, which means read only_

![MR8 function](https://cdn.hackclub.com/01a020bd-ead2-797b-a6b7-3c75506ef276/image.png)

## Supporting Circuitry

Chose and added crystals and caps for them for the SAMA7:

![crystals and calculations](https://cdn.hackclub.com/01a020d6-7153-7398-ba3d-c26c8fef7134/image.png)

Added DDR VREF voltage divider:
![ddr voltage divider](https://cdn.hackclub.com/01a020d9-60d9-721a-b0ed-8a5b2b74c472/image.png)

Added reference resistors:
![reference resistors](https://cdn.hackclub.com/01a020d9-640d-7cd2-bb38-591860b2787b/image.png)

Wired up the PMIC pwr signals, and added a JTAG connector:
![pwr ctrl and JTAGSEL](https://cdn.hackclub.com/01a020d9-6724-715f-bfcb-f176cc0355fa/image.png)

![JTAG connector](https://cdn.hackclub.com/01a020d9-6a75-786e-b922-19d3ebe3654d/image.png)

## _Time Spent: 6h_

# 2026.08.26: Audio, SD cards, RF, Touchpad

_I have done a lot of stuff_

## Audio

Finally figured out how to implement what I wanted to do: a 3.5mm single ended and 2.5mm balanced output

My audio chip supports both balanced and single ended outputs which is awesome!

I'm actually not using true single ended, because I would need to use a DC blocking capacitor if I did so, which filters bass frequencies. So I'm actually using the pseudo-differential output of my CODEC.

### Common Mode Voltage

You may ask: WTF is a pseudo-differential output and DC blocking cap??
The audio output of the CODEC always has a common-mode voltage, which means that the audio signal is not centered around 0 volts; instead, an arbitrary DC voltage. Imagine it like the audio signal is riding on a DC voltage.

For example, this is a sinusoidal audio voltage with a 2V common mode:
![sinusoidal audio voltage with a 2V common mode](https://cdn.hackclub.com/01a03a60-cbaa-7617-a8a6-393c9cb219d5/image.png)

But there is an issue; if we connect the negative terminal of our headphones to GND, all that common mode voltage will flow through our headphones, which may both damage our CODEC and headphones.

![negative to gnd in jack](https://cdn.hackclub.com/01a03a64-6bf3-7fb4-a346-583308bbe84e/image.png)

There are two solutions:

1. Putting a series capacitor on our audio lines

This will let the AC sinusoidal audio through, and block the DC common mode

![DC blocking caps](https://cdn.hackclub.com/01a03a67-ad08-7ba2-a916-7e27e67d9b1c/image.png)

The audio will now be centered around 0V:

![audio without common mode](https://cdn.hackclub.com/01a03a69-ed20-7ef5-9d13-00448061efb3/image.png)

But as mentioned earlier, the capacitors also filter out the lower frequencies of our audio, aka our bass, which we don't want

2. Replace the GND reference with our common mode voltage
   _AKA pseudo-differential_

![common mode as reference](https://cdn.hackclub.com/01a03a6c-d7d1-7a61-8509-cb10c110ed6c/image.png)

Now our headphones think that our 2V common mode is GND, which gives us the same result: the headphones now see the audio signal centered around 0V, but our bass is not filtered out

![audio with common mode as reference](https://cdn.hackclub.com/01a03a69-ed20-7ef5-9d13-00448061efb3/image.png)

**_Fun Fact:_**
When I designed Meko V2, I didn't know all this, and tied the negative of the jack to GND, and didn't use DC blocking caps, so I almost certainly damaged my CODEC a bit. I had to add these caps in afterwards, it was not pretty.

![meko v2 bodge](https://blueprint.hackclub.com/user-attachments/blobs/proxy/eyJfcmFpbHMiOnsiZGF0YSI6MTAyNzY1LCJwdXIiOiJibG9iX2lkIn19--5070daed04b49cfc4c4b04822cdd74ecbc39b64e/1000014726.jpg)

### Differential audio

Differential output is basically the same as pseudo-differential, but each audio channel (left, right) gets its own negative terminal that has the inverted signal of the positive terminal; both terminals ride on a common mode voltage

![differential output](https://cdn.hackclub.com/01a03a74-ef9a-772e-b378-09fb4c2c2441/image.png)

### Switching between pseudo and regular differential output at runtime

At first I thought I needed an analog switch, since I wanted to mimic the datasheet for the pseudo-diff mode, where _OUT1M_ and _OUT2M_ are connected. But in true differential mode these two need to be disconnected:

![datasheet pseudo-diff](https://cdn.hackclub.com/01a03a7e-e7d8-7219-90fe-3942e4b3cc48/image.png)

![circuit with analog switch](https://cdn.hackclub.com/01a03a85-7eb1-76f2-966f-d0d66e6079f2/image.png)

_I researched a bunch and made a symbol_

But turns out if I don't use _OUT2M_ as a sense, the output will be only slightly worse, which I can accept for one less component.

![circuit without analog switch](https://cdn.hackclub.com/01a03a86-c47f-7559-9378-e9d54d3f6918/image.png)

You may notice some _100K_ resistors on the `TN` pins of the jacks; these are used to detect if a jack is plugged.

When a jack is not plugged in, `TN` is shorted to the tip(`T`), and when a jack is inserted `TN` is disconnected from `T`. The audio lines always sit around the common mode voltage (in my case 1.65V), so when a jack is not plugged in, the `DET_x` lines sit at around 1.65V, but when a jack is plugged in, the `DET_x` lines get pulled down to GND by the resistor.

This took me a whole lot of time to figure out.

### Microphone

#### Mic Bias

The microphones that are in the average earphones need a bias voltage; this gives the power to the amp of the microphone.

![mic bias](https://cdn.hackclub.com/01a03a92-ae77-7f05-9e78-ef95da1af912/image.png)

Since the negative pin of our 3.5mm jack is tied to the common mode voltage, our mic bias needs to be a bit higher to compensate. So instead of the standard 2.2k resistor I only use a 1k one:

#### Play/Pause/Skip

Earbuds sometimes have buttons for play/pause/etc. These signals go through the mic line. Each button when pressed connects the mic to gnd with a series resistor in between, forming a voltage divider with the bias resistor.

![resistors of buttons](https://cdn.hackclub.com/01a03aa6-9317-7d57-bd33-8d5c54a80961/image.png)

The resulting voltage can be measured by the ADC of the CODEC.

_Image from [here](https://source.android.com/docs/core/interaction/accessories/headset/plug-headset-spec)_

### TI support

I love how TI and other large IC manufacturers still give free support and design reviews; they helped a ton!!

### Linux driver

TI provides a kinda ok driver for this CODEC, which doesn't expose a lot of the cool features of this CODEC, but it is what it is.

## SD Cards

This was pretty easy, I looked at what SD card footprint Cyao's CKL library had, and used those

I saw in the SAMA7 example design that they had a load switch for the SD card, which led me down the rabbit hole of how SD card slots need to be handled. I stumbled across an [Altium article](https://resources.altium.com/p/how-to-design-microsd-power-circuits-without-destabilizing-on-board-voltage-supply) which had the advice that for prototype boards, you should place a 47uF capacitor on the power rail of the SD card, so it limits the inrush current the regulator has to handle when a new SD card is plugged into a live system

![sd cards](https://cdn.hackclub.com/01a03aef-d6dc-7234-9685-9c3b873f6610/image.png)

I also did a lil side quest on why SDMMC needs pull-ups; it's so the data lines never go in an unexpected state.

## RF

![finished RF schematic](https://cdn.hackclub.com/01a03d19-7851-7dfd-9bd3-44327ac16df1/image.png)

### SMIF lines solved

After U-BLOX support didn't respond, I reached out to Infineon's support. They responded really quickly! My assumption was correct, in that I don't need to connect the SMIF pins when I use this chipset with Linux.

### GPIOs

I didn't use any, so this was pretty easy. I just looked over the datasheet to see if any of them had any special function; they didn't.

### Linux Driver

Infineon provides two drivers, one for Wi-Fi and one for Bluetooth. I was kinda confused at first, because they didn't mention these drivers anywhere on the product/docs page. Infineon support came in clutch again, and pointed me in the correct direction.

## Trackpads

### Steam Deck trackpad

Since I wanted to make a trackpad that is similar to the Steam Deck's, I looked at a [teardown](https://www.youtube.com/watch?v=5PB3VBK8VJk&t=432s) from JerryRigEverything, and I saw that each trackpad had 3 PCBs:

![first pcb](https://cdn.hackclub.com/01a03d2b-68d3-71e9-9f1f-b70675d267f7/image_.png)
![second PCB](https://cdn.hackclub.com/01a03d2b-6c6d-794e-97b3-e7318c89aabb/_image.png)
![third PCB](https://cdn.hackclub.com/01a03d2b-6fe7-7e4e-9466-f81d0f674053/sdimage.png)

I did a bit more research and couldn't find anything. So I asked on the KiCad Discord, and a really cool person responded:

![trackpad response](https://cdn.hackclub.com/01a03d37-3580-765d-9822-7d159083d83a/image.png)

Turns out that the flex PCB and the serpentine trace are used to detect the deflection of the trackpad. I thought trackpads could infer this, but turns out some can, and some can't.

### Choosing a trackpad IC

I saw a [video](https://www.youtube.com/watch?v=ycMgIToLav8) a while back of someone making a custom Steam Controller where they had to make custom trackpad PCBs, because Valve doesn't sell trackpad replacements for the Steam Deck. I saw that they used an obscure IC called the Azoteq IQS7211, which had bad availability.

So I continued my research; turns out the ICs used in laptops and the Steam Deck are not available to hobbyists. So I went back to Azoteq, who sold ICs to regular people.

Then I found the IQS9151. This is a really cool IC that has gesture support, and a bunch of other cool features.

### Generating trackpad PCB

![trackpad PCB](https://cdn.hackclub.com/01a03d45-4245-7bef-9f67-d3cd89fb8b25/image.png)

Capacitive trackpads work by having a bunch of rows and columns of these squares and sensing the change in capacitance. When a finger gets close, the capacitance decreases.

![trackpad illustration](https://cdn.hackclub.com/01a03d4b-7ac1-77ec-9e03-43a6cf3d6894/image.png)

But drawing all these squares by hand in KiCad would be painful. So I went on a search for generators. And I found a [pretty cool one](https://github.com/timonsku/Touchpad-Generator). This generator was made for the MNT Reform Next OSHW laptop, and turns out they also used the IQS9150 (which is the same as IQS9151 but with more pins).

### Linux Driver

I searched around a bit, but I couldn't find a Linux driver for the IQS9151. But I could find a YouTube [video](https://www.youtube.com/watch?v=0G95vEnHm-k&t=32s) of someone demoing the driver.

![video screen shot](https://cdn.hackclub.com/01a03d51-599e-7a07-8850-67fb7f7a170c/image.png)

But I got a lead; the guy is probably named Jeff LaBundy. So I searched for `Jeff LaBundy embedded` and a [personal site](https://labundy.com/) came up with the same style

![labundy site](https://cdn.hackclub.com/01a03d54-6b07-7a94-91e2-6631be638a8b/image.png)

And luckily the site had an email.

I then proceeded to cold email this guy asking if he would send me his driver 💀

After I sent my email, I looked if the IQS7211 had a Linux driver. It had. But when I opened the source code, guess who was the maintainer, Jeff LaBundy.

## _Time Spent: 14h_

# 2026.09.01: Switched out RAM, working on touchpad, looking over schematic

## Ram

Microchip responded to my support case, and said that they were wrong before about LPDDR3 and using x32 memory with the SAMA7. Turns out I would only get half the capacity if I did use LPDDR3. So I switched to DDR3L. This wasn't that hard, since KiCad already had the most popular DDR3L in its built-in library. And the rest was just matching labels and looking at example designs. I also had to swap from the MCP16502AD PMIC to MCP16502AB, because the AD variant is for LPDDR and the AB is for regular DDR3/L.

![DDR3L](https://cdn.hackclub.com/01a05c3a-20f9-750c-bff2-9c77f0fbe30f/image.png)

## Touchpad

### IQS9151 driver

Jeff LaBundy responded to my email with a [link](https://github.com/jlabundy/linux/tree/iqs9150-release) to the driver!!!! It was sitting in an obscure GitHub repo.

### Generated PCB

![generated PCB](https://cdn.hackclub.com/01a05c3f-b2fe-731c-8e64-1dbbe118204a/image.png)

As mentioned in the previous journal entry, I used a generator. It was pretty easy, I had to install OpenSCAD and the rest was just modifying variables to fit my needs.

### Trying to fit a QFN52 on the back

After I made the symbol for the IQS9151, I realized that it had a QFN52 6mm x 6mm package, which I needed to fit on the back of the touchpad. The issue is that the touchpad has a bunch of vias, which make it impossible to use a normal QFN52 footprint, so I modified it:

![modified footprint](https://cdn.hackclub.com/01a05c43-b6de-7811-a901-05ec724e71da/image.png)

I then asked for feedback on my design in the KiCad Discord and on Reddit, and everybody said that this will not work 😭
A lot of people recommended a bunch of complicated solutions, but Ebastler recommended to put the IC on a second PCB with castellated pads along the edge, then hand solder that small PCB onto the large one. This seems like the best solution! But it's still more complicated than I want. So I might just switch to the IQS7211E, which has a way smaller footprint, but also has fewer channels, so the resolution will be worse.

If I do switch out the trackpad IC, I will have to regenerate the PCB and maybe make a new symbol

## Looking over the main schematic

I found a few places where I needed to add pull-up/pull-down resistors, it was an easy fix.

I also added a bunch of decoupling caps to the ICs that needed it

![bunch of caps](https://cdn.hackclub.com/01a05c4f-1aa7-7087-a46f-6e1261914bbc/image.png)

I also found a footprint for my power path IC:

![power path IC footprint](https://cdn.hackclub.com/01a05c50-afe9-7066-ad70-42cc26e82f4a/image.png)

I also assigned a bunch of footprints and chose a bunch of parts from LCSC:

![footprints](https://cdn.hackclub.com/01a05c52-0bec-727c-a5c8-0322320f0d3d/image.png)

## _Time Spent: 10h_

# 2026.09.11: Got reviewed by Microchip, added a bunch of test points

I got a response from a Microchip review, and I got some small mistakes so I fixed those.

![](https://cdn.hackclub.com/01a091f0-100c-7f5c-b5d2-fb1509c7e287/image.png)
![](https://cdn.hackclub.com/01a091f0-12e9-760a-9bdd-eea94ba88d22/image.png)

I also reorganized some stuff in the schematic and looked over everything again and added a bunch of test points.

![](https://cdn.hackclub.com/01a091f7-3319-7a08-99ca-a0ce0d302d4f/image.png)

I learned a bit about how test points affect signal integrity, and how it almost all depends on the wavelength of your signal, and I also learned that KiCad has a pretty good wavelength calculator built in, pretty cool!

## _Time Spent: 3h_

# 2026.09.15: Contributing to KiCad

I got my [PR](https://gitlab.com/kicad/libraries/kicad-library-tools/-/merge_requests/2132) for the SAMA7 footprint accepted into the KiCad footprint library :yayay:

![merged PR](https://cdn.hackclub.com/01a0a1da-e25d-7676-9220-b30df2a28d18/image.png)

With this new found motivation I wanted to also PR in the SAMA7 symbol I made!

But I had to change my symbol to follow the [_**KiCad Library Conventions**_](https://klc.kicad.org/) to get my symbol merged.

They have an automated CI/CD that checks your symbol before you PR, and gives you all the rules you violated. It took a few back and forths to get most of the violations resolved! In the end I ended up with one error and 2 warnings, which are fine.

While researching I found out that KiCad supports stacked pins, which are pretty cool:

![stacked pins](https://cdn.hackclub.com/01a0a1e2-697b-7727-a8dd-17d30e705145/image.png)

Here is my [PR](https://gitlab.com/kicad/libraries/kicad-symbols/-/merge_requests/5616) and finished symbol:
![units pt 1](https://cdn.hackclub.com/01a0a1e3-71a2-7243-a047-4440955a39e3/image.png)

![units pt 2](https://cdn.hackclub.com/01a0a1e3-5813-7b44-b26d-45848bd1ef79/image.png)

## _Time Spent: 2h_

# 2026.09.16: Mucking around with _iced_

I kinda burnt out from hardware, so I wanted to learn something new. Since I want the music player program on the device to be written in Rust, I looked around for graphics libraries.

## Choosing a graphics lib

Web-based frameworks like Tauri were out of the question, since this is a really low-powered device, and only has half a gig of RAM.

I narrowed down the choice to three options:

- _slint_: I used this for Hackxpansion. It has a custom language for UI definition, which I have mixed feelings about

- _egui_: This is an immediate mode graphics lib, so it doesn't have a structured markup, instead it's very dynamic, which I don't really like

- _iced_: This is a graphics lib inspired by Elm, it has you define your application state in a single struct, and all the interactions that could be done in the UI also in a struct/enum. I really like this, because it allows you to leverage Rust's strong type system to prevent states that are not possible.

In the end the choice was quite obvious for me. I went with _**iced**_

## Getting started with iced

The docs for iced are kinda bad. There is a book which teaches you the basic architecture of the lib that walks you through a basic counter app. Besides that, there aren't any detailed "guided" docs.

It took a bit to wrap my head around how iced expects me to write apps, but at one point it just clicked.

Here is the basic clicker app, with the addition of the going up each second:

![counter app](https://cdn.hackclub.com/01a0a95d-0d6b-76f8-ac64-5c85332306dc/image.png)

## _Time Spent: 2h_

# 2026.09.20: Layout, Stackup, Impedance, Length Matching, BGA stuff, 3D models

_I did all kinds of stuff, small chores and bigger tasks, so this will be kinda all unrelated._

## Layout

I wanted to finalize the placement of all components that the user will interact with. First I updated my 3D mockup with accurate dimensions, then I added the buttons and audio jacks. Also, I actually made the trackpad the same size as the screen. I'll use this mockup as a reference for the final layout.

![3D mockup](https://cdn.hackclub.com/01a0bfee-5a32-7755-9a79-cf018d7e8d72/image.png)

_The thickness of the mockup is not final_

Then following the mockup I placed the components on the PCB.

![PCB layout](https://cdn.hackclub.com/01a0bfee-5747-707f-babd-fab9a6891dfb/image.png)

I placed the microSD card slots on the bottom of the PCB, so I have plenty of space for the DDR routing. I also added these handy lil indicator drawings to the microSD footprints that show the positions of the SD card.

I still have to add the cutout for the trackpad FFC cable.

## Stackup and Impedance

As a first step, I started looking at PCBWay's stackups, at first I chose a 1.6mm 6L stackup, but then realized after some calculations that my 50Ω traces would be 0.2mm, which is too large. So I needed to choose a stackup that had a thinner dielectric between the outer copper layers. After looking at PCBWay's stackup offerings, I realized that I had to choose a 0.8mm board to get a thinner dielectric. This thickness is fine, all M.2 PCBs are 0.8mm.

![PCB stackup](https://cdn.hackclub.com/01a0bffe-b9ca-7fb1-9f13-8e1fdd6d8d7a/image.png)

After all this, I entered in the stackup details into KiCad:

![KiCad stackup](https://cdn.hackclub.com/01a0bfee-4ba4-729b-8c96-66d7ee6f82ea/image.png)

This was needed so I can use KiCad's tuning profiles, which make it really easy to create impedance-controlled traces

![tuning profile](https://cdn.hackclub.com/01a0c000-315f-7d6d-af66-9d32d0d7d6b0/image.png)

## Creating Net Classes

To actually use these tuning profiles, you have to create net classes. For the first time in my KiCad career I used `Directive Labels` and `Rule Areas` in the schematic editor:

![Directive Labels and Rule Areas](https://cdn.hackclub.com/01a0bfee-518d-7842-8413-0d7b3104beda/image.png)
![Directive Labels](https://cdn.hackclub.com/01a0bfee-5450-70ce-bf08-3719938dbd7b/image.png)

These allow you to assign net classes visually instead of with Regex, which is a lot nicer!

Also, you can use net classes to create custom rules related to length matching, which makes it a lot easier to length match DDR and SDMMC:

![custom rules](https://cdn.hackclub.com/01a0c006-6994-7979-993f-dd7959460870/image.png)

## BGA Soldermask Retraction & Pad Size

After looking at Micron's datasheet and other PCBs that use DDR3L and BGAs, I realized that I can shrink down the pads of the DDR3L footprint to 0.42mm from 0.52mm. While I was doing this research I also found out that I need to set a soldermask retraction for these BGAs, the most common value I found was 0.05mm.

![BGA pads with measurement](https://cdn.hackclub.com/01a0c00a-0bc1-799c-9380-6d0ad3ed64e4/image.png)

## Added a Bunch of 3D models

I was missing a lot of the 3D models of my components so I added those. Easyeda2kicad was very useful!!

As part of this process I also vendored in a bunch of footprints from libraries, so I can edit the library footprint, instead of only editing the footprint on the PCB

![3D PCB with components](https://cdn.hackclub.com/01a0bfee-4eb6-7ec5-8446-15327ee19a69/image.png)

## _Time Spent: 8h_

# 2026.09.25: Touchpad, other small stuff

Since I'm waiting for Microchip to give me the pad-to-die lengths/timings for the SAMA7, so I can start routing the DDR, I'm doing other stuff.

## Touchpad

First I added a sketch in my 3D mockup that represented the touchpad PCB, so I can position the FFC connectors correctly.

![sketch of touchpad pcb](https://cdn.hackclub.com/01a0d91c-7b31-722d-a50b-695060b4d9c8/rdbzml6.png)

After that, I chose the connector for the FFC that will connect the trackpad and main PCB. I went with the same series of connectors that my display used, because they seem high quality and are made by Molex. I just use a 5 pin variant instead of the 10 pin one.

Since both the main pcb and touchpad pcb need this symbol and footprint, I moved all the libraries to a shared folder called `pcb_lib`.

I already had the touchpad pattern generated, so I _only_ needed to lay out the components and do the routing.

I laid out and started routing 3 times, and then realized that I was dumb and that it won't work. The 4th attempt finally turned out pretty good.

![touchpad schematic](https://cdn.hackclub.com/01a0d904-3559-7b4d-814a-ef721a747cd0/fov85mk.png)
![touchpad front 3d](https://cdn.hackclub.com/01a0d904-39f0-7e42-b50b-cc70ea47350d/zlz9jcd.png)
![touchpad back 3d](https://cdn.hackclub.com/01a0d904-3db2-7920-b741-2802fc128d1e/91r34y3.png)

The thing you gotta pay attention to when routing touchpads is to keep a good distance between the RX, TX and data lines.

I also needed to add a cutout for the FFC on the main PCB, I made it a lil bit wider, so the LRA (linear actuator, that makes the vibrations) cables also fit through.

![main board touchpad cutout](https://cdn.hackclub.com/01a0d919-a929-7454-9292-f296e9959c09/dqmxjqx.png)

I sent over the design to Azoteq for review, the company who makes my touchpad IC.

## Other stuff

I separated out the components so they are grouped based on what components they need to connect to/need to support and where they will go in the final PCB.

![grouped components](https://cdn.hackclub.com/01a0d910-3273-756a-a446-615ba7224392/5czzptl.png)

Also placed the ESD for the USB, and routed it.

![usb](https://cdn.hackclub.com/01a0d910-3742-7f29-a56e-7e467f89ed9b/lmmvjzc.png)

## _Time Spent: 4h_

# 2026.10.05: Routing DDR

`This will be long 😭`

## Net classes

I started by setting up some net classes and coloring them to make differentiating the different signal groups easier.

I used some schematic rule areas and directive labels to assign net classes visually
![rule areas and labels](https://cdn.hackclub.com/01a10b10-9ff4-742b-bbc3-e4a86a50ee0c/paste-1791187000737.png)

Net classes will also be important for length matching later on.

## Laying out caps and vias

Then I laid out the caps and other passives and connecting them, this was not that hard, I looked at how other people did it.

![ddr passives](https://cdn.hackclub.com/01a10b0a-c664-7594-a29a-27e0c262050f/paste-1791186617222.png)
![SAMA passives](https://cdn.hackclub.com/01a10b0b-a913-78dc-9eb6-bf77db0d141a/paste-1791186675644.png)

I then realized that I messed up, and had to redo the whole process, because I couldn't fan out the BGA with the way I did things.

So I caved and used Microchip's [reference design](https://365.altium.com/files/45053653-DFF7-4FBD-83A4-7ECC4038BD7C) to redo the whole thing. This time I also used this reference design to place the vias for certain signals.

![new ddr passive layout](https://cdn.hackclub.com/01a10b1e-c4e2-799d-8be5-65392f0a81bc/paste-1791187927583.png)
![new SAMA passive layout](https://cdn.hackclub.com/01a10b1e-ecd0-70d5-9e8c-f0fc3d376edc/paste-1791187937780.png)

## Rule areas

I had a faint memory that you could set up custom rules for a specific part of your PCB. Turns out this memory was true! You have to create a rule area, I already knew that this existed, but I didn't know that you could create custom rules for these areas.

You can make the min clearance smaller for traces in specific net classes in specific areas. This way, I'm forced to follow the 3h rule outside of the BGA areas, and also have more freedom to fan out the BGAs with tighter clearance.

![ddr rule area](https://cdn.hackclub.com/01a10b0c-76e3-7700-937e-cb2d98e90b4f/paste-1791186728364.png)

![ddr custom rules](https://cdn.hackclub.com/01a10b17-4ae9-7455-a841-dddfe74f4c58/paste-1791187437832.png)

I messed around with this a bunch, because KiCad doesn't support this very well yet.

## Setting up length matching rules

In KiCad you can set up custom rules (just like with the areas) to make length matching easier. You can make KiCad force you to make all lines in a net class be the same length.

I found [this](https://youtu.be/OrjdTfpJeWw?si=aGC9p7ROnE3OcyjS&t=240) tutorial that had a really good explanation of the whole length matching process in KiCad.

Here is one of the custom rules for the LANE1 signal group:
![length matching rule](https://cdn.hackclub.com/01a10b16-fce3-7675-819a-6f885e1b2ddb/paste-1791187417890.png)

I had done a ton of research on how closely you have to match each group, in the end I found [this](https://docs.altera.com/r/docs/683385/current/length-matching-rules) document that had a pretty good explanation.

## Routing and Length Matching

`This was the most painful part, and I'm still not done`

I started by looking at the reference design to see how it was done there. I copied the fanout because I didn't want to reinvent the wheel, and it would have taken ages to figure out a somewhat good fanout on my own - maybe for a future project.

I then routed both lane0 and lane1, and started length matching lane0, and realized that my layout was terrible, and I couldn't length match the traces because I didn't have enough space.

![bad layout + traces](https://cdn.hackclub.com/01a10b26-e7fe-7e27-b162-96ac9e332248/paste-1791188460826.png)

I then rotated everything 45 degrees, and spaced the SAMA7 and the RAM further apart.

![new layout](https://cdn.hackclub.com/01a10b28-ddb7-71a9-9a7d-bf7131fd52ee/paste-1791188589278.png)

After this, I routed lane0

![lane0 routed](https://cdn.hackclub.com/01a10b29-30db-7233-9727-5431fed3d0e4/paste-1791188611038.png)

And this time I could actually length match it

![lane0 length matched](https://cdn.hackclub.com/01a10b29-d0d5-7783-94b3-26acc3a90395/paste-1791188651982.png)

I then did the same with lane1

![lane1 routed](https://cdn.hackclub.com/01a10b2a-4b76-7618-a125-89090996c3de/paste-1791188683393.png)

![lane1 matched](https://cdn.hackclub.com/01a10b2a-a3dd-7427-aacf-8840c7eca2b8/paste-1791188706032.png)

Finished with lane1 and lane0, I continued onto the address and command/control lines, which I'm still working on

![started on addr and cmd/ctl](https://cdn.hackclub.com/01a10b2b-5c5c-73f3-b0fb-610dd23fa2c6/paste-1791188753228.png)

This whole process took an immense amount of time, and is mostly monotonous/grueling work, but it's a nice challenge.

## Getting my SAMA symbol merged into KiCad

This was like a side storyline, I did this while doing all the other stuff mentioned in this and the previous journals.

I had gone back and forth with a librarian a few times with changes that they requested, but these were mostly simple fixes.

Here is the [MR](https://gitlab.com/kicad/libraries/kicad-symbols/-/merge_requests/5616)

## _Time Spent: 15h_

# 2026.10.11: Finished DDR routing, Regulator layout and Power Plane

_I haven't journaled in a long time, so this will be kinda long_

## DDR Routing Finished

This was mostly the same repetitive process, trial and error. But I pushed through! But never again in the near future (╥ ω ╥)

I connected all the pads first:

![routed addr/ctl traces](https://cdn.hackclub.com/01a12bda-f9d2-7c46-9f19-14666bc6f375/paste-1791737131737.png)

And then I length tuned them:

![tuned traces](https://cdn.hackclub.com/01a12bde-fa83-71c2-bf66-40cf10c6308b/paste-1791737395106.png)

And then moved inside the PCB:

![inside edge.cuts](https://cdn.hackclub.com/01a12be1-9eb7-7e58-8ab2-a6fe905ffee5/paste-1791737568578.png)

## Regulator layout

I haven't done switching regulator layout in a while, so I did some research, and along the way got a lot of help from the KiCad Discord. I also found this pretty good [video](https://youtu.be/AmfLhT5SntE?si=eNHKXGZVunnbMAcD) from Phil's Lab.

At first I wanted my power train right after the USB port, but then realized that I wouldn't have enough space for the PMIC.

![BMS next to USB](https://cdn.hackclub.com/01a12be7-cd74-71da-bc5b-54eb73a921db/paste-1791737973570.png)

Realizing this, I did the layout outside the PCB edge cut, so I could later find space for each component block. 

Here is the beginning of the PMIC layout.

![PMIC started](https://cdn.hackclub.com/01a12be6-f216-7d11-bd00-8843942f1eb3/paste-1791737917472.png)

Here is the BMS moved outside of the PCB edge cut.

![BMS outside](https://cdn.hackclub.com/01a12bec-4f6a-77de-beea-65e43a46c8c2/paste-1791738268858.png)

After looking at the recommended layout and getting feedback from the KiCad Discord, I finished the PMIC layout:

![PMIC finished](https://cdn.hackclub.com/01a12bec-9b5f-7062-9aaa-36b0c7d49169/paste-1791738288650.png)

After some fiddling around, I found the top left corner of the PCB is the best spot to put the battery connector, so I also laid out the fuel gauge and moved the BMS next to all this.

![Fuel gauge and BMS](https://cdn.hackclub.com/01a12bec-f95d-7f71-93e4-2f7defd519b5/paste-1791738312489.png)

Thanks to the KiCad Discord, I learned what a Kelvin connection is; it's a separate trace to the battery connector, different from the main power trace, that lets the BMS sense the actual voltage of the battery.

After debating where I should place my PMIC block, next to the audio circuit, or further away, the answer became obvious ಥ﹏ಥ Here is the first layout of the full power train.

![finished pwr train](https://cdn.hackclub.com/01a12bed-509a-7cf3-8c16-dfeab2164115/paste-1791738335179.png)

## Power plane and caps

I tried to pour/route/make (idk what verb I should use here) the power plane, but I realized I should first lay out and route the caps for my MPU, so I know the placement of the vias, so I stopped with the power plane.

![bad pwr plane](https://cdn.hackclub.com/01a12bed-90f1-7cc4-a5ee-0a9333a538db/paste-1791738351435.png)

Placing caps is a monotonous process, but I could almost feel the light at the end of the tunnel for these grueling tasks, so I pushed through and started placing the caps.

![started placing caps](https://cdn.hackclub.com/01a12bed-f58d-7e92-8e6d-94c06721a16d/paste-1791738377323.png)

While doing the layout I noticed that all my tuning sections for the DDR have gone away, I had the traces, but the tuning meanders were _baked_ and couldn't be edited. While redoing some of the tuning, I realized that I didn't tune one of the traces correctly, and I just had enough space to add some more delay and bring it up to snuff.

After a while, I finished placing the caps

![finished placing caps](https://cdn.hackclub.com/01a12bee-2bf6-7665-b77c-84599234c7d4/paste-1791738391229.png)

Now that I know where the power pours were actually needed on the power plane, I started laying out the pours, now with good looking 45 degree angles (thanks tty and simon in #electronics for pointing out that I should make the pours 45 degrees).

After a **bunch** of trial and error I ended up with this, I think it should be all right.

![finished pwr plane](https://cdn.hackclub.com/01a12bee-6b02-7a85-bf70-e60b604eb9dc/paste-1791738407324.png)

## What's left?

I still need to
- lay out and wire up the audio circuit
- wire up both of the SD cards
- wire up the wireless module
- place a **ton** of test points
- make a cutout for the display cable
- place a bunch of passives


## _Time Spent: 12.5h_

# 2026.10.18: Finished initial PCB done !!!

Since power was done, I moved on to the next most important subsystem, the boot SD card! This was pretty easy to route, I needed to switch to the other layer to avoid the USB line, so I placed some GND return VIAs for good measure. I also routed the SDMMC for the Wi-Fi.

![RF and Boot SDMMC routed](https://cdn.hackclub.com/01a14fa9-86fd-75d4-bc07-a73143f24b63/Screenshot_20261018_182407.png)

After this, logically I moved onto the external SD card, this was even easier to route, since I didn't have to switch layers.

![ext sdmmc](https://cdn.hackclub.com/01a14fad-25d9-7a83-83a7-91f44c6497ec/paste-1792338109695.png)

I then realized that it would be a good idea to add net classes to other buses, like SDMMC, so I can length match them later, so I did that.

![more net classes](https://cdn.hackclub.com/01a14fac-d3bf-7551-91fd-e78eb9038f02/paste-1792338088727.png)

I then started to route the UART for Bluetooth, and some other low speed lines for the wireless module.

![uart 'n stuff](https://cdn.hackclub.com/01a14fac-a78d-740b-ae0e-732ec4d237f5/paste-1792338077374.png)

I also started to route the lines from the power subsystem.

![some routing](https://cdn.hackclub.com/01a14fa9-f96d-7f21-98ba-c17e925043d2/paste-1792337901757.png)

While on a walk home, I realized that I should probably add a cutout for the display flex cable, so I added that, but I'll have to redo this later, because the initial width of the FFC is thicker than the rest.

![initial disp edge cut](https://cdn.hackclub.com/01a14faa-276e-73e3-9535-12654255134b/paste-1792337913194.png)

I started to fan out the MPU, along the way I reassigned some pins, so the fanout is easier

![started fanout](https://cdn.hackclub.com/01a14faa-6788-71c7-87b4-0d07248ebcde/paste-1792337929246.png)

One of the things I had to pay close attention to was to not break up the power plane too much with the VIAs, otherwise the power plane would get split up

![vias and pwr plane](https://cdn.hackclub.com/01a14faf-af4d-7833-bf26-e545945cd518/paste-1792338275909.png)

At first I routed every trace as close as I could without getting too much cross talk, later I'll add more spacing

![more routing](https://cdn.hackclub.com/01a14faa-98e6-7e49-9ec4-8d0d68edf2cd/paste-1792337942520.png)

![more more routing](https://cdn.hackclub.com/01a14faa-d0ab-7ec7-abb3-cdc869924a3b/paste-1792337956765.png)

This is the point where I almost routed everything

![more more more routing](https://cdn.hackclub.com/01a14fab-6b1e-784d-a918-85f9f5d7b86c/paste-1792337996205.png)

I placed a ton of the test points and spaced out the traces, most of them have a 2.5h spacing, where the space allowed it. I had choke points next to the MPU, DDR, and PMIC, so I couldn't have a wide spacing there.

![more more more more routing](https://cdn.hackclub.com/01a14fab-8579-7bf9-bcd4-fc4024eeea01/paste-1792338003037.png)

I placed more test points and passives:

![more more more more more routing](https://cdn.hackclub.com/01a14fab-b082-7ba2-bb27-f8c66e336190/paste-1792338013998.png)

![more more more more more more routing](https://cdn.hackclub.com/01a14fab-cb2d-7b44-856d-f4f22dea8924/paste-1792338020857.png)

![more more more more more more routing](https://cdn.hackclub.com/01a14fab-ef95-722f-a578-bfa0b0dc6072/paste-1792338030153.png)

And finally I fixed the too small display edge cut

![new disp edgecut](https://cdn.hackclub.com/01a14fad-e4b8-7f06-8da3-ffc32fa2b527/paste-1792338158652.png)

## _Time Spent: 17h_

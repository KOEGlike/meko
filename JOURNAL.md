# 2026.07.12: Thinking of what I need to change

*This will be a long journal, because I did a lot of research beforehand*

![meko v2](images/PXL_20260314_073009498~2.jpg)

For V2, I went with an MCU(microcontroller unit) which are low power processors, and can't run normal OSs. This - I found out while developing the firmware - was a really limiting factor, mainly because the embedded RTOS that I was forced to use with this specific MCU(nRF5380), Zephyr. 

## Zephyr rant

![zephyr logo](https://cdn.hackclub.com/019f6765-8668-7584-b6df-d85233e2b156/image.png)

The thing to know about Zephyr is that it has literally no docs for any of the built-in drivers, so you have to look at examples(if they even exist) to figure out how the hell the driver works. In theory, Zephyr would be awesome; it is similarly structured to how Linux works, has a bunch of built-in drivers, has standard APIs for similar peripherals, and a bunch of cool stuff, but in reality the lack of docs, the complicated build system, and the unclear runtime errors just make it impossible to actually use.

Thank you for listening to my rant.

## The solution: Linux

![linux logo](https://cdn.hackclub.com/019f6765-df8c-71df-9d94-99a626b2e400/image.png)

I realized that with the features I wanted (wifi, Bluetooth, BLE, high-quality audio, streaming support, USB DAC functionality), Linux was a must; it has better docs, support for a bunch of ICs that I need, etc. But to run Linux, I need an MPU(microprocessor unit); the main difference between an MPU and MCU is that the MPU has an MMU(memory management unit), which allows the use of external memory - like DDR - which Linux needs to run (doesn't actually, but in reality it's a necessity).

## Choosing an MPU

![sama7d65-v/4hb](https://cdn.hackclub.com/019f6768-2877-740e-92f0-70b723a492ab/image.png)

This is the part that I'm still not done with; I'm really torn between the SAMA7 series from Microchip and the STM32MP1 series from STM, both are really awesome chips, the sama7 has a really good audio engine and relatively good GPU, and the stm32 is really easy to implement and it also has a pretty good gpu and audio peripheral. I would lean towards the sama7, but that is only available in a 0.65mm BGA package, which is really hard to fan out, while the stm32mp1 has a 0.8mm pitch, which is really easy to use. I think the strategy I will go with is to try to route the SAMA7, and if I fail miserably, I will switch to the stm32.

Two articles were really helpful researching this topic: [this one](https://jaycarlson.net/embedded-linux/), and [this one](https://www.thirtythreeforty.net/posts/mastering-embedded-linux-part-1-concepts/)


## 70Hz e-paper

![drawing of display](https://cdn.hackclub.com/019f6764-a657-7f59-a516-7d014b1332f0/image.png)

V2 had a normal e-ink screen, which had a max partial refresh rate of 0.5s, which is really bad, but for a music player it's alright. But I wanted more!!! So I found out about Sharp MIP displays, which give the effect of e-ink - they don't have a backlight, are mostly black and white, and they are really low power - but they have a higher refresh rate and always need to be powered; for example, the display that I chose (LS022B7DH03) has 70Hz.

## RAM

![lpddr3](https://cdn.hackclub.com/019f6767-5722-7828-809c-23a2a2671b86/image.png)

One of the main reasons I didn't go with a SiP(an IC where both the MPU and RAM are in the same package) is because they mostly only package DDR3L or DDR2L, which have significantly higher power consumptions than LPDDR2/3. Both of my chosen MPUs support both LPDDR2 and LPDDR3, so I will be most likely going to use LPDDR3, and 512MB of it, because these MPUs would be sooner bottlenecked by their performance than from the amount of RAM, and 512MB seems to be the sweet spot from what I read on forums/articles.

## *Time Spent: 8h*

# 2026.07.15: Making a custom BGA symbol = HELL

So I realized that the sama7 doesn't have a premade footprint and symbol :YAYAYAY: 

## Footprint

I heard from Cyao that KiCad has some pretty good built-in BGA footprint generators, so I started researching. Turns out it's pretty easy to use; you only need to add a new entry to a YAML file with the specs of your footprint, and boom, you have a 3d model and footprint. I even made a [pull request](https://gitlab.com/kicad/libraries/kicad-footprint-generator/-/merge_requests/2132) to the main repo, so the footprint can be included in the KiCad default library.


![footprint](https://cdn.hackclub.com/019f6759-1979-74bb-8e4a-e8a1b97e00c4/image.png)
![3d model](https://cdn.hackclub.com/019f6759-1d18-708f-9c76-50ef3c12f1f2/image.png)

## Symbol

This is the part that is hell.

First, the [official KiCad symbol generator](https://gitlab.com/kicad/libraries/kicad-library-utils/-/tree/master/symbol-generators?ref_type=heads) doesn't work out of the box; I had to ask Gemini to fix it 💀 Also, the documentation is really hard to find for both the footprint generator and symbol generator. Also, Microchip doesn't provide a clean .csv file that I can easily process; that would be too easy. Instead, they have all their pins listed in an HTML table, with a bunch of row groups and stuff that makes it really hard to parse. I spent like 1.5h getting this fricking script working, but in the end, with the help of Gemini, I had made a script that converts the HTML table into a CSV file that the KiCad symbol generator can use. So now I have a massive monolithic symbol, with all the pins and their alternate functions that I now need to split up into separate units.

![massive symbol](https://cdn.hackclub.com/019f6759-21a5-749a-91b8-43729f18471b/image.png)

## Also, I did some RAM research

I asked around in a bunch of communities for advice on DDR3 learning resources, and I got some really good answers. Turns out bit/byte swapping on LPDDR3 is a bit more complicated, but I still don't fully understand and need to do more research. I hope I don't even need to do this, crossing my fingers!!!

## *Time Spent: 6h*

# 2026.07.16: Split apart the symbol

This was mostly a long monotonous but fun process of looking at the datasheet and organizing the pins into units. I took a bunch of inspiration from Cyao's sbc.

![split up symbol](https://cdn.hackclub.com/019f6f8c-4fbe-7dd1-bb52-e04dcd09edba/image.png)

## *Time Spent: 4h*

# 2026.07.19: Made PMIC symbol and did some research

## PMIC

Microchip recommends two PMICs for the sama7, the mcp16501 and mcp16502; the mcp16501 can't do dynamic voltage adjustment, and doesn't let the sama7 go up to 1GHz, so the obvious choice was the mcp16502. Luckily Component Search Engine already had a base symbol that I could use as a starting point, but it had the pins arranged based on the footprint, so I just needed to arrange the pins in a way that it made sense. I used a built-in footprint from KiCad, so I didn't have to make that.

![pmic symbol](https://cdn.hackclub.com/019f7bef-e38d-7d60-a8aa-58aecc442bcb/image.png)

## RAM research

I messaged Cyao about where he sourced his RAM when he made his sbc, because I couldn't find LPDDR3 on Mouser/LCSC/Digikey, and other western sites sold these chips for pretty expensive. Turns out Taobao has some pretty cheap RAM, $5 for 1GB. 

Also I learned that GB and Gb are different, GB is a gigabyte and Gb is a gigabit, which is 8 times smaller than a gigabyte. Thanks Cyao!

In the end I landed on a 16Gb chip from Samsung called K4E6E304EC; it's a 174 ball BGA, and is around $7.5. I don't need 2 GB, but you only live once, and it's not that expensive compared to the whole board.

![bottom of ram ic](https://cdn.hackclub.com/019f7bfb-ccc6-7792-9111-293e7c1a0969/c2803256-______.jpg)

I submitted a footprint creation request to Component Search Engine; it should take 1-2 days for them to make it; I will make a custom symbol.

## Thank you again Cyao for all the help!!!!!

## *Time Spent: 4h*

# 2026.07.20: Making RAM symbol and RAM troubles

## Symbol

I realized that I really like making symbols; it's just a really relaxing process, and I can learn a lot about the IC I'm making the symbol for.

Turns out, the pin table in KiCad doesn't have a "visible" field, so I had to use a text editor to mass hide pins, like gnd and vcc, so for example I can have one gnd pin instead of sixty-seven-thousand.

![ram symbol](https://cdn.hackclub.com/019f84ac-c970-7b97-bbe3-0f5766acd44d/image.png)

But I realized something...

## RAM troubles

The DRAM IC I chose has a 32 bit wide data bus, but my MPU only has a 16 bit wide DRAM controller, hmmmmmmmmmmmmmmmmm

So I dived into the datasheet, now this is where it got really confusing, because the datasheet mentioned x16 multiple times, so I went to the EE Discord to ask what the helly is going on, does this IC support both x16 and x32??

![datasheet talking about x16, and an extra column (c10)](https://cdn.hackclub.com/019f84b4-e9a3-78a5-823f-d685090f87e8/image.png)

The first answer I got told me that I can't use this IC, but then another guy joined the conversation and said that I could use this IC, and they also provided some evidence hmmmmmmmmmmmmmmmmmmm

So I went on a search for an LPDDR3 chip that had a 16 bit wide data bus. But I couldn't find any, they were all 32 bit wide 😮 So my DRAM IC must have support for a 16 bit wide data bus, but I'm still not 100% sure, and still have to do more research.

Also made a stack exchange post, but that didn't get any replies :sob:

## *Time Spent: 4h*

# 2026.07.26: Microchip support saves me

## RAM

So after I did a bunch more research, I asked Microchip's live chat if they had any example of the sama7 being used with LPDDR3, and turns out there are examples with x32 memory WOOOOOOOOOOOOOOOOOOO

But I still had a bunch of questions about this example, like do I lose half the capacity, or do I only lose speed, but the live chat support person said that I should create a regular support ticket for these questions, cuz they didn't know. So I did that, and waited eagerly.

A few days later I got a wall of text as a response, which explained everything. I LOVE U BARATH V. FROM MICROCHIP

Turns out almost all x32 LPDDR3 devices(I learned that they call DDR ICs devices from Barath) have an x16 mode, but the datasheets don't make this clear at all, but I also got feedback on the specific DDR device I chose (<3 Microchip) and it has this feature; in x16 you get half the speed but the full capacity of the device. 

But turns out that there was another factor that would have halved my capacity, which was that the device I chose was actually two DDR chips put in one package, and required two CS and CKE pins, but the sama7 only has one CS and CKE pin for DDR devices, so I could have only used one of the chips in the package. The solution? Use a device that doesn't have two chips inside one package, which means use one with half the capacity, so in the end I will have an 8Gb/1GB ddr device.

Luckily the footprint doesn't change at all; I only have to mark two pins as NC (CS1 and CKE1), and rename CS0 to CS and CKE0 to CKE.

With my newfound knowledge I connected the RAM to the sama:

![DDR with labels](https://cdn.hackclub.com/019fa4c3-a62d-7dfa-be17-d944adf23414/image.png)
![hierarchical sheets of DDR and sama](https://cdn.hackclub.com/019fa4c3-d397-7b00-b78e-523cc5d47cbe/image.png)

## Display

I looked around a bit for displays to see if there were any better options than my current choice, mainly I wanted a larger display, so I could have more room for the PCB, but all the larger MIP panels had a horrible refresh rate, like 15Hz, which was unacceptable compared to the current 70Hz one. So I didn't change anything else.

## PWR

Started looking for a powerpath, charger and fuel gauge IC; I may have found one from Analog Devices, but I'm still not sure about it.


## *Time Spent: 6h*

# 2026.08.06: Wireless shenanigans and making power IC symbols

## Finding a good wireless IC and datasheet shenanigans

At first I wanted to use the NXP IW611 as a bare IC, but the PCB layout looked painful, and if I want to sell Meko V3 later I have to go through an expensive certification process. So I went looking for modules, and along the way I found the U-Blox Maya-W3, which uses the Infineon CYW55513, which has Bluetooth 6 :yayayayay:

I asked Component Search Engine to make a footprint and symbol for the Maya-W3, but the first time they rejected it for the reason of "The datasheet doesn't have enough info", but it did. So I submitted again, and now they made it in under 24h, yipeee

But as always, the footprints are nice from CSE, but the symbols are crap. So I had to remake that, and I'm glad I did, because I discovered that the Maya-W3 datasheet is also terrible. It lists the max I2S sample rate as 8kHz, which is really bad, like old call quality, and I realized this just at the end of me finishing the symbol, shi. I also looked at the NXP IW611 I2S sample rate, and it also capped out at 8kHz... Then, as my last hope, I checked the datasheet of the Infineon CYW55513 (the chip that the Maya uses), and it listed its max I2S sample rate at 96kHz; this is excellent!!! So in the end I will use the Maya-W3.

Side note: Both the Maya-W3 and CYW55513 datasheet mention SMIF pins, but don't mention at all what they are used for. If you google SMIF it comes up with an Infineon page that says that it's just SPI, and if you check out CYW55513 example designs the SMIF pins are connected to an external flash and PSRAM, so idk if I should connect them, so I reached out to support, but they haven't responded.

![maya-w3 symbol](https://cdn.hackclub.com/019fd843-4a07-7c6e-9934-ca50763a6a7f/image.png)
![maya-w3 cse footprint](https://cdn.hackclub.com/019fd8cb-d08f-7f26-a10d-9289489aa3f8/image.png)

## Finding power ICs

Turns out there aren't any good ICs that all have powerpath, a fuel-gauge and a battery charger, so I separated the fuel gauge into a separate IC. For the battery charger I chose the BQ25640; it has USB-OTG, USB-PD, voltage monitoring support and a bunch of other cool features. And for the fuel gauge I chose the MAX17260, which is a really simple and good fuel gauge IC, nothing special, it uses a TDFN-14 package. On the other hand the BQ has a really funky TI package, so I asked Snapmagic to make that for me :skull:

I made the symbols for them cuz the premade ones were ass:
![fuel gauge and battery IC symbol](https://cdn.hackclub.com/019fd843-4d5f-702a-a33b-c356d10559ca/image.png)

There are also some shenanigans with the TI BQ IC, cuz it has D- and D+ pins, and the datasheet doesn't mention what to do when you don't want to use them, so I made a support ticket.

## *Time Spent: 7h*

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

Also the BMS doesn't shut down the battery output until it reaches 2.4V, and by that point, that battery would probably be completely dead and unusable. So I will need to implement a software shutdown when the battery voltage reaches like 3.2V. Luckily the fuel-gauge has a battery voltage readout register, so I can use that. My MPU works down to 3V, so 3.2V should be fine.

### Fuel-Gauge

I learned a lot about fuel-gauges. One of the things I learned is how a Coulomb counter works, and how to choose the sense resistor.

### PMIC

Setting up the switching regulators was pretty easy, just had to read the recommended part values.

The more interesting part is the low-power/high-power/hibernate modes. The SAMA7D6 needs a backup source called VBAT to keep the RAM in self-refresh mode. First I thought that I needed another LDO for this input which is always on, so I again found a part, made a symbol, etc. But then again realized that my PMIC had an unused LDO, which I could configure via I2C to always be on, except when the PMIC fully shuts down. This way, the device can hibernate while keeping the RAM in self-refresh mode.



![power schematic](https://cdn.hackclub.com/01a00bc3-9d2e-7ea7-bc93-700ef7ba0172/image.png)

## *Time Spent: 6h*

# 2026.08.20: DDR Troubles and Adding Supporting Circuitry

I discovered maybe a problem with my LPDDR RAM and I also continued to add supporting circuitry to the MPU

## DDR

Turns out that the answer that I got from my Microchip support inquiry - regarding using LPDDR3 with half of its data bus - might have been written by AI (thanks Electronics Stack Exchange for pointing this out).

Microchip said that a register of the LPDDR3 memory device which tells you if the device supports x16 is writable, but it's not, it's read only.

So this might mean that the sama7 example that uses LPDDR3 might be just plain wrong.

I reached out to Micron if the memory device used in the sama example truly supports x16 operation, but they haven't responded yet.

![MR8 read only](https://cdn.hackclub.com/01a020bd-e708-79ed-b440-a28730f384a7/image.png)
_Notice the R, which means read only_

![MR8 function](https://cdn.hackclub.com/01a020bd-ead2-797b-a6b7-3c75506ef276/image.png)

## Supporting Circuitry

Chose and added crystals and caps for them for the sama:

![crystals and calculations](https://cdn.hackclub.com/01a020d6-7153-7398-ba3d-c26c8fef7134/image.png)

Added DDR VREF voltage divider:
![ddr voltage divider](https://cdn.hackclub.com/01a020d9-60d9-721a-b0ed-8a5b2b74c472/image.png)

Added reference resistors:
![reference resistors](https://cdn.hackclub.com/01a020d9-640d-7cd2-bb38-591860b2787b/image.png)

Wired up the PMIC pwr signals, and added a JTAG connector:
![pwr ctrl and JTAGSEL](https://cdn.hackclub.com/01a020d9-6724-715f-bfcb-f176cc0355fa/image.png)

![JTAG connector](https://cdn.hackclub.com/01a020d9-6a75-786e-b922-19d3ebe3654d/image.png)

## *Time Spent: 6h*

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

At first I thought I needed an analog switch, since I wanted to mimic the datasheet for the pseudo diff mode, where _OUT1M_ and _OUT2M_ are connected. But in true differential mode these two need to be disconnected:

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

I saw in the sama7 example design that they had a load switch for the SD card, which led me down the rabbit hole of how SD card slots need to be handled. I stumbled across an [Altium article](https://resources.altium.com/p/how-to-design-microsd-power-circuits-without-destabilizing-on-board-voltage-supply) which had the advice that for prototype boards, you should place a 47uF capacitor on the power rail of the SD card, so it limits the inrush current the regulator has to handle when a new SD card is plugged into a live system

![sd cards](https://cdn.hackclub.com/01a03aef-d6dc-7234-9685-9c3b873f6610/image.png)

I also did a lil sidequest on why SDMMC needs pull-ups; it's so the datalines never go in an unexpected state.

## RF 

![finished RF schematic](https://cdn.hackclub.com/01a03d19-7851-7dfd-9bd3-44327ac16df1/image.png)

### SMIF lines solved

After U-BLOX support didn't respond, I reached out to Infineon's support. They responded really quickly! My assumption was correct, in that I don't need to connect the SMIF pins when I use this chipset with Linux.

### GPIOs

I didn't use any, so this was pretty easy. I just looked over the datasheet if any of them had any special function; they didn't.

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

## *Time Spent: 14h*

# 2026.09.01: Switched out RAM, working on touchpad, looking over schematic

## Ram

Microchip responded to my support case, and said that they wrong before about LPDDR3 and using x32 memory with the SAMA7. Turns out I would only get half the capacity I did use LPDDR3. So I switched to DDR3L. This wasn't that hard, since KiCAD already had the most popular DDR3L in its built in library. And the rest was just matching labels and looking at example designs. I also had to swap from the MCP16502AD PMIC to MCP16502AB, because the AD variant is for LPDDR and the AB is for regular DDR3/L.

![DDR3L](https://cdn.hackclub.com/01a05c3a-20f9-750c-bff2-9c77f0fbe30f/image.png)

## Touchpad

### IQS9151 driver

Jeff LaBundy responded to my email with a [link](https://github.com/jlabundy/linux/tree/iqs9150-release) to the driver!!!! It was sitting in a obscure github repo.

### Generated PCB

![generated PCB](https://cdn.hackclub.com/01a05c3f-b2fe-731c-8e64-1dbbe118204a/image.png)

As mentioned in the previous journal entry, I used a generator. It was pretty easy, I had to install OpenSCAD and the rest was just modifying variables to fit my needs.

### Trying to fit a QFN52 on the back

After I made the symbol for the IQS9151, I realized that it had a QFN52 6mmx6mm package, which I needed to fit on the back of the touchpad. The issue is that the touchpad has a bunch of VIAs, which make it impossible to use a normal QFN52 footprint, so I modified it:

![modified footprint](https://cdn.hackclub.com/01a05c43-b6de-7811-a901-05ec724e71da/image.png)

I than asked for feedback on my design in the KiCAD discord and on Reddit, and everybody said that this will not work 😭 
A Lot of people recommended a bunch of complicated solutions, but Ebastler recommended to put the IC on a second PCB with castellated pads along the edge, then hand solder that small PCB onto the large one. This seems like the best solution! But it's still more complicated then I want. So I might just switch to the IQS7211E, which has a way smaller footprint, but also has less channels, so the resolution will be worse.

If I do switch out the trackpad IC, I will have to regenerate the PCB and maybe make a new symbol

## Looking over the main schematic

I found a few places where I needed to add pull-up/pull-down resistors, was an easy fix.

I also added a bunch of decoupling caps to the ICs that needed it

![bunch of caps](https://cdn.hackclub.com/01a05c4f-1aa7-7087-a46f-6e1261914bbc/image.png)

I also found a footprint for my power path IC:

![power path IC footprint](https://cdn.hackclub.com/01a05c50-afe9-7066-ad70-42cc26e82f4a/image.png)

I also assigned a bunch of footprints and choose a bunch of parts from LCSC:

![footprints](https://cdn.hackclub.com/01a05c52-0bec-727c-a5c8-0322320f0d3d/image.png)

## *Time Spent: 10h*

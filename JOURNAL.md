# 2026.07.12: Thinking of what I need to change

*This will be a long journal, because I did a lot of research beforehand*

![meko v2](images/PXL_20260314_073009498~2.jpg)

For v2 I went with a MCU(microcontroller unit) which are low power processors, and can't run normal OSs. This - I found out while developing the firmware - was a really limiting factor, mainly because the embedded rots that I was forced to use with this specific MCU(nrf5380), Zephyr. 

## Zephyr rant

![zephyr logo](https://cdn.hackclub.com/019f6765-8668-7584-b6df-d85233e2b156/image.png)

The thing to know about Zephyr that is has literally no docs for any of the built-in drivers, so you have to look at examples(if they even exist) to figure out how the hell the driver works. In theory Zephyr would be awesome, it is similarly structured to how linux works, has a bunch of built-in drivers, has standard APIs for similar peripherals, and a bunch of cool stuff, but in reality the lack of docs, the complicated build system, the unclear runtime errors just make it impossible to actually use.

Thank you for listening to my rant.

## The solution: Linux

![linux logo](https://cdn.hackclub.com/019f6765-df8c-71df-9d94-99a626b2e400/image.png)

I realized with the features I wanted (wifi, bluetooth, ble, high quality audio, streaming support, usb dac functionality) linux was a must, it has better docs, support for a bunch of ICs that I need, etc. But to run Linux I need an MPU(microprocessor unit), the main difference between an MPU and MCU is that the MPU has an MMU(memory management unit), which allows the use of external memory - like DDR - which Linux needs to run (doesn't actually, but in reality it's a necessity.

## Choosing an MPU

![sama7d65-v/4hb](https://cdn.hackclub.com/019f6768-2877-740e-92f0-70b723a492ab/image.png)

This is the part that I'm still not done with, I'm really torn between the SAMA7 series from Microchip and the STM32MP1 series from STM, both are really awesome chips, the sama7 has a really good audio engine and relatively good gpu, and the stm32 is really easy to implement and it also has a pretty good gpu and audio peripheral. I would lean towards the sama7, but that is only available in a 0.65mm BGA package, which is really hard to fan out, while the stm32mp1 has a 0.8mm pitch, which is really easy to use. I think the strategy i will go with is to try to route the sama7, and if i fail miserably, I will switch to the stm32.

Two articles were really helpful researching this topic: [this one](https://jaycarlson.net/embedded-linux/), and [this one](https://www.thirtythreeforty.net/posts/mastering-embedded-linux-part-1-concepts/)


## 70hz e-paper

![drawing of display](https://cdn.hackclub.com/019f6764-a657-7f59-a516-7d014b1332f0/image.png)

V2 had a normal e-ink screen, which had a max partial refresh rate of 0.5s, which is really bad, but for a music player it's alright. But I wanted more!!! So I found out about Sharp MIP displays, which give the effect of e-ink - they don't have a back light, are mostly black and white and they are really low power - but they have a higher refresh rate, for example the display that I choose(LS022B7DH03) it has 70Hz.

## RAM

![lpddr3](https://cdn.hackclub.com/019f6767-5722-7828-809c-23a2a2671b86/image.png)

One of the main reasons I didn't go with a SiP(an IC where both the MPU and RAM are in the same package), because they mostly only package DDR3L or DDR2L, which have significantly higher power consumptions than LPDDR2/3. Both of my chosen MPUs support both LPDDR2 and LPDDR3, so I will be most likely going to use LPDDR3, and 512MB of it, because these MPUs would be sooner bottle necked by their performance than from the amount of RAM, and 512MB seems to be the sweet spot from what I read on forms/articles.

## *Time Spent: 8h*

# 2026.07.15: Making a custom BGA symbol = HELL

So I realized that the sama7 doesn't have a premade footprint and symbol :YAYAYAY: 

## Footprint

I heard from Cyao that kicad has some pretty good built in BGA footprint generators, so I started researching. Turns out it's pretty easy to use, you only need to add a new entry to a YAML file with the specs of your footprint, and boom, you have a 3d model and footprint. I even made a [pool request](https://gitlab.com/kicad/libraries/kicad-footprint-generator/-/merge_requests/2132) to the main repo, so the footprint can be included in the kicad default library.


![footprint](https://cdn.hackclub.com/019f6759-1979-74bb-8e4a-e8a1b97e00c4/image.png)
![3d model](https://cdn.hackclub.com/019f6759-1d18-708f-9c76-50ef3c12f1f2/image.png)

## Symbol

This is the part that is hell.

First the [official kicad symbol generator](https://gitlab.com/kicad/libraries/kicad-library-utils/-/tree/master/symbol-generators?ref_type=heads) doesn't work out of the box, I had to ask gemini to fix it 💀 Also the documentation is really hard to find for both the footprint generator and symbol generator. Also microchip doesn't provide a clean .csv file that I can easily process, that would be to easy, instead they have all their pins listed in a html table, with a bunch of rowgroups and stuff, that makes it really hard to parse. I spent like 1.5h getting this fricking script working, but in the end with the help of gemini I had made a script that converts the html table into a csv file that the kicad symbol generator can use. So now I have a massive monolithic symbol, with all the pins, and their alternate functions, that I now need to split up into separate units.

![massive symbol](https://cdn.hackclub.com/019f6759-21a5-749a-91b8-43729f18471b/image.png)

## Also, I did some ram research

I asked around in a bunch of communities for advice on ddr3 learning resources, and I got some really god answers. Turns out bit/byte swapping on lpddr3 is a bit more complicated, but I still don't fully understand and need to do more research. I hope I don't even need to do this, crossing my fingers!!!

## *Time Spent: 6h*

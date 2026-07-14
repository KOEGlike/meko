# 2026.07.12: Thinking of what I need to change

*This will be a long journal, because I did a lot of research beforehand*

For v2 I went with a MCU(microcontroller unit) which are low power processors, and can't run normal OSs. This - I found out while developing the firmware - was a really limiting factor, mainly because the embedded rots that I was forced to use with this specific MCU(nrf5380), Zephyr. 

## Zephyr rant

The thing to know about Zephyr that is has literally no docs for any of the built-in drivers, so you have to look at examples(if they even exist) to figure out how the hell the driver works. In theory Zephyr would be awesome, it is similarly structured to how linux works, has a bunch of built-in drivers, has standard APIs for similar peripherals, and a bunch of cool stuff, but in reality the lack of docs, the complicated build system, the unclear runtime errors just make it impossible to actually use.

Thank you for listening to my rant.

## The solution: Linux

I realized with the features I wanted (wifi, bluetooth, ble, high quality audio, streaming support, usb dac functionality) linux was a must, it has better docs, support for a bunch of ICs that I need, etc. But to run Linux I need an MPU(microprocessor unit), the main difference between an MPU and MCU is that the MPU has an MMU(memory management unit), which allows the use of external memory - like DDR - which Linux needs to run (doesn't actually, but in reality it's a necessity.

## Choosing an MPU

This is the part that I'm still not done with, I'm really torn between the SAMA7 series from Microchip and the STM32MP1 series from STM, both are really awesome chips, the sama7 has a really good audio engine and relatively good gpu, and the stm32 is really easy to implement and it also has a pretty good gpu and audio peripheral. I would lean towards the sama7, but that is only available in a 0.65mm BGA package, which is really hard to fan out, while the stm32mp1 has a 0.8mm pitch, which is really easy to use. I think the strategy i will go with is to try to route the sama7, and if i fail miserably, I will switch to the stm32.

Two articles were really helpful researching this topic: [this one](https://jaycarlson.net/embedded-linux/), and [this one](https://www.thirtythreeforty.net/posts/mastering-embedded-linux-part-1-concepts/)


## 70hz e-paper

V2 had a normal e-ink screen, which had a max partial refresh rate of 0.5s, which is really bad, but for a music player it's alright. But I wanted more!!! So I found out about

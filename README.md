> [!CAUTION]
> V3 is a WIP, if you want updates follow my [journal](JOURNAL.md). Check out the [v2 branch](https://github.com/KOEGlike/meko/tree/v2) for a completed project

# Meko

A Linux handheld with ddr3, a 70Hz e-paper display and a haptic touchpad

![hero](images/renders/assembled.png)

## Why??

I wanted to challenge myself and create a unique MP3 player, but realized that this lil device could do so much more, so I dropped the DAP(Digital Audio Player) only branding

You could:
- Use it as a DAP
- Use it's haptic touchpad as a synth
- Put your AI agent on it (if you really want to)
- Host your website
- Play games

## Components

- **_MPU_**: SAMA7D65, it can boost up to 1GHz, good audio subsystem and gpu
- **_RAM_**: Half a gig of DDR3L(MT41K256M16TW)
- **_EPD_**: Sharp MIP LS022B7DH03, can go up to 70Hz, 240x320
- **_Audio_**: TAC5212 
  - **_DAC+AMP_**: 192kHz, 32-bit, 120dB SNR, 2Vrms
  - **_ADC_**: 192kHz, 32-bit, 119dB SNR
- **_Wireless_**: Bluetooth 6 with LE audio and WiFi 6E
- **_Touchpad_**: IQS7211E touch IC with DRV2605 haptic LRA driver
- **_USB_**: USB 2.0 with OTG

## PCBs

The main-board is a 0.8mm 6L PCB with a SIG/GND/PWR/GND/GND/SIG stackup.

The touchpad PCB is a standard 2L 1.6mm board.

### Main board

| Front | Back | Back (no silkscreen) |
|:---:|:---:|:---:|
| <a href="images/renders/main_pcb_front.png"><img src="images/renders/main_pcb_front.png" alt="Main PCB front" width="300"></a> | <a href="images/renders/main_pcb_back.png"><img src="images/renders/main_pcb_back.png" alt="Main PCB back" width="300"></a> | <a href="images/renders/main_pcb_back_no_silk.png"><img src="images/renders/main_pcb_back_no_silk.png" alt="Main PCB back without silkscreen" width="300"></a> |

### Touchpad

| Front | Back |
|:---:|:---:|
| <a href="images/renders/touchpad_pcb_front.png"><img src="images/renders/touchpad_pcb_front.png" alt="Touchpad PCB front" width="350"></a> | <a href="images/renders/touchpad_pcb_back.png"><img src="images/renders/touchpad_pcb_back.png" alt="Touchpad PCB back" width="350"></a> |


## Schematics & PCBs

<details>
<summary><i>Bunch of images</i></summary>

<br>

### Main board

<img src="images/main_pcb/front.png" alt="Main board PCB front" width="100%">

<img src="images/main_pcb/back.png" alt="Main board PCB back" width="100%">

<img src="images/main_pcb/pwr.png" alt="Main board PCB power planes" width="100%">

<img src="images/main_schematic/meko-1.webp" alt="Overview schematic" width="100%">

<img src="images/main_schematic/meko-2.webp" alt="SAMA7 schematic" width="100%">

<img src="images/main_schematic/meko-3.webp" alt="DDR schematic" width="100%">

<img src="images/main_schematic/meko-4.webp" alt="Power schematic" width="100%">

<img src="images/main_schematic/meko-5.webp" alt="Wireless schematic" width="100%">

<img src="images/main_schematic/meko-6.webp" alt="USB schematic" width="100%">

<img src="images/main_schematic/meko-7.webp" alt="Audio schematic" width="100%">

<img src="images/main_schematic/meko-8.webp" alt="SD cards schematic" width="100%">

<img src="images/main_schematic/meko-9.webp" alt="Display schematic" width="100%">

<img src="images/main_schematic/meko-10.webp" alt="Touchpad schematic" width="100%">

<img src="images/main_schematic/meko-11.webp" alt="Buttons schematic" width="100%">

### Touchpad

<img src="images/touchpad_pcb/front.png" alt="Touchpad PCB front" width="100%">

<img src="images/touchpad_pcb/back.png" alt="Touchpad PCB back" width="100%">

<img src="images/touchpad_schematic.webp" alt="Touchpad schematic" width="100%">

</details>

## Software

This lil guy will be running on a custom Linux image built with Yocto, which is currently WIP.

## Fabrication

This board was designed for PCBWAYs process and stackup. For more info about the stackup check out the user.comments layer in KiCAD.

Every part has a _MFR_, _MPN_, and a _LCSC_/_DigiKey no._ field. You can export a complete BOM from KiCAD.

## External KiCAD Libraries

I used Cyao's [ckl](https://github.com/cheyao/ckl) library.

## Shoutouts

- Diamond Master from The KiCAD discord: Thank you for doing sims! Without you doing the impedance sim the project would have failed!
- Cyao: Thank you for taking a deep look at my DDR routing and pointing out a **BUNCH** of issues! The performance of my DDR would have been cooked without you!
- Daniel from The KiCAD discord: Thank you for helping me with all the high-speed basics, and pointing out issues with my DDR!
- r/PrintedCircuitBoard: Thank you for pointing out a bunch of small and large mistakes both in my schematic and PCB
- Hack Club: Thank you for providing an awesome community and funding for my project!!
- All the other people from the KiCAD Discord! Y'all are awesome!!

## AI usage

The hardware and software was 100% _Human Designed™_ .

AI was used to find datasheets, as a tool to point me in the right direction, and to fix my horrible grammar.

## Journals

Each versions has a detailed journal:

[V3 journal](JOURNAL.md)

[V2 journal](JOURNAL_OLD_V2.md)

[V1 journal](JOURNAL_OLD_V1.md)

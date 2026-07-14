> [!CAUTION]
> I'm currently working on v3, so if you want see the source files for v2 which this readme describes, go check out the v2 branch

# Meko
Meko is a high audio quality DAP, it has an e-ink screen, a physical spinning wheel, small formfactor, Bluetooth, micro SD slot, transparent case. Its design was inspired by the iPod nano 2. The size of the case is 41x73x14mm  

[Demo Video](https://youtu.be/EwbpijFxXzg?si=dRHZZMwsa-1tPmkg)

![IRL](images/PXL_20260314_073009498~2.jpg)
<img src="https://rawcdn.githack.com/KOEGlike/meko/f5fcdac62bb8b718516981f5efe12eb97afa4bd7/meko-blend/renders/peresentation/front.png" height=500/>  

## Why?

I really miss the era of gadgets, where every device served one specific function, without distraction, like a mp3 player, a camera, a gps navigator, an e reader, etc. With this player I wanted to make something unique

## PCB 

![render of pcb front](https://cdn.hackclub.com/rescue?url=https://hc-cdn.hel1.your-objectstorage.com/s/v3/28628c18f999bf452bae8aa2b9f1559c4c9c38e4_meko-front.png)
![render of pcb back](https://rawcdn.githack.com/KOEGlike/meko/f915e92f74e80db6822fabad6e413f22e3d987a9/meko-blend/renders/PCB/meko-front.png)
![schematic](https://cdn.hackclub.com/rescue?url=https://hc-cdn.hel1.your-objectstorage.com/s/v3/b3219307270260e8b242c8adf0ab8544015bc564_meko-pcb-1.png)
  
Production files in `Releases`  
  
The PCB has 6 layers, in the SIG/GND/SIG/GND/GND/SIG stackup.  
  
It is impedance controlled for JLCs default 6 layer PCB stackup, but not many of the lines are impedance controlled, and if they are they are short, so if you must, you can use other stackups.

### Chips

- main SOC: NRF5340
- DAC/AMP: TAD5212
- PMIC: npm1300
- hall-effect sensor: AS5600-ASOM

## Case 

![render of case exploaded](https://cdn.hackclub.com/rescue?url=https://hc-cdn.hel1.your-objectstorage.com/s/v3/1a27d850232c1081d954c8f7dde6c17a460f477e_exploaded.png)  
  
Production files in `Releases`  
  
The case in designed in FreeCAD, which is an Open Source  and free CAD program, you will need this program to edit the case.

### 3D printing 

I recommend you to print this in resin because it requires accurate dimensions for the best result. You can print this on a FDM, but you need to change the `tolerance` and maybe other parameters in the model.

## Firmware 

The firmware is being developed in [this repo](https://github.com/KOEGlike/eno-os)

The firmware is very WIP!!!! It is written with the zephyr rtos.

If I have time I will try to port rockbox

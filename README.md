> [!CAUTION]
> The PCB of the first prototype does not have 100% of it's features working. If you want to make one wait until I fix all of the issues 

# Meko
Meko is a high audio quality DAP, it has an e-ink screen, a physical spinning wheel, small formfactor, Bluetooth, micro SD slot, transparent case. Its design was inspired by the iPod nano 2. The size of the case is 41x73x14mm  
<img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/2c2f0d34a5722b5a69f6c69a4d09989515afc17d_0746bcb8a689a1f602909d25effef6bb8056e4da.png" height=500/>  

## Why?

I really miss the era of gadgets, where every device served one specific function, without distraction, like a mp3 player, a camera, a gps navigator, an e reader, etc. With this player I wanted to make something unique

## PCB 


![render of pcb back](https://hc-cdn.hel1.your-objectstorage.com/s/v3/e13d12c71f71050b8f1916d442237825d7bf3a5c_pcb-back_optimized.png)  
![render of pcb front](https://hc-cdn.hel1.your-objectstorage.com/s/v3/22816fbb7ae5d4e87e992a025cd9d627be469620_pcb-front_optimized.png)

  
Production files in `Releases`  
  
The PCB has 6 layers, in the SIG/GND/SIG/GND/GND/SIG stackup.  
  
It is impedance controlled for JLCs default 6 layer PCB stackup, but not many of the lines are impedance controlled, and if they are they are short, so if you must, you can use other stackups.

### Chips

- main SOC: NRF5340
- DAC/AMP: TAD5212
- PMIC: npm1300
- hall-effect sensor: AS5600-ASOM

## Case 

![render of case exploaded](https://hc-cdn.hel1.your-objectstorage.com/s/v3/bbbaaf101a9f005d0980b7fd177fbc70151c9b29_expload_optimized.png)  
  
Production files in `Releases`  
  
The case in designed in FreeCAD, which is an Open Source  and free CAD program, you will need this program to edit the case.

### 3D printing 

I recommend you to print this in resin because it requires accurate dimensions for the best result. You can print this on a FDM, but you need to change the `tolerance` and maybe other parameters in the model.

### Parameters

![params](https://hc-cdn.hel1.your-objectstorage.com/s/v3/28701e145fee447792843a0d50e1efcada36852c_screenshot_20250621_093625.png)  
The case has parametric design, so you can change the design very easily, and I included some easily changeable parameters, here what they do:

- `battery_height` and `battery_width` are to set the size of the hole in the `bottom_cade`, the case is designed to have a 5mm thick battery, so you need to change the length of the first pad in `bottom_case` to account for the thicker battery 
- `bearing_inner` and `bearing_outer` set the inner and outer diameter of the bearing, this might mess up the top case, and if you dont want to use the recommended magnet,the wheel, so you might need to go in deeper to change these kinds of stuff. These parameters won't change the 3D model of the bearing in the model. 
- `bearing_height` this sets the hight of the bearing, this will change the size of the hole in the `top_case` and the rim of the `wheel`. This parameter won't change the 3D model of the bearing in the model. 
- `bearing_tolerance` this sets the tightness of the friction fit of the bearing int the `top_case` and `wheel`
- `button_fillet` this sets the roundness of the buttons 
- `button_height` and `button_width` set the width and hight of the buttons 
- `button_reatiner_edge` set the size of the edge that keeps the button inside of the case and doesn't let it fall out 
- `button_tolerance` sets the tolerance of the buttons to the case, this is a different form the general `tolerance` parameter, because the buttons are moving, and may wobble more if you set a loos tolerance
- `case_offset` this parameter is still WIP, so don't use it, it sets the offset of the PCB form the point where the `top_case` and `bottom_case` meet 
- `tolerance` this sets the general tolerance for inaccuracies in the 3D print 
- `wall_thickness` this sets the thickness for the case walls 
- `wheel_thickness` this sets how thick the wheel should be 

## Firmware 

The firmware is being developed in [this repo](https://github.com/KOEGlike/eno-os)

The firmware is very WIP!!!! It will be written in rust with the esp-idf-svc and embassy-executor frameworks. I choose the std route for rust instead of the no-std one, because with std i can use existing std libraries for audio processing, no-std has more performance but it's still in ts infancy, and doesn't have mature libraries. It will support lots of file formats, Spotify connect support, AirPlay 2 Support, and maybe qobuz
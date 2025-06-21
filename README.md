# Meko
Meko is a high audio quality DAP, it has an e-ink screen, a physical spinning wheel, small formfactor, WIFI and Bluetooth, micro SD slot, transparent case. Its design was inspired by the iPod nano 2
![render of meko](https://hc-cdn.hel1.your-objectstorage.com/s/v3/2ca4afc27af675cd22b7a771083a7da3a2da0dd6_68747470733a2f2f68632d63646e2e68.png)

## PCB 

![render of pcb](https://hc-cdn.hel1.your-objectstorage.com/s/v3/c48284d859844763172703596e5ee1b2c6a2917b_frame_6_1_.png)  
  
Production files in `Releases`  
  
The PCB has 4 layers, in the SIG/GND/GND/SIG stackup.  
  
It is impedance controlled for JLCs default 4 layer PCB stackup, but not many of the lines are impedance controlled, and if they are they are short, so if you must, you can use other stackups.

### Chips

- main SOC: ESP32 pico mini 02
- DAC/AMP: ES9218PQ
- USB to UART: CP2102N
- battery charger: BQ24075RGT
- fueal gauge: BQ27427YZFR
- low noise regulators: LP59075-X.X/NOPB
- large 3V3 regulator: LP5912-3.3DRVR
- hall-effect sensor: AS5600-ASOM

## Case 

![render of case](https://hc-cdn.hel1.your-objectstorage.com/s/v3/7aa9fc54eb5928e18ea7e6aec79b7fc0703189de_0001_1_.png)  
  
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

The firmware is very WIP!!!! It will be written in rust with the esp-idf-svc and embassy-executor frameworks. I choose the std route for rust instead of the no-std one, because with std i can use existing std libraries for audio processing, no-std has more performance but it's still in ts infancy, and doesn't have mature libraries.

## BOM 




|Qty|Value                      |MPN/link               |Order Unit Price|Total |
|---|---------------------------|-----------------------|----------------|------|
|1  |ECS-2520SMV-500-GP-TR      |ECS-2520SMV-500-GP-TR  |$2.73           |$2.73  |
|1  |CP2102N-Axx-xQFN24         |CP2102N-A02-GQFN24R    |$3.46           |$3.46  |
|1  |USBLC6-2SC6                |USBLC6-2SC6            |$0.36           |$0.36  |
|2  |LP5907SNX-1.8/NOPB         |LP5907SNX-1.8/NOPB     |$1.07           |$2.14  |
|3  |LP5907SNX-3.3/NOPB         |LP5907SNX-3.3/NOPB     |$1.07           |$3.21  |
|1  |BQ24075RGT                 |BQ24075RGTR            |$1.99           |$1.99  |
|1  |ESP32-PICO-MINI-02         |ESP32-PICO-MINI-02-N8R2|$3.51           |$3.51  |
|2  |SW_Push                    |SKRKAGE020             |$0.466          |$0.932 |
|5  |SW_Push                    |SKRTLAE010             |$0.455          |$2.275 |
|1  |100k                       |RC0402FR-07100KL       |$0.10           |$0.1   |
|2  |5.1k                       |RC0402FR-075K1L        |$0.10           |$0.2   |
|1  |1.8k                       |RC0402FR-071K8L        |$0.10           |$0.1   |
|2  |1.5k                       |RC0402FR-071K5L        |$0.10           |$0.2   |
|3  |47k                        |RC0402FR-0747KL        |$0.10           |$0.3   |
|1  |2.2R                       |RC0402FR-072R2L        |$0.10           |$0.10 |
|1  |1M                         |RC0402FR-071ML         |$0.10           |$0.10 |
|1  |1k                         |RC0402FR-071KL         |$0.10           |$0.10 |
|22 |10k                        |CRCW040210K0FKED       |$0.025          |$0.55 |
|1  |Si1308EDL                  |SI1308EDL-T1-GE3       |$0.451          |$0.45 |
|3  |SS8050                     |SS8050-HF              |$0.291          |$0.87 |
|1  |HD-EMB1204-SM              |HD-EMB1204-SM          |$3.54           |$3.54 |
|1  |47uF                       |MLZ2012M470WT000       |$0.10           |$0.10 |
|1  |SJ2-35954B-SMT-TR          |SJ2-35954B-SMT-TR      |$1.25           |$1.25 |
|1  |USB_C_Receptacle_USB2.0_16P|USB4105-GF-A           |$0.78           |$0.78 |
|1  |MEM2090-00-145-00-A        |MEM2090-00-145-00-A    |$1.56           |$1.56 |
|1  |GDEY0154D67                |FH34SRJ-24S-0.5SH(99)  |$2.74           |$2.74 |
|1  |BQ27427YZFR                |BQ27427YZFR            |$1.42           |$1.42 |
|1  |ES9218PQ                   |ES9218PQ               |$12.00          |$12.00|
|1  |LP5912-3.3DRVR             |LP5912-3.3DRVR         |$1.04           |$1.04 |
|1  |TCAL9538RSVR               |TCAL9538RSVR           |$1.71           |$1.71 |
|1  |AS5600-ASOM                |AS5600-ASOM            |$2.58           |$2.58 |
|1  |500mA                      |MF-FSMF050X-2          |$0.411          |$0.41 |
|1  |LED                        |150060AS75003          |$0.351          |$0.35 |
|4  |D_TVS                      |CD0201-T2.0LC          |$0.291          |$1.16 |
|3  |D3V3X8U9LP3810             |D3V3F8U9LP3810-7       |$0.26           |$0.78 |
|3  |MBR0530                    |MBR0530T1G             |$0.171          |$0.51 |
|1  |SK6805                     |SK6805-EC14            |$0.1            |$0.10 |
|1  |US1B                       |US1B                   |$0.171          |$0.17 |
|4  |2.2nF                      |CL05B222KB5NNNC        |$0.10           |$0.40 |
|1  |2.2uF                      |CL05A225KO5NQNC        |$0.10           |$0.10 |
|1  |22uF                       |CL10A226MQ8NRNC        |$0.22           |$0.22 |
|1  |10uF                       |CL05A106MQ5NUNC        |$0.10           |$0.10 |
|11 |4.7uF                      |CL05A475KP5NRNC        |$0.116          |$1.28 |
|27 |1uF                        |CL05A105KO5NNNC        |$0.011          |$0.30 |
|10 |100nF                      |CL05B104KO5NNNC        |$0.004          |$0.04 |
|1  |Battery_Cell               |S2B-PH-SM4-TB          |$0.511          |$0.51 |
|1  |e-ink screen               |[GDEY0154D67](https://www.aliexpress.com/item/1005004027620986.html)            | $7 + $5 shipping | $12|
|1  |magnet                     |[link](https://www.first4magnets.com/product/6mm-dia-x-1mm-thick-diametrically-magnetised-n42-neodymium-magnet-20413) | $3 + $16 shipping | 19$ |
|1  |battery with PH2.0 conn.   |[link](https://www.aliexpress.com/item/1005006043243361.html) | $4| $4|
|1  |6701 bearing               |[ceramic](https://www.aliexpress.com/item/1005007752030168.html) or [ZZ](https://www.aliexpress.com/item/1005006822613982.html) | $6 | $6|
|5  |M1.6 8mm coutnersunk screw |[link](https://www.aliexpress.com/item/1005003620203113.html) | $1.5 | $1.5|
|5  |M1.6 2.5mm OD 2mm thick    |[link](https://www.aliexpress.com/item/1005007653131713.html) | $1.8 |$1.8|
|   |PCB at JLC                 | -   |$11 + $7 stencil + $22.25 shipping | $31 |
| - |1kg clear resin            |[link](https://store.anycubic.com/products/standard-resin-v2?variant=43909069897890)| $28 | $28|
|   |                           |                       |                |≈$170|


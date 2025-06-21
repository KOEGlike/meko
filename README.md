# Meko
Meko is a high audio quality DAP, it has an e-ink screen, a physical spinning wheel, small formfactor, WIFI and Bluetooth, micro SD slot, transparent case. Its design was inspired by the iPod nano 2
![render of meko](https://hc-cdn.hel1.your-objectstorage.com/s/v3/83b9b50cc86617301cda5601078db6ff36537eb6_0049.png)

## PCB 

![render of pcb]()  
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

![render of case]()  
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

## BOM 


|Qty|Value                      |MPN/Souecing link      |
|---|---------------------------|-----------------------|
|1  |Battery_Cell               |S2B-PH-SM4-TB          |
|10 |100nF                      |CL05B104KO5NNNC        |
|27 |1uF                        |CL05A105KO5NNNC        |
|11 |4.7uF                      |CL05A475KP5NRNC        |
|1  |10uF                       |CL05A106MQ5NUNC        |
|1  |22uF                       |CL10A226MQ8NRNC        |
|1  |2.2uF                      |CL05A225KO5NQNC        |
|4  |2.2nF                      |CL05B222KB5NNNC        |
|1  |US1B                       |US1B                   |
|1  |SK6805                     |SK6805-EC14            |
|3  |MBR0530                    |MBR0530T1G             |
|3  |D3V3X8U9LP3810             | D3V3F8U9LP3810-7      |
|4  |D_TVS                      | CD0201-T2.0LC         |
|1  |LED                        |150060AS75003          |
|1  |500mA                      |MF-FSMF050X-2          |
|1  |AS5600-ASOM                |AS5600-ASOM            |
|1  |TCAL9538RSVR               |TCAL9538RSVR           |
|1  |LP5912-3.3DRVR             |LP5912-3.3DRVR         |
|1  |ES9218PQ                   |ES9218PQ               |
|1  |BQ27427YZFR                |BQ27427YZFR            |
|1  |GDEY0154D67                |FH34SRJ-24S-0.5SH(99)  |
|1  |MEM2090-00-145-00-A        |MEM2090-00-145-00-A    |
|1  |USB_C_Receptacle_USB2.0_16P|USB4105-GF-A           |
|1  |SJ2-35954B-SMT-TR          | SJ2-35954B-SMT-TR     |
|1  |47uF                       |MLZ2012M470WT000       |
|1  |HD-EMB1204-SM              | HD-EMB1204-SM         |
|3  |SS8050                     |SS8050-HF              |
|1  |Si1308EDL                  |SI1308EDL-T1-GE3       |
|22 |10k                        |CRCW040210K0FKED       |
|1  |1k                         |RC0402FR-071KL         |
|1  |1M                         |RC0402FR-071ML         |
|1  |2.2R                       |RC0402FR-072R2L        |
|3  |47k                        |RC0402FR-0747KL        |
|2  |1.5k                       |RC0402FR-071K5L        |
|1  |1.8k                       |RC0402FR-071K8L        |
|2  |5.1k                       |RC0402FR-075K1L        |
|1  |100k                       |RC0402FR-07100KL       |
|5  |SW_Push                    |SKRTLAE010             |
|2  |SW_Push                    |SKRKAGE020             |
|1  |ESP32-PICO-MINI-02         |ESP32-PICO-MINI-02-N8R2|
|1  |BQ24075RGT                 |BQ24075RGTR            |
|3  |LP5907SNX-3.3/NOPB         |LP5907SNX-3.3/NOPB     |
|2  |LP5907SNX-1.8/NOPB         |LP5907SNX-1.8/NOPB     |
|1  |USBLC6-2SC6                |USBLC6-2SC6            |
|1  |CP2102N-Axx-xQFN24         |CP2102N-A02-GQFN24R    |
|1  |ECS-2520SMV-500-GP-TR      |ECS-2520SMV-500-GP-TR  |
|1  |e-ink screen               |GDEY0154D67            |
|1  |magnet                     |[link](https://www.first4magnets.com/product/6mm-dia-x-1mm-thick-diametrically-magnetised-n42-neodymium-magnet-20413) |
|1  |battery with PH2.0 conn.   |[link](https://www.aliexpress.com/item/1005006043243361.html) |
|1  |6701 bearing               |[ceramic](https://www.aliexpress.com/item/1005007752030168.html) or [ZZ](https://www.aliexpress.com/item/1005006822613982.html) |
|5  |M1.6 8mm coutnersunk screw |[link](https://www.aliexpress.com/item/1005003620203113.html) |
|5  |M1.6 2.5mm OD 2mm thick    |[link](https://www.aliexpress.com/item/1005007653131713.html) |

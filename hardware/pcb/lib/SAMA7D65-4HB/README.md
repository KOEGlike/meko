# Generating the footprint and symbol

## Footrpint

Use [my fork](https://gitlab.com/KOEGlike/kicad-footprint-generator/-/tree/add-4hb) of the kicad footprint generator and generate the BGA footprints and 3D models

## Symbol

Copy the html of the table using devtools from the [sama7d65-v/4hb datasheet pin description section](https://onlinedocs.microchip.com/oxy/GUID-82119957-1E11-4B69-84AC-EF0EA08F5595-en-US-5/GUID-DECB5F30-A85E-43E6-AF76-690E82329CF9.html) and make a html file, and use the html_to_csv.py script to create a .csv file that the [kicad symbol generator](https://gitlab.com/kicad/libraries/kicad-library-utils/-/tree/master/symbol-generators?ref_type=heads) can accept, and then use the symbol generator to creat the symbol. This will be one big symbol that you will have to manually split into units.

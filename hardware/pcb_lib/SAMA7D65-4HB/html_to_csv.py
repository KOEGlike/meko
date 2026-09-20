import sys
import csv
from bs4 import BeautifulSoup

def parse_html_to_csv(html_file, output_csv):
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading HTML file: {e}")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    
    tbody = soup.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
    else:
        # Fallback if there is no tbody
        rows = soup.find_all('tr')
        # Skip header rows
        rows = [r for r in rows if r.find('td')]
    
    pins_data = []
    current_pin_data = None
    rowspan_remaining = 0
    
    for row in rows:
        tds = row.find_all('td')
        if not tds:
            continue
            
        if rowspan_remaining == 0:
            # First row for a pin (could have rowspan for multiple PIO functions)
            if len(tds) >= 12:
                # Based on the SAMA7D65 table structure provided:
                # 0: 343-pin TFBGA
                # 1: 375-pin TFBGA
                # 2: Power Rail
                # 3: I/O Type
                # 4: Primary Signal
                # 5: Primary Dir
                # 6: Alternate Signal
                # 7: Alternate Dir
                # 8: PIO Peripheral Func
                # 9: PIO Peripheral Signal
                # 10: PIO Peripheral Dir
                # 11: PIO Peripheral I/O Set
                # 12: Reset State
                
                pin_343 = tds[0].get_text(strip=True)
                rowspan_attr = tds[0].get('rowspan')
                rowspan = int(rowspan_attr) if rowspan_attr else 1
                rowspan_remaining = rowspan - 1
                
                primary_sig = tds[4].get_text(strip=True)
                primary_dir = tds[5].get_text(strip=True)
                alt_sig = tds[6].get_text(strip=True)
                # alt_dir = tds[7].get_text(strip=True)
                # pio_func = tds[8].get_text(strip=True)
                pio_sig = tds[9].get_text(strip=True)
                
                names = []
                if primary_sig and primary_sig != '-':
                    names.append(primary_sig)
                if alt_sig and alt_sig != '-':
                    names.append(alt_sig)
                if pio_sig and pio_sig != '-':
                    names.append(pio_sig)
                
                # Determine KiCad pin type
                pin_type = 'bidirectional' # default
                if primary_dir == 'I':
                    pin_type = 'input'
                elif primary_dir == 'O':
                    pin_type = 'output'
                elif primary_dir in ['P', 'Power']:
                    pin_type = 'power_in'
                
                current_pin_data = {
                    'pin': pin_343,
                    'names': names,
                    'type': pin_type,
                    'side': 'left'  # Default side, to be adjusted manually or by logic if needed
                }
                
                if rowspan_remaining == 0:
                    pins_data.append(current_pin_data)
        else:
            # Continuation rows only contain the PIO peripheral columns (and sometimes Reset State)
            # Typically 4 columns: Func, Signal, Dir, I/O Set
            if len(tds) >= 2:
                pio_sig = tds[1].get_text(strip=True)
                if pio_sig and pio_sig != '-':
                    current_pin_data['names'].append(pio_sig)
            
            rowspan_remaining -= 1
            if rowspan_remaining == 0:
                pins_data.append(current_pin_data)
                
    # Write output to CSV formatted for from_csv_generator.py
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write Metadata Header
            writer.writerow(['reference', 'U'])
            writer.writerow(['name', 'SAMA7D65_343'])
            writer.writerow(['footprint', 'Package_BGA:TFBGA-343']) # Example footprint
            writer.writerow(['footprint_filter', 'TFBGA*'])
            writer.writerow(['datasheet', ''])
            writer.writerow(['description', 'SAMA7D65 343-pin TFBGA'])
            # We set generator_split_pin_names to 1 to separate the first name (Primary)
            # from the rest (Alt/PIO functions) as alternate names in the symbol.
            writer.writerow(['generator_split_pin_names', '1']) 
            writer.writerow([])
            
            # Write Pin Data Header
            writer.writerow(['pin', 'name', 'type', 'side'])
            
            # Filter out pins that don't exist on the 343-pin package
            valid_pins = [p for p in pins_data if p['pin'] != '-']
            
            # Write Pin Rows
            for p in valid_pins:
                # If a pin has no names (e.g. NC or power pins structured differently), give it a generic name
                name_field = '/'.join(p['names']) if p['names'] else f"PIN_{p['pin']}"
                writer.writerow([
                    p['pin'],
                    name_field,
                    p['type'],
                    p['side']
                ])
                
        print(f"Successfully wrote {len(valid_pins)} pins to {output_csv}")
        
    except Exception as e:
        print(f"Error writing to CSV: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python html_to_csv.py <input.html> <output.csv>")
        sys.exit(1)
        
    parse_html_to_csv(sys.argv[1], sys.argv[2])

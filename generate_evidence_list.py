import json
import os
import re

# Paths
SOURCE_FILE = r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\exports\migracion_20260129_124821\evidencias_source.json'
OUTPUT_FILE = r'C:\Users\regil.batista\.gemini\antigravity\brain\abee3a5e-f22b-4d0a-8e70-4bca4f839e1f\renamed_evidences.md'

def natural_sort_key(s):
    """Sorts strings that contain numbers naturally."""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def main():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: Source file not found at {SOURCE_FILE}")
        return

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    valid_entries = []
    inconsistencies = []

    print(f"Processing {len(data)} entries...")

    for entry in data:
        code = entry.get('Codigo')
        name = entry.get('NombreArchivo')
        
        if not code or not name:
            inconsistencies.append(f"Missing Code or Name: ID={entry.get('EvidenciaID')} Data={entry}")
            continue

        # Clean whitespace
        code = code.strip()
        name = name.strip()
        
        # Check code format (heuristic: digits.digits...)
        # User confirmed Np/Ns are valid, so we adjust regex to allow them or just check for weird chars
        if not re.match(r'^[\w\d\.\s]+$', code):
             inconsistencies.append(f"Suspicious Code format: {code} (ID: {entry.get('EvidenciaID')})")

        # Create standardized name
        new_name = f"{code} {name}"
        
        # Parse code for sorting
        # Remove 'Np', 'Ns' prefixes if they exist for sorting, or handle them?
        # User said "Mantén los puntos decimales".
        # Example: "01.1.1".
        # Some codes in file: "Np 07.1.9". "Ns 07.1.9".
        # We need to handle these prefixes in sorting, or just sort strings naturally.
        
        valid_entries.append({
            'code': code,
            'name': name,
            'full_str': new_name
        })

    # Sort
    # We sort by the code mostly.
    valid_entries.sort(key=lambda x: natural_sort_key(x['code']))

    # Generate Report
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Listado de Evidencias Renombradas y Organizadas\n\n")
        
        if inconsistencies:
            f.write("## ⚠️ Inconsistencias Detectadas\n")
            for inc in inconsistencies:
                f.write(f"- {inc}\n")
            f.write("\n---\n\n")
        
        f.write("## Listado Oficial\n\n")
        f.write("```text\n")
        for item in valid_entries:
            f.write(f"{item['full_str']}\n")
        f.write("```\n")

    print(f"Generated list with {len(valid_entries)} entries. Found {len(inconsistencies)} inconsistencies.")

if __name__ == '__main__':
    main()

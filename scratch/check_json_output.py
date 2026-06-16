import json

json_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\extracted_raw_tables.json"

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total entries in JSON: {len(data)}")
for idx, entry in enumerate(data):
    print(f"Entry {idx+1}: Page {entry.get('page')}")
    print(f"  Ámbito: {entry.get('ambito')}")
    print(f"  Indicador: {entry.get('indicador')}")
    print(f"  Subindicador: {entry.get('subindicador')}")
    items = entry.get('items', [])
    print(f"  Items count: {len(items)}")
    # Print first item
    if items:
        print(f"    First item raw evidence: {items[0].get('evidence_raw')}")
        print(f"    First item criterion: {items[0].get('criterion')}")

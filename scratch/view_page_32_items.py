import json

json_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\extracted_raw_tables.json"

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for entry in data:
    if entry.get("page") == 32:
        print("Page 32 items:")
        for idx, item in enumerate(entry.get("items", [])):
            print(f"  Item {idx+1}:")
            print(f"    Raw Evidence: {repr(item.get('evidence_raw'))}")
            print(f"    Criterion: {repr(item.get('criterion'))}")

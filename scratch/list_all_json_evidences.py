import json

json_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\exports\migracion_20260129_124821\evidencias_source.json"

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Sort by code
data.sort(key=lambda x: x.get("Codigo", ""))

output_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\all_evidences_json.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    for item in data:
        f.write(f"ID: {item.get('EvidenciaID')} | Code: {item.get('Codigo')} | Name: {item.get('NombreArchivo')}\n")

print(f"Wrote {len(data)} items to all_evidences_json.txt")

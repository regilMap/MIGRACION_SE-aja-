import json

json_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\exports\migracion_20260129_124821\evidencias_source.json"

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Searching for PEC or Proyecto Educativo:")
count = 0
for item in data:
    name = item.get("NombreArchivo", "")
    code = item.get("Codigo", "")
    criterio = item.get("Criterio", "")
    if "proyecto" in name.lower() or "pec" in name.lower() or "proyecto" in str(criterio).lower() or "pec" in str(criterio).lower():
        print(f"ID: {item.get('EvidenciaID')}, Code: {code}, Name: {name}")
        print(f"  Criterio: {criterio}")
        count += 1
        if count > 10:
            break

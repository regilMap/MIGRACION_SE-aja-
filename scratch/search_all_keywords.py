import json

json_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\exports\migracion_20260129_124821\evidencias_source.json"

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

keywords = ["consolidado", "diagnóstica", "seguimiento", "marzo", "diciembre", "junio"]

print("Searching database evidences by keywords:")
found_codes = set()
for item in data:
    name = item.get("NombreArchivo", "") or ""
    criterio = item.get("Criterio", "") or ""
    code = item.get("Codigo", "") or ""
    
    match = False
    for kw in keywords:
        if kw.lower() in name.lower() or kw.lower() in criterio.lower():
            match = True
            break
            
    if match:
        print(f"ID: {item.get('EvidenciaID')} | Code: {code} | Name: {name}")
        print(f"  Criterio: {criterio.strip()}")
        found_codes.add(code)

print(f"\nTotal unique matching codes: {len(found_codes)}")

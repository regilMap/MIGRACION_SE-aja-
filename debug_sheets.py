import pandas as pd
import json

file_path = "MINERD- LISTA DE TECNICOS  SISMAP EDUCACION- actualizado 5-3-2026.xlsx"
sheets = ["PUNTUADOR- COOR EJE", "VEEDOR- TECNICO REGIONAL SISMAP"]
results = {}

for s in sheets:
    try:
        df = pd.read_excel(file_path, sheet_name=s, header=None, nrows=15)
        rows = []
        for i, row in df.iterrows():
            rows.append([str(v).strip() for v in row.fillna("")])
        results[s] = rows
    except Exception as e:
        results[s] = str(e)

with open("debug_rows.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

import pandas as pd
import json

file_path = "MINERD- LISTA DE TECNICOS  SISMAP EDUCACION- actualizado 5-3-2026.xlsx"
xl = pd.ExcelFile(file_path)

data = {"sheets": xl.sheet_names, "samples": {}}
for sheet in xl.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)
    data["samples"][sheet] = df.head(0).columns.tolist()

with open("inspect_excel.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

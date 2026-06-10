import pandas as pd

file_path = "Centros modalidad  Primario - Secundario.xlsx"
xl = pd.ExcelFile(file_path)

for sheet in xl.sheet_names:
    df = xl.parse(sheet, header=None)
    print(f"\nSheet '{sheet}': rows={df.shape[0]}, cols={df.shape[1]}")
    for idx, row in df.iterrows():
        # Look for headers containing CODIGO or SIGERD or INSTANCIA
        vals = [str(x).strip().upper() for x in row.fillna("").tolist()]
        if any("SIGERD" in v or "INSTANCIA" in v for v in vals):
            print(f"  Header found at row {idx}: {row.tolist()}")
            break

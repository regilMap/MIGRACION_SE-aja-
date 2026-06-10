import pandas as pd

file_path = "Centros modalidad  Primario - Secundario.xlsx"
xl = pd.ExcelFile(file_path)

for sheet in ['Verificación', 'Organizado por ejes']:
    df = xl.parse(sheet, header=None)
    print(f"\n================ SHEET '{sheet}' FIRST 10 ROWS ================")
    for idx in range(min(10, len(df))):
        print(f"Row {idx}: {df.iloc[idx].tolist()}")

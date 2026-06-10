import pandas as pd

file_path = "Centros modalidad  Primario - Secundario.xlsx"

try:
    xl = pd.ExcelFile(file_path)
    for sheet in ['Matriz', 'Verificación', 'Matriz (2)']:
        df = xl.parse(sheet, nrows=20)
        print(f"\n================ SHEET '{sheet}' FIRST 20 ROWS ================")
        print(df.to_string())
except Exception as e:
    print(f"Error: {e}")

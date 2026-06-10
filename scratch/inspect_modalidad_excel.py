import pandas as pd
import openpyxl

file_path = "Centros modalidad  Primario - Secundario.xlsx"

try:
    xl = pd.ExcelFile(file_path)
    print("Sheet names:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = xl.parse(sheet, nrows=5)
        print(f"\nSheet '{sheet}' head:")
        print(df.to_string())
except Exception as e:
    print(f"Error: {e}")

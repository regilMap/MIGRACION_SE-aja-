import pandas as pd

file_path = "Centros modalidad  Primario - Secundario.xlsx"
xl = pd.ExcelFile(file_path)

for sheet in xl.sheet_names:
    df = xl.parse(sheet)
    print(f"\nSheet '{sheet}': shape={df.shape}")
    # print first non-null values to locate where table headers are
    non_null_rows = df.dropna(how='all')
    print(f"Non-null rows count: {len(non_null_rows)}")
    # Print the first 15 non-null rows
    print(non_null_rows.head(15).to_string())

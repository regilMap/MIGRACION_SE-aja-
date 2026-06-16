import pandas as pd

file_path = "Centros modalidad  Primario - Secundario.xlsx"
xl = pd.ExcelFile(file_path)
print("Sheet names:", xl.sheet_names)

for sheet in xl.sheet_names:
    print(f"\n================ SHEET: {sheet} ================")
    df = xl.parse(sheet, header=None)
    print("Shape:", df.shape)
    # Find rows that might contain the header (looking for CODIGO SIGERD or similar)
    for idx, row in df.head(15).iterrows():
        row_vals = [str(x).strip() for x in row.fillna("").tolist()]
        # Check if "CODIGO SIGERD" or similar is in row_vals
        matched = [v for v in row_vals if "SIGERD" in v.upper() or "CÓDIGO" in v.upper() or "CODIGO" in v.upper()]
        if matched:
            print(f"Row {idx} looks like a header: {row_vals}")
    # Show first few data rows
    print("First 5 rows (raw):")
    print(df.head(12).to_string())

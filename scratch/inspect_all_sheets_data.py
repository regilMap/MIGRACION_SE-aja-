import pandas as pd
import re

file_path = "Centros modalidad  Primario - Secundario.xlsx"
xl = pd.ExcelFile(file_path)

for sheet in xl.sheet_names:
    df = xl.parse(sheet, header=None)
    print(f"\n================ SHEET: {sheet} (Shape: {df.shape}) ================")
    
    # We will search each cell for keywords
    keywords = ["PRIMARIO", "SECUNDARIO", "INICIAL", "POLITÉCNICO", "POLITECNICO", "SECUNDARIA"]
    found_cols = set()
    for col in df.columns:
        col_series = df[col].astype(str).str.upper()
        for kw in keywords:
            matches = col_series[col_series.str.contains(kw, na=False, regex=False)]
            if len(matches) > 0:
                found_cols.add(col)
                print(f"  Col {col} has {len(matches)} matches for '{kw}'")
                
    if found_cols:
        # Show sample rows for columns that contain the keywords
        print("  Sample rows for matching columns:")
        # Let's find first 10 rows where any of the found_cols has one of the keywords
        matched_rows = []
        for idx, row in df.iterrows():
            row_str = [str(val).upper() for val in row.fillna("").tolist()]
            has_kw = False
            for col in found_cols:
                val = row_str[col]
                if any(kw in val for kw in keywords):
                    has_kw = True
                    break
            if has_kw:
                matched_rows.append(idx)
                if len(matched_rows) >= 5:
                    break
        for idx in matched_rows:
            print(f"    Row {idx}: {df.iloc[idx].tolist()[:10]}")

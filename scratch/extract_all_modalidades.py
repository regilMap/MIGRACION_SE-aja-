import pandas as pd
import re

file_path = "Centros modalidad  Primario - Secundario.xlsx"
xl = pd.ExcelFile(file_path)

def clean_code(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s.endswith('.0'):
        s = s[:-2]
    s = re.sub(r'\D', '', s)
    if s:
        return s.zfill(5)
    return None

df = xl.parse("Matriz (2)", header=None)
print("Matriz (2) Shape:", df.shape)

# Let's inspect rows around the header (row 9)
for r in range(7, 13):
    print(f"Row {r}: {df.iloc[r].tolist()}")

# Extract from first table (cols 2 & 3) and second table (cols 7 & 8)
centers_data = []

# Table 1: rows 10 to end, cols 2 & 3 (and 1 for name)
for r in range(10, len(df)):
    c1_code = clean_code(df.iloc[r, 2])
    c1_nivel = str(df.iloc[r, 3]).strip()
    c1_name = str(df.iloc[r, 1]).strip()
    if c1_code:
        centers_data.append({'code': c1_code, 'name': c1_name, 'nivel': c1_nivel, 'source': 'T1'})
        
    c2_code = clean_code(df.iloc[r, 7])
    c2_nivel = str(df.iloc[r, 8]).strip()
    c2_name = str(df.iloc[r, 6]).strip()
    if c2_code:
        centers_data.append({'code': c2_code, 'name': c2_name, 'nivel': c2_nivel, 'source': 'T2'})

centers_df = pd.DataFrame(centers_data)
print(f"\nTotal extracted centers from 'Matriz (2)': {len(centers_df)}")
print("Unique codes count:", centers_df['code'].nunique())
print("Value counts of 'nivel':")
print(centers_df['nivel'].value_counts())

# Let's check duplicates
dupes = centers_df[centers_df.duplicated(subset=['code'], keep=False)]
print(f"\nDuplicate codes count in Excel: {len(dupes['code'].unique())}")
if not dupes.empty:
    print("Sample duplicate codes:")
    print(dupes.sort_values('code').head(10))

import pandas as pd

file_path = "MINERD- LISTA DE TECNICOS  SISMAP EDUCACION- actualizado 5-3-2026.xlsx"
sheet_name = "REVISOR - TEC- DISTRITAL"
skip_rows = 5

df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip_rows)
df.columns = df.columns.str.strip()
name_col = "TECNICO DISTRITAL"

print("Columns:", df.columns.tolist())
print(f"Total rows before dropna: {len(df)}")
df = df.dropna(subset=[name_col])
print(f"Total rows after dropna: {len(df)}")
for i, row in df.head(5).iterrows():
    name = str(row[name_col]).strip()
    print(f"Row {i}: Name='{name}', lower='{name.lower()}'")

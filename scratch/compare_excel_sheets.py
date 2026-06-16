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

# Load Matriz
df_matriz = xl.parse("Matriz", skiprows=6)
df_matriz.columns = [str(c).strip() for c in df_matriz.columns]
matriz_codes = {}
for idx, r in df_matriz.iterrows():
    code = clean_code(r.get('CODIGO SIGERD'))
    if code:
        nivel = str(r.get('NIVEL')).strip()
        name = str(r.get('NOMBRE DE LA INSTANCIA')).strip()
        matriz_codes[code] = {'nivel': nivel, 'name': name, 'row': idx + 7}

# Load Matriz (2)
df_m2 = xl.parse("Matriz (2)", header=None)
m2_codes = {}
# Table 1: cols 2 & 3
for r in range(10, len(df_m2)):
    code = clean_code(df_m2.iloc[r, 2])
    if code:
        nivel = str(df_m2.iloc[r, 3]).strip()
        name = str(df_m2.iloc[r, 1]).strip()
        m2_codes[code] = {'nivel': nivel, 'name': name, 'source': 'T1'}
# Table 2: cols 7 & 8
for r in range(10, len(df_m2)):
    code = clean_code(df_m2.iloc[r, 7])
    if code:
        nivel = str(df_m2.iloc[r, 8]).strip()
        name = str(df_m2.iloc[r, 6]).strip()
        m2_codes[code] = {'nivel': nivel, 'name': name, 'source': 'T2'}

print(f"Total codes in Matriz sheet: {len(matriz_codes)}")
print(f"Total codes in Matriz (2) sheet: {len(m2_codes)}")

matriz_set = set(matriz_codes.keys())
m2_set = set(m2_codes.keys())

print(f"Overlap: {len(matriz_set.intersection(m2_set))}")
print(f"In Matriz but not in Matriz (2): {len(matriz_set - m2_set)}")
print(f"In Matriz (2) but not in Matriz: {len(m2_set - matriz_set)}")

# Let's inspect some that are in Matriz but not in Matriz (2)
not_in_m2 = list(matriz_set - m2_set)
print("\nSamples in Matriz but not in Matriz (2):")
for c in not_in_m2[:10]:
    print(f"Code: {c} | Name: {matriz_codes[c]['name']} | Nivel in Matriz: {matriz_codes[c]['nivel']}")

# Check levels in Matriz for those NOT in Matriz (2)
levels_for_missing = {}
for c in not_in_m2:
    lvl = matriz_codes[c]['nivel']
    levels_for_missing[lvl] = levels_for_missing.get(lvl, 0) + 1
print("\nNivel distribution for codes in Matriz but not in Matriz (2):")
for lvl, count in levels_for_missing.items():
    print(f"  {lvl}: {count}")

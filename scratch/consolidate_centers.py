import pandas as pd
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

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

# Map to store: code -> set of level strings
code_levels = {}
# Map to store: code -> set of names
code_names = {}

# Helper to add a record
def add_record(code, name, nivel):
    code = clean_code(code)
    if not code:
        return
    nivel_str = str(nivel).strip()
    if nivel_str.lower() in ['nan', 'null', '']:
        nivel_str = ''
    name_str = str(name).strip()
    
    if code not in code_levels:
        code_levels[code] = set()
        code_names[code] = set()
    if nivel_str:
        code_levels[code].add(nivel_str)
    if name_str:
        code_names[code].add(name_str)

# Parse Matriz
df_matriz = xl.parse("Matriz", skiprows=6)
for idx, r in df_matriz.iterrows():
    add_record(r.get('CODIGO SIGERD'), r.get('NOMBRE DE LA INSTANCIA'), r.get('NIVEL'))

# Parse Matriz (2)
df_m2 = xl.parse("Matriz (2)", header=None)
for r in range(10, len(df_m2)):
    add_record(df_m2.iloc[r, 2], df_m2.iloc[r, 1], df_m2.iloc[r, 3])
    add_record(df_m2.iloc[r, 7], df_m2.iloc[r, 6], df_m2.iloc[r, 8])

# Parse Verificación
df_ver = xl.parse("Verificación", header=None)
# Find header row
v_hdr_row = 24 # from inspect
for r in range(v_hdr_row + 1, len(df_ver)):
    add_record(df_ver.iloc[r, 2], df_ver.iloc[r, 1], df_ver.iloc[r, 6]) # col 6 has some text, but col 1 is name, col 2 is SIGERD

# Parse Organizado por ejes
df_org = xl.parse("Organizado por ejes", header=None)
for r in range(11, len(df_org)):
    add_record(df_org.iloc[r, 2], df_org.iloc[r, 1], df_org.iloc[r, 15] if df_org.shape[1] > 15 else '')

print(f"Total consolidated codes: {len(code_levels)}")

# Connect to database and retrieve the CoedomId map
conn = conectar_destino()
if not conn:
    print("Could not connect to database")
    sys.exit(1)

cursor = conn.cursor()

# Get all organisms from view
cursor.execute("SELECT OrganismoID, Codigo_Minerd, Nombre FROM dbo.vOrganismosEducacionX")
db_orgs = cursor.fetchall()
# Map: MinerdCode -> (OrganismoID, Nombre)
db_map = {}
for org in db_orgs:
    c = clean_code(org[1])
    if c:
        db_map[c] = (org[0], org[2])

# Map using SigerdCoedom as fallback
cursor.execute("SELECT CODIGO_MINERD, CODIGO_COEDOM, CENTRO FROM dbo.SigerdCoedom")
sc_rows = cursor.fetchall()
sc_map = {}
for r in sc_rows:
    c = clean_code(r[0])
    if c and r[1]:
        sc_map[c] = (int(r[1]), r[2])

print(f"vOrganismosEducacionX unique codes: {len(db_map)}")
print(f"SigerdCoedom unique codes: {len(sc_map)}")

mapped_count = 0
unmapped_codes = []
resolved_centers = []

# Nivel categorization logic
def categorize_level(lvls):
    # lvls is a set of level strings for a code
    if not lvls:
        return 'UNKNOWN'
    
    # Check if there is any string indicating both levels
    both_keywords = ['PRIMARIO - SECUNDARIO', 'PRIMARIO / SECUNDARIO', 'INICIAL / PRIMARIO / SECUNDARIO', 'INICIAL/PRIMARIA/ SECUNDARIA', 'INICIAL/PRIMARIA/SECUNDARIA']
    for lvl in lvls:
        lvl_u = lvl.upper()
        if any(bk in lvl_u for bk in both_keywords):
            return 'BOTH'
            
    # Check if it has both a primary-like and secondary-like string in the set
    has_prim = False
    has_sec = False
    for lvl in lvls:
        lvl_u = lvl.upper()
        if 'SECUNDARIO' in lvl_u or 'SECUNDARIA' in lvl_u or 'POLITÉCNICO' in lvl_u or 'POLITECNICO' in lvl_u:
            has_sec = True
        if 'PRIMARIO' in lvl_u or 'PRIMARIA' in lvl_u:
            has_prim = True
            
    if has_prim and has_sec:
        return 'BOTH'
    elif has_sec:
        return 'SECUNDARIO_ONLY'
    elif has_prim:
        return 'PRIMARIO_ONLY'
    
    return 'UNKNOWN'

level_stats = {'PRIMARIO_ONLY': 0, 'SECUNDARIO_ONLY': 0, 'BOTH': 0, 'UNKNOWN': 0}

for code, lvls in code_levels.items():
    cat = categorize_level(lvls)
    level_stats[cat] += 1
    
    # Map to DB CoedomId
    coedom_id = None
    db_name = ""
    source = ""
    if code in db_map:
        coedom_id, db_name = db_map[code]
        source = "vOrganismosEducacionX"
    elif code in sc_map:
        coedom_id, db_name = sc_map[code]
        source = "SigerdCoedom"
        
    if coedom_id:
        mapped_count += 1
        resolved_centers.append({
            'code': code,
            'name': list(code_names[code])[0] if code_names[code] else db_name,
            'coedom_id': coedom_id,
            'nivel_cat': cat,
            'excel_levels': list(lvls)
        })
    else:
        unmapped_codes.append(code)

print("\n=== LEVEL CATEGORIZATION STATS (ALL EXCEL CODES) ===")
print(level_stats)

print(f"\nTotal mapped to DB CoedomId: {mapped_count} / {len(code_levels)}")
print(f"Total unmapped: {len(unmapped_codes)}")

# Let's count resolved centers per level category
resolved_stats = {'PRIMARIO_ONLY': 0, 'SECUNDARIO_ONLY': 0, 'BOTH': 0, 'UNKNOWN': 0}
for rc in resolved_centers:
    resolved_stats[rc['nivel_cat']] += 1
print("\n=== RESOLVED CENTERS BY LEVEL CATEGORY ===")
print(resolved_stats)

conn.close()

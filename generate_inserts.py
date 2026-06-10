import pandas as pd
import uuid
import re

try:
    from config.database import conectar_destino
    conn = conectar_destino()
    cursor = conn.cursor()
    cursor.execute("SELECT OrganismoID, Nombre, REGIONAL, DISTRITO, Codigo_Minerd FROM SISMAP_EDUCACION_M2.dbo.vOrganismosEducacionX WHERE OrganismoID IS NOT NULL")
    organismos = cursor.fetchall()
    
    org_dict = {}
    code_dict = {}
    for org in organismos:
        coedom_id = int(org[0])
        nombre = org[1].strip().upper() if org[1] else ""
        regional = org[2].strip().upper() if org[2] else ""
        distrito = org[3].strip().upper() if org[3] else ""
        codigo = org[4].strip().upper() if org[4] else ""
        
        if nombre: org_dict[nombre] = coedom_id
        if regional: org_dict[regional] = coedom_id
        if distrito: org_dict[distrito] = coedom_id
        if codigo: 
            c = re.sub(r'[^0-9]', '', codigo)
            if c:
                code_dict[c] = (nombre, coedom_id)
        
    print(f"-- Loaded {len(org_dict)} names and {len(code_dict)} codes from DB.")
except Exception as e:
    print(f"-- Error connecting to DB: {e}")
    org_dict = {}
    code_dict = {}

def clean_org_name(name):
    if pd.isna(name) or str(name).strip() == "": return ""
    return re.sub(r'[^A-ZM0-9]', '', str(name).upper())

org_dict_clean = {clean_org_name(k): (k, v) for k, v in org_dict.items()}

def find_coedom(query_name, is_fixed=False):
    if is_fixed:
        return 98, "Fixed (98)"
    if pd.isna(query_name) or str(query_name).strip() == "":
        return None, "No name provided"
        
    cname = clean_org_name(query_name)
    
    nums = re.findall(r'\d+', cname)
    if nums:
        code = nums[0]
        if len(code) == 3: code = "0" + code 
        
        # Manual overrides for district edge cases provided by user
        overrides = {
            "1801": "NEIBA",
            "1201": "HIGUEY",
            "0705": "MACORISSURE",
            "0706": "MACORISNORO",
            "0807": "VILLABISONO",
            "1101": "SOSUA"
        }
        if code in overrides:
            cname = overrides[code]

    if cname in org_dict_clean:
        return org_dict_clean[cname][1], org_dict_clean[cname][0]
        
    for k, v in org_dict_clean.items():
        if cname in k or k in cname:
            return v[1], v[0]
            
    if nums:
        code = nums[0]
        if len(code) == 3: code = "0" + code
        if code in code_dict:
            return code_dict[code][1], code_dict[code][0]

    return None, f"Not found: {query_name}"

file_path = "MINERD- LISTA DE TECNICOS  SISMAP EDUCACION- actualizado 5-3-2026.xlsx"
sql_inserts = []
comments = []
unmatched = []

def process_sheet(sheet_name, rol_id, fixed_coedom, name_col, email_col, org_col=None):
    try:
        df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        header_idx = -1
        for i in range(min(200, len(df_raw))):
            row_vals = df_raw.iloc[i].fillna("").astype(str).str.strip().str.upper().tolist()
            if any(name_col.upper() in val for val in row_vals):
                header_idx = i
                break
                
        if header_idx == -1:
            return
            
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=header_idx+1, header=None)
        # Find exact header names in the identified row
        df.columns = df_raw.iloc[header_idx].fillna("").astype(str).str.strip()
        
        # Search for name_col inside columns (handling variations like "Nombres y apellidos")
        actual_name_col = None
        for col in df.columns:
            if name_col.upper() in str(col).upper():
                actual_name_col = col
                break
        
        if not actual_name_col:
            return
            
        for _, row in df.iterrows():
            name = str(row[actual_name_col]).strip()
            if not name or name.lower() in ['nan', 'nombre y apellido', 'nombres y apellidos', 'revisor tecnico nacional', 'tecnico distrital', 'no.']:
                continue

                
            # Remove "Sr.", "Sra.", "Sr", "Sra" prefixes
            name = re.sub(r'^(Sr\.|Sra\.|Sr|Sra)\s+', '', name, flags=re.IGNORECASE).strip()

                
            email_val = row[email_col] if email_col in df.columns else None
            email = str(email_val).strip() if pd.notna(email_val) and str(email_val).strip() != "" else f"{name.replace(' ', '.').lower()}@minerd.gob.do"
            if email.lower() in ['nan', 'none']:
                email = f"{name.replace(' ', '.').lower()}@minerd.gob.do"
                
            org_val = ""
            if org_col and org_col in df.columns:
                val = row[org_col]
                org_val = str(val).strip() if pd.notna(val) else ""
            
            coedom, match_info = find_coedom(org_val, is_fixed=fixed_coedom)
            
            if coedom is None:
                unmatched.append(f"{sheet_name} | {name} | Org: {org_val}")
                continue
                
            comments.append(f"-- MATCH: '{org_val}' -> {match_info} (CoedomId: {coedom})")
            
            parts = name.split(' ', 1)
            first_name = parts[0].replace("'", "''")
            last_name = parts[1].replace("'", "''") if len(parts) > 1 else ""
            
            user_id = str(uuid.uuid4())
            clave_id = str(uuid.uuid4())
            clave_hash = "$2b$10$hXEa0XLQk.RrY99QXa0GpO.yL1YxRRmUYm/VvBJzj5G2TpfBsJLlW"
            
            sql_inserts.append(f"INSERT INTO Usuario.UsuarioClaves (Id, ClaveHasheada, CambioClave, CreatedAt, IsActive, IsDeleted) VALUES ('{clave_id}', '{clave_hash}', 0, GETDATE(), 1, 0);")
            sql_inserts.append(f"INSERT INTO Usuario.Usuarios (Id, Nombre, Apellido, Genero, Telefono, Direccion, Correo, ClaveId, CargoId, RolId, CoedomId, CreatedAt, CreatedBy, IsActive, IsDeleted) VALUES ('{user_id}', '{first_name}', '{last_name}', 0, '+18000000000', 'n/a', '{email}', '{clave_id}', 1, {rol_id}, {coedom}, GETDATE(), 'MigrationScript', 1, 0);")
    except Exception as e:
        print(f"-- Failed to process {sheet_name}: {e}")

process_sheet("REVISOR - TEC- DISTRITAL", 4, False, name_col="TECNICO DISTRITAL", email_col="CORREO", org_col="DISTRITO EDUCATIVO")
process_sheet("REVISOR- TECNICO NACIONAL ", 4, True, name_col="NOMBRE Y APELLIDO", email_col="CORREO")
process_sheet("PUNTUADOR- COOR EJE", 2, True, name_col="NOMBRES Y APELLIDOS", email_col="CORREO")
process_sheet("EQUIPO SEGUIMIENTO SISMAP EDUC", 3, True, name_col="NOMBRE Y APELLIDO", email_col="CORREO")
process_sheet("VEEDOR- TECNICO REGIONAL SISMAP", 8, False, name_col="NOMBRE Y APELLIDO", email_col="CORREO", org_col="REGIONAL EDUCATIVA")

with open("output_inserts.sql", "w", encoding="utf-8") as f:
    f.write("-- =======================================================\n")
    f.write("-- MATCHES ENCONTRADOS\n")
    f.write("-- =======================================================\n")
    for c in sorted(list(set(comments))):
        f.write(c + "\n")
    f.write("\n-- =======================================================\n")
    f.write("-- INSERTS DE USUARIOS\n")
    f.write("-- =======================================================\n")
    f.write("\n".join(sql_inserts))

with open("unmatched_users.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(unmatched))

print("Done. Created output_inserts.sql and unmatched_users.txt")

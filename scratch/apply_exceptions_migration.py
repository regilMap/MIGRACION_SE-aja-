import sys
import os
import re
import uuid
import datetime
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

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

def categorize_level(lvls):
    if not lvls:
        return 'UNKNOWN'
    
    both_keywords = ['PRIMARIO - SECUNDARIO', 'PRIMARIO / SECUNDARIO', 'INICIAL / PRIMARIO / SECUNDARIO', 'INICIAL/PRIMARIA/ SECUNDARIA', 'INICIAL/PRIMARIA/SECUNDARIA']
    for lvl in lvls:
        lvl_u = lvl.upper()
        if any(bk in lvl_u for bk in both_keywords):
            return 'BOTH'
            
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

def main():
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--run':
        dry_run = False

    print("==================================================")
    print("      SISMAP EDUCACION - MIGRACION EXCEPCIONES    ")
    print(f"      MODO: {'DRY RUN (PRUEBA - NO COMMIT)' if dry_run else 'REAL (APLICAR CAMBIOS)'}")
    print("==================================================")

    # 1. Read PDF file
    pdf_filename = "Circular Inactivación de Indicadores del SISMAP Educación.pdf"
    if not os.path.exists(pdf_filename):
        print(f"Error: No se encontró el archivo PDF '{pdf_filename}'")
        return
        
    with open(pdf_filename, 'rb') as f:
        pdf_bytes = f.read()
    print(f"[OK] Leído archivo PDF: {pdf_filename} ({len(pdf_bytes)} bytes)")

    # 2. Read and consolidate Excel data
    excel_filename = "Centros modalidad  Primario - Secundario.xlsx"
    if not os.path.exists(excel_filename):
        print(f"Error: No se encontró el archivo Excel '{excel_filename}'")
        return
        
    xl = pd.ExcelFile(excel_filename)
    code_levels = {}
    code_names = {}
    
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
    v_hdr_row = 24
    for r in range(v_hdr_row + 1, len(df_ver)):
        add_record(df_ver.iloc[r, 2], df_ver.iloc[r, 1], df_ver.iloc[r, 6])

    # Parse Organizado por ejes
    df_org = xl.parse("Organizado por ejes", header=None)
    for r in range(11, len(df_org)):
        add_record(df_org.iloc[r, 2], df_org.iloc[r, 1], df_org.iloc[r, 15] if df_org.shape[1] > 15 else '')

    print(f"[OK] Excel consolidado: {len(code_levels)} códigos únicos.")

    # 3. Connect to DB and fetch mapping and targets
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino.")
        return
        
    cursor = conn.cursor()
    
    try:
        # Get all organisms from view
        cursor.execute("SELECT OrganismoID, Codigo_Minerd, Nombre FROM dbo.vOrganismosEducacionX")
        db_map = {}
        for org in cursor.fetchall():
            c = clean_code(org[1])
            if c:
                db_map[c] = (org[0], org[2])
                
        # Fallback from SigerdCoedom
        cursor.execute("SELECT CODIGO_MINERD, CODIGO_COEDOM, CENTRO FROM dbo.SigerdCoedom")
        sc_map = {}
        for r in cursor.fetchall():
            c = clean_code(r[0])
            if c and r[1]:
                sc_map[c] = (int(r[1]), r[2])
                
        print(f"[DB] Códigos mapeados en vOrganismosEducacionX: {len(db_map)}")
        print(f"[DB] Códigos mapeados en SigerdCoedom: {len(sc_map)}")

        # 4. Resolve CoedomId and Nivel Category
        resolved_centers = []
        unmapped_count = 0
        
        for code, lvls in code_levels.items():
            cat = categorize_level(lvls)
            
            # Map using view or fallback
            coedom_id = None
            db_name = ""
            if code in db_map:
                coedom_id, db_name = db_map[code]
            elif code in sc_map:
                coedom_id, db_name = sc_map[code]
                
            if coedom_id:
                name = list(code_names[code])[0] if code_names[code] else db_name
                resolved_centers.append({
                    'code': code,
                    'name': name,
                    'coedom_id': coedom_id,
                    'nivel_cat': cat
                })
            else:
                unmapped_count += 1

        print(f"[DB] Centros mapeados exitosamente: {len(resolved_centers)}")
        print(f"[DB] Centros no mapeados: {unmapped_count}")

        # Count levels
        resolved_stats = {'PRIMARIO_ONLY': 0, 'SECUNDARIO_ONLY': 0, 'BOTH': 0, 'UNKNOWN': 0}
        for rc in resolved_centers:
            resolved_stats[rc['nivel_cat']] += 1
        print(f"[DB] Distribución de centros mapeados: {resolved_stats}")

        # 5. Insert Evidence file
        # We will insert it once
        # Parameters
        now = datetime.datetime.now()
        user_config_id = '4011D474-7472-4FC4-9EE0-0C9B23AF1B17'
        created_by = 'migracion'
        
        # Insert statement for Evidencia.Archivos
        # CoedomId: 25269 (as per user screenshot sample)
        # SubIndicadorEvidenciaId: 20 (corresponding to Np 7.01)
        # EstadoArchivoId: 3 (Puntuado)
        # TipoAlmacenamiento: 1 (stored as binary in DB)
        # RowGuid: random UUID
        
        row_guid = str(uuid.uuid4())
        
        insert_archivo_sql = """
            INSERT INTO Evidencia.Archivos (
                CoedomId, SubIndicadorEvidenciaId, NombreOriginal, ArchivoBinario, EstadoArchivoId,
                EvidenciaId, CreatedAt, CreatedBy, IsActive, IsDeleted, RowGuid, TipoAlmacenamiento, RutaExterna
            )
            OUTPUT INSERTED.Id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        print("\n--- PASO 1: Registro del Archivo Evidencia ---")
        if dry_run:
            archivo_id = 999999
            print(f"[DRY-RUN] Insertaría archivo '{pdf_filename}' para CoedomId 25269, SubIndicadorEvidenciaId 20")
            print(f"[DRY-RUN] ID temporal de archivo asignado: {archivo_id}")
        else:
            # Check if it was already inserted to avoid duplication on re-run
            cursor.execute("SELECT Id FROM Evidencia.Archivos WHERE NombreOriginal = ? AND CoedomId = 25269", pdf_filename)
            existing_file = cursor.fetchone()
            if existing_file:
                archivo_id = existing_file[0]
                print(f"[DB] El archivo ya existe con ID: {archivo_id}. Reutilizando.")
            else:
                cursor.execute(
                    insert_archivo_sql,
                    25269, 20, pdf_filename, pyodbc.Binary(pdf_bytes), 3,
                    None, now, created_by, True, False, row_guid, 1, None
                )
                archivo_id = cursor.fetchone()[0]
                print(f"[DB] Archivo insertado exitosamente. ID asignado: {archivo_id}")

        # 6. Generate Exceptions List
        # NP sub-indicators: Np 7.01 (ID: 5)
        # NS sub-indicators: Ns 7.02 (ID: 6), Ns 7.01 (ID: 43)
        # Exceptions logic:
        # - If PRIMARIO_ONLY: NS sub-indicators (6 and 43) DO NOT APPLY -> exception added.
        # - If SECUNDARIO_ONLY: NP sub-indicator (5) DOES NOT APPLY -> exception added.
        
        exceptions_to_insert = []
        for rc in resolved_centers:
            coedom_id = rc['coedom_id']
            nivel_cat = rc['nivel_cat']
            
            if nivel_cat == 'PRIMARIO_ONLY':
                # NS does not apply
                exceptions_to_insert.append((coedom_id, 6)) # Ns 7.02
                exceptions_to_insert.append((coedom_id, 43)) # Ns 7.01
            elif nivel_cat == 'SECUNDARIO_ONLY':
                # NP does not apply
                exceptions_to_insert.append((coedom_id, 5)) # Np 7.01

        print(f"\n--- PASO 2: Generación de Excepciones ---")
        print(f"Total de excepciones a insertar: {len(exceptions_to_insert)}")
        print(f"  - Para centros Primarios (desactivar subindicadores Secundarios 6 y 43): {resolved_stats['PRIMARIO_ONLY'] * 2}")
        print(f"  - Para centros Secundarios (desactivar subindicador Primario 5): {resolved_stats['SECUNDARIO_ONLY']}")

        # 7. Insert Exceptions
        insert_ex_sql = """
            INSERT INTO Mantenimiento.ConfiguracionOrganismoExcepcion (
                CoedomId, TipoEntidadId, EntidadId, Aplica, FechaVencimiento, FechaExtension,
                UsuarioConfiguracionId, FechaConfiguracion, TipoVencimientoId, CreatedAt, CreatedBy,
                IsActive, IsDeleted, ArchivoId
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        print("\n--- PASO 3: Inserción de Excepciones ---")
        inserted_count = 0
        for coedom_id, sub_ind_id in exceptions_to_insert:
            if dry_run:
                inserted_count += 1
            else:
                # To prevent duplicates on re-run, check if the exception already exists
                cursor.execute("""
                    SELECT COUNT(*) FROM Mantenimiento.ConfiguracionOrganismoExcepcion 
                    WHERE CoedomId = ? AND TipoEntidadId = 2 AND EntidadId = ?
                """, coedom_id, sub_ind_id)
                exists = cursor.fetchone()[0]
                if exists > 0:
                    continue
                
                cursor.execute(
                    insert_ex_sql,
                    coedom_id,
                    2, # TipoEntidadId = 2 (SubIndicador)
                    sub_ind_id, # EntidadId = sub_ind_id
                    True, # Aplica = 1 (bit)
                    None, # FechaVencimiento = NULL
                    None, # FechaExtension = NULL
                    user_config_id,
                    now,
                    2, # TipoVencimientoId = 2 (Manual)
                    now,
                    created_by,
                    True,
                    False,
                    archivo_id
                )
                inserted_count += 1

        if dry_run:
            print(f"[DRY-RUN] Se simularía la inserción de {inserted_count} excepciones.")
        else:
            print(f"[DB] Se insertaron {inserted_count} excepciones exitosamente (omitidas las duplicadas).")
            conn.commit()
            print("[DB] Commit realizado exitosamente.")

    except Exception as e:
        print(f"[ERROR] Ocurrió un error en la migración: {e}")
        if not dry_run:
            conn.rollback()
            print("[DB] Rollback realizado debido a error.")
    finally:
        conn.close()

if __name__ == '__main__':
    # Import pyodbc inside since it is required for DB connections
    import pyodbc
    main()

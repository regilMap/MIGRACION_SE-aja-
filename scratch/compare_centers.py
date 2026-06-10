import pandas as pd
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def clean_code(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    # Remove decimal .0 if it's float-like
    if s.endswith('.0'):
        s = s[:-2]
    # Pad with zeros to standard SIGERD length (usually 5 digits, e.g. "02334" or "00681")
    s = re.sub(r'\D', '', s)
    if s:
        return s.zfill(5)
    return None

def main():
    # 1. Load Excel codes
    file_path = "Centros modalidad  Primario - Secundario.xlsx"
    xl = pd.ExcelFile(file_path)
    
    excel_records = []
    # Let's inspect unique codes across the sheets
    for sheet in ['Matriz', 'Matriz (2)', 'Verificación', 'Organizado por ejes']:
        df = xl.parse(sheet, header=None)
        header_row_idx = -1
        # Find header row
        for idx, row in df.iterrows():
            vals = [str(x).strip().upper() for x in row.fillna("").tolist()]
            if any("SIGERD" in v or "INSTANCIA" in v for v in vals):
                header_row_idx = idx
                break
        
        if header_row_idx == -1:
            print(f"No header found in sheet '{sheet}'")
            continue
            
        # Re-load sheet with correct header
        df = xl.parse(sheet, skiprows=header_row_idx + 1)
        
        # Print column names
        cols = df.columns.tolist()
        print(f"Sheet '{sheet}' columns: {cols}")
        
        # Locate the SIGERD column
        sigerd_cols = [c for c in cols if 'SIGERD' in str(c).upper() or 'CODIGO' in str(c).upper()]
        for col in sigerd_cols:
            for idx, val in df[col].items():
                code = clean_code(val)
                if code:
                    excel_records.append({
                        'sheet': sheet,
                        'code': code,
                        'name': str(df.iloc[idx].get('NOMBRE DE LA INSTANCIA', df.iloc[idx].get('NOMBRE DE LA INSTANCIA ', ''))).strip(),
                        'nivel': str(df.iloc[idx].get('NIVEL', '')).strip(),
                    })
                    
    excel_df = pd.DataFrame(excel_records)
    print(f"Total excel records extracted: {len(excel_df)}")
    excel_unique_codes = set(excel_df['code'].unique())
    print(f"Unique excel codes: {len(excel_unique_codes)}")

    # 2. Load DB codes
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino")
        return
        
    cursor = conn.cursor()
    db_records = []
    try:
        cursor.execute("SELECT OrganismoID, Nombre, REGIONAL, DISTRITO, Codigo_Minerd FROM vOrganismosEducacionX")
        for r in cursor.fetchall():
            code = clean_code(r[4])
            db_records.append({
                'id': r[0],
                'name': r[1],
                'regional': r[2],
                'distrito': r[3],
                'code': code
            })
    except Exception as e:
        print(f"Error querying view: {e}")
        conn.close()
        return
    finally:
        conn.close()
        
    db_df = pd.DataFrame(db_records)
    print(f"Total DB records extracted: {len(db_df)}")
    db_unique_codes = set(db_df['code'].dropna().unique())
    print(f"Unique DB codes: {len(db_unique_codes)}")
    
    # 3. Analyze differences
    missing_in_db = excel_unique_codes - db_unique_codes
    missing_in_excel = db_unique_codes - excel_unique_codes
    
    print(f"\nMissing in DB (in Excel but not in vOrganismosEducacionX): {len(missing_in_db)}")
    print(f"Missing in Excel (in vOrganismosEducacionX but not in Excel): {len(missing_in_excel)}")
    
    # Show sample of missing in DB
    print("\nSample missing in DB:")
    sample_missing = excel_df[excel_df['code'].isin(missing_in_db)].drop_duplicates(subset=['code']).head(20)
    print(sample_missing.to_string())
    
    # Show sample of missing in Excel
    print("\nSample missing in Excel:")
    sample_excel = db_df[db_df['code'].isin(missing_in_excel)].head(20)
    print(sample_excel.to_string())

if __name__ == '__main__':
    main()

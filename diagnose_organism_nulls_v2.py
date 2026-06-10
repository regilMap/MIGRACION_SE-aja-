import pyodbc
import sys

# Standalone config
class DatabaseConfig:
    FUENTE = {
        'driver': 'ODBC Driver 17 for SQL Server',
        'server': 'D1491N2023',
        'database': 'SISMAPV1DB_ED',
        'trusted_connection': True
    }

def conectar_fuente():
    cfg = DatabaseConfig.FUENTE
    try:
        conn = pyodbc.connect(
            f"DRIVER={{{cfg['driver']}}};"
            f"SERVER={cfg['server']};"
            f"DATABASE={cfg['database']};"
            "Trusted_Connection=yes;",
            timeout=10
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return None

def diagnose():
    print("Connecting to Source DB (Standalone)...")
    conn = conectar_fuente()
    if not conn:
        return
        
    try:
        cursor = conn.cursor()
        
        print("\n--- Checking CargaEvidencia (Uploads) ---")
        query_upload = """
            SELECT 
                COUNT(*) as Total,
                SUM(CASE WHEN OrganismoID IS NULL THEN 1 ELSE 0 END) as NullOrganismo,
                SUM(CASE WHEN OrganismoID = 0 THEN 1 ELSE 0 END) as ZeroOrganismo
            FROM CargaEvidencia
        """
        cursor.execute(query_upload)
        row = cursor.fetchone()
        print(f"Total Uploads: {row[0]}")
        print(f"NULL Organismo: {row[1]}")
        print(f"0 Organismo:    {row[2]}")
        
        print("\n--- Checking Evidencia (Templates/Definitions) ---")
        # Transformation logic: if item.NombreArchivo and len(item.NombreArchivo) < 85
        # This creates files with CoedomId = 0
        query_template = """
            SELECT COUNT(*) 
            FROM Evidencia 
            WHERE NombreArchivo IS NOT NULL 
            AND LEN(NombreArchivo) < 85
            AND LEN(NombreArchivo) > 0
        """
        cursor.execute(query_template)
        row_template = cursor.fetchone()
        print(f"Potential Template Files (will have CoedomId=0): {row_template[0]}")
        
        if row_template[0] > 0:
            print("These records will be inserted into Evidencias.Archivos with CoedomId = 0 by default.")
            print("Sample Template Filenames:")
            cursor.execute("SELECT TOP 5 NombreArchivo FROM Evidencia WHERE NombreArchivo IS NOT NULL AND LEN(NombreArchivo) < 85 AND LEN(NombreArchivo) > 0")
            for r in cursor.fetchall():
                print(f" - {r[0]}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    diagnose()

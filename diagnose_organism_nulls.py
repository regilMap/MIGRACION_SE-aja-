import pyodbc
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import db_config
except ImportError:
    # Fallback if running directly without package structure
    class Config:
        DB_DRIVER = 'ODBC Driver 17 for SQL Server'
        DB_SERVER = 'localhost' # Adjust or read from env
        # ...
    print("Warning: Could not import config. Please ensure config/db_config.py exists or providing params manually.")
    sys.exit(1)

def diagnose():
    print("Connecting to Source DB...")
    try:
        conn = pyodbc.connect(db_config.get_connection_string_source())
        cursor = conn.cursor()
        
        print("Checking CargaEvidencia for NULL or 0 OrganismoID...")
        
        query = """
            SELECT 
                COUNT(*) as Total,
                SUM(CASE WHEN OrganismoID IS NULL THEN 1 ELSE 0 END) as NullOrganismo,
                SUM(CASE WHEN OrganismoID = 0 THEN 1 ELSE 0 END) as ZeroOrganismo,
                SUM(CASE WHEN OrganismoID IS NOT NULL AND OrganismoID <> 0 THEN 1 ELSE 0 END) as ValidOrganismo
            FROM CargaEvidencia
        """
        
        cursor.execute(query)
        row = cursor.fetchone()
        
        print(f"Total Records: {row[0]}")
        print(f"NULL OrganismoID: {row[1]}")
        print(f"0 OrganismoID:    {row[2]}")
        print(f"Valid OrganismoID: {row[3]}")
        
        if row[1] > 0 or row[2] > 0:
            print("\nSample records with issue:")
            query_sample = """
                SELECT TOP 10 CargaEvidenciaID, IndicadorID, EvidenciaID, OrganismoID, FechaVencimiento
                FROM CargaEvidencia
                WHERE OrganismoID IS NULL OR OrganismoID = 0
            """
            cursor.execute(query_sample)
            print(f"{'ID':<10} {'Indicador':<10} {'Evidencia':<10} {'Organismo':<10} {'FechaVenc'}")
            print("-" * 60)
            for r in cursor.fetchall():
                print(f"{r[0]:<10} {r[1]:<10} {r[2]:<10} {r[3] if r[3] is not None else 'NULL':<10} {r[4]}")
                
        else:
            print("\nNo records found with NULL or 0 OrganismoID in CargaEvidencia.")
            
            # Check if maybe they are talking about Evidencia table based ones
            print("\nChecking logic for Plantillas (Evidencia table sources)...")
            # This is hardcoded in python, so we can't query DB for the result of python transformation directly 
            # unless we run the migration.
            print("Note: In transformation_service.transformar_evidencia, 'Plantilla' files are explicitly created with CoedomId=0.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    diagnose()

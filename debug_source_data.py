
import pyodbc
from config.database import conectar_fuente

def check_data():
    try:
        conn = conectar_fuente()
        if not conn:
            return
        cursor = conn.cursor()
        
        print("Checking Evidencia.NombreArchivo...")
        cursor.execute("SELECT EvidenciaID, NombreArchivo FROM Evidencia WHERE LEN(NombreArchivo) > 90")
        rows = cursor.fetchall()
        for row in rows:
            print(f"EvidenciaID: {row.EvidenciaID}, NombreArchivo: {row.NombreArchivo[:100]}...")
            
        print("\nChecking ArchivoCargaEvidencia.NombreArchivo...")
        cursor.execute("SELECT ArchivoCargaEvidenciaID, NombreArchivo FROM ArchivoCargaEvidencia WHERE LEN(NombreArchivo) > 90")
        rows = cursor.fetchall()
        for row in rows:
            print(f"ACEvidenciaID: {row.ArchivoCargaEvidenciaID}, NombreArchivo: {row.NombreArchivo[:100]}...")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_data()

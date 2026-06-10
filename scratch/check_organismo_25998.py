import sys
import os
sys.path.append(os.getcwd())
from config.database import conectar_fuente

def check_organismo_25998():
    conn = conectar_fuente()
    cursor = conn.cursor()
    
    organismo_id = 25998
    print(f"--- Records for Organismo {organismo_id} in ArchivoCargaEvidencia ---")
    query = """
        SELECT ace.ArchivoCargaEvidenciaID, ace.NombreArchivo, ace.Estado
        FROM ArchivoCargaEvidencia ace
        JOIN CargaEvidencia ce ON ace.CargaEvidenciaID = ce.CargaEvidenciaID
        WHERE ce.OrganismoID = ?
    """
    cursor.execute(query, organismo_id)
    rows = cursor.fetchall()
    for r in rows[:10]:
        print(f"ID: {r[0]} | File: {r[1]} | Estado: {r[2]}")
        
    print(f"\nTotal records for {organismo_id}: {len(rows)}")
    
    conn.close()

if __name__ == "__main__":
    check_organismo_25998()

import sys
import os
sys.path.append(os.getcwd())
from config.database import conectar_fuente

def find_evidence_info():
    conn = conectar_fuente()
    cursor = conn.cursor()
    
    query = """
        SELECT e.EvidenciaID, e.Codigo, e.NombreArchivo 
        FROM Evidencia e 
        JOIN SubIndicadores si ON e.IndicadorID = si.IndicadorID 
        WHERE si.Codigo = '06.4' AND e.Codigo = '06.4.2'
    """
    
    cursor.execute(query)
    row = cursor.fetchone()
    if row:
        print(f"EvidenciaID: {row[0]}, Codigo: {row[1]}, Nombre: {row[2]}")
        
        evidencia_id = row[0]
        organismo_id = 25324
        
        print(f"\n--- Checking files for Organismo {organismo_id} and Evidencia {evidencia_id} ---")
        query_files = """
            SELECT 
                ace.ArchivoCargaEvidenciaID, 
                ace.NombreArchivo, 
                ace.Fecha, 
                ce.FechaVencimiento, 
                ce.ValorActual,
                re.EstadoEnvio
            FROM CargaEvidencia ce
            JOIN ArchivoCargaEvidencia ace ON ce.CargaEvidenciaID = ace.CargaEvidenciaID
            LEFT JOIN RepositorioDeEnvio re ON ace.NombreArchivo = re.Archivo
            WHERE ce.OrganismoID = ? AND ce.EvidenciaID = ?
            ORDER BY ace.Fecha DESC
        """
        cursor.execute(query_files, (organismo_id, evidencia_id))
        rows = cursor.fetchall()
        for r in rows:
            print(f"ID: {r[0]} | File: {r[1]} | Fecha: {r[2]} | Venc: {r[3]} | Val: {r[4]} | State: {r[5]}")
            
    else:
        print("Evidence 06.4.2 not found.")
        
    conn.close()

if __name__ == "__main__":
    find_evidence_info()

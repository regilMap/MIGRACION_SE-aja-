import sys
import os
sys.path.append(os.getcwd())
from config.database import conectar_fuente

def count_031():
    conn = conectar_fuente()
    cursor = conn.cursor()
    
    query = """
        SELECT COUNT(*) 
        FROM CargaEvidencia ce
        JOIN ArchivoCargaEvidencia ace ON ce.CargaEvidenciaID = ace.CargaEvidenciaID
        JOIN SubIndicadores si ON ce.IndicadorID = si.IndicadorID
        JOIN RepositorioDeEnvio re ON ace.NombreArchivo = re.Archivo
        WHERE si.Codigo = '03.1'
        AND ce.FechaVencimiento > '2026-01-30'
        AND re.EstadoEnvio = 'Puntuado'
    """
    
    cursor.execute(query)
    count = cursor.fetchone()[0]
    print(f"Total records for '03.1' with filters: {count}")
    
    conn.close()

if __name__ == "__main__":
    count_031()

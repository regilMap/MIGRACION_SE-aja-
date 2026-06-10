import sys
import os
sys.path.append(os.getcwd())
from config.database import conectar_fuente

def test_query():
    conn = conectar_fuente()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            ce.CargaEvidenciaID, 
            ace.ArchivoCargaEvidenciaID,
            si.Codigo,
            ce.FechaVencimiento,
            re.EstadoEnvio
        FROM CargaEvidencia ce
        JOIN ArchivoCargaEvidencia ace ON ce.CargaEvidenciaID = ace.CargaEvidenciaID
        JOIN SubIndicadores si ON ce.IndicadorID = si.IndicadorID
        JOIN RepositorioDeEnvio re ON ace.NombreArchivo = re.Archivo
        WHERE ace.ArchivoCargaEvidenciaID = 25327
    """
    
    cursor.execute(query)
    row = cursor.fetchone()
    if row:
        print("Record found with raw join:")
        print(row)
        
        # Now test with filters
        carga_id, ace_id, codigo, fecha_venc, estado_envio = row
        
        print(f"Filter si.Codigo = '03.1': {codigo == '03.1'}")
        print(f"Filter ce.FechaVencimiento > '2026-01-30': {fecha_venc.strftime('%Y-%m-%d') > '2026-01-30' if fecha_venc else 'N/A'}")
        print(f"Filter re.EstadoEnvio = 'Puntuado': {estado_envio == 'Puntuado'}")
    else:
        print("Record NOT found with raw join.")
        
    conn.close()

if __name__ == "__main__":
    test_query()

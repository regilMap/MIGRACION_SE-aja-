import sys
import os
sys.path.append(os.getcwd())
from config.database import conectar_fuente

def search_5998():
    conn = conectar_fuente()
    cursor = conn.cursor()
    
    val = '%5998%'
    query = """
        SELECT * FROM ArchivoCargaEvidencia 
        WHERE NombreArchivo LIKE ? OR Descripcion LIKE ? 
        OR UsuarioID LIKE ? OR NombreUSuario LIKE ?
        OR CAST(ArchivoCargaEvidenciaID AS VARCHAR) LIKE ?
        OR CAST(CargaEvidenciaID AS VARCHAR) LIKE ?
    """
    cursor.execute(query, (val, val, val, val, val, val))
    rows = cursor.fetchall()
    if rows:
        cols = [c[0] for c in cursor.description]
        for r in rows:
            print(dict(zip(cols, r)))
    else:
        print("Not found in ArchivoCargaEvidencia.")
        
    print("\n--- RepositorioDeEnvio ---")
    query_re = """
        SELECT * FROM RepositorioDeEnvio 
        WHERE Archivo LIKE ? OR UsuarioEnviaID LIKE ? 
        OR CAST(RepositorioDeEnvioID AS VARCHAR) LIKE ?
        OR CAST(OrganismoID AS VARCHAR) LIKE ?
    """
    cursor.execute(query_re, (val, val, val, val))
    rows = cursor.fetchall()
    if rows:
        cols = [c[0] for c in cursor.description]
        for r in rows:
            print(dict(zip(cols, r)))
    else:
        print("Not found in RepositorioDeEnvio.")
        
    conn.close()

if __name__ == "__main__":
    search_5998()

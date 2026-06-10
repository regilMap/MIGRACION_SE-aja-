import sys
import os
sys.path.append(os.getcwd())
from config.database import conectar_fuente

def test_repo_query():
    conn = conectar_fuente()
    cursor = conn.cursor()
    
    codigos = ['01.1', '01.2', '09.1', '08.1', 'Np 07.1', 'Ns 07.2', '06.1', '06.2', '5.04', '01.6', '02.2', '02.3', '04.3', '03.2', '03.3', '03.4', '03.5', '03.6', '02.7', 'Ns 07.1', '06.3', '01.4', '06.4', '06.5', '01.3', '5.06', '04.1', '04.2', '5.01', '5.02', '5.03', '01.5', '5.05', '02.1', '5.07', '5.08', '5.09', '5.10', '03.1', '02.4', '02.5', '02.6', '02.8']
    
    placeholders = ','.join(['?'] * len(codigos))
    query = f"""
        SELECT
            ce.CargaEvidenciaID,
            ace.ArchivoCargaEvidenciaID,
            ce.IndicadorID,
            ce.EvidenciaID,
            ce.OrganismoID,
            ace.NombreArchivo,
            ce.ValorActual, -- Score
            ace.Fecha
        FROM CargaEvidencia ce
        JOIN ArchivoCargaEvidencia ace ON ce.CargaEvidenciaID = ace.CargaEvidenciaID
        JOIN SubIndicadores si ON ce.IndicadorID = si.IndicadorID
        JOIN RepositorioDeEnvio re ON ace.NombreArchivo = re.Archivo
        WHERE si.Codigo IN ({placeholders})
        AND re.EstadoEnvio = 'Puntuado'
    """
    
    cursor.execute(query, codigos)
    rows = cursor.fetchall()
    print(f"Total rows returned: {len(rows)}")
    
    found = False
    for row in rows:
        if row[1] == 25327:
            print("Record 25327 FOUND in query result!")
            found = True
            break
            
    if not found:
        print("Record 25327 NOT found in query result.")
        
        # Investigate why
        cursor.execute("SELECT ce.CargaEvidenciaID FROM CargaEvidencia ce WHERE ce.CargaEvidenciaID = 16987")
        if not cursor.fetchone(): print("CargaEvidencia 16987 missing")
        
        cursor.execute("SELECT ace.ArchivoCargaEvidenciaID FROM ArchivoCargaEvidencia ace WHERE ace.ArchivoCargaEvidenciaID = 25327")
        if not cursor.fetchone(): print("ArchivoCargaEvidencia 25327 missing")
        
        cursor.execute("SELECT si.IndicadorID FROM SubIndicadores si WHERE si.IndicadorID = 32 AND si.Codigo = '03.1'")
        if not cursor.fetchone(): print("SubIndicador 32 with code 03.1 missing")
        
        cursor.execute("SELECT re.RepositorioDeEnvioID FROM RepositorioDeEnvio re WHERE re.Archivo = '639056247030524154-INFORME-DE-INSCRIPCION--SIGERD-..pdf' AND re.EstadoEnvio = 'Puntuado'")
        if not cursor.fetchone(): print("RepositorioDeEnvio for the file missing or not Puntuado")

    conn.close()

if __name__ == "__main__":
    test_repo_query()

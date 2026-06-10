import sys
import os
sys.path.append(os.getcwd())
import pyodbc
from config.database import conectar_fuente

def check_specific_record():
    conn = conectar_fuente()
    if not conn:
        print("Error connecting to source DB")
        return

    cursor = conn.cursor()

    carga_evidencia_id = 16987
    archivo_carga_evidencia_id = 25327

    print(f"--- Checking ArchivoCargaEvidencia (ID: {archivo_carga_evidencia_id}) ---")
    cursor.execute("SELECT * FROM ArchivoCargaEvidencia WHERE ArchivoCargaEvidenciaID = ?", archivo_carga_evidencia_id)
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        data = dict(zip(columns, row))
        print(data)
    else:
        print("Not found in ArchivoCargaEvidencia")

    print(f"\n--- Checking CargaEvidencia (ID: {carga_evidencia_id}) ---")
    cursor.execute("SELECT * FROM CargaEvidencia WHERE CargaEvidenciaID = ?", carga_evidencia_id)
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        data = dict(zip(columns, row))
        print(data)
        
        indicador_id = data.get('IndicadorID')
        evidencia_id = data.get('EvidenciaID')
        
        print(f"\n--- Checking SubIndicadores (ID: {indicador_id}) ---")
        cursor.execute("SELECT * FROM SubIndicadores WHERE IndicadorID = ?", indicador_id)
        row_si = cursor.fetchone()
        if row_si:
            cols_si = [column[0] for column in cursor.description]
            print(dict(zip(cols_si, row_si)))
        else:
            print("SubIndicador not found")

        print(f"\n--- Checking Evidencia (ID: {evidencia_id}) ---")
        cursor.execute("SELECT * FROM Evidencia WHERE EvidenciaID = ?", evidencia_id)
        row_e = cursor.fetchone()
        if row_e:
            cols_e = [column[0] for column in cursor.description]
            print(dict(zip(cols_e, row_e)))
        else:
            print("Evidencia not found")

        print(f"\n--- Checking RepositorioDeEnvio (Archivo: {data.get('NombreArchivo')}) ---")
        # Wait, CargaEvidencia doesn't have NombreArchivo. ArchivoCargaEvidencia does.
        cursor.execute("SELECT NombreArchivo FROM ArchivoCargaEvidencia WHERE ArchivoCargaEvidenciaID = ?", archivo_carga_evidencia_id)
        filename = cursor.fetchone()[0]
        
        cursor.execute("SELECT * FROM RepositorioDeEnvio WHERE Archivo = ?", filename)
        row_re = cursor.fetchone()
        if row_re:
            cols_re = [column[0] for column in cursor.description]
            print(dict(zip(cols_re, row_re)))
        else:
            print(f"Not found in RepositorioDeEnvio for file: {filename}")

    conn.close()

if __name__ == "__main__":
    check_specific_record()

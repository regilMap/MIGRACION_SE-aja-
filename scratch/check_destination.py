import sys
import os
sys.path.append(os.getcwd())
from config.database import conectar_destino

def check_destination():
    conn = conectar_destino()
    cursor = conn.cursor()
    
    # In destination, ArchivoCargaEvidenciaID from source might be stored in a column?
    # No, it seems the Id is auto-generated or mapped.
    
    # In transformation_service, file Id = file_id_counter (incremental).
    # But wait! Look at ArchivoDest:
    # Id=file_id_counter
    
    # So we don't store the source ArchivoCargaEvidenciaID in destination?
    # Let's check the schema of Evidencia.Archivos in destination.
    
    cursor.execute("SELECT TOP 1 * FROM Evidencia.Archivos")
    cols = [column[0] for column in cursor.description]
    print(f"Columns in Evidencia.Archivos: {cols}")
    
    # Search by NombreOriginal
    filename = '639056247030524154-INFORME-DE-INSCRIPCION--SIGERD-..pdf'
    cursor.execute("SELECT * FROM Evidencia.Archivos WHERE NombreOriginal LIKE ?", f"%{filename}%")
    row = cursor.fetchone()
    if row:
        print("Record FOUND in destination Archivos table!")
        print(dict(zip([column[0] for column in cursor.description], row)))
        
        file_id = row[0]
        cursor.execute("SELECT * FROM Evidencia.Puntuacion WHERE ArchivoEvidenciaId = ?", file_id)
        p_row = cursor.fetchone()
        if p_row:
            print("Score FOUND in destination Puntuacion table!")
            print(dict(zip([column[0] for column in cursor.description], p_row)))
        else:
            print("Score NOT FOUND in destination.")
    else:
        print("Record NOT FOUND in destination Archivos table.")
        
    conn.close()

if __name__ == "__main__":
    check_destination()

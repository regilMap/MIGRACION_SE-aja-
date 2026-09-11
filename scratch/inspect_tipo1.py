import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar")
        return
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Id, CoedomId, SubIndicadorEvidenciaId, NombreOriginal, CreatedAt, CreatedBy, TipoAlmacenamiento, EstadoArchivoId, RutaExterna FROM Evidencia.Archivos WHERE TipoAlmacenamiento = 1")
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        if row:
            print(dict(zip(columns, row)))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

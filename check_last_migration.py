import pyodbc
from config.database import conectar_destino

def check_last_migration():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino.")
        return

    try:
        cursor = conn.cursor()
        
        # Check max ID in SubIndicadorEvidencias
        query = """
        SELECT TOP 5 
            sie.Id, 
            sie.SubIndicadorId, 
            sie.EvidenciaId,
            si.Codigo as SubIndicadorCodigo,
            e.Descripcion as EvidenciaDesc
        FROM Evidencia.SubIndicadorEvidencias sie
        LEFT JOIN Mantenimiento.SubIndicadores si ON sie.SubIndicadorId = si.Id
        LEFT JOIN Evidencia.Evidencias e ON sie.EvidenciaId = e.Id
        ORDER BY sie.Id DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print("\n--- Últimos 5 registros en Evidencia.SubIndicadorEvidencias ---")
        if rows:
            for row in rows:
                print(f"ID: {row.Id}, SubIndicador: {row.SubIndicadorCodigo} ({row.SubIndicadorId}), EvidenciaID: {row.EvidenciaId}")
        else:
            print("No se encontraron registros en la tabla.")

        # Also check count
        cursor.execute("SELECT COUNT(*) FROM Evidencia.SubIndicadorEvidencias")
        count = cursor.fetchval()
        print(f"\nTotal de SubIndicadorEvidencias: {count}")

        # Check Puntuacion count
        cursor.execute("SELECT COUNT(*) FROM Evidencia.Puntuacion")
        count_scores = cursor.fetchval()
        print(f"Total de Puntuaciones: {count_scores}")

    except Exception as e:
        print(f"Error consultando la base de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_last_migration()

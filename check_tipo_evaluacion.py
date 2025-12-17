from config.database import conectar_destino

def check_tipo_evaluacion():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a destino")
        return

    cursor = conn.cursor()
    try:
        # Check if table exists (confirmed by error, but good to verify schema)
        cursor.execute("SELECT * FROM Evidencia.TipoEvaluacion")
        rows = cursor.fetchall()
        print(f"Filas en Evidencia.TipoEvaluacion: {len(rows)}")
        for row in rows:
            print(row)
            
        if len(rows) == 0:
            print("Insertando valor por defecto Id=1...")
            # Assuming columns based on typical lookup: Id, Nombre/Descripcion, etc.
            # I need to know the columns.
            # I'll query columns first.
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'Evidencia' AND TABLE_NAME = 'TipoEvaluacion'")
            columns = [row[0] for row in cursor.fetchall()]
            print(f"Columnas: {columns}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_tipo_evaluacion()

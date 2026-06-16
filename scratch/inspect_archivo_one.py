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
        cursor.execute("SELECT TOP 1 * FROM Evidencia.Archivos")
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        if row:
            for col, val in zip(columns, row):
                if col == 'ArchivoBinario':
                    print(f"{col}: <binary data of length {len(val)}>")
                else:
                    print(f"{col}: {val}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

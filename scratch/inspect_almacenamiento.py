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
        cursor.execute("SELECT TipoAlmacenamiento, COUNT(*) FROM Evidencia.Archivos GROUP BY TipoAlmacenamiento")
        print("=== TipoAlmacenamiento distribution ===")
        for r in cursor.fetchall():
            print(r)
            
        cursor.execute("SELECT EstadoArchivoId, COUNT(*) FROM Evidencia.Archivos GROUP BY EstadoArchivoId")
        print("\n=== EstadoArchivoId distribution ===")
        for r in cursor.fetchall():
            print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

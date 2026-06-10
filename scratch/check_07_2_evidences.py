import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_fuente

def main():
    conn = conectar_fuente()
    if not conn:
        print("No se pudo conectar a la base de datos fuente")
        return
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT e.Codigo, e.Descipcion, s.Codigo as SubIndicadorCodigo
            FROM Evidencia e
            JOIN SubIndicadores s ON e.IndicadorID = s.IndicadorID
            WHERE s.Codigo = '07.2'
            ORDER BY e.Codigo
        """)
        print("Evidences for 07.2 in FUENTE:")
        for r in cursor.fetchall():
            print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

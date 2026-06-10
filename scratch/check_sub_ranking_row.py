import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino")
        return
    cursor = conn.cursor()
    try:
        print("=== RANKING SUBINDICADOR ROW FOR 25889 AND 14 ===")
        cursor.execute("""
            SELECT SubIndicadorId, CodigoSubIndicador, Avance, Estado
            FROM Cache.RankingSubIndicador
            WHERE CoedomId = 25889 AND SubIndicadorId = 14
        """)
        print(cursor.fetchone())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

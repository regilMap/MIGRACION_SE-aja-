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
        cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'Cache' AND TABLE_NAME = 'RankingOrganismos'")
        print("Columns in Cache.RankingOrganismos:")
        for r in cursor.fetchall():
            print(r)
            
        cursor.execute("SELECT TOP 5 * FROM Cache.RankingOrganismos")
        print("\nSample rows in Cache.RankingOrganismos:")
        for r in cursor.fetchall():
            print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

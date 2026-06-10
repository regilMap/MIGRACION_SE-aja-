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
        print("=== STADO COUNTS IN Cache.RankingSubIndicador ===")
        cursor.execute("SELECT Estado, COUNT(*) FROM Cache.RankingSubIndicador GROUP BY Estado")
        for r in cursor.fetchall():
            print(r)
            
        print("\n=== FUNCTION DEFINITION IN DB ===")
        cursor.execute("SELECT OBJECT_DEFINITION(OBJECT_ID('dbo.fn_RankingSubIndicadores_Inline'))")
        row = cursor.fetchone()
        if row and row[0]:
            print(row[0])
        else:
            print("dbo.fn_RankingSubIndicadores_Inline not found in DB")
            
        print("\n=== SAMPLE RESULTS FROM fn_RankingSubIndicadores_Inline ===")
        cursor.execute("SELECT TOP 5 * FROM dbo.fn_RankingSubIndicadores_Inline()")
        for r in cursor.fetchall():
            print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

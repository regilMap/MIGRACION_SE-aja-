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
        # Search for routine names matching *Ranking*
        cursor.execute("""
            SELECT ROUTINE_SCHEMA, ROUTINE_NAME, ROUTINE_TYPE
            FROM INFORMATION_SCHEMA.ROUTINES
            WHERE ROUTINE_NAME LIKE '%Ranking%'
        """)
        print("Found routines matching '%Ranking%':")
        routines = cursor.fetchall()
        for r in routines:
            print(r)
            
        # Get definition of fn_RankingSubIndicadores_Inline if found
        inline_funcs = [r[1] for r in routines if 'fn_RankingSubIndicadores' in r[1]]
        for func_name in inline_funcs:
            print(f"\n--- Definition of {func_name} ---")
            cursor.execute(f"SELECT OBJECT_DEFINITION(OBJECT_ID('{func_name}'))")
            defn = cursor.fetchone()[0]
            print(defn)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

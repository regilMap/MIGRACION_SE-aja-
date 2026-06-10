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
        funcs = ['fn_RankingSubIndicadores_Inline', 'fn_RankingSubIndicadoresV2_Inline']
        for func in funcs:
            cursor.execute(f"SELECT OBJECT_DEFINITION(OBJECT_ID('{func}'))")
            row = cursor.fetchone()
            if row and row[0]:
                filename = f"scratch/{func}.sql"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(row[0])
                print(f"Saved definition of {func} to {filename}")
            else:
                print(f"Function {func} not found or has no definition")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

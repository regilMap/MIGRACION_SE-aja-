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
        cursor.execute("SELECT OBJECT_DEFINITION(OBJECT_ID('dbo.fn_AvanceSubIndicador_Optimized'))")
        row = cursor.fetchone()
        if row and row[0]:
            print(row[0])
        else:
            print("fn_AvanceSubIndicador_Optimized not found")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

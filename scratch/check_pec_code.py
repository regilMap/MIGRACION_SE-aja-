import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        return
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Id, Codigo, Nombre FROM Evidencia.Evidencias WHERE Nombre LIKE '%PEC%'")
        for r in cursor.fetchall():
            print(f"Id: {r[0]} | Codigo: '{r[1]}' | Nombre: {r[2]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

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
        cursor.execute("SELECT COUNT(*) FROM Mantenimiento.ConfiguracionGeneral")
        cnt = cursor.fetchone()[0]
        print(f"Total rows in Mantenimiento.ConfiguracionGeneral: {cnt}")
        
        if cnt > 0:
            cursor.execute("SELECT TOP 10 * FROM Mantenimiento.ConfiguracionGeneral")
            columns = [column[0] for column in cursor.description]
            for r in cursor.fetchall():
                print(dict(zip(columns, r)))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

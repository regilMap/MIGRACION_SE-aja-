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
        print("=== COLUMNS IN Mantenimiento.Indicadores ===")
        cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'Mantenimiento' AND TABLE_NAME = 'Indicadores'")
        for r in cursor.fetchall():
            print(r)
            
        print("\n=== COLUMNS IN Mantenimiento.SubIndicadores ===")
        cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'Mantenimiento' AND TABLE_NAME = 'SubIndicadores'")
        for r in cursor.fetchall():
            print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

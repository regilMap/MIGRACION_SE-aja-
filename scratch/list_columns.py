import sys
sys.path.append(r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)')
from config.database import conectar_destino

def list_columns():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar.")
        return

    try:
        cursor = conn.cursor()
        print("--- COLUMNS FOR dbo.vOrganismosEducacionX ---")
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'vOrganismosEducacionX'")
        rows = cursor.fetchall()
        for r in rows:
            print(r[0])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    list_columns()

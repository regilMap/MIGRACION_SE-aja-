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
        # Check columns of vOrganismosEducacionX
        cursor.execute("SELECT TOP 5 * FROM dbo.vOrganismosEducacionX")
        columns = [column[0] for column in cursor.description]
        print("Columns in dbo.vOrganismosEducacionX:")
        print(columns)
        
        # Let's print some sample rows
        rows = cursor.fetchall()
        for idx, r in enumerate(rows):
            print(f"Row {idx}: {dict(zip(columns, r))}")

        # Check if CoedomId is also inside this view
        coedom_cols = [c for c in columns if "COEDOM" in c.upper()]
        print(f"Columns containing COEDOM in view: {coedom_cols}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

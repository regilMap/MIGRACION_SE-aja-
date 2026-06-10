import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return
    cursor = conn.cursor()
    try:
        # Check columns of [SISMAP_EDUCACION].[dbo].[vOrganismosEducacionX]
        cursor.execute("SELECT TOP 1 * FROM [SISMAP_EDUCACION].[dbo].[vOrganismosEducacionX]")
        columns = [column[0] for column in cursor.description]
        print("Columns in vOrganismosEducacionX:")
        print(columns)
        
        row = cursor.fetchone()
        print("Sample row:")
        print(row)
        
        # Now query details for 26706 and 26034 using actual columns
        for coedom in [26706, 26034]:
            cursor.execute(f"SELECT * FROM [SISMAP_EDUCACION].[dbo].[vOrganismosEducacionX] WHERE OrganismoID = {coedom}")
            res = cursor.fetchone()
            if res:
                print(f"Organism {coedom}:")
                for col, val in zip(columns, res):
                    print(f"  {col}: {val}")
            else:
                print(f"Organism {coedom} not found in vOrganismosEducacionX")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

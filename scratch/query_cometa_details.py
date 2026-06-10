import sys
sys.path.append(r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)')
from config.database import conectar_destino

def query_cometa_details():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar.")
        return

    try:
        cursor = conn.cursor()
        print("--- QUERY DETAILS FOR COEDOM 25889 ---")
        cursor.execute("""
            SELECT OrganismoID, Nombre, CodigoProvincia, NombreProvincia, REGIONAL, DISTRITO, Descripcion 
            FROM dbo.vOrganismosEducacionX 
            WHERE OrganismoID = 25889
        """)
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        if row:
            print(dict(zip(columns, row)))
        else:
            print("No se encontró.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    query_cometa_details()

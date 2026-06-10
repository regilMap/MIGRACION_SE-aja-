import sys
sys.path.append(r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)')
from config.database import conectar_destino

def test_cache_config():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar.")
        return

    try:
        cursor = conn.cursor()
        print("--- QUERY Cache.ConfiguracionEntidad FOR COEDOM 25889 AND EntidadId 7 ---")
        cursor.execute("SELECT * FROM Cache.ConfiguracionEntidad WHERE CoedomId = 25889 AND EntidadId = 7")
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        for r in rows:
            print(dict(zip(columns, r)))

        print("\n--- QUERY OBJECT_DEFINITION FOR Cache.ConfiguracionEntidad ---")
        cursor.execute("SELECT OBJECT_DEFINITION(OBJECT_ID('Cache.ConfiguracionEntidad'))")
        defn = cursor.fetchval()
        if defn:
            print(defn)
        else:
            # Let's check what kind of object it is (table, view, etc.)
            cursor.execute("SELECT type_desc FROM sys.objects WHERE name = 'ConfiguracionEntidad'")
            type_desc = cursor.fetchval()
            print(f"Object type: {type_desc}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_cache_config()

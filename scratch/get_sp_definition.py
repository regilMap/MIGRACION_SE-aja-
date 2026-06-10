import sys
sys.path.append(r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)')
from config.database import conectar_destino

def get_sp_definition():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT OBJECT_DEFINITION(OBJECT_ID('Cache.sp_ActualizarRankingGlobal'))")
        definition = cursor.fetchval()
        if definition:
            with open("sp_ActualizarRankingGlobal.sql", "w", encoding="utf-8") as f:
                f.write(definition)
            print("Escrito a sp_ActualizarRankingGlobal.sql con éxito.")
        else:
            print("No se encontro la definicion.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    get_sp_definition()

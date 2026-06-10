import sys
sys.path.append(r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)')
from config.database import conectar_destino

def get_fn_obtener_config_defn():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT OBJECT_DEFINITION(OBJECT_ID('dbo.fn_ObtenerConfiguracionEntidad_Inline'))")
        defn = cursor.fetchval()
        if defn:
            with open("fn_ObtenerConfiguracionEntidad_Inline.sql", "w", encoding="utf-8") as f:
                f.write(defn)
            print("Escrito a fn_ObtenerConfiguracionEntidad_Inline.sql con éxito.")
        else:
            print("fn_ObtenerConfiguracionEntidad_Inline no encontrada.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    get_fn_obtener_config_defn()

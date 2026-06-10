import sys
sys.path.append(r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)')
from config.database import conectar_destino

def run_all_cache_updates():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar.")
        return

    try:
        conn.autocommit = True
        cursor = conn.cursor()
        print("--- 1. RUNNING Cache.sp_ActualizarConfiguracionEntidad ---")
        cursor.execute("EXEC Cache.sp_ActualizarConfiguracionEntidad @TipoEntidadNombre=NULL, @CoedomId=?", 25889)
        print("ConfiguracionEntidad updated.")

        print("\n--- 2. RUNNING Cache.sp_ActualizarRankingSubIndicador ---")
        cursor.execute("EXEC Cache.sp_ActualizarRankingSubIndicador @CoedomId=?, @SubIndicadorId=NULL", 25889)
        print("RankingSubIndicador updated.")

        print("\n--- 3. RUNNING Cache.sp_ActualizarRankingGlobal ---")
        cursor.execute("EXEC Cache.sp_ActualizarRankingGlobal @CoedomId=?", 25889)
        print("RankingGlobal updated.")

        print("\nAll procedures executed successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_all_cache_updates()

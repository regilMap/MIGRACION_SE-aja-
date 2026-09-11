import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino")
        return
    
    # Set autocommit to True since executing large procedures might handle their own transactions
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        print("--- 1. RUNNING Cache.sp_ActualizarConfiguracionEntidad ---")
        cursor.execute("EXEC Cache.sp_ActualizarConfiguracionEntidad")
        print("ConfiguracionEntidad updated for all schools.")
        
        print("\n--- 2. RUNNING Cache.sp_ActualizarRankingSubIndicador ---")
        cursor.execute("EXEC Cache.sp_ActualizarRankingSubIndicador")
        print("RankingSubIndicador updated for all schools.")
        
        print("\n--- 3. RUNNING Cache.sp_ActualizarRankingGlobal ---")
        cursor.execute("EXEC Cache.sp_ActualizarRankingGlobal")
        print("RankingGlobal updated for all schools.")
        
        print("\nAll database caches rebuilt successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

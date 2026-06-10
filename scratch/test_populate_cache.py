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
        conn.autocommit = True
        print("Running Cache.sp_ActualizarConfiguracionEntidad for 26706...")
        cursor.execute("EXEC Cache.sp_ActualizarConfiguracionEntidad @CoedomId = 26706")
        print("Execution complete.")
        
        # Verify counts in Cache.ConfiguracionEntidad
        cursor.execute("SELECT COUNT(*) FROM Cache.ConfiguracionEntidad WHERE CoedomId = 26706")
        cnt = cursor.fetchone()[0]
        print(f"New configuration records count for 26706: {cnt}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

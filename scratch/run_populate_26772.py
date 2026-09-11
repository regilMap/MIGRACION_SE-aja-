import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino")
        return
    cursor = conn.cursor()
    try:
        coedom_id = 26772
        print(f"Executing Cache.sp_ActualizarConfiguracionEntidad for Coedom {coedom_id}...")
        cursor.execute("EXEC Cache.sp_ActualizarConfiguracionEntidad @CoedomId = ?", coedom_id)
        conn.commit()
        print("Commit completed.")
        
        print(f"\n=== CACHE RECORDS IN Cache.ConfiguracionEntidad FOR COEDOM {coedom_id} ===")
        cursor.execute("""
            SELECT TipoEntidadId, TipoEntidad, EntidadId, TipoConfiguracion, AplicaFinal, ExcepcionId
            FROM Cache.ConfiguracionEntidad
            WHERE CoedomId = ?
        """, coedom_id)
        rows = cursor.fetchall()
        print(f"Total rows found: {len(rows)}")
        for r in rows[:20]:
            print(r)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

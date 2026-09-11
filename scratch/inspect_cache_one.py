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
        # Check a sample school that got the Np exception (e.g. CoedomId = 25295)
        # and see what is in Cache.ConfiguracionEntidad
        cursor.execute("""
            SELECT TipoEntidad, EntidadId, CoedomId, AplicaGeneral, ExcepcionId, AplicaExcepcion, TipoConfiguracion, AplicaFinal
            FROM Cache.ConfiguracionEntidad
            WHERE CoedomId = 25295 AND EntidadId IN (5, 6, 43) AND TipoEntidadId = 2
        """)
        columns = [column[0] for column in cursor.description]
        print("=== CACHE ENTRIES FOR COEDOM 25295 (Secundario) ===")
        for r in cursor.fetchall():
            print(dict(zip(columns, r)))
            
        # Check a sample school that got the Ns exception (e.g. CoedomId = 25263)
        # Wait, let's find a Primario school CoedomId from our resolved list
        # In our script, we mapped codes. Let's find one Primario school's CoedomId
        cursor.execute("""
            SELECT TOP 3 CoedomId 
            FROM Mantenimiento.ConfiguracionOrganismoExcepcion 
            WHERE EntidadId = 6
        """)
        prim_coedoms = [r[0] for r in cursor.fetchall()]
        print(f"\nPrimario CoedomIds found in exceptions: {prim_coedoms}")
        
        if prim_coedoms:
            cursor.execute(f"""
                SELECT TipoEntidad, EntidadId, CoedomId, AplicaGeneral, ExcepcionId, AplicaExcepcion, TipoConfiguracion, AplicaFinal
                FROM Cache.ConfiguracionEntidad
                WHERE CoedomId = {prim_coedoms[0]} AND EntidadId IN (5, 6, 43) AND TipoEntidadId = 2
            """)
            print(f"\n=== CACHE ENTRIES FOR COEDOM {prim_coedoms[0]} (Primario) ===")
            for r in cursor.fetchall():
                print(dict(zip(columns, r)))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

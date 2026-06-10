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
        # Check vOrganismosEducacionX for both IDs
        for coedom in [26706, 26034]:
            print(f"\n==================================================")
            print(f"Checking details for CoedomId: {coedom}")
            print(f"==================================================")
            
            # Check in [SISMAP_EDUCACION].[dbo].[vOrganismosEducacionX]
            try:
                cursor.execute("""
                    SELECT OrganismoID, Nombre, Codigo, Descripcion, Distrito, Regional
                    FROM [SISMAP_EDUCACION].[dbo].[vOrganismosEducacionX]
                    WHERE OrganismoID = ?
                """, (coedom,))
                org = cursor.fetchone()
                if org:
                    print(f"vOrganismosEducacionX: ID={org[0]}, Nombre='{org[1]}', Codigo='{org[2]}', Descripcion='{org[3]}', Distrito='{org[4]}', Regional='{org[5]}'")
                else:
                    print(f"vOrganismosEducacionX: NOT FOUND")
            except Exception as e:
                print(f"Error querying vOrganismosEducacionX: {e}")
                
            # Check if there are ANY files for this organism (even inactive/deleted ones)
            try:
                cursor.execute("""
                    SELECT Id, SubIndicadorEvidenciaId, IsActive, IsDeleted, CreatedAt
                    FROM Evidencia.Archivos
                    WHERE CoedomId = ?
                """, (coedom,))
                archs = cursor.fetchall()
                print(f"All files in Evidencia.Archivos for CoedomId {coedom} (regardless of status): {len(archs)}")
                for a in archs[:5]:
                    print(f"  File ID={a[0]}, SubIndicadorEvidenciaId={a[1]}, IsActive={a[2]}, IsDeleted={a[3]}, CreatedAt={a[4]}")
            except Exception as e:
                print(f"Error querying Evidencia.Archivos: {e}")
                
            # Check if there are sub-indicator config records
            try:
                cursor.execute("""
                    SELECT TipoEntidad, COUNT(*)
                    FROM Cache.ConfiguracionEntidad
                    WHERE CoedomId = ?
                    GROUP BY TipoEntidad
                """, (coedom,))
                print("Cache.ConfiguracionEntidad records by type:")
                for r in cursor.fetchall():
                    print(f"  Type '{r[0]}': {r[1]}")
            except Exception as e:
                print(f"Error querying Cache.ConfiguracionEntidad: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

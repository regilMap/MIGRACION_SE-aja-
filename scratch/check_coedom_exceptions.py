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
        print(f"=== EXCEPTIONS IN Mantenimiento.ConfiguracionOrganismoExcepcion FOR COEDOM {coedom_id} ===")
        cursor.execute("""
            SELECT Id, TipoEntidadId, EntidadId, Aplica, FechaVencimiento, FechaExtension, CreatedAt
            FROM Mantenimiento.ConfiguracionOrganismoExcepcion
            WHERE CoedomId = ? AND IsActive = 1 AND IsDeleted = 0
        """, coedom_id)
        for r in cursor.fetchall():
            print(r)
            
        print(f"\n=== CACHE RECORDS IN Cache.ConfiguracionEntidad FOR COEDOM {coedom_id} ===")
        cursor.execute("""
            SELECT TipoEntidadId, TipoEntidad, EntidadId, TipoConfiguracion, AplicaFinal, ExcepcionId
            FROM Cache.ConfiguracionEntidad
            WHERE CoedomId = ?
        """, coedom_id)
        for r in cursor.fetchall():
            print(r)
            
        print(f"\n=== EVIDENCIAS FOR SUBINDICADOR 5 ===")
        cursor.execute("""
            SELECT sie.Id, sie.SubIndicadorId, e.Nombre, sie.EvidenciaId
            FROM Evidencia.SubIndicadorEvidencias sie
            INNER JOIN Evidencia.Evidencias e ON e.Id = sie.EvidenciaId
            WHERE sie.SubIndicadorId = 5 AND sie.IsActive = 1 AND sie.IsDeleted = 0
        """)
        for r in cursor.fetchall():
            print(r)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

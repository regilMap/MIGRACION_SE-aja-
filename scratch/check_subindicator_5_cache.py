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
        print(f"=== CACHE RECORDS FOR SUBINDICADOR 5 AND ITS EVIDENCIAS ===")
        cursor.execute("""
            SELECT TipoEntidad, EntidadId, TipoConfiguracion, AplicaFinal, ExcepcionId
            FROM Cache.ConfiguracionEntidad
            WHERE CoedomId = ? AND (
                (TipoEntidad = 'SubIndicador' AND EntidadId = 5)
                OR
                (TipoEntidad = 'SubIndicadorEvidencia' AND EntidadId IN (
                    SELECT Id FROM Evidencia.SubIndicadorEvidencias WHERE SubIndicadorId = 5
                ))
            )
        """, coedom_id)
        for r in cursor.fetchall():
            print(r)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

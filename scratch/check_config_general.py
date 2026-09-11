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
        print("=== CONFIGURACIONES GENERALES ===")
        cursor.execute("""
            SELECT TipoEntidadId, EntidadId, Aplica
            FROM Mantenimiento.ConfiguracionGeneral
            WHERE IsActive = 1 AND IsDeleted = 0
              AND (
                (TipoEntidadId = 2 AND EntidadId = 5)
                OR
                (TipoEntidadId = 3 AND EntidadId IN (
                    SELECT EvidenciaId FROM Evidencia.SubIndicadorEvidencias WHERE SubIndicadorId = 5
                ))
              )
        """)
        for r in cursor.fetchall():
            print(r)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

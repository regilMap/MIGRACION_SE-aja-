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
        print("=== CONFIGURACION ENTIDAD FOR EVIDENCIAS ===")
        cursor.execute("""
            SELECT EntidadId, TipoConfiguracion, AplicaFinal, TipoVencimientoId, FechaVencimiento
            FROM Cache.ConfiguracionEntidad
            WHERE CoedomId = 25889 AND TipoEntidad = 'SubIndicadorEvidencia' AND EntidadId IN (6, 7, 8, 96, 99)
        """)
        for r in cursor.fetchall():
            print(r)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

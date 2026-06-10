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
        print("=== CONFIGURACION ENTIDAD COUNTS ===")
        cursor.execute("""
            SELECT TipoEntidad, AplicaFinal, 
                   CASE WHEN TipoVencimientoId IS NOT NULL THEN 1 ELSE 0 END as HasVencimiento, 
                   COUNT(*) 
            FROM Cache.ConfiguracionEntidad 
            GROUP BY TipoEntidad, AplicaFinal, CASE WHEN TipoVencimientoId IS NOT NULL THEN 1 ELSE 0 END
        """)
        for r in cursor.fetchall():
            print(r)
            
        print("\n=== ARE THERE ANY EXCEPTIONS AT SUBINDICADOR LEVEL? ===")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM Cache.ConfiguracionEntidad 
            WHERE TipoEntidad = 'SubIndicador' AND (AplicaFinal = 0 OR TipoVencimientoId IS NOT NULL)
        """)
        print("SubIndicador exceptions count:", cursor.fetchone()[0])

        print("\n=== ARE THERE ANY EXCEPTIONS AT INDICADOR LEVEL? ===")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM Cache.ConfiguracionEntidad 
            WHERE TipoEntidad = 'Indicador' AND (AplicaFinal = 0 OR TipoVencimientoId IS NOT NULL)
        """)
        print("Indicador exceptions count:", cursor.fetchone()[0])
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

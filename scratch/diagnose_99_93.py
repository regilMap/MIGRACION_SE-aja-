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
        # 1. Query indicators for 25903
        print("\n=== Indicators for CoedomId 25903 ===")
        cursor.execute("SELECT * FROM fn_DetalleIndicadoresOrganismo(25903) ORDER BY IndicadorId")
        columns_ind = [c[0] for c in cursor.description]
        print(", ".join(columns_ind))
        indicators = cursor.fetchall()
        for ind in indicators:
            print(ind)
            
        # Find which indicator has a value around 99.93 (PorcentajeAvance or PuntajeObtenido)
        # Let's inspect subindicators for each of the indicators to see which one has the issue
        for ind in indicators:
            ind_id = ind[1]
            ind_code = ind[2]
            ind_name = ind[3]
            pct_avance = ind[7] # PorcentajeAvance
            score = ind[8] # PuntajeObtenido
            
            print(f"\n=== Subindicators for Indicator {ind_code} ({ind_name}) - Pct: {pct_avance}, Score: {score} ===")
            cursor.execute("SELECT * FROM fn_DetalleSubIndicadoresPorIndicador(?, 25903) ORDER BY SubIndicadorId", (ind_id,))
            columns_sub = [c[0] for c in cursor.description]
            print(", ".join(columns_sub))
            subs = cursor.fetchall()
            for sub in subs:
                print(sub)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

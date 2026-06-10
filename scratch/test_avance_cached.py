import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino")
        return
    cursor = conn.cursor()
    try:
        t0 = time.time()
        # Query using Cache.RankingSubIndicador weighted by fn_SubindicadoresValidos_Inline().PesoNormalizado
        query = """
            WITH AvancesSubIndicadores AS (
                SELECT 
                    sv.IndicadorId,
                    asi.CoedomId,
                    SUM((asi.Avance / 100.0) * sv.PesoNormalizado) AS TotalAvance
                FROM Cache.RankingSubIndicador asi
                INNER JOIN dbo.fn_SubindicadoresValidos_Inline() sv 
                    ON sv.Id = asi.SubIndicadorId 
                    AND sv.CoedomId = asi.CoedomId
                GROUP BY sv.IndicadorId, asi.CoedomId
            )
            SELECT TOP 20
                iv.Id AS IndicadorId,
                iv.Codigo,
                iv.Nombre,
                iv.CoedomId,
                iv.PesoDistribuido,
                iv.PesoOriginal,
                ROUND(
                    CASE 
                        WHEN (ISNULL(avs.TotalAvance, 0) * iv.PesoDistribuido / NULLIF(iv.PesoOriginal, 0)) > iv.PesoDistribuido 
                        THEN iv.PesoDistribuido
                        ELSE (ISNULL(avs.TotalAvance, 0) * iv.PesoDistribuido / NULLIF(iv.PesoOriginal, 0))
                    END, 
                    2
                ) AS Avance
            FROM dbo.fn_IndicadoresValidos_Inline() iv
            LEFT JOIN AvancesSubIndicadores avs
                ON iv.Id = avs.IndicadorId 
                AND iv.CoedomId = avs.CoedomId
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        t1 = time.time()
        print(f"Query completed in {t1 - t0:.3f} seconds. Rows returned: {len(rows)}")
        for r in rows:
            print(r)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

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
        query = """
            WITH ConfigData AS (
                 SELECT EntidadId, CoedomId, AplicaFinal, TipoVencimientoId
                 FROM Cache.ConfiguracionEntidad
                 WHERE TipoEntidad = 'Indicador'
            ),
            Organismos AS (
                SELECT OrganismoID as CoedomId 
                FROM [SISMAP_EDUCACION].[dbo].[vOrganismosEducacionX] 
                WHERE Descripcion = 'Escuelas'
            ),
            BaseIndicadores AS (
                SELECT 
                    i.Id as IndicadorId,
                    i.Codigo,
                    i.Nombre,
                    o.CoedomId,
                    ISNULL(cfg.AplicaFinal, 1) as Aplica,
                    cfg.TipoVencimientoId,
                    iv.PesoDistribuido
                FROM Mantenimiento.Indicadores i
                CROSS JOIN Organismos o
                LEFT JOIN ConfigData cfg ON cfg.EntidadId = i.Id AND cfg.CoedomId = o.CoedomId
                LEFT JOIN dbo.fn_IndicadoresValidos_Inline() iv ON iv.Id = i.Id AND iv.CoedomId = o.CoedomId
                WHERE i.IsActive = 1 AND (i.IsDeleted = 0 OR i.IsDeleted IS NULL)
            ),
            SubIndicadoresEvidenciasInfo AS (
                SELECT 
                    si.IndicadorId,
                    asi.CoedomId,
                    SUM(CASE WHEN asi.Estado <> 'NoRemitido' THEN 1 ELSE 0 END) AS CantidadRemitidos,
                    SUM((asi.Avance / 100.0) * sv.PesoNormalizado) AS TotalAvance
                FROM Cache.RankingSubIndicador asi
                INNER JOIN dbo.fn_SubindicadoresValidos_Inline() sv 
                    ON sv.Id = asi.SubIndicadorId 
                    AND sv.CoedomId = asi.CoedomId
                INNER JOIN Mantenimiento.SubIndicadores si ON si.Id = asi.SubIndicadorId
                GROUP BY si.IndicadorId, asi.CoedomId
            ),
            CalculoEstados AS (
                SELECT 
                    bi.IndicadorId,
                    bi.Codigo,
                    bi.Nombre,
                    bi.CoedomId,
                    CASE
                        WHEN bi.Aplica = 0 THEN 'NoAplica'
                        WHEN bi.TipoVencimientoId IS NOT NULL THEN 'InactivoTemporal'
                        WHEN ISNULL(sei.CantidadRemitidos, 0) = 0 THEN 'NoRemitido'
                        WHEN ROUND(ISNULL(sei.TotalAvance, 0) * 100.0 / NULLIF(bi.PesoDistribuido, 0), 2) >= 80 THEN 'Verde'
                        WHEN ROUND(ISNULL(sei.TotalAvance, 0) * 100.0 / NULLIF(bi.PesoDistribuido, 0), 2) >= 60 THEN 'Amarillo'
                        ELSE 'Rojo'
                    END AS Estado
                FROM BaseIndicadores bi
                LEFT JOIN SubIndicadoresEvidenciasInfo sei 
                    ON sei.IndicadorId = bi.IndicadorId 
                    AND sei.CoedomId = bi.CoedomId
            )
            SELECT 
                ROW_NUMBER() OVER (
                    ORDER BY 
                        CASE 
                            WHEN PATINDEX('%[0-9]%', Codigo) > 0 
                            THEN RIGHT('00' + SUBSTRING(Codigo, PATINDEX('%[0-9]%', Codigo), 
                                 PATINDEX('%.%', Codigo + '.') - PATINDEX('%[0-9]%', Codigo)), 2)
                            ELSE Codigo 
                        END,
                        Codigo
                ) AS Posicion,
                Codigo,
                IndicadorId,
                Nombre,
                SUM(CASE WHEN Estado = 'Verde' THEN 1 ELSE 0 END) AS Verde,
                SUM(CASE WHEN Estado = 'Amarillo' THEN 1 ELSE 0 END) AS Amarillo,
                SUM(CASE WHEN Estado = 'Rojo' THEN 1 ELSE 0 END) + 
                SUM(CASE WHEN Estado = 'NoRemitido' THEN 1 ELSE 0 END) AS Rojo,
                SUM(CASE WHEN Estado = 'InactivoTemporal' THEN 1 ELSE 0 END) AS InactivoTemporal,
                SUM(CASE WHEN Estado = 'NoAplica' THEN 1 ELSE 0 END) AS NoAplica,
                COUNT(*) AS Total,
                SUM(CASE WHEN Estado = 'NoRemitido' THEN 1 ELSE 0 END) AS NoRemitido
            FROM CalculoEstados
            GROUP BY Codigo, Nombre, IndicadorId
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        t1 = time.time()
        print(f"Ranking query completed in {t1 - t0:.3f} seconds. Rows: {len(rows)}")
        for r in rows:
            print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

-- =============================================
-- Versión INLINE (sin parámetros fijos)
-- =============================================
CREATE OR ALTER FUNCTION fn_PesoDistribuidoSubIndicadores_Inline()
RETURNS TABLE
AS
RETURN
(
    WITH CoedomsUnicos AS (
        SELECT DISTINCT CoedomId
        FROM Evidencia.Archivos
        WHERE IsActive = 1 AND IsDeleted = 0
    ),
    IndicadoresPesos AS (
        -- Obtener el peso de cada indicador
        SELECT 
            i.Id as IndicadorId,
            i.CoedomId,
            i.PesoDistribuido AS PesoIndicador  -- ✅ Usar PesoDistribuido en lugar de Peso
        FROM fn_PesoDistribuidoIndicadores_Inline() i
        WHERE Aplica = 1
    ),
    Hijos AS (
        SELECT 
            s.Id,
            s.IndicadorId,
            s.Peso,
            cu.CoedomId,
            CASE 
                WHEN ISNULL(cfg.AplicaFinal, 1) = 0 THEN 0
                WHEN NOT EXISTS (
                    SELECT 1 
                    FROM Evidencia.SubIndicadorEvidencias sie
                    INNER JOIN Evidencia.Evidencias e ON e.Id = sie.EvidenciaId
                    LEFT JOIN fn_ObtenerConfiguracionEntidad_Inline() ce
                        ON ce.TipoEntidad = 'SubIndicadorEvidencia'
                       AND ce.EntidadId = sie.Id
                       AND ce.CoedomId = cu.CoedomId
                    WHERE sie.SubIndicadorId = s.Id
                      AND sie.IsActive = 1 AND sie.IsDeleted = 0
                      AND e.IsActive = 1 AND (e.IsDeleted = 0 OR e.IsDeleted IS NULL)
                      AND ISNULL(ce.AplicaFinal, 1) = 1
                ) THEN 0
                ELSE 1
            END AS Aplica
        FROM Mantenimiento.SubIndicadores s
        CROSS JOIN CoedomsUnicos cu
        LEFT JOIN fn_ObtenerConfiguracionEntidad_Inline() cfg  -- ✅ Usar versión inline
            ON cfg.TipoEntidad = 'SubIndicador'
           AND cfg.EntidadId = s.Id
           AND cfg.CoedomId = cu.CoedomId
        WHERE s.IsActive = 1
          AND s.IsDeleted = 0
    ),
    PesoTotal AS (
        SELECT 
            IndicadorId,
            CoedomId,
            SUM(CASE WHEN Aplica = 1 THEN Peso ELSE 0 END) AS Total
        FROM Hijos
        GROUP BY IndicadorId, CoedomId
    ),
    Ajuste AS (
        SELECT 
            h.Id,
            h.IndicadorId,
            h.CoedomId,
            h.Peso AS PesoOriginal,
            h.Aplica,
            pt.Total AS PesoSuma,
            ip.PesoIndicador,
            -- Ajuste proporcional
            CASE 
                WHEN h.Aplica = 0 THEN 0
                WHEN pt.Total > 0 THEN 
                    CAST((h.Peso * ip.PesoIndicador) / pt.Total AS DECIMAL(10,4))
                ELSE 
                    CAST((ip.PesoIndicador / NULLIF(COUNT(CASE WHEN h.Aplica = 1 THEN 1 END) OVER(PARTITION BY h.IndicadorId, h.CoedomId), 0)) AS DECIMAL(10,4))
            END AS PesoDistribuido
        FROM Hijos h
        INNER JOIN PesoTotal pt 
            ON pt.IndicadorId = h.IndicadorId
            AND pt.CoedomId = h.CoedomId
        INNER JOIN IndicadoresPesos ip 
            ON ip.IndicadorId = h.IndicadorId
            AND ip.CoedomId = h.CoedomId 
    )
    SELECT 
        Id,
        IndicadorId,
        CoedomId,
        PesoOriginal,
        PesoDistribuido,
        ISNULL(Aplica, 0) AS Aplica
    FROM Ajuste
);

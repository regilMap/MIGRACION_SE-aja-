CREATE   FUNCTION fn_AvanceIndicador_Inline()
RETURNS TABLE
AS
RETURN
(
    WITH AvancesSubIndicadores AS (
        -- Obtener todos los avances de subindicadores usando la función INLINE
        SELECT 
            si.IndicadorId,
            asi.CoedomId,
            SUM(asi.Avance) AS TotalAvance
        FROM fn_AvanceSubIndicador_Inline() asi
        INNER JOIN Mantenimiento.SubIndicadores si 
            ON si.Id = asi.SubIndicadorId
        WHERE si.IsActive = 1
          AND (si.IsDeleted = 0 OR si.IsDeleted IS NULL)
        GROUP BY si.IndicadorId, asi.CoedomId
    )
    SELECT 
        iv.Id AS IndicadorId,
        iv.CoedomId,
        iv.PesoDistribuido,
        iv.PesoOriginal,
        -- Calcular avance ponderado limitado por el peso distribuido
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
);

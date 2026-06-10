
-- Función: Obtener indicadores válidos para un organismo (versión dinámica)

-- =============================================
-- Versión INLINE (sin parámetros fijos)
-- =============================================

CREATE   FUNCTION fn_IndicadoresValidos_Inline()
RETURNS TABLE
AS
RETURN
(
    SELECT 
        i.Id,
        i.Codigo,
        i.Nombre,
        i.Descripcion,
        CAST(NULL AS INT) AS TipoIndicadorId,
        ph.CoedomId,
        ph.PesoOriginal,
        ph.PesoDistribuido,
        -- ✅ Usar AplicaFinal directamente de la configuración
        CASE 
            WHEN cfg.AplicaFinal = 0 THEN 0
            WHEN cfg.AplicaFinal = 1 THEN 1
            ELSE 1  -- Por defecto aplica si no hay configuración
        END AS Aplica,
        CASE 
            WHEN cfg.TipoVencimientoId IS NOT NULL THEN 1 
            ELSE 0 
        END AS TieneExtensionPlazo
    FROM Mantenimiento.Indicadores i
    INNER JOIN fn_PesoDistribuidoIndicadores_Inline() ph
        ON ph.Id = i.Id
    -- ✅ Verificar explícitamente con fn_ObtenerConfiguracionEntidad_Inline
    LEFT JOIN fn_ObtenerConfiguracionEntidad_Inline() cfg
        ON cfg.TipoEntidad = 'Indicador'
       AND cfg.EntidadId = i.Id
       AND cfg.CoedomId = ph.CoedomId
    WHERE i.IsActive = 1
      AND (i.IsDeleted = 0 OR i.IsDeleted IS NULL)
      -- ✅ Solo incluir los que aplican según configuración
      AND (cfg.AplicaFinal IS NULL OR cfg.AplicaFinal = 1)
);

CREATE   FUNCTION fn_SubindicadoresValidos_Inline()
RETURNS TABLE
AS
RETURN
(
    SELECT 
        si.Id,
        si.IndicadorId,
        si.Codigo,
        si.Nombre,
        si.TipoSubIndicadorId,
        si.Descripcion,
        ph.CoedomId,
        si.Peso AS PesoOriginal,
        ph.PesoDistribuido AS PesoNormalizado,
        -- ✅ Usar AplicaFinal directamente de la configuración
        CASE 
            WHEN cfg.AplicaFinal = 0 THEN 0
            WHEN cfg.AplicaFinal = 1 THEN 1
            ELSE 1  -- Por defecto aplica si no hay configuración
        END AS Aplica
    FROM Mantenimiento.SubIndicadores si
    INNER JOIN fn_PesoDistribuidoSubIndicadores_Inline() ph
        ON ph.Id = si.Id
    -- ✅ Verificar explícitamente con fn_ObtenerConfiguracionEntidad_Inline
    LEFT JOIN fn_ObtenerConfiguracionEntidad_Inline() cfg
        ON cfg.TipoEntidad = 'SubIndicador'
       AND cfg.EntidadId = si.Id
       AND cfg.CoedomId = ph.CoedomId
    WHERE si.IsActive = 1
      AND (si.IsDeleted = 0 OR si.IsDeleted IS NULL)
      -- ✅ Solo incluir los que aplican según configuración
      AND (cfg.AplicaFinal IS NULL OR cfg.AplicaFinal = 1)
);

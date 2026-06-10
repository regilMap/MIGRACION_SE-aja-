CREATE   PROCEDURE Cache.sp_ActualizarRankingSubIndicador
    @CoedomId INT = NULL,      -- Opcional (Contexto)
    @SubIndicadorId INT = NULL -- Opcional (Si es NULL, actualiza TODO)
AS
BEGIN
    SET NOCOUNT ON;

    -- 1. (Sin validación bloqueante) Si Params son NULL, procedemos a actualizar todo.

    -- 2. Recalcular usando lógica INLINE
    ;WITH Organismos AS (
        SELECT 
            OrganismoID AS CoedomId,
            Nombre AS NombreOrganismo,
            Codigo_Minerd AS CodigoMINERD,
            NombreProvincia,
            NombreMunicipio,
            NombreDistrito,
            REGIONAL,
            DISTRITO
        FROM [SISMAP_EDUCACION].[dbo].[vOrganismosEducacionX]
        WHERE Descripcion = 'Escuelas'
    ),
    RawConfig AS (
        SELECT 
            ce.EntidadId,
            ce.TipoEntidad,
            ce.CoedomId,
            ce.AplicaFinal,
            ce.TipoVencimientoId
        FROM Cache.ConfiguracionEntidad ce
        WHERE ce.TipoEntidad IN ('Indicador', 'SubIndicador', 'SubIndicadorEvidencia')
    ),
    IndicadoresBase AS (
        SELECT 
            i.Id,
            i.Peso,
            o.CoedomId,
            ISNULL(cfg.AplicaFinal, 1) AS Aplica
        FROM Mantenimiento.Indicadores i
        CROSS JOIN Organismos o
        LEFT JOIN RawConfig cfg 
            ON cfg.TipoEntidad = 'Indicador' AND cfg.EntidadId = i.Id AND cfg.CoedomId = o.CoedomId
        WHERE i.IsActive = 1 AND (i.IsDeleted = 0 OR i.IsDeleted IS NULL)
    ),
    IndicadoresCalculados AS (
        SELECT 
            Id,
            CoedomId,
            Peso AS PesoOriginal,
            Aplica,
            CASE 
                WHEN Aplica = 0 THEN 0
                WHEN SUM(CASE WHEN Aplica = 1 THEN Peso ELSE 0 END) OVER (PARTITION BY CoedomId) > 0 THEN
                     CASE WHEN Peso > 0 THEN CAST((Peso * 100.0) / SUM(CASE WHEN Aplica = 1 THEN Peso ELSE 0 END) OVER (PARTITION BY CoedomId) AS DECIMAL(5,2)) ELSE 0 END
                WHEN SUM(CASE WHEN Aplica = 1 THEN 1 ELSE 0 END) OVER (PARTITION BY CoedomId) > 0 THEN
                     CAST(100.0 / SUM(CASE WHEN Aplica = 1 THEN 1 ELSE 0 END) OVER (PARTITION BY CoedomId) AS DECIMAL(5,2))
                ELSE 0
            END AS PesoDistribuido
        FROM IndicadoresBase
    ),
    SubIndicadoresBase AS (
        SELECT 
            s.Id,
            s.IndicadorId,
            s.Codigo,
            s.Nombre,
            s.TipoSubIndicadorId,
            s.Peso,
            o.CoedomId,
            ISNULL(cfg.AplicaFinal, 1) AS Aplica,
            cfg.TipoVencimientoId,
            ic.PesoDistribuido AS PesoIndicador
        FROM Mantenimiento.SubIndicadores s
        INNER JOIN Mantenimiento.Indicadores i ON i.Id = s.IndicadorId
        CROSS JOIN Organismos o
        INNER JOIN IndicadoresCalculados ic ON ic.Id = s.IndicadorId AND ic.CoedomId = o.CoedomId
        LEFT JOIN RawConfig cfg 
            ON cfg.TipoEntidad = 'SubIndicador' AND cfg.EntidadId = s.Id AND cfg.CoedomId = o.CoedomId
        WHERE s.IsActive = 1 AND (s.IsDeleted = 0 OR s.IsDeleted IS NULL)
    ),
    SubIndicadoresCalculados AS (
        SELECT 
            Id AS SubIndicadorId,
            Codigo AS CodigoSubIndicador,
            Nombre AS NombreSubIndicador,
            TipoSubIndicadorId,
            CoedomId,
            Peso AS PesoOriginal,
            Aplica,
            TipoVencimientoId,
            CASE 
                WHEN Aplica = 0 THEN 0
                WHEN SUM(CASE WHEN Aplica = 1 THEN Peso ELSE 0 END) OVER (PARTITION BY IndicadorId, CoedomId) > 0 THEN
                     CAST((Peso * PesoIndicador) / SUM(CASE WHEN Aplica = 1 THEN Peso ELSE 0 END) OVER (PARTITION BY IndicadorId, CoedomId) AS DECIMAL(5,2))
                ELSE 
                     CAST((PesoIndicador / NULLIF(COUNT(CASE WHEN Aplica = 1 THEN 1 END) OVER (PARTITION BY IndicadorId, CoedomId), 0)) AS DECIMAL(5,2))
            END AS PesoNormalizado
        FROM SubIndicadoresBase
    ),
    SubIndicadoresFiltrados AS (
        SELECT * 
        FROM SubIndicadoresCalculados
        WHERE (@SubIndicadorId IS NULL OR SubIndicadorId = @SubIndicadorId) -- Filtro Opcional
    ),
    PuntajesRaw AS (
        SELECT 
            sic.SubIndicadorId,
            sic.CoedomId,
            sic.PesoNormalizado,
            sic.TipoSubIndicadorId,
            (CASE WHEN p.Calificacion IS NOT NULL THEN (p.Calificacion / 100.0) ELSE 0 END) AS PuntajeNormalizado,
             CASE WHEN p.Id IS NOT NULL THEN 1 ELSE 0 END AS TienePuntuacion
        FROM SubIndicadoresFiltrados sic
        INNER JOIN Evidencia.SubIndicadorEvidencias sie 
            ON sie.SubIndicadorId = sic.SubIndicadorId AND sie.IsActive = 1 AND sie.IsDeleted = 0
        LEFT JOIN RawConfig cfge 
            ON cfge.TipoEntidad = 'SubIndicadorEvidencia' AND cfge.EntidadId = sie.Id AND cfge.CoedomId = sic.CoedomId
        LEFT JOIN (
             SELECT 
                a.SubIndicadorEvidenciaId,
                a.CoedomId,
                a.Id AS ArchivoId,
                ROW_NUMBER() OVER (PARTITION BY a.SubIndicadorEvidenciaId, a.CoedomId ORDER BY a.CreatedAt DESC) as rn
             FROM Evidencia.Archivos a
             INNER JOIN Mantenimiento.EstadoArchivos ea ON ea.Id = a.EstadoArchivoId
             -- AQUÍ ESTABA "Vencida"
             WHERE a.IsActive = 1 AND a.IsDeleted = 0  AND ea.Nombre NOT IN ('Vencido', 'Rechazado', 'Pendiente')
        ) arch ON arch.SubIndicadorEvidenciaId = sie.Id AND arch.CoedomId = sic.CoedomId AND arch.rn = 1
        LEFT JOIN Evidencia.Puntuacion p 
            ON p.ArchivoEvidenciaId = arch.ArchivoId AND p.IsActive = 1 AND p.IsDeleted = 0
        WHERE (cfge.AplicaFinal IS NULL OR cfge.AplicaFinal = 1)
          AND sic.Aplica = 1
    ),
    AgregadoPorSubIndicador AS (
        SELECT 
            SubIndicadorId,
            CoedomId,
            MAX(CASE WHEN TienePuntuacion = 1 THEN 1 ELSE 0 END) AS TieneEvidencia,
            CASE 
                -- TIPO 1: Acumulativo. Se suma y se topea a 100.0
                WHEN TipoSubIndicadorId = 1 THEN 
                     CASE WHEN SUM(PuntajeNormalizado * 100.0) > 100.0 THEN 100.0 
                     ELSE SUM(PuntajeNormalizado * 100.0) END
                -- TIPO 2: Escalonado. Se toma el MAX
                WHEN TipoSubIndicadorId = 2 THEN MAX(PuntajeNormalizado * 100.0)
                ELSE SUM(PuntajeNormalizado * 100.0)
            END AS AvanceCalculado
        FROM PuntajesRaw
        GROUP BY SubIndicadorId, CoedomId, TipoSubIndicadorId
    ),
    EvidenciasConfig AS (
        SELECT 
            sie.SubIndicadorId,
            o.CoedomId,
            COUNT(*) AS TotalEvidencias,
            SUM(CASE WHEN cfg.AplicaFinal = 0 AND cfg.TipoVencimientoId IS NULL THEN 1 ELSE 0 END) AS EvidenciasNoAplica,
            SUM(CASE WHEN cfg.TipoVencimientoId IS NOT NULL THEN 1 ELSE 0 END) AS EvidenciasInactivas,
            SUM(CASE WHEN cfg.AplicaFinal = 0 OR cfg.TipoVencimientoId IS NOT NULL THEN 1 ELSE 0 END) AS EvidenciasExceptuadas
        FROM Evidencia.SubIndicadorEvidencias sie
        CROSS JOIN Organismos o
        LEFT JOIN RawConfig cfg 
            ON cfg.TipoEntidad = 'SubIndicadorEvidencia' 
            AND cfg.EntidadId = sie.Id 
            AND cfg.CoedomId = o.CoedomId
        WHERE sie.IsActive = 1 AND sie.IsDeleted = 0
        GROUP BY sie.SubIndicadorId, o.CoedomId
    ),
    CalculoFinal AS (
        SELECT 
            sic.SubIndicadorId,
            sic.CodigoSubIndicador,
            sic.NombreSubIndicador,
            o.CoedomId,
            o.CodigoMINERD,
            o.NombreOrganismo,
            o.NombreProvincia,
            o.NombreMunicipio,
            o.NombreDistrito,
            o.REGIONAL,
            o.DISTRITO,
            CAST(ROUND(CASE 
                WHEN sic.Aplica = 0 OR sic.TipoVencimientoId IS NOT NULL THEN 0
                WHEN ec.TotalEvidencias > 0 AND ec.EvidenciasExceptuadas = ec.TotalEvidencias THEN 0
                ELSE ISNULL(agg.AvanceCalculado, 0)
            END, 2) AS DECIMAL(5,2)) AS Avance,
            CASE
                WHEN sic.Aplica = 0 THEN 'NoAplica'
                WHEN sic.TipoVencimientoId IS NOT NULL THEN 'InactivoTemporal'
                WHEN ec.TotalEvidencias > 0 AND ec.EvidenciasNoAplica = ec.TotalEvidencias THEN 'NoAplica'
                WHEN ec.TotalEvidencias > 0 AND ec.EvidenciasExceptuadas = ec.TotalEvidencias AND ec.EvidenciasInactivas > 0 THEN 'InactivoTemporal'
                WHEN ISNULL(agg.TieneEvidencia, 0) = 0 THEN 'NoRemitido'
                WHEN ISNULL(agg.AvanceCalculado, 0) >= 80 THEN 'Verde'
                WHEN ISNULL(agg.AvanceCalculado, 0) >= 60 THEN 'Amarillo'
                ELSE 'Rojo'
            END AS Estado
        FROM SubIndicadoresFiltrados sic
        INNER JOIN Organismos o ON o.CoedomId = sic.CoedomId
        LEFT JOIN AgregadoPorSubIndicador agg 
            ON agg.SubIndicadorId = sic.SubIndicadorId AND agg.CoedomId = sic.CoedomId
        LEFT JOIN EvidenciasConfig ec
            ON ec.SubIndicadorId = sic.SubIndicadorId AND ec.CoedomId = sic.CoedomId
    )
    -- 3. Upsert en CACHE
    MERGE Cache.RankingSubIndicador AS TARGET
    USING CalculoFinal AS SOURCE
    ON (TARGET.SubIndicadorId = SOURCE.SubIndicadorId AND TARGET.CoedomId = SOURCE.CoedomId)
    
    WHEN MATCHED THEN
        UPDATE SET 
            Avance = SOURCE.Avance,
            Estado = SOURCE.Estado,
            NombreProvincia = SOURCE.NombreProvincia,
            NombreMunicipio = SOURCE.NombreMunicipio,
            NombreDistrito = SOURCE.NombreDistrito,
            REGIONAL = SOURCE.REGIONAL,
            DISTRITO = SOURCE.DISTRITO,
            LastUpdated = GETDATE()
            
    WHEN NOT MATCHED BY TARGET THEN
        INSERT (SubIndicadorId, CoedomId, CodigoSubIndicador, NombreSubIndicador, CodigoMINERD, NombreOrganismo, NombreProvincia, NombreMunicipio, NombreDistrito, REGIONAL, DISTRITO, Avance, Estado, LastUpdated)
        VALUES (SOURCE.SubIndicadorId, SOURCE.CoedomId, SOURCE.CodigoSubIndicador, SOURCE.NombreSubIndicador, SOURCE.CodigoMINERD, SOURCE.NombreOrganismo, SOURCE.NombreProvincia, SOURCE.NombreMunicipio, SOURCE.NombreDistrito, SOURCE.REGIONAL, SOURCE.DISTRITO, SOURCE.Avance, SOURCE.Estado, GETDATE())
    
    -- Eliminación CONDICIONAL
    -- Si @SubIndicadorId tiene valor, borramos solo los de ese ID que ya no existen
    -- Si es NULL, borramos cualquiera que ya no exista en el cálculo masivo
    WHEN NOT MATCHED BY SOURCE AND (@SubIndicadorId IS NULL OR TARGET.SubIndicadorId = @SubIndicadorId) THEN
        DELETE;

    -- 4. Retorno (Solo si se pidieron datos específicos se retornan, si es masivo no)
    IF @SubIndicadorId IS NOT NULL AND @CoedomId IS NOT NULL
    BEGIN
        SELECT * 
        FROM Cache.RankingSubIndicador
        WHERE SubIndicadorId = @SubIndicadorId 
          AND CoedomId = @CoedomId;
    END
END

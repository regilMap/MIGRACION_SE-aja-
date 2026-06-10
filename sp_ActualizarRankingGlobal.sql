-- =============================================
-- Stored Procedure: Actualizar Ranking Global (Cache)
-- =============================================
CREATE OR ALTER PROCEDURE Cache.sp_ActualizarRankingGlobal
    @CoedomId INT = NULL -- Opcional (Si es NULL, recalcula todo)
AS
BEGIN
    SET NOCOUNT ON;

    -- ==========================================
    -- 1. Organismos
    -- ==========================================
    IF OBJECT_ID('tempdb..#Organismos') IS NOT NULL DROP TABLE #Organismos;
    CREATE TABLE #Organismos (
        CoedomId INT PRIMARY KEY,
        NombreOrganismo VARCHAR(255),
        CodigoMINERD VARCHAR(50),
        NombreProvincia VARCHAR(255),
        NombreMunicipio VARCHAR(255),
        NombreDistrito VARCHAR(255),
        REGIONAL VARCHAR(50),
        DISTRITO VARCHAR(50)
    );

    INSERT INTO #Organismos (CoedomId, NombreOrganismo, CodigoMINERD, NombreProvincia, NombreMunicipio, NombreDistrito, REGIONAL, DISTRITO)
    SELECT 
        OrganismoID,
        Nombre,
        Codigo_Minerd,
        NombreProvincia,
        NombreMunicipio,
        NombreDistrito,
        REGIONAL,
        DISTRITO
    FROM [SISMAP_EDUCACION].[dbo].[vOrganismosEducacionX]
    WHERE Descripcion = 'Escuelas'
      AND (@CoedomId IS NULL OR OrganismoID = @CoedomId);

    -- ==========================================
    -- 2. Configuración Caché
    -- ==========================================
    IF OBJECT_ID('tempdb..#ConfiguracionCache') IS NOT NULL DROP TABLE #ConfiguracionCache;
    SELECT 
        ce.TipoEntidad,
        ce.EntidadId,
        ce.CoedomId,
        ce.AplicaFinal,
        ce.TipoVencimientoId
    INTO #ConfiguracionCache
    FROM Cache.ConfiguracionEntidad ce
    WHERE ce.TipoEntidad IN ('Indicador', 'SubIndicador', 'SubIndicadorEvidencia')
      AND EXISTS (SELECT 1 FROM #Organismos o WHERE o.CoedomId = ce.CoedomId);

    CREATE CLUSTERED INDEX IX_ConfigCache_PK ON #ConfiguracionCache(CoedomId, TipoEntidad, EntidadId);

    -- ==========================================
    -- 3. Indicadores Base y Pesos
    -- ==========================================
    IF OBJECT_ID('tempdb..#PesoIndicadores') IS NOT NULL DROP TABLE #PesoIndicadores;
    SELECT 
        i.Id AS IndicadorId,
        oa.CoedomId,
        i.Peso AS PesoOriginal,
        ISNULL(cfg.AplicaFinal, 1) AS Aplica,
        cfg.TipoVencimientoId,
        CAST(0.0 AS DECIMAL(5,2)) AS PesoDistribuido
    INTO #PesoIndicadores
    FROM Mantenimiento.Indicadores i
    CROSS JOIN #Organismos oa
    LEFT JOIN #ConfiguracionCache cfg
        ON cfg.TipoEntidad = 'Indicador'
       AND cfg.EntidadId = i.Id
       AND cfg.CoedomId = oa.CoedomId
    WHERE i.IsActive = 1 AND (i.IsDeleted = 0 OR i.IsDeleted IS NULL);

    CREATE CLUSTERED INDEX IX_PesoInd_PK ON #PesoIndicadores(IndicadorId, CoedomId);

    -- Distribuir el peso de los Indicadores
    ;WITH Calc AS (
        SELECT 
            IndicadorId, CoedomId, PesoOriginal, Aplica,
            CASE 
                WHEN Aplica = 0 THEN 0
                WHEN SUM(CASE WHEN Aplica = 1 THEN PesoOriginal ELSE 0 END) OVER(PARTITION BY CoedomId) = 0 THEN
                    CAST(100.0 / NULLIF(COUNT(CASE WHEN Aplica = 1 THEN 1 END) OVER(PARTITION BY CoedomId), 0) AS DECIMAL(5,2))
                ELSE
                    CAST((PesoOriginal * 100.0) / NULLIF(SUM(CASE WHEN Aplica = 1 THEN PesoOriginal ELSE 0 END) OVER(PARTITION BY CoedomId), 0) AS DECIMAL(5,2))
            END AS NuevoPeso
        FROM #PesoIndicadores
    )
    UPDATE p
    SET p.PesoDistribuido = c.NuevoPeso
    FROM #PesoIndicadores p
    INNER JOIN Calc c ON p.IndicadorId = c.IndicadorId AND p.CoedomId = c.CoedomId;

    -- ==========================================
    -- 4. SubIndicadores Base y Pesos
    -- ==========================================
    IF OBJECT_ID('tempdb..#PesoSubIndicadores') IS NOT NULL DROP TABLE #PesoSubIndicadores;
    SELECT 
        si.Id AS SubIndicadorId,
        si.IndicadorId,
        pi.CoedomId,
        si.Peso AS PesoSubOriginal,
        pi.PesoDistribuido AS PesoIndicadorPadre,
        CASE 
            WHEN ISNULL(cfg.AplicaFinal, 1) = 0 THEN 0
            WHEN NOT EXISTS (
                SELECT 1 
                FROM Evidencia.SubIndicadorEvidencias sie
                INNER JOIN Evidencia.Evidencias e ON e.Id = sie.EvidenciaId
                LEFT JOIN Cache.ConfiguracionEntidad ce
                    ON ce.TipoEntidad = 'SubIndicadorEvidencia'
                   AND ce.EntidadId = sie.Id
                   AND ce.CoedomId = pi.CoedomId
                WHERE sie.SubIndicadorId = si.Id
                  AND sie.IsActive = 1 AND sie.IsDeleted = 0
                  AND e.IsActive = 1 AND (e.IsDeleted = 0 OR e.IsDeleted IS NULL)
                  AND ISNULL(ce.AplicaFinal, 1) = 1
            ) THEN 0
            ELSE 1
        END AS AplicaSub,
        cfg.TipoVencimientoId AS TipoVencimientoSub,
        CAST(0.0 AS DECIMAL(10,4)) AS PesoSubDistribuido,
        si.TipoSubIndicadorId
    INTO #PesoSubIndicadores
    FROM Mantenimiento.SubIndicadores si
    INNER JOIN #PesoIndicadores pi ON pi.IndicadorId = si.IndicadorId
    LEFT JOIN #ConfiguracionCache cfg
        ON cfg.TipoEntidad = 'SubIndicador'
       AND cfg.EntidadId = si.Id
       AND cfg.CoedomId = pi.CoedomId
    WHERE si.IsActive = 1 AND (si.IsDeleted = 0 OR si.IsDeleted IS NULL)
      AND pi.Aplica = 1;

    CREATE CLUSTERED INDEX IX_PesoSubInd_PK ON #PesoSubIndicadores(SubIndicadorId, CoedomId);
    CREATE NONCLUSTERED INDEX IX_PesoSubInd_Ind ON #PesoSubIndicadores(IndicadorId);

    -- Distribuir el peso de los SubIndicadores
    ;WITH CalcSub AS (
        SELECT 
            SubIndicadorId, IndicadorId, CoedomId, PesoSubOriginal, AplicaSub, PesoIndicadorPadre,
            CASE 
                WHEN AplicaSub = 0 THEN 0
                WHEN SUM(CASE WHEN AplicaSub = 1 THEN PesoSubOriginal ELSE 0 END) OVER(PARTITION BY IndicadorId, CoedomId) > 0 THEN
                    CAST((PesoSubOriginal * PesoIndicadorPadre) / SUM(CASE WHEN AplicaSub = 1 THEN PesoSubOriginal ELSE 0 END) OVER(PARTITION BY IndicadorId, CoedomId) AS DECIMAL(10,4))
                ELSE
                    CAST(PesoIndicadorPadre / NULLIF(COUNT(CASE WHEN AplicaSub = 1 THEN 1 END) OVER(PARTITION BY IndicadorId, CoedomId), 0) AS DECIMAL(10,4))
            END AS NuevoPesoSub
        FROM #PesoSubIndicadores
    )
    UPDATE p
    SET p.PesoSubDistribuido = c.NuevoPesoSub
    FROM #PesoSubIndicadores p
    INNER JOIN CalcSub c ON p.SubIndicadorId = c.SubIndicadorId AND p.CoedomId = c.CoedomId;

    -- ==========================================
    -- 5. Evidencias Base
    -- ==========================================
    IF OBJECT_ID('tempdb..#EvidenciasBase') IS NOT NULL DROP TABLE #EvidenciasBase;
    SELECT 
        sie.Id AS SubIndicadorEvidenciaId,
        sie.SubIndicadorId,
        psi.IndicadorId,
        sie.EvidenciaId,
        psi.CoedomId,
        psi.PesoSubDistribuido,
        UPPER(ti.Nombre) AS TipoSubIndicador,
        e.Valor AS ValorEvidencia,
        ISNULL(cfg.AplicaFinal, 1) AS AplicaEvidencia
    INTO #EvidenciasBase
    FROM Evidencia.SubIndicadorEvidencias sie
    INNER JOIN Evidencia.Evidencias e ON e.Id = sie.EvidenciaId
    INNER JOIN #PesoSubIndicadores psi ON psi.SubIndicadorId = sie.SubIndicadorId
    INNER JOIN Mantenimiento.TiposSubIndicador ti ON ti.Id = psi.TipoSubIndicadorId
    LEFT JOIN #ConfiguracionCache cfg
        ON cfg.TipoEntidad = 'SubIndicadorEvidencia'
       AND cfg.EntidadId = sie.Id
       AND cfg.CoedomId = psi.CoedomId
    WHERE sie.IsActive = 1 AND sie.IsDeleted = 0
      AND e.IsActive = 1 AND (e.IsDeleted = 0 OR e.IsDeleted IS NULL)
      AND psi.AplicaSub = 1;

    CREATE CLUSTERED INDEX IX_EvidenciasBase_PK ON #EvidenciasBase(CoedomId, SubIndicadorEvidenciaId);

    -- =========================================================
    -- 6. Puntuaciones (Reemplazo del OUTER APPLY para Rendimiento)
    -- =========================================================
    IF OBJECT_ID('tempdb..#UltimaPuntuacion') IS NOT NULL DROP TABLE #UltimaPuntuacion;
    WITH RankedScores AS (
        SELECT 
            a.CoedomId, 
            a.SubIndicadorEvidenciaId, 
            p.Calificacion,
            ROW_NUMBER() OVER(PARTITION BY a.CoedomId, a.SubIndicadorEvidenciaId ORDER BY a.CreatedAt DESC) as rn
        FROM Evidencia.Archivos a
        INNER JOIN Evidencia.Puntuacion p ON p.ArchivoEvidenciaId = a.Id
        INNER JOIN Mantenimiento.EstadoArchivos ea ON a.EstadoArchivoId = ea.Id
        WHERE a.IsActive = 1 AND a.IsDeleted = 0
          AND p.IsActive = 1 AND p.IsDeleted = 0
          AND ea.Nombre NOT IN ('Vencido', 'Rechazado', 'Pendiente')
          AND EXISTS (SELECT 1 FROM #EvidenciasBase eb WHERE eb.CoedomId = a.CoedomId AND eb.SubIndicadorEvidenciaId = a.SubIndicadorEvidenciaId)
    )
    SELECT CoedomId, SubIndicadorEvidenciaId, Calificacion
    INTO #UltimaPuntuacion
    FROM RankedScores
    WHERE rn = 1;

    CREATE CLUSTERED INDEX IX_UltimaPuntuacion_PK ON #UltimaPuntuacion(CoedomId, SubIndicadorEvidenciaId);

    -- ==========================================
    -- 7. Puntuaciones Finales Ajustadas
    -- ==========================================
    IF OBJECT_ID('tempdb..#PuntajesEvidenciasFinal') IS NOT NULL DROP TABLE #PuntajesEvidenciasFinal;
    
    SELECT 
        eva.SubIndicadorEvidenciaId,
        eva.SubIndicadorId,
        eva.IndicadorId,
        eva.CoedomId,
        eva.PesoSubDistribuido,
        eva.TipoSubIndicador,
        CASE 
            WHEN eva.AplicaEvidencia = 0 THEN 0
            ELSE ISNULL(up.Calificacion, 0)
        END AS PuntajeFinal
    INTO #PuntajesEvidenciasFinal
    FROM #EvidenciasBase eva
    LEFT JOIN #UltimaPuntuacion up ON up.CoedomId = eva.CoedomId AND up.SubIndicadorEvidenciaId = eva.SubIndicadorEvidenciaId;

    -- ==========================================
    -- 8. Cálculo Final y Guardado
    -- ==========================================
    ;WITH AvanceSubIndicadores AS (
        SELECT 
            IndicadorId,
            SubIndicadorId,
            CoedomId,
            PesoSubDistribuido,
            CASE 
                WHEN TipoSubIndicador = 'ACUMULATIVO' THEN 
                     -- CAP A 100 en el subindicador
                     CASE WHEN SUM(PuntajeFinal) > 100.0 THEN PesoSubDistribuido 
                     ELSE (SUM(PuntajeFinal) / 100.0) * PesoSubDistribuido END
                WHEN TipoSubIndicador = 'ESCALONADO' THEN 
                     (MAX(PuntajeFinal) / 100.0) * PesoSubDistribuido
                ELSE (SUM(PuntajeFinal) / 100.0) * PesoSubDistribuido
            END AS AvanceSubWeighted
        FROM #PuntajesEvidenciasFinal
        GROUP BY IndicadorId, SubIndicadorId, CoedomId, PesoSubDistribuido, TipoSubIndicador
    ),
    AvanceIndicadores AS (
        SELECT 
            pi.IndicadorId,
            pi.CoedomId,
            pi.PesoDistribuido,
            pi.PesoOriginal,
            SUM(ISNULL(asi.AvanceSubWeighted, 0)) AS TotalAvanceSub
        FROM #PesoIndicadores pi
        LEFT JOIN AvanceSubIndicadores asi ON asi.IndicadorId = pi.IndicadorId AND asi.CoedomId = pi.CoedomId
        WHERE pi.Aplica = 1
        GROUP BY pi.IndicadorId, pi.CoedomId, pi.PesoDistribuido, pi.PesoOriginal
    ),
    AvanceIndicadoresFinal AS (
        SELECT 
            CoedomId,
            ROUND(CASE 
                WHEN TotalAvanceSub > PesoDistribuido THEN PesoDistribuido 
                ELSE TotalAvanceSub 
            END, 2) AS AvanceIndicadorFinal
        FROM AvanceIndicadores
    ),
    CalculoFinal AS (
        SELECT 
            oa.CoedomId,
            oa.CodigoMINERD,
            oa.NombreOrganismo,
            oa.NombreProvincia,
            oa.NombreMunicipio,
            oa.NombreDistrito,
            oa.REGIONAL,
            oa.DISTRITO,
            ISNULL(SUM(aif.AvanceIndicadorFinal), 0) AS PuntajeTotal,
            RANK() OVER (ORDER BY ISNULL(SUM(aif.AvanceIndicadorFinal), 0) DESC) AS Ranking
        FROM #Organismos oa
        LEFT JOIN AvanceIndicadoresFinal aif ON aif.CoedomId = oa.CoedomId
        GROUP BY 
            oa.CoedomId, oa.CodigoMINERD, oa.NombreOrganismo, 
            oa.NombreProvincia, oa.NombreMunicipio, oa.NombreDistrito, oa.REGIONAL, oa.DISTRITO
    )
    
    -- MERGE (UPSERT)
    MERGE Cache.RankingGlobal AS TARGET
    USING CalculoFinal AS SOURCE
    ON (TARGET.CoedomId = SOURCE.CoedomId)
    
    WHEN MATCHED THEN
        UPDATE SET
            PuntajeTotal = SOURCE.PuntajeTotal,
            Ranking = SOURCE.Ranking,
            NombreProvincia = SOURCE.NombreProvincia,
            NombreMunicipio = SOURCE.NombreMunicipio,
            NombreDistrito = SOURCE.NombreDistrito,
            REGIONAL = SOURCE.REGIONAL,
            DISTRITO = SOURCE.DISTRITO,
            LastUpdated = GETDATE()
 
    WHEN NOT MATCHED BY TARGET THEN
        INSERT (CoedomId, CodigoMINERD, NombreOrganismo, NombreProvincia, NombreMunicipio, NombreDistrito, REGIONAL, DISTRITO, PuntajeTotal, Ranking, LastUpdated)
        VALUES (SOURCE.CoedomId, SOURCE.CodigoMINERD, SOURCE.NombreOrganismo, SOURCE.NombreProvincia, SOURCE.NombreMunicipio, SOURCE.NombreDistrito, SOURCE.REGIONAL, SOURCE.DISTRITO, SOURCE.PuntajeTotal, SOURCE.Ranking, GETDATE())
    
    -- Eliminación 
    WHEN NOT MATCHED BY SOURCE AND (@CoedomId IS NULL OR TARGET.CoedomId = @CoedomId) THEN
        DELETE;

    -- Recalcular el ranking global de todos los centros para asegurar consistencia
    ;WITH NewRankings AS (
        SELECT 
            CoedomId,
            RANK() OVER (ORDER BY PuntajeTotal DESC) as NewRank
        FROM Cache.RankingGlobal
    )
    UPDATE rg
    SET rg.Ranking = nr.NewRank
    FROM Cache.RankingGlobal rg
    INNER JOIN NewRankings nr ON rg.CoedomId = nr.CoedomId;

    IF @CoedomId IS NOT NULL
    BEGIN
        SELECT * FROM Cache.RankingGlobal WHERE CoedomId = @CoedomId;
    END
END

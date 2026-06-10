CREATE   FUNCTION fn_AvanceSubIndicador_Optimized()
RETURNS TABLE
AS
RETURN
(
    WITH 
    -- 1. Organismos Base (1 scan hopefully, if optimized by SQL Engine)
    Organismos AS (
        SELECT OrganismoID AS CoedomId 
        FROM [SISMAP_EDUCACION].[dbo].[vOrganismosEducacionX]
        WHERE Descripcion = 'Escuelas'
    ),
    -- 2. Configuracin (3 scans - can be Hash Joined preferably)
    ConfigIndicadores AS (
        SELECT EntidadId, CoedomId, AplicaFinal 
        FROM Cache.ConfiguracionEntidad 
        WHERE TipoEntidad = 'Indicador'
    ),
    ConfigSubIndicadores AS (
        SELECT EntidadId, CoedomId, AplicaFinal, TipoVencimientoId
        FROM Cache.ConfiguracionEntidad 
        WHERE TipoEntidad = 'SubIndicador'
    ),
    ConfigEvidencias AS (
        SELECT EntidadId, CoedomId, AplicaFinal 
        FROM Cache.ConfiguracionEntidad 
        WHERE TipoEntidad = 'SubIndicadorEvidencia'
    ),
    -- 3. Clculo Peso Indicadores (GROUP BY instead of Window)
    IndicadoresRaw AS (
        SELECT 
            i.Id,
            i.Peso,
            o.CoedomId,
            ISNULL(cfg.AplicaFinal, 1) AS Aplica
        FROM Mantenimiento.Indicadores i
        CROSS JOIN Organismos o
        LEFT JOIN ConfigIndicadores cfg ON cfg.EntidadId = i.Id AND cfg.CoedomId = o.CoedomId
        WHERE i.IsActive = 1 AND (i.IsDeleted = 0 OR i.IsDeleted IS NULL)
    ),
    IndicadoresAgg AS (
        SELECT 
            CoedomId,
            SUM(CASE WHEN Aplica = 1 THEN Peso ELSE 0 END) as TotalPeso,
            COUNT(CASE WHEN Aplica = 1 THEN 1 END) as CantidadAplican
        FROM IndicadoresRaw
        GROUP BY CoedomId
    ),
    PesoIndicadores AS (
        SELECT 
            ir.Id AS IndicadorId, ir.CoedomId,
            CASE 
                WHEN ir.Aplica = 0 THEN 0
                WHEN ia.TotalPeso = 0 AND ia.CantidadAplican > 0 THEN CAST(100.0 / NULLIF(ia.CantidadAplican, 0) AS DECIMAL(5,2))
                WHEN ia.TotalPeso > 0 AND ir.Peso > 0 THEN CAST((ir.Peso * 100.0) / ia.TotalPeso AS DECIMAL(5,2))
                ELSE 0
            END AS PesoDistribuido
        FROM IndicadoresRaw ir
        JOIN IndicadoresAgg ia ON ia.CoedomId = ir.CoedomId
    ),
    -- 4. Clculo Peso SubIndicadores (CHAINED JOIN to avoid Cross Join Organismos again)
    SubIndicadoresRaw AS (
        SELECT 
            si.Id, si.IndicadorId, si.Peso, pi.CoedomId,
            ISNULL(cfg.AplicaFinal, 1) AS Aplica,
            cfg.TipoVencimientoId,
            pi.PesoDistribuido as PesoPadre
        FROM Mantenimiento.SubIndicadores si
        INNER JOIN PesoIndicadores pi ON pi.IndicadorId = si.IndicadorId -- Inherit CoedomId from Indicator
        LEFT JOIN ConfigSubIndicadores cfg ON cfg.EntidadId = si.Id AND cfg.CoedomId = pi.CoedomId
        WHERE si.IsActive = 1 AND (si.IsDeleted = 0 OR si.IsDeleted IS NULL)
          AND pi.PesoDistribuido > 0 -- Optimization: Ignore if parent has no weight
    ),
    SubIndicadoresAgg AS (
         SELECT 
             sir.IndicadorId, sir.CoedomId,
             SUM(CASE WHEN sir.Aplica = 1 THEN sir.Peso ELSE 0 END) as TotalPesoSibling,
             COUNT(*) as CountSibling
         FROM SubIndicadoresRaw sir
         GROUP BY sir.IndicadorId, sir.CoedomId
    ),
    PesoSubIndicadores AS (
        SELECT 
            sir.Id AS SubIndicadorId, sir.IndicadorId, sir.CoedomId, sir.Aplica, sir.TipoVencimientoId,
            CASE 
                WHEN sia.TotalPesoSibling > 0 THEN 
                    CAST((sir.Peso * sir.PesoPadre) / sia.TotalPesoSibling AS DECIMAL(5,2))
                ELSE 
                    CAST((sir.PesoPadre / NULLIF(sia.CountSibling, 0)) AS DECIMAL(5,2))
            END AS PesoDistribuido
        FROM SubIndicadoresRaw sir
        JOIN SubIndicadoresAgg sia ON sia.IndicadorId = sir.IndicadorId AND sia.CoedomId = sir.CoedomId
    ),
    -- 5. Evidencias y Puntuaciones
    EvidenciasBase AS (
        SELECT 
            psi.SubIndicadorId,
            psi.CoedomId,
            psi.PesoDistribuido,
            psi.Aplica AS SubIndAplica, 
            psi.TipoVencimientoId,
            sie.Id AS SubIndicadorEvidenciaId,
            si.TipoSubIndicadorId AS TipoIndicadorId,
            -- Determine Evidence Aplica
            CASE 
                WHEN cfg.AplicaFinal IS NOT NULL THEN cfg.AplicaFinal
                WHEN e.IsActive = 1 AND (e.IsDeleted = 0 OR e.IsDeleted IS NULL) THEN 1
                ELSE 0 
            END AS EvidenciaAplica
        FROM PesoSubIndicadores psi
        JOIN Mantenimiento.SubIndicadores si ON si.Id = psi.SubIndicadorId
        LEFT JOIN Evidencia.SubIndicadorEvidencias sie ON sie.SubIndicadorId = psi.SubIndicadorId AND sie.IsActive = 1 AND sie.IsDeleted = 0
        LEFT JOIN Evidencia.Evidencias e ON e.Id = sie.EvidenciaId
        LEFT JOIN ConfigEvidencias cfg ON cfg.EntidadId = sie.Id AND cfg.CoedomId = psi.CoedomId
    ),
    -- Keep Window Function ONLY here as it is necessary for 'Last File' logic and simpler than self-join
    UltimosArchivos AS (
        SELECT 
            a.SubIndicadorEvidenciaId,
            a.CoedomId,
            MAX(a.Id) as ArchivoId -- Using MAX ID as proxy for latest (Optimization trade-off vs strict CreatedAt)
        FROM Evidencia.Archivos a
        JOIN Mantenimiento.EstadoArchivos ea ON ea.Id = a.EstadoArchivoId
        WHERE a.IsDeleted = 0 AND a.IsActive = 1
              AND ea.Nombre NOT IN ('Vencida', 'Rechazado', 'Pendiente')
        GROUP BY a.SubIndicadorEvidenciaId, a.CoedomId
    ),
    Puntuaciones AS (
        SELECT ArchivoEvidenciaId, Calificacion 
        FROM Evidencia.Puntuacion 
        WHERE IsActive = 1 AND IsDeleted = 0
    ),
    FinalScores AS (
        SELECT 
            eb.SubIndicadorId,
            eb.CoedomId,
            eb.PesoDistribuido,
            eb.SubIndAplica,
            eb.TipoVencimientoId,
            eb.TipoIndicadorId,
            COALESCE(p.Calificacion, 0) as Score,
            CASE WHEN ua.ArchivoId IS NOT NULL THEN 1 ELSE 0 END as HasFile
        FROM EvidenciasBase eb
        LEFT JOIN UltimosArchivos ua 
            ON ua.SubIndicadorEvidenciaId = eb.SubIndicadorEvidenciaId 
           AND ua.CoedomId = eb.CoedomId
        LEFT JOIN Puntuaciones p 
            ON p.ArchivoEvidenciaId = ua.ArchivoId
        WHERE eb.EvidenciaAplica = 1 -- Only consider applicable evidences for scoring
    ),
    -- 6. Aggregation
    Aggregated AS (
        SELECT 
            SubIndicadorId,
            CoedomId,
            PesoDistribuido as PesoNormalizado, -- This is the normalized weight
            SubIndAplica as Aplica,
            TipoVencimientoId,
            CASE 
                WHEN TipoIndicadorId = 1 THEN -- Acumulativo
                    SUM((Score / 100.0) * PesoDistribuido)
                WHEN TipoIndicadorId = 2 THEN -- Escalonado
                    MAX((Score / 100.0) * PesoDistribuido)
                ELSE 0
            END as Avance,
            MAX(HasFile) as HasFile
        FROM FinalScores
        GROUP BY SubIndicadorId, CoedomId, PesoDistribuido, SubIndAplica, TipoVencimientoId, TipoIndicadorId
    )
    SELECT 
        SubIndicadorId,
        CoedomId,
        CAST(ISNULL(Avance, 0) AS DECIMAL(5,2)) as Avance,
        CAST(Aplica AS BIT) as Aplica,
        TipoVencimientoId,
        PesoNormalizado,
        CAST(ISNULL(HasFile, 0) AS BIT) as HasArchivo
    FROM Aggregated
);

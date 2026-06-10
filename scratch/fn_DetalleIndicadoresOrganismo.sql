CREATE   FUNCTION fn_DetalleIndicadoresOrganismo
(
    @CoedomId INT
)
RETURNS TABLE
AS
RETURN
(
    WITH OrganismoTarget AS (
        SELECT @CoedomId AS CoedomId
    ),
    ConfiguracionCache AS (
        SELECT 
            ce.TipoEntidad,
            ce.EntidadId,
            ce.CoedomId,
            ce.AplicaFinal,
            ce.TipoVencimientoId,
            ce.TipoConfiguracion -- Needed for Estado
        FROM Cache.ConfiguracionEntidad ce
        WHERE ce.CoedomId = @CoedomId
    ),
    IndicadoresBase AS (
        SELECT 
            i.Id AS IndicadorId,
            i.Codigo,
            i.Nombre,
            i.Descripcion,
            ISNULL(i.Peso, 0) AS Peso,
            ot.CoedomId,
            ISNULL(cfg.AplicaFinal, 1) AS Aplica,
            cfg.TipoVencimientoId,
            cfg.TipoConfiguracion
        FROM Mantenimiento.Indicadores i
        CROSS JOIN OrganismoTarget ot
        LEFT JOIN ConfiguracionCache cfg
            ON cfg.TipoEntidad = 'Indicador'
           AND cfg.EntidadId = i.Id
           AND cfg.CoedomId = ot.CoedomId
        WHERE i.IsActive = 1 AND (i.IsDeleted = 0 OR i.IsDeleted IS NULL)
    ),
    PesoIndicadores AS (
        SELECT 
            ib.IndicadorId,
            ib.CoedomId,
            ib.Peso AS PesoOriginal,
            ib.Aplica,
            ib.TipoVencimientoId,
            CASE 
                WHEN ib.Aplica = 0 THEN 0
                WHEN SUM(CASE WHEN ib.Aplica = 1 THEN ib.Peso ELSE 0 END) OVER(PARTITION BY ib.CoedomId) = 0 THEN
                    CAST(100.0 / NULLIF(COUNT(CASE WHEN ib.Aplica = 1 THEN 1 END) OVER(PARTITION BY ib.CoedomId), 0) AS DECIMAL(5,2))
                ELSE
                    CAST((ib.Peso * 100.0) / NULLIF(SUM(CASE WHEN ib.Aplica = 1 THEN ib.Peso ELSE 0 END) OVER(PARTITION BY ib.CoedomId), 0) AS DECIMAL(5,2))
            END AS PesoDistribuido
        FROM IndicadoresBase ib
    ),
    SubIndicadoresBase AS (
        SELECT 
            si.Id AS SubIndicadorId,
            si.IndicadorId,
            ISNULL(si.Peso, 0) AS PesoSubOriginal,
            pi.CoedomId,
            ISNULL(pi.PesoDistribuido, 0) AS PesoIndicadorPadre,
            ISNULL(cfg.AplicaFinal, 1) AS AplicaSub,
            cfg.TipoVencimientoId AS TipoVencimientoSub
        FROM Mantenimiento.SubIndicadores si
        INNER JOIN PesoIndicadores pi ON pi.IndicadorId = si.IndicadorId
        LEFT JOIN ConfiguracionCache cfg
            ON cfg.TipoEntidad = 'SubIndicador'
           AND cfg.EntidadId = si.Id
           AND cfg.CoedomId = pi.CoedomId
        WHERE si.IsActive = 1 AND (si.IsDeleted = 0 OR si.IsDeleted IS NULL)
          AND pi.Aplica = 1
    ),
    PesoSubIndicadores AS (
        SELECT 
            sib.SubIndicadorId,
            sib.IndicadorId,
            sib.CoedomId,
            sib.PesoSubOriginal,
            sib.AplicaSub,
            sib.TipoVencimientoSub,
            CASE 
                WHEN sib.AplicaSub = 0 THEN 0
                WHEN SUM(CASE WHEN sib.AplicaSub = 1 THEN sib.PesoSubOriginal ELSE 0 END) OVER(PARTITION BY sib.IndicadorId, sib.CoedomId) > 0 THEN
                    CAST((sib.PesoSubOriginal * sib.PesoIndicadorPadre) / SUM(CASE WHEN sib.AplicaSub = 1 THEN sib.PesoSubOriginal ELSE 0 END) OVER(PARTITION BY sib.IndicadorId, sib.CoedomId) AS DECIMAL(10,4))
                ELSE
                    CAST(sib.PesoIndicadorPadre / NULLIF(COUNT(CASE WHEN sib.AplicaSub = 1 THEN 1 END) OVER(PARTITION BY sib.IndicadorId, sib.CoedomId), 0) AS DECIMAL(10,4))
            END AS PesoSubDistribuido
        FROM SubIndicadoresBase sib
    ),
    EvidenciasBase AS (
        SELECT 
            sie.Id AS SubIndicadorEvidenciaId,
            sie.SubIndicadorId,
            sie.EvidenciaId,
            psi.CoedomId,
            ISNULL(psi.PesoSubDistribuido, 0) AS PesoSubDistribuido,
            ISNULL(UPPER(ti.Nombre), 'OTROS') AS TipoSubIndicador, 
            ISNULL(e.Valor, 0) AS ValorEvidencia,
            ISNULL(cfg.AplicaFinal, 1) AS AplicaEvidencia
        FROM Evidencia.SubIndicadorEvidencias sie
        INNER JOIN Evidencia.Evidencias e ON e.Id = sie.EvidenciaId
        INNER JOIN PesoSubIndicadores psi ON psi.SubIndicadorId = sie.SubIndicadorId
        INNER JOIN Mantenimiento.SubIndicadores si_p ON si_p.Id = sie.SubIndicadorId
        INNER JOIN Mantenimiento.Indicadores i ON i.Id = si_p.IndicadorId
        LEFT JOIN Mantenimiento.TiposSubIndicador ti ON ti.Id = si_p.TipoSubIndicadorId 
        LEFT JOIN ConfiguracionCache cfg
            ON cfg.TipoEntidad = 'SubIndicadorEvidencia'
           AND cfg.EntidadId = sie.Id
           AND cfg.CoedomId = psi.CoedomId
        WHERE sie.IsActive = 1 AND sie.IsDeleted = 0
          AND e.IsActive = 1 AND (e.IsDeleted = 0 OR e.IsDeleted IS NULL)
          AND psi.AplicaSub = 1
    ),
    EvidenceTotals AS (
        SELECT 
            SubIndicadorId,
            CoedomId,
            SUM(CASE WHEN TipoSubIndicador = 'ACUMULATIVO' AND AplicaEvidencia = 1 THEN ValorEvidencia ELSE 0 END) AS SumaTotal
        FROM EvidenciasBase
        GROUP BY SubIndicadorId, CoedomId
    ),
    EvidenceValuesAdjusted AS (
        SELECT 
            eb.*,
            ISNULL(et.SumaTotal, 0) AS SumaTotal,
            CASE 
                WHEN eb.TipoSubIndicador = 'ACUMULATIVO' AND eb.AplicaEvidencia = 1 THEN
                    CASE 
                        WHEN et.SumaTotal < 100 AND et.SumaTotal > 0 THEN (100.0 - et.SumaTotal) * (eb.ValorEvidencia * 1.0 / NULLIF(et.SumaTotal, 0))
                        WHEN et.SumaTotal > 100 THEN ((eb.ValorEvidencia * 1.0 / NULLIF(et.SumaTotal, 0)) * 100.0) - eb.ValorEvidencia
                        ELSE 0
                    END
                ELSE 0
            END AS IncrementoAplicado
        FROM EvidenciasBase eb
        INNER JOIN EvidenceTotals et ON et.SubIndicadorId = eb.SubIndicadorId AND et.CoedomId = eb.CoedomId
    ),
    PuntajesEvidenciasFinal AS (
        SELECT 
            eva.SubIndicadorEvidenciaId,
            eva.SubIndicadorId,
            eva.CoedomId,
            eva.PesoSubDistribuido,
            eva.TipoSubIndicador,
            CASE 
                WHEN eva.TipoSubIndicador = 'ACUMULATIVO' THEN 
                    CASE WHEN (ISNULL(UltimaPuntuacion.Calificacion, 0) + ISNULL(eva.IncrementoAplicado, 0)) < 0 THEN 0 
                    ELSE ISNULL(UltimaPuntuacion.Calificacion, 0) + ISNULL(eva.IncrementoAplicado, 0) END 
                ELSE ISNULL(UltimaPuntuacion.Calificacion, 0) 
            END AS PuntajeFinal
        FROM EvidenceValuesAdjusted eva
        OUTER APPLY (
            -- Obtenemos estrictamente la última puntuación del archivo más reciente que sea válido
            SELECT TOP 1 p.Calificacion
            FROM Evidencia.Archivos a
            INNER JOIN Evidencia.Puntuacion p ON p.ArchivoEvidenciaId = a.Id
            INNER JOIN Mantenimiento.EstadoArchivos ea ON a.EstadoArchivoId = ea.Id
            WHERE a.CoedomId = eva.CoedomId 
              AND a.SubIndicadorEvidenciaId = eva.SubIndicadorEvidenciaId 
              AND a.IsActive = 1 AND a.IsDeleted = 0
              AND p.IsActive = 1 AND p.IsDeleted = 0
              AND ea.Nombre NOT IN ('Vencido', 'Rechazado', 'Pendiente')
            ORDER BY a.CreatedAt DESC, p.Id DESC
        ) AS UltimaPuntuacion
        WHERE eva.AplicaEvidencia = 1
    ),
    AvanceSubIndicadores AS (
        SELECT 
            psi.IndicadorId,
            pef.SubIndicadorId,
            pef.CoedomId,
            pef.PesoSubDistribuido,
            CASE 
                WHEN pef.TipoSubIndicador = 'ACUMULATIVO' THEN 
                    CASE WHEN SUM((pef.PuntajeFinal / 100.0) * pef.PesoSubDistribuido) > pef.PesoSubDistribuido THEN pef.PesoSubDistribuido 
                    ELSE SUM((pef.PuntajeFinal / 100.0) * pef.PesoSubDistribuido) END
                WHEN pef.TipoSubIndicador = 'ESCALONADO' THEN 
                    MAX((pef.PuntajeFinal / 100.0) * pef.PesoSubDistribuido)
                ELSE SUM((pef.PuntajeFinal / 100.0) * pef.PesoSubDistribuido)
            END AS AvanceSubWeighted
        FROM PuntajesEvidenciasFinal pef
        INNER JOIN PesoSubIndicadores psi ON psi.SubIndicadorId = pef.SubIndicadorId AND psi.CoedomId = pef.CoedomId
        GROUP BY psi.IndicadorId, pef.SubIndicadorId, pef.CoedomId, pef.PesoSubDistribuido, pef.TipoSubIndicador
    ),
    AvanceIndicadores AS (
        SELECT 
            pi.IndicadorId,
            pi.CoedomId,
            ISNULL(pi.PesoDistribuido, 0) AS PesoDistribuido,
            ISNULL(pi.PesoOriginal, 0) AS PesoOriginal,
            SUM(ISNULL(asi.AvanceSubWeighted, 0)) AS TotalAvanceSub
        FROM PesoIndicadores pi
        LEFT JOIN AvanceSubIndicadores asi ON asi.IndicadorId = pi.IndicadorId AND asi.CoedomId = pi.CoedomId
        WHERE pi.Aplica = 1
        GROUP BY pi.IndicadorId, pi.CoedomId, pi.PesoDistribuido, pi.PesoOriginal
    ),
    ResultadosFinales AS (
         SELECT 
            ai.CoedomId,
            ai.IndicadorId,
            ai.PesoOriginal,
            ai.PesoDistribuido,
            ROUND(
                CASE 
                    WHEN ai.TotalAvanceSub > ai.PesoDistribuido THEN ai.PesoDistribuido 
                    ELSE ai.TotalAvanceSub 
                END, 2
            ) AS PuntajeObtenido
        FROM AvanceIndicadores ai
    )
    SELECT 
        ot.CoedomId,
        ib.IndicadorId,
        ib.Codigo AS CodigoIndicador,
        ib.Nombre AS NombreIndicador,
        ib.Descripcion AS DescripcionIndicador,
        ib.Peso AS PesoOriginal,
        
        -- Peso Distribuido
        CASE 
            WHEN ib.Aplica = 0 OR ib.TipoVencimientoId IS NOT NULL THEN NULL
            ELSE rf.PesoDistribuido
        END AS PesoDistribuido,
        
        -- Porcentaje de avance
        CASE 
            WHEN ib.Aplica = 0 OR ib.TipoVencimientoId IS NOT NULL THEN NULL
            WHEN rf.PesoDistribuido > 0 THEN 
                CAST((ISNULL(rf.PuntajeObtenido, 0) / rf.PesoDistribuido) * 100 AS DECIMAL(5,2))
            ELSE 0
        END AS PorcentajeAvance,
        
        -- Puntaje Obtenido
        CASE 
            WHEN ib.Aplica = 0 OR ib.TipoVencimientoId IS NOT NULL THEN NULL
            ELSE ISNULL(rf.PuntajeObtenido, 0)
        END AS PuntajeObtenido,

        CASE 
            WHEN ib.TipoConfiguracion IS NULL THEN 'Aplica' 
            ELSE ib.TipoConfiguracion 
        END AS Estado
        
    FROM OrganismoTarget ot
    CROSS JOIN IndicadoresBase ib
    LEFT JOIN ResultadosFinales rf
        ON rf.IndicadorId = ib.IndicadorId
       AND rf.CoedomId = ot.CoedomId
    WHERE ib.CoedomId = ot.CoedomId
);

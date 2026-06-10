CREATE   FUNCTION fn_DetalleSubIndicadoresPorIndicador
(
    @IndicadorId INT,
    @CoedomId INT
)
RETURNS TABLE
AS
RETURN
(
    WITH SubIndicadoresCompletos AS (
        SELECT 
            si.Id AS SubIndicadorId,
            si.Codigo AS CodigoSubIndicador,
            si.Nombre AS NombreSubIndicador,
            si.IndicadorId,
            i.Codigo AS CodigoIndicador,
            i.Nombre AS NombreIndicador,
            cfg.AplicaFinal,
            cfg.TipoVencimientoId,
            cfg.TipoConfiguracion
        FROM Mantenimiento.SubIndicadores si
        INNER JOIN Mantenimiento.Indicadores i 
            ON i.Id = si.IndicadorId
        LEFT JOIN fn_ObtenerConfiguracionEntidad_Inline() cfg
            ON cfg.TipoEntidad = 'SubIndicador'
           AND cfg.EntidadId = si.Id
           AND cfg.CoedomId = @CoedomId
        WHERE si.IndicadorId = @IndicadorId
          AND si.IsActive = 1
          AND (si.IsDeleted = 0 OR si.IsDeleted IS NULL)
    ),
    SubIndicadoresDelIndicador AS (
        SELECT 
            si.Id AS SubIndicadorId,
            si.Codigo AS CodigoSubIndicador,
            si.Nombre AS NombreSubIndicador,
            si.TipoSubIndicadorId,
            ti.Nombre AS TipoIndicador
        FROM Mantenimiento.SubIndicadores si
        INNER JOIN Mantenimiento.TiposSubIndicador ti
            ON ti.Id = si.TipoSubIndicadorId
        WHERE si.IndicadorId = @IndicadorId
          AND si.IsActive = 1
          AND (si.IsDeleted = 0 OR si.IsDeleted IS NULL)
    ),
    EvidenciasCompletas AS (
        SELECT 
            sie.Id AS SubIndicadorEvidenciaId,
            sie.SubIndicadorId,
            sie.EvidenciaId,
            e.Valor AS ValorOriginal,
            sd.TipoIndicador,
            cfg.AplicaFinal,
            cfg.TipoVencimientoId
        FROM Evidencia.SubIndicadorEvidencias sie
        INNER JOIN Evidencia.Evidencias e 
            ON e.Id = sie.EvidenciaId
        INNER JOIN SubIndicadoresDelIndicador sd
            ON sd.SubIndicadorId = sie.SubIndicadorId
        LEFT JOIN fn_ObtenerConfiguracionEntidad_Inline() cfg
            ON cfg.TipoEntidad = 'SubIndicadorEvidencia'
           AND cfg.EntidadId = sie.Id
           AND cfg.CoedomId = @CoedomId
        WHERE sie.IsActive = 1
          AND sie.IsDeleted = 0
          AND e.IsActive = 1
          AND (e.IsDeleted = 0 OR e.IsDeleted IS NULL)
    ),
    UltimosArchivosInfo AS (
        SELECT 
            a.Id AS UltimoArchivoId,
            a.SubIndicadorEvidenciaId,
            a.CreatedAt AS FechaSubida,
            ROW_NUMBER() OVER (
                PARTITION BY a.SubIndicadorEvidenciaId 
                ORDER BY a.CreatedAt DESC, a.Id DESC
            ) AS rn
        FROM Evidencia.Archivos a
        INNER JOIN Mantenimiento.EstadoArchivos ea 
            ON a.EstadoArchivoId = ea.Id
        WHERE a.CoedomId = @CoedomId
          AND a.IsActive = 1
          AND a.IsDeleted = 0
          AND ea.Nombre NOT IN ('Vencido', 'Rechazado', 'Pendiente')
    ),
    UltimasPuntuaciones AS (
        SELECT 
            p.ArchivoEvidenciaId,
            p.Calificacion,
            ROW_NUMBER() OVER (
                PARTITION BY p.ArchivoEvidenciaId 
                ORDER BY p.CreatedAt DESC, p.Id DESC
            ) AS rn
        FROM Evidencia.Puntuacion p
        WHERE p.IsActive = 1
          AND p.IsDeleted = 0
    ),
    PuntajesCalculados AS (
        SELECT 
            ec.SubIndicadorId,
            ec.SubIndicadorEvidenciaId,
            ec.TipoIndicador,
            -- Asignar puntaje bruto (sobre 100)
            CASE 
                WHEN ec.AplicaFinal = 0 OR ec.TipoVencimientoId IS NOT NULL THEN 0
                ELSE ISNULL(up.Calificacion, 0)
            END AS Puntaje
        FROM EvidenciasCompletas ec
        LEFT JOIN UltimosArchivosInfo ua
            ON ua.SubIndicadorEvidenciaId = ec.SubIndicadorEvidenciaId
           AND ua.rn = 1
        LEFT JOIN UltimasPuntuaciones up
            ON up.ArchivoEvidenciaId = ua.UltimoArchivoId
           AND up.rn = 1
    ),
    PuntajesValidos AS (
        SELECT 
            SubIndicadorId,
            CASE 
                WHEN UPPER(MAX(TipoIndicador)) = 'ACUMULATIVO' THEN 
                    CASE WHEN SUM(Puntaje) > 100.0 THEN 100.0 ELSE SUM(Puntaje) END
                WHEN UPPER(MAX(TipoIndicador)) = 'ESCALONADO' THEN 
                    MAX(Puntaje)
                ELSE SUM(Puntaje)
            END AS SumaPuntajes,
            COUNT(SubIndicadorEvidenciaId) AS TotalEvidencias
        FROM PuntajesCalculados
        GROUP BY SubIndicadorId
    ),
    PesosDistribuidos AS (
        SELECT 
            Id AS SubIndicadorId,
            PesoDistribuido
        FROM fn_PesoDistribuidoSubIndicadores_Inline()
        WHERE IndicadorId = @IndicadorId
          AND CoedomId = @CoedomId
    ),
    AvancesCalculados AS (
        SELECT 
            SubIndicadorId,
            Avance
        FROM fn_AvanceSubIndicador_Inline()
        WHERE SubIndicadorId IN (
            SELECT SubIndicadorId 
            FROM SubIndicadoresCompletos
        )
          AND CoedomId = @CoedomId
    )
    SELECT 
        si.SubIndicadorId,
        si.CodigoSubIndicador,
        si.NombreSubIndicador,
        si.CodigoIndicador,
        si.NombreIndicador,
        sd.TipoIndicador AS TipoSubIndicador,
        
        -- Estado del subindicador
        ISNULL(si.TipoConfiguracion, 'Aplica') AS Estado,
        
        -- SumaPuntajes (Acumulado o Escalonado)
        CASE 
            WHEN si.AplicaFinal = 0 OR si.TipoVencimientoId IS NOT NULL THEN NULL
            ELSE ISNULL(pv.SumaPuntajes, 0)
        END AS SumaPuntajes,
        
        -- TotalEvidencias
        CASE 
            WHEN si.AplicaFinal = 0 OR si.TipoVencimientoId IS NOT NULL THEN NULL
            ELSE ISNULL(pv.TotalEvidencias, 0)
        END AS TotalEvidencias,
        
        -- ✅ PuntajePonderado = (SumaPuntajes / 100) * PesoDistribuido
        CASE 
            WHEN si.AplicaFinal = 0 OR si.TipoVencimientoId IS NOT NULL THEN NULL
            WHEN pd.PesoDistribuido IS NULL OR pv.SumaPuntajes IS NULL THEN 0
            ELSE CAST((pv.SumaPuntajes / 100.0) * pd.PesoDistribuido AS DECIMAL(10,2))
        END AS Resultado,
        
        -- PesoDistribuido
        CASE 
            WHEN si.AplicaFinal = 0 OR si.TipoVencimientoId IS NOT NULL THEN NULL
            ELSE CAST(pd.PesoDistribuido AS DECIMAL(5,2))
        END AS PesoDistribuido,
        
        -- AvanceObtenido
        CASE 
            WHEN si.AplicaFinal = 0 OR si.TipoVencimientoId IS NOT NULL THEN NULL
            ELSE ISNULL(ac.Avance, 0)
        END AS AvanceObtenido
        
    FROM SubIndicadoresCompletos si
    LEFT JOIN SubIndicadoresDelIndicador sd
        ON sd.SubIndicadorId = si.SubIndicadorId
    LEFT JOIN PuntajesValidos pv
        ON pv.SubIndicadorId = si.SubIndicadorId
    LEFT JOIN PesosDistribuidos pd
        ON pd.SubIndicadorId = si.SubIndicadorId
    LEFT JOIN AvancesCalculados ac
        ON ac.SubIndicadorId = si.SubIndicadorId
);

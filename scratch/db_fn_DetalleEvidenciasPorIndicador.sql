-- =======================================================================
-- Nombre de la Función: dbo.fn_DetalleEvidenciasPorIndicador
-- Modificación: Soporte de vencimiento Fijo (TipoVencimientoId = 3) 
--              y COALESCE para evidencias sin envíos (no vacías).
-- =======================================================================

CREATE   FUNCTION [dbo].[fn_DetalleEvidenciasPorIndicador]
(
    @IndicadorId INT,
    @CoedomId INT
)
RETURNS TABLE
AS
RETURN
(
    WITH SubIndicadoresDelIndicador AS (
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
            e.Nombre AS NombreEvidencia,
            e.Descripcion AS DescripcionEvidencia,
            e.Valor AS ValorOriginal,
            sd.CodigoSubIndicador,
            sd.NombreSubIndicador,
            sd.TipoIndicador,
            cfg.AplicaFinal,
            cfg.TipoVencimientoId,
            cfg.TipoConfiguracion,
            cfg.FechaVencimiento AS FechaVencimientoException,
            sie.FechaVenciento AS FechaVencimientoBase
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
            a.NombreOriginal AS NombreArchivo,
            a.CreatedAt AS FechaSubida,
            COALESCE(fv.FechaVencimiento, sie.FechaVenciento) AS FechaVencimiento,
            sie.CreatedAt AS SieCreatedAt,
            sie.FechaVenciento AS SieFechaVencimiento,
            fv.PeriodicidadDias,
            fv.Id AS FechaVencimientoRelacionId,
            fv.TipoVencimientoId, -- Seleccionamos el Tipo de Vencimiento de la evidencia
            ea.Nombre AS EstadoArchivo,
            ROW_NUMBER() OVER (
                PARTITION BY a.SubIndicadorEvidenciaId 
                ORDER BY a.CreatedAt DESC, a.Id DESC
            ) AS rn
        FROM Evidencia.Archivos a
        INNER JOIN Mantenimiento.EstadoArchivos ea 
            ON a.EstadoArchivoId = ea.Id
        INNER JOIN Evidencia.SubIndicadorEvidencias sie
            ON sie.Id = a.SubIndicadorEvidenciaId
        LEFT JOIN Evidencia.FechaVencimientoSubIndicadorEvidencias fv
            ON fv.Id = sie.FechaVencimientoSubIndicadorEvidenciaId
           AND fv.IsActive = 1
           AND fv.IsDeleted = 0
        WHERE a.CoedomId = @CoedomId
          AND a.IsActive = 1
          AND a.IsDeleted = 0
    ),
    UltimasRevisiones AS (
        SELECT 
            re.ArchivoEvidenciaId,
            CONCAT(ISNULL(u.Nombre, ''), ' ', ISNULL(u.Apellido, '')) AS RevisadoPor,
            re.FechaRevisionConcluida,
            ROW_NUMBER() OVER (
                PARTITION BY re.ArchivoEvidenciaId 
                ORDER BY 
                    ISNULL(re.FechaRevisionConcluida, re.CreatedAt) DESC,
                    re.Id DESC
            ) AS rn
        FROM Evidencia.RevisionEvidencias re
        LEFT JOIN Usuario.Usuarios u
            ON u.Id = re.UsuarioId
        WHERE re.IsActive = 1
          AND re.IsDeleted = 0
    ),
    UltimasPuntuaciones AS (
        SELECT 
            p.ArchivoEvidenciaId,
            p.Calificacion,
            CONCAT(ISNULL(u.Nombre, ''), ' ', ISNULL(u.Apellido, '')) AS PuntuadoPor,
            p.CreatedAt AS FechaPuntuacion,
            ROW_NUMBER() OVER (
                PARTITION BY p.ArchivoEvidenciaId 
                ORDER BY p.CreatedAt DESC, p.Id DESC
            ) AS rn
        FROM Evidencia.Puntuacion p
        LEFT JOIN Usuario.Usuarios u
            ON u.Id = p.PuntuadorUsuarioId
        WHERE p.IsActive = 1
          AND p.IsDeleted = 0
    )
    SELECT 
        ec.SubIndicadorId,
        ec.SubIndicadorEvidenciaId,
        ec.NombreEvidencia,
        
        -- Valor Original
        CASE 
            WHEN ec.AplicaFinal = 0 THEN NULL
            WHEN ec.TipoConfiguracion = 'Inactivo Temporalmente' THEN NULL
            ELSE ec.ValorOriginal
        END AS Valor,
        
        -- Fecha de Vencimiento (prioriza tabla de vencimientos y respeta TipoVencimientoId = 3 Fijo)
        CASE 
            WHEN ec.TipoConfiguracion = 'Inactivo Temporalmente' THEN ec.FechaVencimientoException
            WHEN ec.TipoConfiguracion = 'Extensión de fecha de plazo' THEN ec.FechaVencimientoException
            WHEN ec.AplicaFinal = 0 THEN NULL
            WHEN ec.TipoVencimientoId IS NOT NULL THEN NULL
            -- Si está aprobada (tiene calificación)
            WHEN up.Calificacion IS NOT NULL THEN 
                CASE 
                    -- Si es de tipo Fijo (TipoVencimientoId = 3), usar la FechaVencimiento directamente
                    WHEN ua.TipoVencimientoId = 3 THEN ua.FechaVencimiento
                    -- Si no, usar la lógica estándar de sumar la periodicidad (Automático)
                    WHEN ua.FechaVencimientoRelacionId IS NOT NULL THEN
                         DATEADD(day, ISNULL(ua.PeriodicidadDias, 0), up.FechaPuntuacion)
                    ELSE
                         DATEADD(day, DATEDIFF(day, ua.SieCreatedAt, ua.SieFechaVencimiento), up.FechaPuntuacion)
                END
            ELSE COALESCE(ua.FechaVencimiento, ec.FechaVencimientoBase)
        END AS FechaVencimiento,
        
        -- Verificado Por
        CASE 
            WHEN ec.AplicaFinal = 0 THEN NULL
            WHEN ec.TipoConfiguracion = 'Inactivo Temporalmente' THEN NULL
            WHEN up.Calificacion IS NOT NULL THEN 
                up.PuntuadoPor
            WHEN ua.EstadoArchivo IN ('En Revisión', 'Revision', 'Rechazado') THEN 
                ur.RevisadoPor
            ELSE NULL
        END AS VerificadoPor,
        
        -- Calificación
        CASE 
            WHEN ec.AplicaFinal = 0 THEN NULL
            WHEN ec.TipoConfiguracion = 'Inactivo Temporalmente' THEN NULL
            ELSE up.Calificacion
        END AS Calificacion,
        
        -- Estado
        CASE 
            WHEN ec.TipoConfiguracion = 'NO Aplica' OR ec.TipoConfiguracion = 'No Aplica' THEN 'No Aplica'
            WHEN ec.TipoConfiguracion = 'Inactivo Temporalmente' THEN 'Inactivo Temporalmente'
            WHEN ec.TipoConfiguracion = 'Extensión de fecha de plazo' AND ua.EstadoArchivo IS NOT NULL AND ua.EstadoArchivo <> 'Pendiente' THEN
                ua.EstadoArchivo
            WHEN ec.TipoConfiguracion = 'Extensión de fecha de plazo' THEN 'Extensión de fecha de plazo'
            WHEN ec.AplicaFinal = 0 THEN 'No Aplica'
            WHEN ua.EstadoArchivo = 'Pendiente' THEN 'Enviado'
            ELSE ISNULL(ua.EstadoArchivo, 'Pendiente')
        END AS Estado
        
    FROM EvidenciasCompletas ec
    LEFT JOIN UltimosArchivosInfo ua
        ON ua.SubIndicadorEvidenciaId = ec.SubIndicadorEvidenciaId
       AND ua.rn = 1
    LEFT JOIN UltimasRevisiones ur
        ON ur.ArchivoEvidenciaId = ua.UltimoArchivoId
       AND ur.rn = 1
    LEFT JOIN UltimasPuntuaciones up
        ON up.ArchivoEvidenciaId = ua.UltimoArchivoId
       AND up.rn = 1
);

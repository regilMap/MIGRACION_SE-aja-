CREATE   FUNCTION fn_RankingSubIndicadoresV2_Inline()
RETURNS TABLE
AS
RETURN
(
    WITH ConfigData AS (
         -- Carga unica de configuracion
         SELECT EntidadId, CoedomId, AplicaFinal, TipoVencimientoId
         FROM Cache.ConfiguracionEntidad
         WHERE TipoEntidad = 'SubIndicador'
    ),
    Organismos AS (
        SELECT OrganismoID as CoedomId 
        FROM [SISMAP_EDUCACION].[dbo].[vOrganismosEducacionX] 
        WHERE Descripcion = 'Escuelas'
    ),
    BaseSubIndicadores AS (
        SELECT 
            si.Id as SubIndicadorId,
            si.Codigo,
            si.Nombre,
            o.CoedomId,
            ISNULL(cfg.AplicaFinal, 1) as Aplica, -- Default 1
            cfg.TipoVencimientoId
        FROM Mantenimiento.SubIndicadores si
        CROSS JOIN Organismos o
        LEFT JOIN ConfigData cfg ON cfg.EntidadId = si.Id AND cfg.CoedomId = o.CoedomId
        WHERE si.IsActive = 1 AND (si.IsDeleted = 0 OR si.IsDeleted IS NULL)
    ),
    -- Optimizacion critica: Obtener Estado solo si aplica y no tiene excepcion, en un solo pass
    EstadoArchivosRaw AS (
         SELECT 
             sie.SubIndicadorId,
             a.CoedomId,
             MAX(a.Id) as MaxArchivoId -- Solo necesitamos saber si existe algun archivo valido
         FROM Evidencia.Archivos a
         JOIN Evidencia.SubIndicadorEvidencias sie ON sie.Id = a.SubIndicadorEvidenciaId
         JOIN Mantenimiento.EstadoArchivos ea ON ea.Id = a.EstadoArchivoId
         WHERE a.IsDeleted = 0 AND a.IsActive = 1
           AND ea.Nombre NOT IN ('Vencida', 'Rechazado', 'Pendiente')
         GROUP BY sie.SubIndicadorId, a.CoedomId
    ),
    Avances AS (
        -- Usamos la version optimizada
        SELECT SubIndicadorId, CoedomId, Avance
        FROM fn_AvanceSubIndicador_Optimized() 
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
        LEFT JOIN Cache.ConfiguracionEntidad cfg 
            ON cfg.TipoEntidad = 'SubIndicadorEvidencia' 
            AND cfg.EntidadId = sie.Id 
            AND cfg.CoedomId = o.CoedomId
        WHERE sie.IsActive = 1 AND (sie.IsDeleted = 0 OR sie.IsDeleted IS NULL)
        GROUP BY sie.SubIndicadorId, o.CoedomId
    ),
    CalculoEstados AS (
        SELECT 
            si.SubIndicadorId,
            si.Codigo,
            si.Nombre,
            si.CoedomId,
            CASE
                WHEN si.Aplica = 0 THEN 'NoAplica'
                WHEN si.TipoVencimientoId IS NOT NULL THEN 'InactivoTemporal'
                WHEN ec.TotalEvidencias > 0 AND ec.EvidenciasNoAplica = ec.TotalEvidencias THEN 'NoAplica'
                WHEN ec.TotalEvidencias > 0 AND ec.EvidenciasExceptuadas = ec.TotalEvidencias AND ec.EvidenciasInactivas > 0 THEN 'InactivoTemporal'
                WHEN ear.MaxArchivoId IS NULL THEN 'NoRemitido'
                WHEN ISNULL(av.Avance, 0) >= 80 THEN 'Verde'
                WHEN ISNULL(av.Avance, 0) >= 60 THEN 'Amarillo'
                ELSE 'Rojo'
            END AS Estado
        FROM BaseSubIndicadores si
        LEFT JOIN EstadoArchivosRaw ear ON ear.SubIndicadorId = si.SubIndicadorId AND ear.CoedomId = si.CoedomId
        LEFT JOIN Avances av ON av.SubIndicadorId = si.SubIndicadorId AND av.CoedomId = si.CoedomId
        LEFT JOIN EvidenciasConfig ec ON ec.SubIndicadorId = si.SubIndicadorId AND ec.CoedomId = si.CoedomId
    )
    SELECT 
        ROW_NUMBER() OVER (ORDER BY Codigo) AS Posicion,
        Codigo,
        SubIndicadorId,
        Nombre,
        SUM(CASE WHEN Estado = 'Verde' THEN 1 ELSE 0 END) AS Verde,
        SUM(CASE WHEN Estado = 'Amarillo' THEN 1 ELSE 0 END) AS Amarillo,
        SUM(CASE WHEN Estado = 'Rojo' THEN 1 ELSE 0 END) + 
        SUM(CASE WHEN Estado = 'NoRemitido' THEN 1 ELSE 0 END) AS Rojo,
        SUM(CASE WHEN Estado = 'InactivoTemporal' THEN 1 ELSE 0 END) AS InactivoTemporal,
        SUM(CASE WHEN Estado = 'NoAplica' THEN 1 ELSE 0 END) AS NoAplica,
        COUNT(*) AS Total,
        SUM(CASE WHEN Estado = 'NoRemitido' THEN 1 ELSE 0 END) AS NoRemitido
    FROM CalculoEstados
    GROUP BY Codigo, Nombre, SubIndicadorId
);

-- =======================================================================
-- Nombre del Stored Procedure: dbo.SP_ActualizarArchivosVencidos
-- Modificación: Respetar fecha fija de vencimiento (Tipo = 3) y Manual (Tipo = 2)
--              en vez de tratarlas de forma dinámica como periodicidad.
--              Tipo Automático (Tipo = 1) sí usa periodicidad.
-- =======================================================================

CREATE OR ALTER PROCEDURE [dbo].[SP_ActualizarArchivosVencidos]
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Actualizar archivos vencidos
        -- Solo se actualizan archivos en estado Aprobado (3) que tienen puntuación
        UPDATE A
        SET
            A.EstadoArchivoId = 13, -- Estado Vencido
            A.UpdatedAt = GETDATE()
        FROM
            [Evidencia].[Archivos] A
        INNER JOIN
            [Evidencia].[SubIndicadorEvidencias] SE ON A.SubIndicadorEvidenciaId = SE.Id
        LEFT JOIN
            [Evidencia].[FechaVencimientoSubIndicadorEvidencias] FV ON SE.FechaVencimientoSubIndicadorEvidenciaId = FV.Id
        LEFT JOIN
            [Mantenimiento].[ConfiguracionOrganismoExcepcion] COE ON
                A.CoedomId = COE.CoedomId
                AND COE.IsActive = 1
                AND COE.Aplica = 1
                AND COE.FechaExtension IS NOT NULL
                -- Verificar que la excepción aplica para SubIndicadorEvidencia (TipoEntidadId apropiado)
                AND (
                    (COE.TipoEntidadId IN (SELECT Id FROM [Mantenimiento].[TipoEntidad] WHERE TablaDestino = 'SubIndicadorEvidencia') AND COE.EntidadId = SE.Id)
                    OR (COE.TipoEntidadId IN (SELECT Id FROM [Mantenimiento].[TipoEntidad] WHERE TablaDestino = 'SubIndicador') AND COE.EntidadId = SE.SubIndicadorId)
                )
        -- Obtener la fecha de la última puntuación del archivo
        CROSS APPLY (
            SELECT TOP 1 P.CreatedAt AS FechaPuntuacion
            FROM [Evidencia].[Puntuacion] P
            WHERE P.ArchivoEvidenciaId = A.Id
            ORDER BY P.CreatedAt DESC
        ) UP
        WHERE
            -- Solo archivos en estado Aprobado
            A.EstadoArchivoId = 3

            -- Determinar si está vencido según el tipo de vencimiento
            AND (
                -- Caso 1: Tipo Fijo (3) y Tipo Manual (2)
                -- Se vencen si la fecha de hoy supera la fecha de vencimiento configurada/seleccionada (+ extensión)
                (
                    FV.TipoVencimientoId IN (2, 3)
                    AND CAST(GETDATE() AS DATE) >= CAST(
                        DATEADD(
                            DAY, 
                            COALESCE(DATEDIFF(DAY, COE.createdAt, COE.FechaExtension), 0), 
                            FV.FechaVencimiento
                        ) AS DATE
                    )
                )
                OR
                -- Caso 2: Tipo Automático (1) u otros
                -- Se vence si han transcurrido más días que la periodicidad (+ extensión) desde la fecha de puntuación
                (
                    ISNULL(FV.TipoVencimientoId, 1) NOT IN (2, 3)
                    AND DATEDIFF(DAY, UP.FechaPuntuacion, GETDATE()) >= (
                        CASE 
                            WHEN FV.Id IS NOT NULL THEN ISNULL(FV.PeriodicidadDias, 0)
                            ELSE DATEDIFF(DAY, SE.CreatedAt, SE.FechaVenciento)
                        END
                        + COALESCE(DATEDIFF(DAY, COE.createdAt, COE.FechaExtension), 0)
                    )
                )
            );

        -- Obtener el número de archivos actualizados
        DECLARE @FilasAfectadas INT = @@ROWCOUNT;

        COMMIT TRANSACTION;

        -- Retornar información sobre la ejecución
        SELECT
            @FilasAfectadas AS ArchivosActualizados,
            GETDATE() AS FechaEjecucion,
            'Proceso completado exitosamente' AS Mensaje;

    END TRY
    BEGIN CATCH
        -- Si hay error, revertir la transacción
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        -- Retornar información del error
        SELECT
            ERROR_NUMBER() AS ErrorNumero,
            ERROR_SEVERITY() AS ErrorSeveridad,
            ERROR_STATE() AS ErrorEstado,
            ERROR_PROCEDURE() AS ErrorProcedimiento,
            ERROR_LINE() AS ErrorLinea,
            ERROR_MESSAGE() AS ErrorMensaje;

        -- Re-lanzar el error
        THROW;
    END CATCH
END;

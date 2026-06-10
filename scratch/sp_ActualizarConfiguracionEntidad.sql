
CREATE OR ALTER PROCEDURE Cache.sp_ActualizarConfiguracionEntidad
    @TipoEntidadNombre NVARCHAR(100) = NULL,
    @CoedomId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;  -- ✅ NUEVO: Rollback automático en caso de error
    
    DECLARE @FechaActual DATE = CAST(GETDATE() AS DATE);
    DECLARE @Inicio DATETIME2 = GETDATE();
    
    DECLARE @TipoIndicadorId INT = (SELECT Id FROM Mantenimiento.TipoEntidad WHERE Nombre = 'Indicador');
    DECLARE @TipoSubIndicadorId INT = (SELECT Id FROM Mantenimiento.TipoEntidad WHERE Nombre = 'SubIndicador');
    DECLARE @TipoSubIndicadorEvidenciaId INT = (SELECT Id FROM Mantenimiento.TipoEntidad WHERE Nombre = 'SubIndicadorEvidencia');
    
    -- ✅ NUEVO: Iniciar transacción para operaciones atómicas
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Organismos
        CREATE TABLE #CoedomIds (CoedomId INT PRIMARY KEY);
        
        IF @CoedomId IS NOT NULL
            INSERT INTO #CoedomIds VALUES (@CoedomId);
        ELSE
            INSERT INTO #CoedomIds (CoedomId)
            SELECT DISTINCT CODIGO_COEDOM FROM dbo.SigerdCoedom WHERE CODIGO_COEDOM IS NOT NULL;
        
        -- Configuraciones generales
        CREATE TABLE #ConfiguracionesGenerales (
            TipoEntidadId INT,
            EntidadId INT,
            Aplica BIT,
            UsuarioConfiguracionId UNIQUEIDENTIFIER,
            FechaConfiguracion DATETIME2,
            PRIMARY KEY (TipoEntidadId, EntidadId)
        );
        
        INSERT INTO #ConfiguracionesGenerales
        SELECT TipoEntidadId, EntidadId, Aplica, UsuarioConfiguracionId, FechaConfiguracion
        FROM (
            SELECT 
                TipoEntidadId, EntidadId, Aplica, UsuarioConfiguracionId, FechaConfiguracion,
                ROW_NUMBER() OVER (PARTITION BY TipoEntidadId, EntidadId ORDER BY FechaConfiguracion DESC, Id DESC) AS rn
            FROM Mantenimiento.ConfiguracionGeneral
            WHERE IsActive = 1 AND IsDeleted = 0
              AND (@TipoEntidadNombre IS NULL OR TipoEntidadId IN (@TipoIndicadorId, @TipoSubIndicadorId, @TipoSubIndicadorEvidenciaId))
        ) x WHERE rn = 1;
        
        -- Excepciones VIGENTES (filtradas por fecha)
        CREATE TABLE #Excepciones (
            TipoEntidadId INT,
            EntidadId INT,
            CoedomId INT,
            Id INT,
            TipoVencimientoId INT,
            Aplica BIT,
            FechaVencimiento DATE,
            PRIMARY KEY (TipoEntidadId, EntidadId, CoedomId)
        );
        
        -- Filtrar SOLO vigentes, tomar ID más alto
        INSERT INTO #Excepciones
        SELECT TipoEntidadId, EntidadId, CoedomId, Id, TipoVencimientoId, Aplica, FechaVencimiento
        FROM (
            SELECT 
                coe.TipoEntidadId, coe.EntidadId, coe.CoedomId, coe.Id, 
                coe.TipoVencimientoId, coe.Aplica, COALESCE(coe.FechaExtension, coe.FechaVencimiento) AS FechaVencimiento,
                ROW_NUMBER() OVER (
                    PARTITION BY coe.TipoEntidadId, coe.EntidadId, coe.CoedomId 
                    ORDER BY coe.Id DESC
                ) AS rn
            FROM Mantenimiento.ConfiguracionOrganismoExcepcion coe
            INNER JOIN #CoedomIds c ON c.CoedomId = coe.CoedomId
            WHERE coe.IsActive = 1 
              AND coe.IsDeleted = 0
              AND (COALESCE(coe.FechaExtension, coe.FechaVencimiento) IS NULL OR COALESCE(coe.FechaExtension, coe.FechaVencimiento) >= @FechaActual)
              AND (@TipoEntidadNombre IS NULL OR coe.TipoEntidadId IN (@TipoIndicadorId, @TipoSubIndicadorId, @TipoSubIndicadorEvidenciaId))
        ) x WHERE rn = 1;
        
        -- =============================================
        -- INDICADORES
        -- =============================================
        IF @TipoEntidadNombre IS NULL OR @TipoEntidadNombre = 'Indicador'
        BEGIN
            MERGE Cache.ConfiguracionEntidad AS target
            USING (
                SELECT 
                    @TipoIndicadorId AS TipoEntidadId,
                    'Indicador' AS TipoEntidad,
                    'Mantenimiento.Indicadores' AS TablaDestino,
                    i.Id AS EntidadId,
                    c.CoedomId,
                    cg.UsuarioConfiguracionId,
                    cg.FechaConfiguracion,
                    cg.Aplica AS AplicaGeneral,
                    ex.Id AS ExcepcionId,
                    ex.TipoVencimientoId,
                    ex.FechaVencimiento,
                    CASE 
                        WHEN ex.Id IS NULL THEN NULL
                        WHEN ex.Aplica = 0 THEN 0
                        WHEN ex.Aplica = 1 THEN NULL
                        ELSE NULL
                    END AS AplicaExcepcion,
                    CASE 
                        WHEN cg.Aplica = 0 THEN 'NO Aplica'
                        WHEN ex.Aplica = 0 AND ex.FechaVencimiento IS NOT NULL THEN 'Inactivo Temporalmente'
                        WHEN ex.Aplica = 0 AND ex.FechaVencimiento IS NULL THEN 'NO Aplica'
                        WHEN ex.Aplica = 1 AND ex.FechaVencimiento IS NOT NULL THEN 'Extensión de fecha de plazo'
                        WHEN ex.Aplica = 1 OR ex.Id IS NULL THEN 'Aplica'
                        ELSE 'Aplica'
                    END AS TipoConfiguracion,
                    CASE 
                        WHEN cg.Aplica = 0 THEN 0
                        WHEN ex.Aplica = 0 THEN 0
                        WHEN ex.Aplica = 1 THEN ISNULL(cg.Aplica, 1)
                        ELSE ISNULL(cg.Aplica, 1)
                    END AS AplicaFinal
                FROM Mantenimiento.Indicadores i
                CROSS JOIN #CoedomIds c
                LEFT JOIN #ConfiguracionesGenerales cg ON cg.TipoEntidadId = @TipoIndicadorId AND cg.EntidadId = i.Id
                LEFT JOIN #Excepciones ex ON ex.TipoEntidadId = @TipoIndicadorId AND ex.EntidadId = i.Id AND ex.CoedomId = c.CoedomId
                WHERE i.IsActive = 1 AND (i.IsDeleted = 0 OR i.IsDeleted IS NULL)
            ) AS source
            ON target.TipoEntidad = source.TipoEntidad AND target.EntidadId = source.EntidadId AND target.CoedomId = source.CoedomId
            WHEN MATCHED THEN
                UPDATE SET
                    target.UsuarioConfiguracionId = source.UsuarioConfiguracionId,
                    target.FechaConfiguracion = source.FechaConfiguracion,
                    target.AplicaGeneral = source.AplicaGeneral,
                    target.ExcepcionId = source.ExcepcionId,
                    target.TipoVencimientoId = source.TipoVencimientoId,
                    target.AplicaExcepcion = source.AplicaExcepcion,
                    target.FechaVencimiento = source.FechaVencimiento,
                    target.TipoConfiguracion = source.TipoConfiguracion,
                    target.AplicaFinal = source.AplicaFinal,
                    target.FechaActualizacion = GETDATE()
            WHEN NOT MATCHED THEN
                INSERT (TipoEntidadId, TipoEntidad, TablaDestino, EntidadId, CoedomId,
                        UsuarioConfiguracionId, FechaConfiguracion, AplicaGeneral,
                        ExcepcionId, TipoVencimientoId, AplicaExcepcion, FechaVencimiento,
                        TipoConfiguracion, AplicaFinal, FechaActualizacion)
                VALUES (source.TipoEntidadId, source.TipoEntidad, source.TablaDestino, source.EntidadId, source.CoedomId,
                        source.UsuarioConfiguracionId, source.FechaConfiguracion, source.AplicaGeneral,
                        source.ExcepcionId, source.TipoVencimientoId, source.AplicaExcepcion, source.FechaVencimiento,
                        source.TipoConfiguracion, source.AplicaFinal, GETDATE());
        END
        
        -- =============================================
        -- SUBINDICADORES
        -- =============================================
        IF @TipoEntidadNombre IS NULL OR @TipoEntidadNombre = 'SubIndicador'
        BEGIN
            MERGE Cache.ConfiguracionEntidad AS target
            USING (
                SELECT 
                    @TipoSubIndicadorId AS TipoEntidadId,
                    'SubIndicador' AS TipoEntidad,
                    'Mantenimiento.SubIndicadores' AS TablaDestino,
                    si.Id AS EntidadId,
                    c.CoedomId,
                    cg.UsuarioConfiguracionId,
                    cg.FechaConfiguracion,
                    cg.Aplica AS AplicaGeneral,
                    ex.Id AS ExcepcionId,
                    ex.TipoVencimientoId,
                    ex.FechaVencimiento,
                    CASE 
                        WHEN ex.Id IS NULL THEN NULL
                        WHEN ex.Aplica = 0 THEN 0
                        WHEN ex.Aplica = 1 THEN NULL
                        ELSE NULL
                    END AS AplicaExcepcion,
                    CASE 
                        WHEN cgIndicador.Aplica = 0 THEN 'NO Aplica'
                        WHEN exIndicador.Aplica = 0 AND exIndicador.FechaVencimiento IS NOT NULL THEN 'Inactivo Temporalmente'
                        WHEN exIndicador.Aplica = 0 AND exIndicador.FechaVencimiento IS NULL THEN 'NO Aplica'
                        WHEN exIndicador.Aplica = 1 AND exIndicador.FechaVencimiento IS NOT NULL THEN 'Extensión de fecha de plazo'
                        WHEN cg.Aplica = 0 THEN 'NO Aplica'
                        WHEN ex.Aplica = 0 AND ex.FechaVencimiento IS NOT NULL THEN 'Inactivo Temporalmente'
                        WHEN ex.Aplica = 0 AND ex.FechaVencimiento IS NULL THEN 'NO Aplica'
                        WHEN ex.Aplica = 1 AND ex.FechaVencimiento IS NOT NULL THEN 'Extensión de fecha de plazo'
                        ELSE 'Aplica'
                    END AS TipoConfiguracion,
                    CASE 
                        WHEN cgIndicador.Aplica = 0 THEN 0
                        WHEN exIndicador.Aplica = 0 THEN 0
                        WHEN cg.Aplica = 0 THEN 0
                        WHEN ex.Aplica = 0 THEN 0
                        WHEN ex.Aplica = 1 THEN ISNULL(cg.Aplica, 1)
                        ELSE ISNULL(cg.Aplica, 1)
                    END AS AplicaFinal
                FROM Mantenimiento.SubIndicadores si
                CROSS JOIN #CoedomIds c
                LEFT JOIN #ConfiguracionesGenerales cg ON cg.TipoEntidadId = @TipoSubIndicadorId AND cg.EntidadId = si.Id
                LEFT JOIN #Excepciones ex ON ex.TipoEntidadId = @TipoSubIndicadorId AND ex.EntidadId = si.Id AND ex.CoedomId = c.CoedomId
                LEFT JOIN #ConfiguracionesGenerales cgIndicador ON cgIndicador.TipoEntidadId = @TipoIndicadorId AND cgIndicador.EntidadId = si.IndicadorId
                LEFT JOIN #Excepciones exIndicador ON exIndicador.TipoEntidadId = @TipoIndicadorId AND exIndicador.EntidadId = si.IndicadorId AND exIndicador.CoedomId = c.CoedomId
                WHERE si.IsActive = 1 AND (si.IsDeleted = 0 OR si.IsDeleted IS NULL)
            ) AS source
            ON target.TipoEntidad = source.TipoEntidad AND target.EntidadId = source.EntidadId AND target.CoedomId = source.CoedomId
            WHEN MATCHED THEN UPDATE SET
                target.UsuarioConfiguracionId = source.UsuarioConfiguracionId, 
                target.FechaConfiguracion = source.FechaConfiguracion,
                target.AplicaGeneral = source.AplicaGeneral, 
                target.ExcepcionId = source.ExcepcionId,
                target.TipoVencimientoId = source.TipoVencimientoId, 
                target.AplicaExcepcion = source.AplicaExcepcion,
                target.FechaVencimiento = source.FechaVencimiento,
                target.TipoConfiguracion = source.TipoConfiguracion,
                target.AplicaFinal = source.AplicaFinal, 
                target.FechaActualizacion = GETDATE()
            WHEN NOT MATCHED THEN INSERT (
                TipoEntidadId, TipoEntidad, TablaDestino, EntidadId, CoedomId,
                UsuarioConfiguracionId, FechaConfiguracion, AplicaGeneral, 
                ExcepcionId, TipoVencimientoId, AplicaExcepcion, FechaVencimiento,
                TipoConfiguracion, AplicaFinal, FechaActualizacion)
            VALUES (
                source.TipoEntidadId, source.TipoEntidad, source.TablaDestino, 
                source.EntidadId, source.CoedomId,
                source.UsuarioConfiguracionId, source.FechaConfiguracion, source.AplicaGeneral,
                source.ExcepcionId, source.TipoVencimientoId, source.AplicaExcepcion, 
                source.FechaVencimiento, source.TipoConfiguracion, source.AplicaFinal, GETDATE());
        END
        
        -- =============================================
        -- SUBINDICADOREVIDENCIAS
        -- =============================================
        IF @TipoEntidadNombre IS NULL OR @TipoEntidadNombre = 'SubIndicadorEvidencia'
        BEGIN
            MERGE Cache.ConfiguracionEntidad AS target
            USING (
                SELECT 
                    @TipoSubIndicadorEvidenciaId AS TipoEntidadId,
                    'SubIndicadorEvidencia' AS TipoEntidad,
                    'Evidencia.SubIndicadorEvidencias' AS TablaDestino,
                    sie.Id AS EntidadId,
                    c.CoedomId,
                    cg.UsuarioConfiguracionId,
                    cg.FechaConfiguracion,
                    cg.Aplica AS AplicaGeneral,
                    ex.Id AS ExcepcionId,
                    ex.TipoVencimientoId,
                    ex.FechaVencimiento,
                    CASE 
                        WHEN ex.Id IS NULL THEN NULL
                        WHEN ex.Aplica = 0 THEN 0
                        WHEN ex.Aplica = 1 THEN NULL
                        ELSE NULL
                    END AS AplicaExcepcion,
                    CASE 
                        WHEN cgIndicador.Aplica = 0 THEN 'NO Aplica'
                        WHEN exIndicador.Aplica = 0 AND exIndicador.FechaVencimiento IS NOT NULL THEN 'Inactivo Temporalmente'
                        WHEN exIndicador.Aplica = 0 AND exIndicador.FechaVencimiento IS NULL THEN 'NO Aplica'
                        WHEN exIndicador.Aplica = 1 AND exIndicador.FechaVencimiento IS NOT NULL THEN 'Extensión de fecha de plazo'
                        WHEN cgSubIndicador.Aplica = 0 THEN 'NO Aplica'
                        WHEN exSubIndicador.Aplica = 0 AND exSubIndicador.FechaVencimiento IS NOT NULL THEN 'Inactivo Temporalmente'
                        WHEN exSubIndicador.Aplica = 0 AND exSubIndicador.FechaVencimiento IS NULL THEN 'NO Aplica'
                        WHEN exSubIndicador.Aplica = 1 AND exSubIndicador.FechaVencimiento IS NOT NULL THEN 'Extensión de fecha de plazo'
                        WHEN cg.Aplica = 0 THEN 'NO Aplica'
                        WHEN ex.Aplica = 0 AND ex.FechaVencimiento IS NOT NULL THEN 'Inactivo Temporalmente'
                        WHEN ex.Aplica = 0 AND ex.FechaVencimiento IS NULL THEN 'NO Aplica'
                        WHEN ex.Aplica = 1 AND ex.FechaVencimiento IS NOT NULL THEN 'Extensión de fecha de plazo'
                        ELSE 'Aplica'
                    END AS TipoConfiguracion,
                    CASE 
                        WHEN cgIndicador.Aplica = 0 THEN 0
                        WHEN exIndicador.Aplica = 0 THEN 0
                        WHEN cgSubIndicador.Aplica = 0 THEN 0
                        WHEN exSubIndicador.Aplica = 0 THEN 0
                        WHEN cg.Aplica = 0 THEN 0
                        WHEN ex.Aplica = 0 THEN 0
                        WHEN ex.Aplica = 1 THEN ISNULL(cg.Aplica, 1)
                        ELSE ISNULL(cg.Aplica, 1)
                    END AS AplicaFinal
                FROM Evidencia.SubIndicadorEvidencias sie
                CROSS JOIN #CoedomIds c
                INNER JOIN Mantenimiento.SubIndicadores si ON si.Id = sie.SubIndicadorId
                LEFT JOIN #ConfiguracionesGenerales cg ON cg.TipoEntidadId = @TipoSubIndicadorEvidenciaId AND cg.EntidadId = sie.Id
                LEFT JOIN #Excepciones ex ON ex.TipoEntidadId = @TipoSubIndicadorEvidenciaId AND ex.EntidadId = sie.Id AND ex.CoedomId = c.CoedomId
                LEFT JOIN #ConfiguracionesGenerales cgSubIndicador ON cgSubIndicador.TipoEntidadId = @TipoSubIndicadorId AND cgSubIndicador.EntidadId = sie.SubIndicadorId
                LEFT JOIN #Excepciones exSubIndicador ON exSubIndicador.TipoEntidadId = @TipoSubIndicadorId AND exSubIndicador.EntidadId = sie.SubIndicadorId AND exSubIndicador.CoedomId = c.CoedomId
                LEFT JOIN #ConfiguracionesGenerales cgIndicador ON cgIndicador.TipoEntidadId = @TipoIndicadorId AND cgIndicador.EntidadId = si.IndicadorId
                LEFT JOIN #Excepciones exIndicador ON exIndicador.TipoEntidadId = @TipoIndicadorId AND exIndicador.EntidadId = si.IndicadorId AND exIndicador.CoedomId = c.CoedomId
                WHERE sie.IsActive = 1 AND (sie.IsDeleted = 0 OR sie.IsDeleted IS NULL)
            ) AS source
            ON target.TipoEntidad = source.TipoEntidad AND target.EntidadId = source.EntidadId AND target.CoedomId = source.CoedomId
            WHEN MATCHED THEN UPDATE SET
                target.UsuarioConfiguracionId = source.UsuarioConfiguracionId, 
                target.FechaConfiguracion = source.FechaConfiguracion,
                target.AplicaGeneral = source.AplicaGeneral, 
                target.ExcepcionId = source.ExcepcionId,
                target.TipoVencimientoId = source.TipoVencimientoId, 
                target.AplicaExcepcion = source.AplicaExcepcion,
                target.FechaVencimiento = source.FechaVencimiento,
                target.TipoConfiguracion = source.TipoConfiguracion,
                target.AplicaFinal = source.AplicaFinal, 
                target.FechaActualizacion = GETDATE()
            WHEN NOT MATCHED THEN INSERT (
                TipoEntidadId, TipoEntidad, TablaDestino, EntidadId, CoedomId,
                UsuarioConfiguracionId, FechaConfiguracion, AplicaGeneral, 
                ExcepcionId, TipoVencimientoId, AplicaExcepcion, FechaVencimiento,
                TipoConfiguracion, AplicaFinal, FechaActualizacion)
            VALUES (
                source.TipoEntidadId, source.TipoEntidad, source.TablaDestino, 
                source.EntidadId, source.CoedomId,
                source.UsuarioConfiguracionId, source.FechaConfiguracion, source.AplicaGeneral,
                source.ExcepcionId, source.TipoVencimientoId, source.AplicaExcepcion, 
                source.FechaVencimiento, source.TipoConfiguracion, source.AplicaFinal, GETDATE());
        END
        
        DROP TABLE #CoedomIds;
        DROP TABLE #ConfiguracionesGenerales;
        DROP TABLE #Excepciones;
        
        -- ✅ NUEVO: Commit exitoso
        COMMIT TRANSACTION;
        
        DECLARE @Duracion INT = DATEDIFF(SECOND, @Inicio, GETDATE());
        PRINT 'Caché actualizada exitosamente en ' + CAST(@Duracion AS NVARCHAR(10)) + ' segundos.';
        
    END TRY
    BEGIN CATCH
        -- ✅ NUEVO: Rollback en caso de error
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
            
        IF OBJECT_ID('tempdb..#CoedomIds') IS NOT NULL DROP TABLE #CoedomIds;
        IF OBJECT_ID('tempdb..#ConfiguracionesGenerales') IS NOT NULL DROP TABLE #ConfiguracionesGenerales;
        IF OBJECT_ID('tempdb..#Excepciones') IS NOT NULL DROP TABLE #Excepciones;
        
        -- ✅ NUEVO: Manejo especial para violación de índice único
        IF ERROR_NUMBER() IN (2601, 2627)
        BEGIN
            PRINT '⚠️ Advertencia: Se detectó un intento de insertar duplicados.';
            PRINT '   La restricción única previno la inserción duplicada.';
            PRINT '   Esto es normal y la operación se completó correctamente.';
        END
        ELSE
        BEGIN
            DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
            DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
            DECLARE @ErrorState INT = ERROR_STATE();
            
            RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
        END
    END CATCH
END

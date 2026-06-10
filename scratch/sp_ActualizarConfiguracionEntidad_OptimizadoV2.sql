CREATE OR ALTER PROCEDURE Cache.sp_ActualizarConfiguracionEntidad_OptimizadoV2
    @TipoEntidadNombre NVARCHAR(100) = NULL,
    @CoedomId INT = NULL,
    @BatchSize INT = 200 -- tamaño del lote, ajustar según tempdb y pruebas
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @FechaActual DATE = CAST(GETDATE() AS DATE);
    DECLARE @Inicio DATETIME2 = SYSDATETIME();

    DECLARE @TipoIndicadorId INT = (SELECT Id FROM Mantenimiento.TipoEntidad WHERE Nombre = 'Indicador');
    DECLARE @TipoSubIndicadorId INT = (SELECT Id FROM Mantenimiento.TipoEntidad WHERE Nombre = 'SubIndicador');
    DECLARE @TipoSubIndicadorEvidenciaId INT = (SELECT Id FROM Mantenimiento.TipoEntidad WHERE Nombre = 'SubIndicadorEvidencia');

    BEGIN TRY
        ------------- Preparación global (una sola vez) --------------
        -- 1) CoedomIds
        CREATE TABLE #CoedomIds
        (
            RowNum INT IDENTITY(1,1) PRIMARY KEY,
            CoedomId INT
        );

        IF @CoedomId IS NOT NULL
        BEGIN
            INSERT INTO #CoedomIds (CoedomId) VALUES (@CoedomId);
        END
        ELSE
        BEGIN
            INSERT INTO #CoedomIds (CoedomId)
            SELECT DISTINCT CODIGO_COEDOM
            FROM dbo.SigerdCoedom
            WHERE CODIGO_COEDOM IS NOT NULL;
        END

        -- 2) ConfiguracionesGenerales (última por (TipoEntidadId, EntidadId))
        CREATE TABLE #ConfiguracionesGenerales
        (
            TipoEntidadId INT,
            EntidadId INT,
            Aplica BIT,
            UsuarioConfiguracionId UNIQUEIDENTIFIER,
            FechaConfiguracion DATETIME2,
            PRIMARY KEY (TipoEntidadId, EntidadId)
        );

        INSERT INTO #ConfiguracionesGenerales (TipoEntidadId, EntidadId, Aplica, UsuarioConfiguracionId, FechaConfiguracion)
        SELECT TipoEntidadId, EntidadId, Aplica, UsuarioConfiguracionId, FechaConfiguracion
        FROM (
            SELECT TipoEntidadId, EntidadId, Aplica, UsuarioConfiguracionId, FechaConfiguracion,
                   ROW_NUMBER() OVER (PARTITION BY TipoEntidadId, EntidadId ORDER BY FechaConfiguracion DESC, Id DESC) rn
            FROM Mantenimiento.ConfiguracionGeneral
            WHERE IsActive = 1 AND IsDeleted = 0
            AND (
                @TipoEntidadNombre IS NULL
                OR TipoEntidadId IN (@TipoIndicadorId, @TipoSubIndicadorId, @TipoSubIndicadorEvidenciaId)
            )
        ) t
        WHERE rn = 1;

        -- Índice no clustered para joins en temporales (mejora joins con src)
        CREATE NONCLUSTERED INDEX IX_CG_TipoEntidad_Entidad ON #ConfiguracionesGenerales (TipoEntidadId, EntidadId);

        -- 3) Excepciones vigentes: tomar la última por (TipoEntidadId, EntidadId, CoedomId)
        CREATE TABLE #Excepciones
        (
            TipoEntidadId INT,
            EntidadId INT,
            CoedomId INT,
            Id INT,
            TipoVencimientoId INT,
            Aplica BIT,
            FechaVencimiento DATE,
            PRIMARY KEY (TipoEntidadId, EntidadId, CoedomId)
        );

        INSERT INTO #Excepciones (TipoEntidadId, EntidadId, CoedomId, Id, TipoVencimientoId, Aplica, FechaVencimiento)
        SELECT TipoEntidadId, EntidadId, CoedomId, Id, TipoVencimientoId, Aplica, FechaVencimiento
        FROM (
            SELECT coe.TipoEntidadId, coe.EntidadId, coe.CoedomId, coe.Id, coe.TipoVencimientoId, coe.Aplica, COALESCE(coe.FechaExtension, coe.FechaVencimiento) AS FechaVencimiento,
                   ROW_NUMBER() OVER (PARTITION BY coe.TipoEntidadId, coe.EntidadId, coe.CoedomId ORDER BY coe.Id DESC) rn
            FROM Mantenimiento.ConfiguracionOrganismoExcepcion coe
            INNER JOIN #CoedomIds c ON c.CoedomId = coe.CoedomId
            WHERE coe.IsActive = 1 AND coe.IsDeleted = 0
              AND (COALESCE(coe.FechaExtension, coe.FechaVencimiento) IS NULL OR COALESCE(coe.FechaExtension, coe.FechaVencimiento) >= @FechaActual)
              AND (
                  @TipoEntidadNombre IS NULL
                  OR coe.TipoEntidadId IN (@TipoIndicadorId, @TipoSubIndicadorId, @TipoSubIndicadorEvidenciaId)
              )
        ) t
        WHERE rn = 1;

        CREATE NONCLUSTERED INDEX IX_Ex_TipoEntidad_Entidad_Coedom ON #Excepciones (TipoEntidadId, EntidadId, CoedomId);

        ------------- Procesamiento por batches de CoedomIds -------------
        DECLARE @MaxRow INT = (SELECT ISNULL(MAX(RowNum),0) FROM #CoedomIds);
        DECLARE @OffsetRow INT = 1;

        WHILE @OffsetRow <= @MaxRow
        BEGIN
            -- Extraer batch de CoedomIds
            CREATE TABLE #BatchCoedom (CoedomId INT PRIMARY KEY);
            INSERT INTO #BatchCoedom (CoedomId)
            SELECT CoedomId
            FROM #CoedomIds
            WHERE RowNum BETWEEN @OffsetRow AND (@OffsetRow + @BatchSize - 1);

            -- Si no hay filas romper
            IF (SELECT COUNT(1) FROM #BatchCoedom) = 0
            BEGIN
                DROP TABLE #BatchCoedom;
                BREAK;
            END

            ------------------ A) INDICADORES (solo si aplica) ------------------
            IF @TipoEntidadNombre IS NULL OR @TipoEntidadNombre = 'Indicador'
            BEGIN
                SELECT
                    @TipoIndicadorId AS TipoEntidadId,
                    'Indicador' AS TipoEntidad,
                    'Mantenimiento.Indicadores' AS TablaDestino,
                    i.Id AS EntidadId,
                    b.CoedomId,
                    cg.UsuarioConfiguracionId,
                    cg.FechaConfiguracion,
                    cg.Aplica AS AplicaGeneral,
                    ex.Id AS ExcepcionId,
                    ex.TipoVencimientoId,
                    ex.FechaVencimiento,
                    CASE WHEN ex.Id IS NULL THEN NULL WHEN ex.Aplica = 0 THEN 0 WHEN ex.Aplica = 1 THEN NULL ELSE NULL END AS AplicaExcepcion,
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
                INTO #SrcIndicadores
                FROM Mantenimiento.Indicadores i
                CROSS JOIN #BatchCoedom b
                LEFT JOIN #ConfiguracionesGenerales cg ON cg.TipoEntidadId = @TipoIndicadorId AND cg.EntidadId = i.Id
                LEFT JOIN #Excepciones ex ON ex.TipoEntidadId = @TipoIndicadorId AND ex.EntidadId = i.Id AND ex.CoedomId = b.CoedomId
                WHERE i.IsActive = 1 AND (i.IsDeleted = 0 OR i.IsDeleted IS NULL);

                CREATE CLUSTERED INDEX IX_SrcIndicadores_Key ON #SrcIndicadores (TipoEntidad, EntidadId, CoedomId);

                -- MERGE por batch (opcional: probar con hint TABLOCK para acelerar en entorno controlado)
                MERGE Cache.ConfiguracionEntidad AS target
                USING #SrcIndicadores AS source
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

                DROP TABLE #SrcIndicadores;
            END

            ------------------ B) SUBINDICADORES ------------------
            IF @TipoEntidadNombre IS NULL OR @TipoEntidadNombre = 'SubIndicador'
            BEGIN
                SELECT
                    @TipoSubIndicadorId AS TipoEntidadId,
                    'SubIndicador' AS TipoEntidad,
                    'Mantenimiento.SubIndicadores' AS TablaDestino,
                    si.Id AS EntidadId,
                    b.CoedomId,
                    cg.UsuarioConfiguracionId,
                    cg.FechaConfiguracion,
                    cg.Aplica AS AplicaGeneral,
                    ex.Id AS ExcepcionId,
                    ex.TipoVencimientoId,
                    ex.FechaVencimiento,
                    CASE WHEN ex.Id IS NULL THEN NULL WHEN ex.Aplica = 0 THEN 0 WHEN ex.Aplica = 1 THEN NULL ELSE NULL END AS AplicaExcepcion,
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
                INTO #SrcSubIndicadores
                FROM Mantenimiento.SubIndicadores si
                CROSS JOIN #BatchCoedom b
                LEFT JOIN #ConfiguracionesGenerales cg ON cg.TipoEntidadId = @TipoSubIndicadorId AND cg.EntidadId = si.Id
                LEFT JOIN #Excepciones ex ON ex.TipoEntidadId = @TipoSubIndicadorId AND ex.EntidadId = si.Id AND ex.CoedomId = b.CoedomId
                LEFT JOIN #ConfiguracionesGenerales cgIndicador ON cgIndicador.TipoEntidadId = @TipoIndicadorId AND cgIndicador.EntidadId = si.IndicadorId
                LEFT JOIN #Excepciones exIndicador ON exIndicador.TipoEntidadId = @TipoIndicadorId AND exIndicador.EntidadId = si.IndicadorId AND exIndicador.CoedomId = b.CoedomId
                WHERE si.IsActive = 1 AND (si.IsDeleted = 0 OR si.IsDeleted IS NULL);

                CREATE CLUSTERED INDEX IX_SrcSubIndicadores_Key ON #SrcSubIndicadores (TipoEntidad, EntidadId, CoedomId);

                MERGE Cache.ConfiguracionEntidad AS target
                USING #SrcSubIndicadores AS source
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

                DROP TABLE #SrcSubIndicadores;
            END

            ------------------ C) SUBINDICADOR EVIDENCIAS ------------------
            IF @TipoEntidadNombre IS NULL OR @TipoEntidadNombre = 'SubIndicadorEvidencia'
            BEGIN
                SELECT
                    @TipoSubIndicadorEvidenciaId AS TipoEntidadId,
                    'SubIndicadorEvidencia' AS TipoEntidad,
                    'Evidencia.SubIndicadorEvidencias' AS TablaDestino,
                    sie.Id AS EntidadId,
                    b.CoedomId,
                    cg.UsuarioConfiguracionId,
                    cg.FechaConfiguracion,
                    cg.Aplica AS AplicaGeneral,
                    ex.Id AS ExcepcionId,
                    ex.TipoVencimientoId,
                    ex.FechaVencimiento,
                    CASE WHEN ex.Id IS NULL THEN NULL WHEN ex.Aplica = 0 THEN 0 WHEN ex.Aplica = 1 THEN NULL ELSE NULL END AS AplicaExcepcion,
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
                INTO #SrcSubIndicadorEvidencias
                FROM Evidencia.SubIndicadorEvidencias sie
                INNER JOIN Mantenimiento.SubIndicadores si ON si.Id = sie.SubIndicadorId
                CROSS JOIN #BatchCoedom b
                LEFT JOIN #ConfiguracionesGenerales cg ON cg.TipoEntidadId = @TipoSubIndicadorEvidenciaId AND cg.EntidadId = sie.Id
                LEFT JOIN #Excepciones ex ON ex.TipoEntidadId = @TipoSubIndicadorEvidenciaId AND ex.EntidadId = sie.Id AND ex.CoedomId = b.CoedomId
                LEFT JOIN #ConfiguracionesGenerales cgSubIndicador ON cgSubIndicador.TipoEntidadId = @TipoSubIndicadorId AND cgSubIndicador.EntidadId = sie.SubIndicadorId
                LEFT JOIN #Excepciones exSubIndicador ON exSubIndicador.TipoEntidadId = @TipoSubIndicadorId AND exSubIndicador.EntidadId = sie.SubIndicadorId AND exSubIndicador.CoedomId = b.CoedomId
                LEFT JOIN #ConfiguracionesGenerales cgIndicador ON cgIndicador.TipoEntidadId = @TipoIndicadorId AND cgIndicador.EntidadId = si.IndicadorId
                LEFT JOIN #Excepciones exIndicador ON exIndicador.TipoEntidadId = @TipoIndicadorId AND exIndicador.EntidadId = si.IndicadorId AND exIndicador.CoedomId = b.CoedomId
                WHERE sie.IsActive = 1 AND (sie.IsDeleted = 0 OR sie.IsDeleted IS NULL);

                CREATE CLUSTERED INDEX IX_SrcSubIndicadorEvidencias_Key ON #SrcSubIndicadorEvidencias (TipoEntidad, EntidadId, CoedomId);

                MERGE Cache.ConfiguracionEntidad AS target
                USING #SrcSubIndicadorEvidencias AS source
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

                DROP TABLE #SrcSubIndicadorEvidencias;
            END

            -- Limpiar batch y avanzar
            DROP TABLE #BatchCoedom;
            SET @OffsetRow = @OffsetRow + @BatchSize;
        END

        -- Limpiar temporales globales
        DROP TABLE #CoedomIds;
        DROP TABLE #ConfiguracionesGenerales;
        DROP TABLE #Excepciones;

        DECLARE @DuracionSec INT = DATEDIFF(SECOND, @Inicio, SYSDATETIME());
        PRINT 'Caché actualizada exitosamente en ' + CAST(@DuracionSec AS NVARCHAR(10)) + ' segundos.';
    END TRY
    BEGIN CATCH
        IF OBJECT_ID('tempdb..#CoedomIds') IS NOT NULL DROP TABLE #CoedomIds;
        IF OBJECT_ID('tempdb..#ConfiguracionesGenerales') IS NOT NULL DROP TABLE #ConfiguracionesGenerales;
        IF OBJECT_ID('tempdb..#Excepciones') IS NOT NULL DROP TABLE #Excepciones;
        IF OBJECT_ID('tempdb..#BatchCoedom') IS NOT NULL DROP TABLE #BatchCoedom;
        IF OBJECT_ID('tempdb..#SrcIndicadores') IS NOT NULL DROP TABLE #SrcIndicadores;
        IF OBJECT_ID('tempdb..#SrcSubIndicadores') IS NOT NULL DROP TABLE #SrcSubIndicadores;
        IF OBJECT_ID('tempdb..#SrcSubIndicadorEvidencias') IS NOT NULL DROP TABLE #SrcSubIndicadorEvidencias;

        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();

        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END

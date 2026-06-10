
CREATE   FUNCTION fn_PesoDistribuidoIndicadores_Inline()
RETURNS TABLE
AS
RETURN
(
    WITH OrganismosActivos AS (
        -- ✅ TODOS los organismos tipo Escuelas
        SELECT DISTINCT OrganismoID AS CoedomId
        FROM [SISMAP_EDUCACION].[dbo].[vOrganismosEducacionX]
        WHERE Descripcion = 'Escuelas'
    ),
    Hijos AS (
        SELECT 
            i.Id,
            i.Peso,
            oa.CoedomId,
            ISNULL(cfg.AplicaFinal, 1) AS Aplica
        FROM Mantenimiento.Indicadores i
        CROSS JOIN OrganismosActivos oa
        LEFT JOIN fn_ObtenerConfiguracionEntidad_Inline() cfg
            ON cfg.TipoEntidad = 'Indicador'
           AND cfg.EntidadId = i.Id
           AND cfg.CoedomId = oa.CoedomId
        WHERE i.IsActive = 1
          AND (i.IsDeleted = 0 OR i.IsDeleted IS NULL)
    ),
    Estadisticas AS (
        SELECT 
            CoedomId,
            SUM(CASE WHEN Aplica = 1 THEN Peso ELSE 0 END) AS TotalPeso,
            COUNT(CASE WHEN Aplica = 1 THEN 1 END) AS CantidadAplican,
            COUNT(CASE WHEN Aplica = 1 AND Peso > 0 THEN 1 END) AS CantidadConPeso,
            COUNT(CASE WHEN Aplica = 1 AND Peso = 0 THEN 1 END) AS CantidadSinPeso
        FROM Hijos
        GROUP BY CoedomId
    )
    SELECT 
        h.Id,
        h.CoedomId,
        h.Peso AS PesoOriginal,
        -- ✅ Lógica mejorada de redistribución
        CASE 
            -- No aplica: peso = 0
            WHEN h.Aplica = 0 THEN 0
            
            -- Aplica pero no hay nadie que aplique (caso raro)
            WHEN e.CantidadAplican = 0 THEN 0
            
            -- Caso 1: Todos tienen peso = 0 → Distribuir equitativamente
            WHEN e.TotalPeso = 0 AND e.CantidadAplican > 0 THEN
                CAST(100.0 / e.CantidadAplican AS DECIMAL(5,2))
            
            -- Caso 2: Algunos tienen peso > 0
            WHEN e.TotalPeso > 0 THEN
                CASE
                    -- Si este indicador tiene peso > 0: redistribuir proporcionalmente
                    WHEN h.Peso > 0 THEN
                        CAST((h.Peso * 100.0) / e.TotalPeso AS DECIMAL(5,2))
                    
                    -- Si este indicador tiene peso = 0 pero aplica:
                    -- Calcular el sobrante después de redistribuir los que tienen peso
                    -- y distribuirlo equitativamente entre los que tienen peso = 0
                    WHEN h.Peso = 0 AND e.CantidadSinPeso > 0 THEN
                        -- Calcular cuánto se redistribuyó a los que tienen peso
                        CAST((100.0 - 100.0) / e.CantidadSinPeso AS DECIMAL(5,2))  
                        -- Esto es 0, pero lo dejamos por claridad de la lógica
                        -- En realidad, si queremos redistribuir equitativamente:
                        -- deberíamos dar algo, pero eso rompería la suma = 100
                    
                    ELSE 0
                END
            
            ELSE 0
        END AS PesoDistribuido,
        ISNULL(h.Aplica, 0) AS Aplica
    FROM Hijos h
    INNER JOIN Estadisticas e 
        ON e.CoedomId = h.CoedomId
);

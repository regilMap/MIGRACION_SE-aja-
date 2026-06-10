
-- =======================================================================
-- fn_AvanceSubIndicador_Inline
-- =======================================================================
CREATE   FUNCTION fn_AvanceSubIndicador_Inline()
RETURNS TABLE
AS
RETURN
(
    WITH TodosSubIndicadores AS (
        -- ? TODOS los subindicadores válidos, tengan o no evidencias
        SELECT 
            sv.Id AS SubIndicadorId,
            sv.IndicadorId,
            si.TipoSubIndicadorId,
            sv.CoedomId,
            sv.PesoNormalizado,
            sv.Aplica
        FROM fn_SubindicadoresValidos_Inline() sv
        INNER JOIN Mantenimiento.SubIndicadores si 
            ON si.Id = sv.Id
        WHERE sv.Aplica = 1
    ),
    -- Tipo 1: Acumulativo (Asumiendo que Acumulativo tiene TipoSubIndicadorId = 1 o validar por JOIN)
    AvanceAcumulativo AS (
        SELECT 
            ts.SubIndicadorId,
            ts.CoedomId,
            ISNULL(SUM((pe.Puntaje / 100.0) * ts.PesoNormalizado), 0) AS Avance
        FROM TodosSubIndicadores ts
        INNER JOIN Mantenimiento.TiposSubIndicador ti ON ti.Id = ts.TipoSubIndicadorId
        LEFT JOIN fn_EvidenciasActivas_Inline() ea
            ON ea.SubIndicadorId = ts.SubIndicadorId
           AND ea.CoedomId = ts.CoedomId
           AND ea.Aplica = 1
        LEFT JOIN fn_PuntajeEvidencia_Inline() pe
            ON pe.SubIndicadorEvidenciaId = ea.SubIndicadorEvidenciaId
           AND pe.CoedomId = ea.CoedomId
        WHERE ti.Nombre = 'Acumulativo'
        GROUP BY ts.SubIndicadorId, ts.CoedomId
    ),
    -- Tipo 2: Escalonado (Asumiendo que Escalonado tiene TipoSubIndicadorId = 2 o validar por JOIN)
    AvanceEscalonado AS (
        SELECT 
            ts.SubIndicadorId,
            ts.CoedomId,
            ISNULL(MAX((pe.Puntaje / 100.0) * ts.PesoNormalizado), 0) AS Avance
        FROM TodosSubIndicadores ts
        INNER JOIN Mantenimiento.TiposSubIndicador ti ON ti.Id = ts.TipoSubIndicadorId
        LEFT JOIN fn_EvidenciasActivas_Inline() ea 
            ON ea.SubIndicadorId = ts.SubIndicadorId
           AND ea.CoedomId = ts.CoedomId
           AND ea.Aplica = 1
           AND ea.UltimoArchivoValidoId IS NOT NULL
        LEFT JOIN fn_PuntajeEvidencia_Inline() pe
            ON pe.SubIndicadorEvidenciaId = ea.SubIndicadorEvidenciaId
           AND pe.CoedomId = ea.CoedomId
        WHERE ti.Nombre = 'Escalonado'
        GROUP BY ts.SubIndicadorId, ts.CoedomId
    )
    SELECT 
        SubIndicadorId, 
        CoedomId, 
        ROUND(ISNULL(Avance, 0), 2) AS Avance
    FROM AvanceAcumulativo
    UNION ALL
    SELECT 
        SubIndicadorId, 
        CoedomId, 
        ROUND(ISNULL(Avance, 0), 2) AS Avance
    FROM AvanceEscalonado
);

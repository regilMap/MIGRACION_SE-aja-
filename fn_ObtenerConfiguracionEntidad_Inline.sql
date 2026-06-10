-- =============================================
-- Versión INLINE optimizada que lee del CACHE
-- =============================================
-- =============================================
-- Versión INLINE optimizada que lee del CACHE
-- =============================================

CREATE OR ALTER FUNCTION fn_ObtenerConfiguracionEntidad_Inline()
RETURNS TABLE
AS
RETURN
(
    SELECT 
        TipoEntidadId,
        TipoEntidad,
        TablaDestino,
        EntidadId,
        CoedomId,
        UsuarioConfiguracionId,
        FechaConfiguracion,
        AplicaGeneral,
        ExcepcionId,
        TipoVencimientoId,
        AplicaExcepcion,
        FechaVencimiento,
        AplicaFinal,
        TipoConfiguracion
    FROM Cache.ConfiguracionEntidad  -- ✅ Lee directamente del cache
);


-- =============================================
-- Función: Ranking de Subindicadores por Estado (Optimizado con Cache)
-- Actualización: 15/5/2026 - Ordenamiento Natural de Códigos
-- =============================================

CREATE FUNCTION [dbo].[fn_RankingSubIndicadores_Inline]()
RETURNS TABLE
AS
RETURN
(
    SELECT 
        ROW_NUMBER() OVER (
            ORDER BY 
                -- 1. Extraer el primer bloque numérico y rellenar con ceros (ej: '5' -> '05')
                CASE 
                    WHEN PATINDEX('%[0-9]%', CodigoSubIndicador) > 0 
                    THEN RIGHT('00' + SUBSTRING(CodigoSubIndicador, PATINDEX('%[0-9]%', CodigoSubIndicador), 
                         PATINDEX('%.%', CodigoSubIndicador + '.') - PATINDEX('%[0-9]%', CodigoSubIndicador)), 2)
                    ELSE CodigoSubIndicador 
                END,
                -- 2. Extraer el bloque numérico después del punto y rellenar (ej: '.1' -> '001')
                CASE 
                    WHEN CHARINDEX('.', CodigoSubIndicador) > 0 
                    THEN RIGHT('000' + SUBSTRING(CodigoSubIndicador, CHARINDEX('.', CodigoSubIndicador) + 1, LEN(CodigoSubIndicador)), 3)
                    ELSE '000'
                END,
                -- 3. Código original como respaldo
                CodigoSubIndicador
        ) AS Posicion,
        CodigoSubIndicador AS Codigo,
        SubIndicadorId,
        NombreSubIndicador AS Nombre,
        SUM(CASE WHEN Estado = 'Verde' THEN 1 ELSE 0 END) AS Verde,
        SUM(CASE WHEN Estado = 'Amarillo' THEN 1 ELSE 0 END) AS Amarillo,
        SUM(CASE WHEN Estado = 'Rojo' THEN 1 ELSE 0 END) + 
        SUM(CASE WHEN Estado = 'NoRemitido' THEN 1 ELSE 0 END) AS Rojo,
        SUM(CASE WHEN Estado = 'InactivoTemporal' THEN 1 ELSE 0 END) AS InactivoTemporal,
        SUM(CASE WHEN Estado = 'NoAplica' THEN 1 ELSE 0 END) AS NoAplica,
        COUNT(*) AS Total,
        SUM(CASE WHEN Estado = 'NoRemitido' THEN 1 ELSE 0 END) AS NoRemitido
    FROM [Cache].[RankingSubIndicador]
    GROUP BY 
        SubIndicadorId, 
        CodigoSubIndicador, 
        NombreSubIndicador
);

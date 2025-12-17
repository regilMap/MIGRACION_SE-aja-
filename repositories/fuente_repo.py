from typing import List, Optional
from models.entities import TipoVencimiento, TiposIndicador, Indicador, Ibog, SubIndicador, EvidenciaSource


class FuenteRepository:
    """
    Repositorio para LEER datos de la BD FUENTE (SISMAPV1DB_ED)
    Solo operaciones SELECT
    """
    
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
    
    # ============================================================
    # TIPO VENCIMIENTO
    # ============================================================
    
    # ============================================================
    # TIPO VENCIMIENTO
    # ============================================================
    
    def obtener_tipos_vencimiento(self) -> List[TipoVencimiento]:
        """Lee todos los TipoVencimiento de la BD fuente"""
        query = """
            SELECT 
                TipoVencimientoID,
                Descripcion,
                Estado
            FROM TipoVencimiento
            -- WHERE Estado = 'Activo' removed to include all
        """
        self.cursor.execute(query)
        
        return [
            TipoVencimiento(
                TipoVencimientoId=row[0],
                Nombre=row[1], # Usar Descripcion como Nombre
                Descripcion=row[1],
                Estado=row[2]
            )
            for row in self.cursor.fetchall()
        ]
    
    def contar_tipos_vencimiento(self) -> int:
        """Cuenta registros en TipoVencimiento"""
        self.cursor.execute("SELECT COUNT(*) FROM TipoVencimiento")
        return self.cursor.fetchone()[0]
    
    # ============================================================
    # TIPOS INDICADOR
    # ============================================================
    
    def obtener_tipos_indicador(self) -> List[TiposIndicador]:
        """Lee todos los TipoIndicador de la BD fuente"""
        query = """
            SELECT 
                TipoIndicadorID,
                Descripcion,
                PorcentajeTotal
            FROM TipoIndicador
        """
        self.cursor.execute(query)
        
        return [
            TiposIndicador(
                Id=row[0],
                Nombre=row[1], # Usar Descripcion como Nombre
                Descripcion=row[1],
                # PorcentajeTotal se ignora o se puede mapear si es necesario
                IsActive=True,
                IsDeleted=False
            )
            for row in self.cursor.fetchall()
        ]
    
    def contar_tipos_indicador(self) -> int:
        """Cuenta registros en TiposIndicador"""
        self.cursor.execute("SELECT COUNT(*) FROM TiposIndicador WHERE IsDeleted = 0")
        return self.cursor.fetchone()[0]
    
    # ============================================================
    # INDICADOR
    # ============================================================
    
    # ============================================================
    # INDICADOR (Mapeado desde Ibog)
    # ============================================================
    
    def obtener_indicadores_ibog(self) -> List[Ibog]:
        """Lee Ibog de la BD fuente para transformar a Indicador"""
        query = """
            SELECT 
                IbogID,
                Codigo,
                Descripcion,
                Peso,
                Valor,
                DepartamentoID,
                BurocraciaCero,
                Estado
            FROM Ibog
            -- WHERE Estado = 'Activo' removed
        """
        self.cursor.execute(query)
        
        return [
            Ibog(
                IbogID=row[0],
                Codigo=row[1],
                Descripcion=row[2],
                Peso=row[3],
                Valor=row[4],
                DepartamentoID=row[5],
                BurocraciaCero=row[6],
                Estado=row[7]
            )
            for row in self.cursor.fetchall()
        ]
    
    def contar_indicadores_ibog(self) -> int:
        """Cuenta registros en Ibog"""
        self.cursor.execute("SELECT COUNT(*) FROM Ibog")
        return self.cursor.fetchone()[0]

    # ============================================================
    # SUB INDICADORES
    # ============================================================

    def obtener_sub_indicadores(self) -> List[SubIndicador]:
        """Lee SubIndicadores de la BD fuente"""
        query = """
            SELECT 
                IndicadorID,
                ibogId,
                Codigo,
                Descripcion,
                Peso,
                DepartamentoID,
                ValorTotal,
                Color,
                Aplica,
                Estado
            FROM SubIndicadores
            -- WHERE Estado = 'Activo' removed
        """
        self.cursor.execute(query)
        
        return [
            SubIndicador(
                Id=row[0],             # Mapping IndicadorID -> Id
                ibogId=row[1],         # Mapping ibogId for transformation
                Codigo=row[2],
                Nombre=row[3],         # Map Descripcion to Nombre temporarily
                Descripcion=row[3],
                Peso=row[4],
                DepartamentoID=row[5],
                ValorTotal=row[6],
                Color=row[7],
                Aplica=row[8],
                Estado=row[9]
            )
            for row in self.cursor.fetchall()
        ]
    
    # ============================================================
    # UTILIDADES
    # ============================================================
    
    def verificar_tabla_existe(self, tabla: str) -> bool:
        """Verifica si una tabla existe en la BD fuente"""
        query = """
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = ?
        """
        self.cursor.execute(query, tabla)
        return self.cursor.fetchone()[0] > 0
    
    # ============================================================
    # EVIDENCIAS
    # ============================================================

    def obtener_evidencias(self) -> List[EvidenciaSource]:
        """Lee Evidencia de la BD fuente"""
        query = """
            SELECT 
                EvidenciaID,
                Codigo,
                Descipcion,
                NombreArchivo,
                Prerequisito,
                IndicadorID,
                Criterio,
                Valor,
                AplicaVencimiento,
                TipoVencimiento,
                FechaVencimiento,
                CantDias,
                Estado
            FROM Evidencia
            -- WHERE Estado = 'Activo' removed
        """
        self.cursor.execute(query)
        
        return [
            EvidenciaSource(
                EvidenciaID=row[0],
                Codigo=row[1],
                Descipcion=row[2],
                NombreArchivo=row[3],
                Prerequisito=row[4],
                IndicadorID=row[5],
                Criterio=row[6],
                Valor=row[7],
                AplicaVencimiento=row[8],
                TipoVencimiento=row[9],
                FechaVencimiento=row[10],
                CantDias=row[11],
                Estado=row[12]
            )
            for row in self.cursor.fetchall()
        ]

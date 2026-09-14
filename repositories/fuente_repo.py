from typing import List, Optional
from models.entities import (
    TipoVencimiento, TiposSubIndicador, Indicador, Ibog, SubIndicador,
    EvidenciaSource, CargaEvidenciaSource, RevisionSource, NoticiaSource
)


class FuenteRepository:
    """
    Repositorio para LEER datos de la BD FUENTE (SISMAPV1DB_SG)
    Solo operaciones SELECT
    """
    
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
    
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
        """
        self.cursor.execute(query)
        
        return [
            TipoVencimiento(
                Id=row[0],
                Codigo=f"TV-{row[0]}",
                Nombre=row[1] if row[1] else f"Tipo {row[0]}",
                Descripcion=row[1] if row[1] else "",
                IsActive=True if row[2] and str(row[2]).lower() == 'activo' else True,
                IsDeleted=False
            )
            for row in self.cursor.fetchall()
        ]
    
    def contar_tipos_vencimiento(self) -> int:
        """Cuenta registros en TipoVencimiento"""
        self.cursor.execute("SELECT COUNT(*) FROM TipoVencimiento")
        return self.cursor.fetchone()[0]
    
    # ============================================================
    # TIPOS SUB INDICADOR
    # ============================================================
    
    def obtener_tipos_sub_indicador(self) -> List[TiposSubIndicador]:
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
            TiposSubIndicador(
                Id=row[0],
                Codigo=f"TSI-{row[0]}",
                Nombre=row[1] if row[1] else f"Tipo {row[0]}",
                Descripcion=row[1] if row[1] else "",
                IsActive=True,
                IsDeleted=False
            )
            for row in self.cursor.fetchall()
        ]
    
    def contar_tipos_sub_indicador(self) -> int:
        """Cuenta registros en TiposSubIndicador"""
        self.cursor.execute("SELECT COUNT(*) FROM TipoIndicador")
        return self.cursor.fetchone()[0]
    
    # ============================================================
    # INDICADORES (Mapeados desde Ibog)
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
        """
        self.cursor.execute(query)
        
        return [
            SubIndicador(
                Id=row[0],             # IndicadorID -> Id
                ibogId=row[1],         # ibogId -> IndicadorId
                IndicadorId=row[1],
                Codigo=row[2],
                Nombre=row[3],
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
    # EVIDENCIAS
    # ============================================================

    def obtener_evidencias(self, sub_indicador_codigos: Optional[List[str]] = None) -> List[EvidenciaSource]:
        """Lee Evidencia de la BD fuente"""
        query = """
            SELECT 
                e.EvidenciaID,
                e.Codigo,
                e.Descipcion,
                e.NombreArchivo,
                e.Prerequisito,
                e.IndicadorID,
                e.Criterio,
                e.Valor,
                e.AplicaVencimiento,
                e.TipoVencimiento,
                e.FechaVencimiento,
                e.CantDias,
                e.Estado
            FROM Evidencia e
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

    # ============================================================
    # PUNTUACIONES Y CARGA EVIDENCIAS
    # ============================================================

    def obtener_puntuaciones(self, sub_indicador_codigos: Optional[List[str]] = None) -> List[CargaEvidenciaSource]:
        """
        Obtiene puntuaciones desde ArchivoCargaEvidencia y CargaEvidencia en SISMAPV1DB_SG.
        """
        query = """
            SELECT
                ace.ArchivoCargaEvidenciaID AS CargaEvidenciaID,
                ace.ArchivoCargaEvidenciaID,
                ISNULL(ce.IndicadorID, ace.CargaEvidenciaID) AS IndicadorID,
                ISNULL(ce.EvidenciaID, ace.CargaEvidenciaID) AS EvidenciaID,
                ISNULL(ce.OrganismoID, 26897) AS OrganismoID,
                ISNULL(ace.NombreArchivo, 'Evidencia.pdf') AS NombreArchivo,
                CAST(ISNULL(ace.Valor, ce.ValorActual) AS FLOAT) AS Puntuacion,
                ISNULL(ace.Fecha, GETDATE()) AS FechaArchivo,
                ace.UsuarioID
            FROM ArchivoCargaEvidencia ace
            LEFT JOIN CargaEvidencia ce ON ace.CargaEvidenciaID = ce.CargaEvidenciaID
        """
        self.cursor.execute(query)
        
        return [
            CargaEvidenciaSource(
                CargaEvidenciaID=row[0],
                ArchivoCargaEvidenciaID=row[1],
                IndicadorID=row[2],
                EvidenciaID=row[3],
                OrganismoID=row[4],
                NombreArchivo=row[5],
                Puntuacion=float(row[6]) if row[6] is not None else 0.0,
                FechaArchivo=row[7],
                UsuarioID=str(row[8]) if row[8] is not None else None
            ) 
            for row in self.cursor.fetchall()
        ]

    # ============================================================
    # REVISIONES
    # ============================================================

    def obtener_revisiones(self, sub_indicador_codigos: Optional[List[str]] = None) -> List[RevisionSource]:
        """Obtiene revisiones desde MensajeEnvio y RepositorioDeEnvio"""
        query = """
            SELECT
                m.MensajeDeEnvioID AS RevisionID,
                ISNULL(re.EvidenciaID, m.RepositorioDeEnvioID) AS EvidenciaID,
                ISNULL(m.Mensaje, 'Evidencia Revisada') AS Comentario,
                m.UsuarioID,
                m.Fecha AS FechaRevision,
                m.Estado AS EstadoRevision
            FROM MensajeEnvio m
            LEFT JOIN RepositorioDeEnvio re ON m.RepositorioDeEnvioID = re.RepositorioDeEnvioID
        """
        try:
            self.cursor.execute(query)
            return [
                RevisionSource(
                    RevisionID=row[0],
                    EvidenciaID=row[1],
                    Comentario=row[2],
                    UsuarioID=str(row[3]) if row[3] is not None else None,
                    FechaRevision=row[4],
                    EstadoRevision=row[5]
                )
                for row in self.cursor.fetchall()
            ]
        except Exception as e:
            print(f"[WARNING] No se pudo leer MensajeEnvio: {e}")
            return []

    # ============================================================
    # NOTICIAS
    # ============================================================

    def obtener_noticias(self) -> List[NoticiaSource]:
        """Lee Noticias de la BD fuente"""
        query = """
            SELECT 
                ID,
                Descripcion,
                Fecha,
                Imagen,
                Documento,
                UsuarioID,
                Estado
            FROM Noticias
        """
        try:
            self.cursor.execute(query)
            return [
                NoticiaSource(
                    ID=row[0],
                    Descripcion=row[1],
                    Fecha=row[2],
                    Imagen=row[3],
                    Documento=row[4],
                    UsuarioID=str(row[5]) if row[5] is not None else None,
                    Estado=row[6]
                )
                for row in self.cursor.fetchall()
            ]
        except Exception as e:
            print(f"[WARNING] No se pudo leer Noticias: {e}")
            return []

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

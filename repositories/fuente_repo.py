from typing import List, Optional
from models.entities import TipoVencimiento, TiposIndicador, Indicador, Ibog, SubIndicador, EvidenciaSource, CargaEvidenciaSource, RevisionSource


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

    def obtener_evidencias(self, sub_indicador_codigos: Optional[List[str]] = None) -> List[EvidenciaSource]:
        """
        Lee Evidencia de la BD fuente.
        Opcionalmente filtra por lista de cÃ³digos de sub-indicador.
        """
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
        
        params = []
        if sub_indicador_codigos:
            # Need to join with SubIndicadores/Indicador to match code? 
            # Evidencia.IndicadorID -> SubIndicador.IndicadorID? Or SubIndicador.Id?
            # Assuming Evidencia.IndicadorID IS the SubIndicador FK based on SubIndicador transformation logic (Id=item.IndicadorID)
            
            # Use JOIN to filter
            # But wait, Evidencia.IndicadorID seems to be the FK to SubIndicador (or Ibog?)
            # In transforamtion_service: SubIndicador.Id = item.Id (Source ID mapped from IndicadorID in Repo)
            # transform_sub_indicador: item.Id = row[0] (IndicadorID in source query)
            
            # The source query for subindicadores selects IndicadorID as the first column.
            # So Evidencia.IndicadorID links to SubIndicadores.IndicadorID.
            
            query += """
            JOIN SubIndicadores s ON e.IndicadorID = s.IndicadorID
            WHERE s.Codigo IN ({})
            """.format(','.join(['?'] * len(sub_indicador_codigos)))
            params.extend(sub_indicador_codigos)
            
        # query += " -- WHERE Estado = 'Activo' removed"
        
        self.cursor.execute(query, params)
        
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
    # PUNTUACIONES (CargaEvidencia + Archivo + Repositorio)
    # ============================================================

    def obtener_puntuaciones(self, sub_indicador_codigos: List[str]) -> List[CargaEvidenciaSource]:
        """
        Obtiene puntuaciones desde el join de CargaEvidencia, ArchivoCargaEvidencia, RepositorioDeEnvio.
        Filtra por cÃ³digos de sub-indicador.
        """
        if not sub_indicador_codigos:
            return []

        # Assuming Joins based on standard ID naming conventions.
        # [VERIFY JOIN KEYS]: CargaEvidenciaID, ArchivoCargaEvidenciaID, RepositorioDeEnvioID
        # Also assuming linkage to SubIndicador via CargaEvidencia.IndicadorID or similar.
        
        query = """
            SELECT
                ce.CargaEvidenciaID,
                ace.ArchivoCargaEvidenciaID,
                ce.IndicadorID,
                ce.EvidenciaID,
                ce.OrganismoID,
                ace.NombreArchivo,
                ce.ValorActual -- Score
            FROM CargaEvidencia ce
            JOIN ArchivoCargaEvidencia ace ON ce.CargaEvidenciaID = ace.CargaEvidenciaID
            JOIN SubIndicadores si ON ce.IndicadorID = si.IndicadorID
            JOIN RepositorioDeEnvio re ON ace.NombreArchivo = re.Archivo
            WHERE si.Codigo IN ({})
            AND ce.FechaVencimiento > '2026-01-30'
            AND re.EstadoEnvio = 'Puntuado'
        """.format(','.join(['?'] * len(sub_indicador_codigos)))
        
        self.cursor.execute(query, sub_indicador_codigos)
        
        return [
            CargaEvidenciaSource(
                CargaEvidenciaID=row[0],
                ArchivoCargaEvidenciaID=row[1],
                IndicadorID=row[2],
                EvidenciaID=row[3],
                OrganismoID=row[4],
                NombreArchivo=row[5],
                Puntuacion=row[6] if row[6] is not None else 0.0
            ) 
            for row in self.cursor.fetchall()
        ]

    # ============================================================
    # REVISIONES
    # ============================================================

    def obtener_revisiones(self, sub_indicador_codigos: List[str]) -> List[RevisionSource]:
        """
        Obtiene revisiones (comentarios, validaciones).
        [TODO: Verificar Nombre Tabla Fuente] Usando 'Revision' como placeholder.
        """
        if not sub_indicador_codigos:
            return []

        # Assuming Revision is linked to Evidencia or CargaEvidencia
        query = """
            SELECT
                r.RevisionID,
                r.EvidenciaID, 
                r.Comentario,
                r.UsuarioID,
                r.FechaRevision,
                r.Estado
            FROM Revision r -- [TODO: UPDATE TABLE NAME]
            JOIN Evidencia e ON r.EvidenciaID = e.EvidenciaID
            JOIN SubIndicadores si ON e.IndicadorID = si.IndicadorID
            WHERE si.Codigo IN ({})
        """.format(','.join(['?'] * len(sub_indicador_codigos)))

        try:
            self.cursor.execute(query, sub_indicador_codigos)
            return [
                RevisionSource(
                    RevisionID=row[0],
                    EvidenciaID=row[1],
                    Comentario=row[2],
                    UsuarioID=row[3],
                    FechaRevision=row[4],
                    EstadoRevision=row[5]
                )
                for row in self.cursor.fetchall()
            ]
        except Exception as e:
            print(f"[WARNING] No se pudo leer tabla Revision: {e}")
            return []


import uuid
from datetime import datetime
from typing import List, Optional
from models.entities import (
    TipoVencimiento, TiposIndicador, Indicador, SubIndicador,
    EvidenciaSource, EvidenciaDest, SubIndicadorEvidencia, FechaVencimientoSubIndicadorEvidencia,
    Ibog, ArchivoDest, CargaEvidenciaSource, PuntuacionDest, RevisionSource, RevisionEvidenciaDest, ComentarioRevisionDest
)

class TransformationService:
    """
    Servicio para transformar datos del esquema FUENTE al esquema DESTINO.
    Mapeos principales:
    - dbo.TipoVencimiento -> Mantenimiento.TipoVencimiento
    - dbo.TipoIndicador -> Mantenimiento.TiposIndicador
    - dbo.Ibog -> Mantenimiento.Indicadores
    - dbo.SubIndicadores -> Mantenimiento.SubIndicadores
    """

    def __init__(self):
        self.archivo_map = {} # Map NombreArchivo -> ArchivoDest.Id
        self.sub_ev_map = {} # Map (IndicadorID, EvidenciaID) -> SubIndicadorEvidencia.Id

    def transformar_tipo_vencimiento(self, source_items: List[TipoVencimiento]) -> List[TipoVencimiento]:
        """
        Transforma TipoVencimiento.
        IGNORA la fuente y retorna lista estática solicitada:
        1: Automático
        2: Manual
        3: Fijo
        """
        # User requested static data:
        # 1	Automático	Cantidad de días automático desde la fecha de puntuación, valor según la guía
        # 2	Manual	La fecha y la puntuación son seleccionables/editables
        # 3	Fijo	Fecha específica en el año, valor fijo o según la guía
        
        static_data = [
            TipoVencimiento(
                Id=1,
                Nombre="Automático",
                Descripcion="Cantidad de días automático desde la fecha de puntuación, valor según la guía",
                CreatedAt=datetime(2025, 10, 31, 15, 33, 21),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            ),
             TipoVencimiento(
                Id=2,
                Nombre="Manual",
                Descripcion="La fecha y la puntuación son seleccionables/editables",
                CreatedAt=datetime(2025, 10, 31, 15, 33, 21),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            ),
             TipoVencimiento(
                Id=3,
                Nombre="Fijo",
                Descripcion="Fecha específica en el año, valor fijo o según la guía",
                CreatedAt=datetime(2025, 9, 12, 9, 2, 0),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            )
        ]
        return static_data

    def transformar_tipo_indicador(self, source_items: List[TiposIndicador]) -> List[TiposIndicador]:
        """
        Transforma TipoIndicador.
        Fuente y Destino son similares, solo ajustar campos de auditoría.
        """
        transformed = []
        for item in source_items:
            new_item = TiposIndicador(
                Id=item.Id,
                Nombre=item.Nombre or "Sin Nombre",
                Descripcion=item.Descripcion or "Sin Descripcion",
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            )
            transformed.append(new_item)
        return transformed

    def transformar_indicador(self, source_items: List[Ibog]) -> List[Indicador]:
        """
        Transforma dbo.Ibog (Fuente) -> Mantenimiento.Indicadores (Destino)
        """
        transformed = []
        for item in source_items:
            new_item = Indicador(
                Id=item.IbogID,
                Codigo=item.Codigo,
                Nombre=item.Descripcion, # Ibog uses Descripcion as name
                Descripcion=item.Descripcion,
                TipoIndicadorId=1, # Default or mapped logic needed
                Peso=item.Peso,
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True if item.Estado == 'Activo' else False,
                IsDeleted=False
            )
            transformed.append(new_item)
        return transformed

    def transformar_sub_indicador(self, source_items: List[SubIndicador]) -> List[SubIndicador]:
        """
        Transforma dbo.SubIndicadores (Fuente) -> Mantenimiento.SubIndicadores (Destino)
        """
        transformed = []
        for item in source_items:
            new_item = SubIndicador(
                Id=item.Id, # Source ID (mapped from IndicadorID in Repo)
                IndicadorId=item.ibogId, # Parent ID
                Codigo=item.Codigo,
                Nombre=item.Descripcion, # Map Desc to Nombre
                Descripcion=item.Descripcion,
                Peso=item.Peso,
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True if item.Estado == 'Activo' else False,
                IsDeleted=False
            )
            transformed.append(new_item)
        return transformed

    # ============================================================
    # EVIDENCIAS (Split Source -> 3 Destination Tables)
    # ============================================================
    
    def _sanitize_date(self, date_val):
        """Convierte fechas str o datetime a algo seguro para SQL Server"""
        if not date_val:
            return None
        if isinstance(date_val, str):
            if date_val.startswith('0001'):
                return None
            try:
                # Truncar si es necesario o devolver tal cual si el driver lo maneja
                # Pero mejor asegurar que no sea 0001
                return datetime.fromisoformat(date_val)
            except ValueError:
                return None
        if isinstance(date_val, datetime):
            if date_val.year < 1753:
                return None
            return date_val
        return None

    def transformar_evidencia(self, items: List[EvidenciaSource]) -> tuple[List[EvidenciaDest], List[FechaVencimientoSubIndicadorEvidencia], List[SubIndicadorEvidencia], List[ArchivoDest]]:
        """
        Transforma dbo.Evidencia en 4 tablas destino:
        - Evidencia.Evidencias
        - Evidencia.FechaVencimientoSubIndicadorEvidencias
        - Evidencia.SubIndicadorEvidencias
        - Evidencia.Archivos
        
        Retorna: (evidencias, fechas_vencimiento, sub_indicador_evidencias, archivos)
        """
        evidencias_dest = []
        fechas_dest = []
        sub_ind_evidencias_dest = []
        archivos_dest = []
        
        # Reset maps
        self.archivo_map = {} 
        self.sub_ev_map = {}
        
        # ID tracking
        fecha_id_counter = 1
        sub_ind_ev_id_counter = 1
        archivo_id_counter = 1
        
        for item in items:
            safe_fecha = self._sanitize_date(item.FechaVencimiento)
            
            # 1. Mapear Evidencia Base
            evidencia = EvidenciaDest(
                Id=item.EvidenciaID,
                Nombre=item.Descipcion if item.Descipcion else f"Evidencia {item.Codigo}",
                Descripcion=item.Descipcion if item.Descipcion else f"Evidencia {item.Codigo}",
                Valor=item.Valor if item.Valor else 0.0,
                PreRequisitoId=int(item.Prerequisito) if item.Prerequisito and item.Prerequisito.isdigit() else None,
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=item.Estado == 'Activo',
                IsDeleted=False,
                AplicaVencimiento=item.AplicaVencimiento,
                CantidadDias=int(item.CantDias) if item.CantDias and item.CantDias.isdigit() else 0,
                FechaVencimiento=safe_fecha,
                Codigo=item.Codigo
            )
            evidencias_dest.append(evidencia)
            
            # 2. Manejar Fecha Vencimiento
            fecha_venc_id = None
            if item.AplicaVencimiento:
                fecha_venc_id = fecha_id_counter
                original_tipo_id = item.TipoVencimiento
                mapped_tipo_id = None
                
                # Mapping logic
                if original_tipo_id == 1:
                    mapped_tipo_id = 2
                elif original_tipo_id == 2:
                    mapped_tipo_id = 1
                else:
                    mapped_tipo_id = original_tipo_id
                
                fecha = FechaVencimientoSubIndicadorEvidencia(
                    Id=fecha_venc_id,
                    TipoVencimientoId=mapped_tipo_id,
                    FechaVencimiento=safe_fecha if safe_fecha else datetime(1900, 1, 1),
                    PeriodicidadDias=int(item.CantDias) if item.CantDias and item.CantDias.isdigit() else 0,
                    CreatedAt=datetime.now(),
                    CreatedBy="MigrationScript",
                    IsActive=item.Estado == 'Activo',
                    IsDeleted=False
                )
                fechas_dest.append(fecha)
                fecha_id_counter += 1
            
            sub_ind_ev = SubIndicadorEvidencia(
                Id=sub_ind_ev_id_counter,
                SubIndicadorId=item.IndicadorID,
                EvidenciaId=item.EvidenciaID,
                FechaVencimientoSubIndicadorEvidenciaId=fecha_venc_id,
                TipoEvaluacionId=1,
                FechaVenciento=safe_fecha if safe_fecha else datetime(1900, 1, 1),
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=item.Estado == 'Activo',
                IsDeleted=False
            )
            sub_ind_evidencias_dest.append(sub_ind_ev)
            
            # Populate Map
            self.sub_ev_map[(item.IndicadorID, item.EvidenciaID)] = sub_ind_ev.Id
            
            # 4. Crear Archivo (Si existe NombreArchivo)
            if item.NombreArchivo:
                archivo = ArchivoDest(
                    Id=archivo_id_counter,
                    CoedomId=0, # Default Global/System
                    SubIndicadorEvidenciaId=sub_ind_ev_id_counter,
                    NombreOriginal=item.NombreArchivo,
                    ArchivoBinario=b'', # Empty binary
                    EstadoArchivoId=1, # Active
                    EvidenciaId=None, # Explicitly valid linking via SubIndicadorEvidencia typically sufficient, but table has EvidenciaId Nullable.
                    CreatedAt=datetime.now(),
                    CreatedBy="MigrationScript",
                    IsActive=True,
                    IsDeleted=False,
                    RowGuid=uuid.uuid4(),
                    TipoAlmacenamiento=2, # Externo (User requested 2)
                    RutaExterna=f"https://www.sismap.gob.do/Educacion/uploads/evidencias/{item.NombreArchivo}"
                )
                archivos_dest.append(archivo)
                
                # Update Map
                self.archivo_map[item.NombreArchivo] = archivo.Id
                
                archivo_id_counter += 1
            
            sub_ind_ev_id_counter += 1
            
        return evidencias_dest, fechas_dest, sub_ind_evidencias_dest, archivos_dest

    # ============================================================
    # PUNTUACION Y REVISIONES
    # ============================================================

    def transformar_puntuacion(self, source_items: List[CargaEvidenciaSource], start_file_id: int, puntuador_id: str = None, start_score_id: int = 1) -> tuple[List[PuntuacionDest], List[ArchivoDest]]:
        """
        Transforma CargaEvidencia -> Evidencia.Puntuacion AND Evidencia.Archivos
        """
        scores = []
        files = []
        file_id_counter = start_file_id
        score_id_counter = start_score_id
        
        for item in source_items:
            # 1. Create File (Upload)
            # Find SubIndicadorEvidenciaId
            key = (item.IndicadorID, item.EvidenciaID)
            sub_ev_id = self.sub_ev_map.get(key)
            
            # If not found, we cannot correctly link the file to the requirement.
            # Log warning or skip? For migration, skipping orphaned uploads is typical or use placeholder.
            # Assuming data consistency, it should be found.
            
            row_guid = uuid.uuid4()
            
            archivo = ArchivoDest(
                Id=file_id_counter,
                CoedomId=item.OrganismoID if item.OrganismoID else 0,
                SubIndicadorEvidenciaId=sub_ev_id if sub_ev_id else None, # Use sub_ev_id from map
                NombreOriginal=item.NombreArchivo if item.NombreArchivo else "SinNombre.pdf",
                ArchivoBinario=b'', 
                EstadoArchivoId=1,
                EvidenciaId=None,
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False,
                RowGuid=row_guid,
                TipoAlmacenamiento=2,
                RutaExterna=f"https://www.sismap.gob.do/Educacion/uploads/evidencias/{item.NombreArchivo}"
            )
            if sub_ev_id:
                archivo.SubIndicadorEvidenciaId = sub_ev_id
            
            files.append(archivo)
            
            # 2. Create Score
            new_score = PuntuacionDest(
                Id=score_id_counter, 
                ArchivoEvidenciaId=file_id_counter, # Link to the file we just made
                PuntuadorUsuarioId=puntuador_id, # Use injected UserID
                Calificacion=item.Puntuacion if item.Puntuacion is not None else 0.0,
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            )
            scores.append(new_score)
            
            file_id_counter += 1
            score_id_counter += 1
            
        return scores, files

    def transformar_revision(self, source_items: List[RevisionSource]) -> tuple[List[RevisionEvidenciaDest], List[ComentarioRevisionDest]]:
        """Transforma Revision -> RevisionEvidencias + Comentarios"""
        revisions = []
        comments = []
        
        for item in source_items:
            rev_dest = RevisionEvidenciaDest(
                Id=item.RevisionID,
                ArchivoEvidenciaId=item.EvidenciaID, # Linking check needed
                FechaRevisionConcluida=item.FechaRevision,
                UsuarioId=None, # Map user
                EstadoDadoId=1, # Default/Map
                NivelRevisionEvidencia=1,
                RevisionCoedomId=1, # Placeholder
                CreatedAt=item.FechaRevision,
                CreatedBy="MigrationScript",
                IsActive=True
            )
            revisions.append(rev_dest)
            
            if item.Comentario:
                comm_dest = ComentarioRevisionDest(
                    Id=item.RevisionID, # Share ID or auto-inc
                    RevisionEvidenciaId=item.RevisionID,
                    Observaciones=item.Comentario,
                    UsuarioId=None,
                    CreatedAt=item.FechaRevision,
                    CreatedBy="MigrationScript",
                    IsActive=True
                )
                comments.append(comm_dest)
                
        return revisions, comments

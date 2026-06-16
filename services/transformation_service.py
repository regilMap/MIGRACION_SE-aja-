import uuid
import re
from datetime import datetime
from typing import List, Optional
from models.entities import (
    TipoVencimiento, TiposSubIndicador, Indicador, SubIndicador,
    EvidenciaSource, EvidenciaDest, SubIndicadorEvidencia, FechaVencimientoSubIndicadorEvidencia,
    Ibog, ArchivoDest, CargaEvidenciaSource, PuntuacionDest, RevisionSource, RevisionEvidenciaDest, ComentarioRevisionDest
)

class TransformationService:
    """
    Servicio para transformar datos del esquema FUENTE al esquema DESTINO.
    Mapeos principales:
    - dbo.TipoVencimiento -> Mantenimiento.TipoVencimiento
    - dbo.TipoSubIndicador -> Mantenimiento.TiposSubIndicador
    - dbo.Ibog -> Mantenimiento.Indicadores
    - dbo.SubIndicadores -> Mantenimiento.SubIndicadores
    """

    def __init__(self):
        self.archivo_map = {} # Map NombreArchivo -> ArchivoDest.Id
        self.sub_ev_map = {} # Map (IndicadorID, EvidenciaID) -> SubIndicadorEvidencia.Id
        self.evidencia_valor_map = {} # Map EvidenciaID -> Valor (float)

    def _ajustar_puntuaciones_por_subindicador(self, items: List[CargaEvidenciaSource]):
        # 0. Deduplicación por EvidenciaID: Quedarse con el ULTIMO archivo por CADA evidencia
        # Agrupar por (OrganismoID, EvidenciaID)
        evidencia_groups = {}
        for item in items:
            if item.Puntuacion is None: continue
            key = (item.OrganismoID, item.EvidenciaID)
            if key not in evidencia_groups: evidencia_groups[key] = []
            evidencia_groups[key].append(item)
            
        min_date = datetime(1900, 1, 1)

        for key, group in evidencia_groups.items():
            if len(group) > 1:
                # Ordenar descendente por FechaArchivo (Mas reciente primero)
                group.sort(key=lambda x: (x.FechaArchivo if x.FechaArchivo else min_date), reverse=True)
                
                # Quedarse con el primero (mas reciente), los demas 0
                for i in range(1, len(group)):
                    # print(f"DEBUG_DEDUP: Zeroing Duplicate {group[i].Puntuacion} (File: {group[i].NombreArchivo})")
                    group[i].Puntuacion = 0.0

    def format_indicator_code(self, code: str) -> str:
        if not code:
            return ""
        code = code.strip()
        match = re.match(r'^([A-Za-z]+)?\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?(.*)$', code)
        if not match:
            return code
        
        prefix, ind_part, sub_part, ev_part, rest = match.groups()
        try:
            indicator = int(ind_part)
        except ValueError:
            return code

        if sub_part is None:
            res = f"{indicator}"
        else:
            try:
                subindicator = int(sub_part)
                res = f"{indicator}.{subindicator:02d}"
            except ValueError:
                res = f"{indicator}.{sub_part}"
                
            if ev_part is not None:
                res = f"{res}.{ev_part}"
                
        prefix_str = f"{prefix} " if prefix else ""
        return f"{prefix_str}{res}{rest}"

    def map_to_source_code(self, code: str) -> str:
        if not code:
            return ""
        code = code.strip()
        match = re.match(r'^([A-Za-z]+)?\s*(\d+)\.(\d+)(.*)$', code)
        if not match:
            return code
        
        prefix, ind_part, sub_part, rest = match.groups()
        try:
            indicator = int(ind_part)
            subindicator = int(sub_part)
        except ValueError:
            return code
            
        if indicator == 5:
            return code
            
        if prefix == 'Ns' and indicator == 7 and subindicator == 2:
            return '07.2'
            
        prefix_str = f"{prefix} " if prefix else ""
        return f"{prefix_str}{indicator:02d}.{subindicator}{rest}"

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

    def transformar_tipo_sub_indicador(self, source_items: List[TiposSubIndicador]) -> List[TiposSubIndicador]:
        """
        Transforma TipoSubIndicador.
        Fuente y Destino son similares, solo ajustar campos de auditoría.
        """
        transformed = []
        for item in source_items:
            new_item = TiposSubIndicador(
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
        sub_indicadores_tipo_2 = {
            "02.2", "02.3", "02.4", "02.6", "02.7", "02.8", "03.1", "03.2", "03.3", "03.5",
            "03.6", "04.1", "04.2", "04.3", "5.01", "5.02", "5.03", "5.04", "5.05", "5.06",
            "5.07", "5.08", "5.09", "5.10", "06.1", "06.2", "06.3", "06.4", "06.5"
        }

        transformed = []
        for item in source_items:
            # Determinar TipoSubIndicadorId
            tipo_sub_indicador_id = 1
            if item.Codigo and item.Codigo.strip() in sub_indicadores_tipo_2:
                tipo_sub_indicador_id = 2

            codigo_transformed = item.Codigo.strip() if item.Codigo else ""
            if codigo_transformed == '07.2':
                codigo_transformed = 'Ns 07.2'
            codigo_transformed = self.format_indicator_code(codigo_transformed)

            nombre_transformed = item.Descripcion.strip() if item.Descripcion else ""
            if item.Codigo and item.Codigo.strip() == '07.2':
                nombre_transformed = 'Porcentaje de Estudiantes Según Niveles de Desempeño en las Pruebas Nacionales (Nivel Secundario)'

            new_item = SubIndicador(
                Id=item.Id, # Source ID (mapped from IndicadorID in Repo)
                IndicadorId=item.ibogId, # Parent ID
                TipoSubIndicadorId=tipo_sub_indicador_id,
                Codigo=codigo_transformed,
                Nombre=nombre_transformed, # Map Desc to Nombre
                Descripcion=nombre_transformed,
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
        self.evidencia_valor_map = {}
        
        # ID tracking
        fecha_id_counter = 1
        sub_ind_ev_id_counter = 1
        archivo_id_counter = 1
        
        for item in items:
            source_codigo = item.Codigo.strip() if item.Codigo else ""
            if source_codigo == '07.2' or source_codigo.startswith('07.2.'):
                source_codigo = 'Ns ' + source_codigo

            final_valor = float(item.Valor) if item.Valor else 0.0
            if source_codigo == '03.3.1' or item.EvidenciaID == 77:
                final_valor = 100.0
            
            self.evidencia_valor_map[item.EvidenciaID] = final_valor
            current_time = datetime.now()
            
            # Aplicar reglas de vencimiento personalizadas
            # Aplicar reglas de vencimiento personalizadas
            if source_codigo == '01.1.2':
                # Evidencia 01.1.2 (PEC): Manual (Tipo 2), sin periodicidad
                mapped_tipo_id = 2
                final_periodicidad = None
                final_fecha = datetime(1900, 1, 1)
                aplica_venc = True
            elif item.IndicadorID == 2 or source_codigo == '01.2' or source_codigo.startswith('01.2.'):
                # Subindicador 01.2 (CAF): Fijo el 30 de noviembre, periodicidad 365 días
                mapped_tipo_id = 3
                final_periodicidad = 365
                final_fecha = datetime(2026, 11, 30)
                aplica_venc = True
            else:
                # Resto de evidencias: Fijo el 15 de agosto, periodicidad 365 días
                mapped_tipo_id = 3
                final_periodicidad = 365
                final_fecha = datetime(2026, 8, 15)
                aplica_venc = True

            clean_codigo = self.format_indicator_code(source_codigo)
            
            # New Standardized Naming: [Code] [Name]
            base_name = item.NombreArchivo.strip() if item.NombreArchivo else (item.Descipcion.strip() if item.Descipcion else "Evidencia")
            new_standard_name = f"{clean_codigo} {base_name}"
            
            # 1. Mapear Evidencia Base
            evidencia = EvidenciaDest(
                Id=item.EvidenciaID,
                Nombre=new_standard_name[:255], # Truncate to fit NVARCHAR(255)
                Descripcion=new_standard_name[:500], # Truncate to fit NVARCHAR(500) just in case
                Valor=final_valor,
                PreRequisitoId=int(item.Prerequisito) if item.Prerequisito and item.Prerequisito.isdigit() else None,
                CreatedAt=current_time,
                CreatedBy="MigrationScript",
                IsActive=item.Estado == 'Activo',
                IsDeleted=False,
                AplicaVencimiento=aplica_venc,
                CantidadDias=final_periodicidad,
                FechaVencimiento=final_fecha,
                Codigo=clean_codigo
            )
            evidencias_dest.append(evidencia)
            
            # 2. Manejar Fecha Vencimiento
            # Requirement: ALL SubIndicadorEvidencia must have a FechaVencimientoSubIndicadorEvidenciaId
            fecha_venc_id = fecha_id_counter
            
            fecha = FechaVencimientoSubIndicadorEvidencia(
                Id=fecha_venc_id,
                TipoVencimientoId=mapped_tipo_id,
                FechaVencimiento=final_fecha,
                PeriodicidadDias=final_periodicidad,
                CreatedAt=current_time,
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
                TipoEvaluacionId=2, # Automática (Id = 2)
                FechaVenciento=final_fecha,
                CreatedAt=current_time,
                CreatedBy="MigrationScript",
                IsActive=item.Estado == 'Activo',
                IsDeleted=False
            )
            sub_ind_evidencias_dest.append(sub_ind_ev)
            
            # Populate Map
            self.sub_ev_map[(item.IndicadorID, item.EvidenciaID)] = sub_ind_ev.Id
            
            # 4. Crear Archivo (Anteriormente se creaban Plantillas aqui)
            # DECISION: Excluir estos archivos de la migracion.
            # Los archivos reales vienen en 'CargaEvidencia' (transformar_puntuacion).
            # Se elimina la logica que creaba ArchivoDest con CoedomId=0.
            pass

            
            sub_ind_ev_id_counter += 1
            
        return evidencias_dest, fechas_dest, sub_ind_evidencias_dest, archivos_dest

    # ============================================================
    # PUNTUACION Y REVISIONES
    # ============================================================

    def transformar_puntuacion(self, source_items: List[CargaEvidenciaSource], start_file_id: int, puntuador_id: str = None, start_score_id: int = 1, existing_file_ids: Optional[set] = None) -> tuple[List[PuntuacionDest], List[ArchivoDest]]:
        """
        Transforma CargaEvidencia -> Evidencia.Puntuacion AND Evidencia.Archivos
        """
        scores = []
        files = []
        file_id_counter = start_file_id
        score_id_counter = start_score_id
        
        # --- Pre-procesamiento: Ajustar puntuaciones de 0 al valor total de la evidencia ---
        for item in source_items:
            # Custom scaling rule for 03.3.1 (EvidenciaID = 77)
            if item.EvidenciaID == 77:
                if item.Puntuacion is not None and item.Puntuacion > 0:
                    # Target weight is 100.0, source weight is 50.0. Scale up by 2.0
                    item.Puntuacion = float(item.Puntuacion) * 2.0

            if item.Puntuacion == 0.0 or item.Puntuacion == 0:
                item.Puntuacion = self.evidencia_valor_map.get(item.EvidenciaID, 0.0)

        # --- Pre-procesamiento: Validar limites de puntuacion ---
        self._ajustar_puntuaciones_por_subindicador(source_items)
        
        for item in source_items:
            if existing_file_ids:
                while file_id_counter in existing_file_ids:
                    file_id_counter += 1
            # 1. Create File (Upload)
            # Find SubIndicadorEvidenciaId
            key = (item.IndicadorID, item.EvidenciaID)
            sub_ev_id = self.sub_ev_map.get(key)
            
            # If not found, we cannot correctly link the file to the requirement.
            # Log warning or skip? For migration, skipping orphaned uploads is typical or use placeholder.
            # Assuming data consistency, it should be found.
            
            row_guid = uuid.uuid4()
            
            # Determine Score and Status
            current_score = item.Puntuacion
            
            # Logic: NULL Score -> SKIP
            if current_score is None:
                continue

            # If here, score is not None (0 or > 0) -> Status 3 (Approved)
            estado_archivo_id = 3 
            
            archivo = ArchivoDest(
                Id=file_id_counter,
                CoedomId=item.OrganismoID if item.OrganismoID else 0,
                SubIndicadorEvidenciaId=sub_ev_id if sub_ev_id else None, # Use sub_ev_id from map
                NombreOriginal=(item.NombreArchivo[:95] + '...') if item.NombreArchivo and len(item.NombreArchivo) > 99 else (item.NombreArchivo if item.NombreArchivo else "SinNombre.pdf"),

                ArchivoBinario=b'', 
                EstadoArchivoId=estado_archivo_id, 
                EvidenciaId=None,
                CreatedAt=self._sanitize_date(item.FechaArchivo) if item.FechaArchivo else datetime.now(),
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
            
            # 2. Create Score (If not None - allowing 0)
            if item.Puntuacion is not None:
                new_score = PuntuacionDest(
                    Id=score_id_counter, 
                    ArchivoEvidenciaId=file_id_counter, # Link to the file we just made
                    PuntuadorUsuarioId=puntuador_id, # Use injected UserID
                    Calificacion=current_score,
                    CreatedAt=self._sanitize_date(item.FechaArchivo) if item.FechaArchivo else datetime.now(),
                    CreatedBy="MigrationScript",
                    IsActive=True,
                    IsDeleted=False
                )
                scores.append(new_score)
                score_id_counter += 1
            
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

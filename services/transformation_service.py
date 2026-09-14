import uuid
import re
from datetime import datetime
from typing import List, Optional, Tuple
from models.entities import (
    TipoVencimiento, TiposSubIndicador, TiposEvaluacion, EstadosArchivo,
    Indicador, SubIndicador, EvidenciaSource, EvidenciaDest, SubIndicadorEvidencia, 
    FechaVencimientoSubIndicadorEvidencia, Ibog, ArchivoDest, CargaEvidenciaSource, 
    PuntuacionDest, RevisionSource, RevisionEvidenciaDest, ComentarioRevisionDest,
    NoticiaSource, NoticiaDest
)

class TransformationService:
    """
    Servicio para transformar datos del esquema FUENTE (SISMAPV1DB_SG) al esquema DESTINO (SISMAP_SEGURIDAD).
    """

    def __init__(self):
        self.archivo_map = {} 
        self.sub_ev_map = {} 
        self.evidencia_valor_map = {} 

    def _sanitize_date(self, date_val):
        """Convierte fechas str o datetime a algo seguro para SQL Server"""
        if not date_val:
            return None
        if isinstance(date_val, str):
            if date_val.startswith('0001'):
                return None
            try:
                return datetime.fromisoformat(date_val)
            except ValueError:
                return None
        if isinstance(date_val, datetime):
            if date_val.year < 1753:
                return None
            return date_val
        return None

    def format_code(self, code: str) -> str:
        if not code:
            return ""
        return code.strip()

    def transformar_tipo_vencimiento(self, source_items: List[TipoVencimiento]) -> List[TipoVencimiento]:
        """
        Retorna catálogo estándar para Seguridad.TiposVencimiento:
        1: Automático
        2: Manual
        3: Fijo
        """
        static_data = [
            TipoVencimiento(
                Id=1,
                Codigo="AUTO",
                Nombre="Automático",
                Descripcion="Generación de vencimiento automática según periodicidad",
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            ),
            TipoVencimiento(
                Id=2,
                Codigo="MANUAL",
                Nombre="Manual",
                Descripcion="Fecha y condiciones gestionadas manualmente",
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            ),
            TipoVencimiento(
                Id=3,
                Codigo="FIJO",
                Nombre="Fijo",
                Descripcion="Fecha específica prefijada en el periodo",
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            )
        ]
        return static_data

    def transformar_indicador(self, source_items: List[Ibog]) -> List[Indicador]:
        """
        Transforma dbo.Ibog (Fuente) -> Seguridad.Indicadores (Destino)
        """
        transformed = []
        for idx, item in enumerate(source_items, 1):
            new_item = Indicador(
                Id=item.IbogID,
                Codigo=item.Codigo.strip() if item.Codigo else f"IND-{item.IbogID}",
                Nombre=item.Descripcion.strip() if item.Descripcion else f"Indicador {item.IbogID}",
                Descripcion=item.Descripcion.strip() if item.Descripcion else "",
                Orden=idx,
                Peso=float(item.Peso) if item.Peso else 0.0,
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True if item.Estado and str(item.Estado).lower() == 'activo' else True,
                IsDeleted=False
            )
            transformed.append(new_item)
        return transformed

    def transformar_sub_indicador(self, source_items: List[SubIndicador]) -> List[SubIndicador]:
        """
        Transforma dbo.SubIndicadores (Fuente) -> Seguridad.SubIndicadores (Destino)
        """
        transformed = []
        for idx, item in enumerate(source_items, 1):
            codigo_clean = item.Codigo.strip() if item.Codigo else f"SUB-{item.Id}"
            nombre_clean = item.Descripcion.strip() if item.Descripcion else f"SubIndicador {item.Id}"

            new_item = SubIndicador(
                Id=item.Id,
                IndicadorId=item.ibogId or item.IndicadorId,
                TipoSubIndicadorId=1, # Default TipoSubIndicador
                TipoVencimientoId=1,   # Default TipoVencimiento
                Codigo=codigo_clean,
                Nombre=nombre_clean,
                Descripcion=nombre_clean,
                Orden=idx,
                Peso=float(item.Peso) if item.Peso else 0.0,
                UnidadResponsable=None,
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True if item.Estado and str(item.Estado).lower() == 'activo' else True,
                IsDeleted=False
            )
            transformed.append(new_item)
        return transformed

    def transformar_evidencia(self, items: List[EvidenciaSource]) -> Tuple[List[EvidenciaDest], List[FechaVencimientoSubIndicadorEvidencia], List[SubIndicadorEvidencia]]:
        """
        Transforma dbo.Evidencia en 3 tablas destino:
        - Seguridad.Evidencias
        - Seguridad.FechasVencimientoSubIndicadorEvidencia
        - Seguridad.SubIndicadorEvidencias
        """
        evidencias_dest = []
        fechas_dest = []
        sub_ind_evidencias_dest = []
        
        self.sub_ev_map = {}
        self.evidencia_valor_map = {}
        
        fecha_id_counter = 1
        sub_ind_ev_id_counter = 1
        
        seen_codigos = {}
        for item in items:
            raw_codigo = item.Codigo.strip() if item.Codigo else f"EV-{item.EvidenciaID}"
            if raw_codigo in seen_codigos:
                seen_codigos[raw_codigo] += 1
                source_codigo = f"{raw_codigo}-{seen_codigos[raw_codigo]}"
            else:
                seen_codigos[raw_codigo] = 1
                source_codigo = raw_codigo

            final_valor = float(item.Valor) if item.Valor else 0.0
            self.evidencia_valor_map[item.EvidenciaID] = final_valor
            current_time = datetime.now()
            
            # Periodicidad / Días
            cant_dias = None
            if item.CantDias and str(item.CantDias).isdigit():
                cant_dias = int(item.CantDias)
                
            base_name = item.NombreArchivo.strip() if item.NombreArchivo else (item.Descipcion.strip() if item.Descipcion else f"Evidencia {item.EvidenciaID}")
            
            # 1. Evidencia Base
            evidencia = EvidenciaDest(
                Id=item.EvidenciaID,
                Codigo=source_codigo[:50],
                Nombre=base_name[:250],
                Descripcion=(item.Descipcion or base_name)[:1000],
                Valor=final_valor,
                AplicaVencimiento=bool(item.AplicaVencimiento),
                CantidadDias=cant_dias,
                FechaVencimiento=self._sanitize_date(item.FechaVencimiento),
                PreRequisitoId=int(item.Prerequisito) if item.Prerequisito and item.Prerequisito.isdigit() else None,
                CreatedAt=current_time,
                CreatedBy="MigrationScript",
                IsActive=True if item.Estado and str(item.Estado).lower() == 'activo' else True,
                IsDeleted=False
            )
            evidencias_dest.append(evidencia)
            
            # 2. Fecha Vencimiento
            fecha_venc_id = fecha_id_counter
            fecha = FechaVencimientoSubIndicadorEvidencia(
                Id=fecha_venc_id,
                TipoVencimientoId=item.TipoVencimiento if item.TipoVencimiento else 1,
                FechaVencimiento=self._sanitize_date(item.FechaVencimiento) or datetime(2026, 12, 31),
                PeriodicidadDias=cant_dias,
                CreatedAt=current_time,
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            )
            fechas_dest.append(fecha)
            fecha_id_counter += 1
            
            # 3. SubIndicadorEvidencia Pivot
            sub_ind_ev = SubIndicadorEvidencia(
                Id=sub_ind_ev_id_counter,
                SubIndicadorId=item.IndicadorID,
                EvidenciaId=item.EvidenciaID,
                FechaVencimientoSubIndicadorEvidenciaId=fecha_venc_id,
                TipoEvaluacionId=1, # Manual / Automática
                FechaVenciento=self._sanitize_date(item.FechaVencimiento) or datetime(2026, 12, 31),
                CreatedAt=current_time,
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            )
            sub_ind_evidencias_dest.append(sub_ind_ev)
            
            # Record map key: (SubIndicadorId, EvidenciaId) -> SubIndicadorEvidencia.Id
            self.sub_ev_map[(item.IndicadorID, item.EvidenciaID)] = sub_ind_ev.Id
            sub_ind_ev_id_counter += 1
            
        return evidencias_dest, fechas_dest, sub_ind_evidencias_dest

    def transformar_puntuacion(self, source_items: List[CargaEvidenciaSource], start_file_id: int = 1, puntuador_id: str = None, existing_file_ids: Optional[set] = None, valid_users: Optional[set] = None, fallback_user_guid: Optional[str] = None) -> Tuple[List[PuntuacionDest], List[ArchivoDest]]:
        """
        Transforma CargaEvidencia -> Seguridad.Archivos y Seguridad.Puntuaciones
        """
        scores = []
        files = []
        file_id_counter = start_file_id
        score_id_counter = 1
        
        default_user_guid = fallback_user_guid or "00000000-0000-0000-0000-000000000001"
        puntuador_guid = puntuador_id if (puntuador_id and valid_users and puntuador_id.upper() in valid_users) else (puntuador_id if puntuador_id else default_user_guid)

        for item in source_items:
            if existing_file_ids:
                while file_id_counter in existing_file_ids:
                    file_id_counter += 1

            key = (item.IndicadorID, item.EvidenciaID)
            sub_ev_id = self.sub_ev_map.get(key)
            row_guid = str(uuid.uuid4())
            
            nombre_archivo = item.NombreArchivo if item.NombreArchivo else "Evidencia.pdf"
            
            # 1. Crear registro en Seguridad.Archivos
            archivo = ArchivoDest(
                Id=file_id_counter,
                CoedomId=item.OrganismoID if item.OrganismoID else 0,
                SubIndicadorEvidenciaId=sub_ev_id,
                NombreOriginal=nombre_archivo[:260],
                ArchivoBinario=b'',
                RowGuid=row_guid,
                EstadoArchivoId=3, # 3 = Aprobado / Puntuado
                TipoAlmacenamiento=2, # External link
                RutaExterna=f"https://www.sismap.gob.do/Seguridad/uploads/evidencias/{nombre_archivo}",
                CreatedAt=self._sanitize_date(item.FechaArchivo) or datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            )
            files.append(archivo)
            
            # 2. Crear registro en Seguridad.Puntuaciones
            calificacion = item.Puntuacion if item.Puntuacion is not None else 0.0
            
            score_user = default_user_guid
            if item.UsuarioID:
                clean_uid = str(item.UsuarioID).strip().upper()
                if valid_users and clean_uid in valid_users:
                    score_user = str(item.UsuarioID).strip()
                elif puntuador_guid:
                    score_user = puntuador_guid

            score = PuntuacionDest(
                Id=score_id_counter,
                ArchivoEvidenciaId=file_id_counter,
                PuntuadorUsuarioId=score_user,
                Calificacion=calificacion,
                Observacion="Migrado de CargaEvidencia",
                CreatedAt=self._sanitize_date(item.FechaArchivo) or datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            )
            scores.append(score)
            
            file_id_counter += 1
            score_id_counter += 1

        return scores, files

    def transformar_revision(self, source_items: List[RevisionSource], valid_users: Optional[set] = None, fallback_user_guid: Optional[str] = None) -> Tuple[List[RevisionEvidenciaDest], List[ComentarioRevisionDest]]:
        """Transforma Revision -> Seguridad.RevisionesEvidencia + Seguridad.ComentariosRevisionEvidencia"""
        revisions = []
        comments = []
        default_user_guid = fallback_user_guid or "00000000-0000-0000-0000-000000000001"
        
        for item in source_items:
            user_guid = default_user_guid
            if item.UsuarioID:
                clean_uid = str(item.UsuarioID).strip().upper()
                if valid_users and clean_uid in valid_users:
                    user_guid = str(item.UsuarioID).strip()

            rev_dest = RevisionEvidenciaDest(
                Id=item.RevisionID,
                ArchivoEvidenciaId=item.EvidenciaID,
                FechaRevisionConcluida=self._sanitize_date(item.FechaRevision),
                UsuarioId=user_guid,
                RevisionCoedomId=1,
                EstadoDadoId=1,
                NivelRevisionEvidencia=1,
                CreatedAt=self._sanitize_date(item.FechaRevision) or datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            )
            revisions.append(rev_dest)
            
            if item.Comentario:
                comm_dest = ComentarioRevisionDest(
                    Id=item.RevisionID,
                    RevisionEvidenciaId=item.RevisionID,
                    UsuarioId=user_guid,
                    Observaciones=item.Comentario,
                    CreatedAt=self._sanitize_date(item.FechaRevision) or datetime.now(),
                    CreatedBy="MigrationScript",
                    IsActive=True,
                    IsDeleted=False
                )
                comments.append(comm_dest)
                
        return revisions, comments

    def transformar_noticia(self, source_items: List[NoticiaSource]) -> List[NoticiaDest]:
        """Transforma dbo.Noticias -> Noticias.Noticia"""
        noticias_dest = []
        for item in source_items:
            noticia = NoticiaDest(
                Id=item.ID,
                Titulo=item.Descripcion[:250] if item.Descripcion else "Noticia Sin Título",
                Descripcion=item.Descripcion,
                TipoNoticiaId=1,
                EsDestacada=False,
                Publicado=True if item.Estado and str(item.Estado).lower() == 'activo' else True,
                VisiblePublico=True,
                CreatedAt=self._sanitize_date(item.Fecha) or datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True,
                IsDeleted=False
            )
            noticias_dest.append(noticia)
        return noticias_dest

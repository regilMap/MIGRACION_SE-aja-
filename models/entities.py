from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Any

# Mixin for dict conversion
class DictMixin:
    def to_dict(self) -> dict:
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, bytes):
                data[key] = None # Don't serialize raw bytes to json
        return data

    @classmethod
    def from_dict(cls, data: dict):
        valid_data = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**valid_data)

# ============================================================
# ENTIDADES DESTINO (Esquema Seguridad y Mantenimiento)
# ============================================================

@dataclass
class TipoVencimiento(DictMixin):
    """Seguridad.TiposVencimiento"""
    Id: int = None
    Codigo: str = None
    Nombre: str = None
    Descripcion: str = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class TiposSubIndicador(DictMixin):
    """Seguridad.TiposSubIndicador"""
    Id: int = None
    Codigo: str = None
    Nombre: str = None
    Descripcion: str = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class TiposEvaluacion(DictMixin):
    """Seguridad.TiposEvaluacion"""
    Id: int = None
    Codigo: str = None
    Nombre: str = None
    Descripcion: str = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class EstadosArchivo(DictMixin):
    """Seguridad.EstadosArchivo"""
    Id: int = None
    Codigo: str = None
    Nombre: str = None
    Descripcion: str = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class Indicador(DictMixin):
    """Seguridad.Indicadores"""
    Id: int = None
    Codigo: str = None
    Nombre: str = None
    Descripcion: str = None
    Orden: int = 1
    Peso: float = 0.0
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class SubIndicador(DictMixin):
    """Seguridad.SubIndicadores"""
    Id: int = None                  # Dest Id / Source IndicadorID
    IndicadorId: int = None         # Dest IndicadorId / Source ibogId
    TipoSubIndicadorId: int = None  # FK -> Seguridad.TiposSubIndicador
    TipoVencimientoId: int = None   # FK -> Seguridad.TiposVencimiento
    Codigo: str = None
    Nombre: str = None
    Descripcion: str = None
    Orden: int = 1
    Peso: float = 0.0
    UnidadResponsable: str = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False
    
    # Source specific fields for migration pipeline logic
    DepartamentoID: int = None
    ValorTotal: str = None
    Color: str = None
    Aplica: str = None
    ibogId: int = None
    Estado: str = None

# ============================================================
# ENTIDADES SOLO FUENTE (dbo.* en SISMAPV1DB_SG)
# ============================================================

@dataclass
class Ibog(DictMixin):
    """dbo.Ibog (Fuente)"""
    IbogID: int
    Codigo: str = None
    Descripcion: str = None
    Peso: float = None
    Valor: float = None
    DepartamentoID: int = None
    BurocraciaCero: bool = None
    Estado: str = None

@dataclass
class EvidenciaSource(DictMixin):
    """dbo.Evidencia (Fuente)"""
    EvidenciaID: int
    Codigo: str = None
    Descipcion: str = None
    NombreArchivo: str = None
    Prerequisito: str = None
    IndicadorID: int = None
    Criterio: str = None
    Valor: float = None
    AplicaVencimiento: bool = None
    TipoVencimiento: int = None
    FechaVencimiento: datetime = None
    CantDias: str = None
    Estado: str = None

@dataclass
class CargaEvidenciaSource(DictMixin):
    """
    Join de: CargaEvidencia, ArchivoCargaEvidencia, RepositorioDeEnvio
    """
    CargaEvidenciaID: int
    ArchivoCargaEvidenciaID: int = None
    IndicadorID: int = None
    EvidenciaID: int = None
    OrganismoID: int = None
    NombreArchivo: str = None
    Puntuacion: float = None
    FechaArchivo: datetime = None
    UsuarioID: str = None

@dataclass
class RevisionSource(DictMixin):
    """Fuente para Revisiones"""
    RevisionID: int
    EvidenciaID: int
    Comentario: str = None
    UsuarioID: str = None
    FechaRevision: datetime = None
    EstadoRevision: str = None

@dataclass
class NoticiaSource(DictMixin):
    """dbo.Noticias (Fuente)"""
    ID: int
    Descripcion: str = None
    Fecha: datetime = None
    Imagen: str = None
    Documento: str = None
    UsuarioID: str = None
    Estado: str = None

# ============================================================
# ENTIDADES DESTINO EVIDENCIA Y PUNTUACION (Esquema Seguridad)
# ============================================================

@dataclass
class EvidenciaDest(DictMixin):
    """Seguridad.Evidencias"""
    Id: int = None
    Codigo: str = None
    Nombre: str = None
    Descripcion: str = None
    Valor: float = 0.0
    AplicaVencimiento: bool = False
    CantidadDias: int = None
    FechaVencimiento: datetime = None
    PreRequisitoId: int = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class FechaVencimientoSubIndicadorEvidencia(DictMixin):
    """Seguridad.FechasVencimientoSubIndicadorEvidencia"""
    Id: int = None
    TipoVencimientoId: int = None
    FechaVencimiento: datetime = None
    PeriodicidadDias: int = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class SubIndicadorEvidencia(DictMixin):
    """Seguridad.SubIndicadorEvidencias"""
    Id: int = None
    SubIndicadorId: int = None
    EvidenciaId: int = None
    FechaVenciento: datetime = None
    TipoEvaluacionId: int = 1
    FechaVencimientoSubIndicadorEvidenciaId: int = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class ArchivoDest(DictMixin):
    """Seguridad.Archivos"""
    Id: int = None
    CoedomId: int = None
    SubIndicadorEvidenciaId: int = None
    NombreOriginal: str = None
    ArchivoBinario: bytes = None
    RowGuid: str = None
    EstadoArchivoId: int = None
    TipoAlmacenamiento: int = None
    RutaExterna: str = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class PuntuacionDest(DictMixin):
    """Seguridad.Puntuaciones"""
    Id: int = None
    ArchivoEvidenciaId: int = None
    PuntuadorUsuarioId: str = None # UniqueIdentifier (GUID)
    Calificacion: float = 0.0
    Observacion: str = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class RevisionEvidenciaDest(DictMixin):
    """Seguridad.RevisionesEvidencia"""
    Id: int = None
    ArchivoEvidenciaId: int = None
    FechaRevisionConcluida: datetime = None
    UsuarioId: str = None # UniqueIdentifier (GUID)
    RevisionCoedomId: int = None
    EstadoDadoId: int = None
    NivelRevisionEvidencia: int = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class ComentarioRevisionDest(DictMixin):
    """Seguridad.ComentariosRevisionEvidencia"""
    Id: int = None
    RevisionEvidenciaId: int = None
    UsuarioId: str = None # UniqueIdentifier (GUID)
    Observaciones: str = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class NoticiaDest(DictMixin):
    """Noticias.Noticia"""
    Id: int = None
    Titulo: str = None
    Descripcion: str = None
    TipoNoticiaId: int = 1
    EsDestacada: bool = False
    Publicado: bool = True
    VisiblePublico: bool = True
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

# ============================================================
# MAPEO DE ENTIDADES
# ============================================================

ENTITY_MAP = {
    'TipoVencimiento': TipoVencimiento,
    'TiposSubIndicador': TiposSubIndicador,
    'TiposEvaluacion': TiposEvaluacion,
    'EstadosArchivo': EstadosArchivo,
    'Indicador': Indicador,
    'SubIndicador': SubIndicador,
    'Ibog': Ibog,
    'EvidenciaSource': EvidenciaSource,
    'EvidenciaDest': EvidenciaDest,
    'FechaVencimientoSubIndicadorEvidencia': FechaVencimientoSubIndicadorEvidencia,
    'SubIndicadorEvidencia': SubIndicadorEvidencia,
    'ArchivoDest': ArchivoDest,
    'CargaEvidenciaSource': CargaEvidenciaSource,
    'PuntuacionDest': PuntuacionDest,
    'RevisionSource': RevisionSource,
    'RevisionEvidenciaDest': RevisionEvidenciaDest,
    'ComentarioRevisionDest': ComentarioRevisionDest,
    'NoticiaSource': NoticiaSource,
    'NoticiaDest': NoticiaDest,
}

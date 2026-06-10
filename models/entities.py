from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Any

# Mixin for dict conversion
class DictMixin:
    def to_dict(self) -> dict:
        data = asdict(self)
        # Convert datetime to ISO string
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict):
        # Convert ISO string to datetime if needed
        # This simple implementation assumes logic handles it or exact match
        # For robustness, we could check specific fields, but standard constructors might suffice
        # if logic passes correct types.
        # However, JSON load returns strings.
        valid_data = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**valid_data)

# ============================================================
# ENTIDADES COMPARTIDAS / DESTINO (Mantenimiento Schema)
# ============================================================

@dataclass
class TipoVencimiento(DictMixin):
    TipoVencimientoId: int = None # Source
    Id: int = None                # Destination
    Nombre: str = None
    Descripcion: str = None
    Estado: str = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class TiposSubIndicador(DictMixin):
    Id: int = None
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
    Id: int = None
    Codigo: str = None
    Nombre: str = None
    Descripcion: str = None
    TipoIndicadorId: int = None
    Peso: float = 0.0
    IsActive: bool = True
    IsDeleted: bool = False
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None

@dataclass
class SubIndicador(DictMixin):
    Id: int = None              # Dest Id / Source IndicadorID
    IndicadorId: int = None     # Dest IndicadorId / Source ibogId
    TipoSubIndicadorId: int = None  # FK -> Mantenimiento.TiposSubIndicador
    Codigo: str = None
    Nombre: str = None
    Descripcion: str = None
    Peso: float = 0.0
    Estado: str = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False
    
    # Source specific fields (optional)
    DepartamentoID: int = None
    ValorTotal: str = None
    Color: str = None
    Aplica: str = None
    ibogId: int = None

# ============================================================
# ENTIDADES SOLO FUENTE
# ============================================================

@dataclass
class Ibog(DictMixin):
    IbogID: int
    Codigo: str = None
    Descripcion: str = None
    Peso: float = None
    Valor: float = None
    DepartamentoID: int = None
    BurocraciaCero: bool = None
    Estado: str = None

# ============================================================
# ENTIDADES MIGRACIÓN EVIDENCIAS
# ============================================================

@dataclass
class EvidenciaSource(DictMixin):
    """dbo.Evidencia (Fuente)"""
    EvidenciaID: int
    Codigo: str = None
    Descipcion: str = None # Note typo in source schema? 'Descipcion' based on schema dump? Checking schema dump... it says 'Descipcion'.
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
class EvidenciaDest(DictMixin):
    """Evidencia.Evidencias (Destino)"""
    Id: int = None
    Nombre: str = None
    Descripcion: str = None
    Valor: float = 0.0
    PreRequisitoId: int = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False
    AplicaVencimiento: bool = False
    CantidadDias: int = None
    FechaVencimiento: datetime = None
    Codigo: str = None

@dataclass
class FechaVencimientoSubIndicadorEvidencia(DictMixin):
    """Evidencia.FechaVencimientoSubIndicadorEvidencias (Destino)"""
    Id: int = None
    TipoVencimientoId: int = None
    FechaVencimiento: datetime = None
    PeriodicidadDias: int = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class SubIndicadorEvidencia(DictMixin):
    """Evidencia.SubIndicadorEvidencias (Destino)"""
    Id: int = None
    SubIndicadorId: int = None
    EvidenciaId: int = None
    FechaVencimientoSubIndicadorEvidenciaId: int = None # Link to the new date table
    TipoEvaluacionId: int = 1 # Default or mapped
    FechaVenciento: datetime = None # Redundant or required? Checking schema... 'FechaVenciento' exists.
    CreatedAt: datetime = None
    CreatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class ArchivoDest(DictMixin):
    """Evidencia.Archivos (Destino)"""
    Id: int = None
    CoedomId: int = None
    SubIndicadorEvidenciaId: int = None
    NombreOriginal: str = None
    ArchivoBinario: bytes = None # or str/base64 depending on handler
    EstadoArchivoId: int = None
    EvidenciaId: int = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    UpdatedAt: datetime = None
    UpdatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False
    RowGuid: str = None # UniqueIdentifier
    TipoAlmacenamiento: int = None
    RutaExterna: str = None

# ============================================================
# ENTIDADES PUNTUACION / REVISION (FUENTE & DESTINO)
# ============================================================

@dataclass
class CargaEvidenciaSource(DictMixin):
    """
    Join de:
    - CargaEvidencia (ce)
    - ArchivoCargaEvidencia (ace)
    - RepositorioDeEnvio (re)
    """
    CargaEvidenciaID: int
    ArchivoCargaEvidenciaID: int
    #RepositorioDeEnvioID: int # Removed
    IndicadorID: int # Para filtrar
    EvidenciaID: int = None
    OrganismoID: int = None # Para CoedomId
    NombreArchivo: str = None
    Puntuacion: float = None
    FechaArchivo: datetime = None
    # Campos adicionales para Revision si estan aqui?
    # Asumimos que la revision esta separada o vinculada aqui.

@dataclass
class PuntuacionDest(DictMixin):
    """Evidencia.Puntuacion (Destino)"""
    Id: int = None
    ArchivoEvidenciaId: int = None
    PuntuadorUsuarioId: str = None # Guid
    Calificacion: float = 0.0
    CreatedAt: datetime = None
    CreatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class RevisionSource(DictMixin):
    """
    Fuente para Revisiones. 
    Nombre tabla pendiente de confirmación.
    """
    RevisionID: int
    EvidenciaID: int # Vinculo
    Comentario: str
    UsuarioID: int # O nombre usuario
    FechaRevision: datetime
    EstadoRevision: str

@dataclass
class RevisionEvidenciaDest(DictMixin):
    """Evidencia.RevisionEvidencias (Destino)"""
    Id: int = None
    ArchivoEvidenciaId: int = None
    FechaRevisionConcluida: datetime = None
    UsuarioId: str = None # Guid
    EstadoDadoId: int = None
    NivelRevisionEvidencia: int = None
    RevisionCoedomId: int = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

@dataclass
class ComentarioRevisionDest(DictMixin):
    """Evidencia.ComentarioRevisionEvidencias (Destino)"""
    Id: int = None
    RevisionEvidenciaId: int = None
    Observaciones: str = None
    UsuarioId: str = None
    CreatedAt: datetime = None
    CreatedBy: str = None
    IsActive: bool = True
    IsDeleted: bool = False

# ============================================================
# MAPEO DE ENTIDADES
# ============================================================

ENTITY_MAP = {
    'TipoVencimiento': TipoVencimiento,
    'TiposSubIndicador': TiposSubIndicador,
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
}

from datetime import datetime
from typing import List, Optional
from models.entities import (
    TipoVencimiento, TiposIndicador, Indicador, SubIndicador,
    EvidenciaSource, EvidenciaDest, SubIndicadorEvidencia, FechaVencimientoSubIndicadorEvidencia,
    Ibog  # Assuming we create a model for Source Ibog
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
        pass

    def transformar_tipo_vencimiento(self, source_items: List[TipoVencimiento]) -> List[TipoVencimiento]:
        """
        Transforma TipoVencimiento.
        Fuente: TipoVencimientoId, Nombre, Descripcion, Estado
        Destino: Id, Nombre, Descripcion, CreatedAt...
        """
        transformed = []
        for item in source_items:
            # Map fields
            new_item = TipoVencimiento(
                Id=item.TipoVencimientoId,
                Nombre=item.Nombre,
                Descripcion=item.Descripcion or item.Nombre, # Fallback
                CreatedAt=datetime.now(),
                CreatedBy="MigrationScript",
                IsActive=True if item.Estado == 'Activo' else False,
                IsDeleted=False
            )
            transformed.append(new_item)
        return transformed

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

    def transformar_evidencia(self, items: List[EvidenciaSource]) -> tuple[List[EvidenciaDest], List[FechaVencimientoSubIndicadorEvidencia], List[SubIndicadorEvidencia]]:
        """
        Transforma dbo.Evidencia en 3 tablas destino.
        Retorna: (evidencias, fechas_vencimiento, sub_indicador_evidencias)
        """
        evidencias_dest = []
        fechas_dest = []
        sub_ind_evidencias_dest = []
        
        # ID tracking (assuming empty destination tables)
        # Using Source EvidenciaID for DEST Evidencia.Id
        
        fecha_id_counter = 1
        sub_ind_ev_id_counter = 1
        
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
            
            # 2. Manejar Fecha Vencimiento (Si aplica)
            fecha_venc_id = None
            if item.AplicaVencimiento:
                fecha_venc_id = fecha_id_counter
                fecha = FechaVencimientoSubIndicadorEvidencia(
                    Id=fecha_venc_id,
                    TipoVencimientoId=item.TipoVencimiento,
                    FechaVencimiento=safe_fecha if safe_fecha else datetime(1900, 1, 1), # Fallback if required? Let's assume NULL is ok or use 1900
                    PeriodicidadDias=int(item.CantDias) if item.CantDias and item.CantDias.isdigit() else 0,
                    CreatedAt=datetime.now(),
                    CreatedBy="MigrationScript",
                    IsActive=item.Estado == 'Activo',
                    IsDeleted=False
                )
                fechas_dest.append(fecha)
                fecha_id_counter += 1
            
            # 3. Crear Enlace SubIndicadorEvidencia
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
            sub_ind_ev_id_counter += 1
            
        return evidencias_dest, fechas_dest, sub_ind_evidencias_dest

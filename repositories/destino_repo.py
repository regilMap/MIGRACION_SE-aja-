from typing import List, Set
from models.entities import (
    TipoVencimiento, TiposSubIndicador, TiposEvaluacion, EstadosArchivo,
    Indicador, SubIndicador, EvidenciaDest, SubIndicadorEvidencia,
    FechaVencimientoSubIndicadorEvidencia, ArchivoDest, PuntuacionDest,
    RevisionEvidenciaDest, ComentarioRevisionDest, NoticiaDest
)

class DestinoRepository:
    """
    Repositorio para ESCRIBIR datos en la BD DESTINO (SISMAP_SEGURIDAD)
    Esquemas principales: Seguridad, Noticias, Mantenimiento, Usuario
    """
    
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
    
    # ============================================================
    # CATALOGOS EN ESQUEMA SEGURIDAD
    # ============================================================
    
    def insertar_tipos_vencimiento(self, datos: List[TipoVencimiento]) -> int:
        """Inserta o Actualiza en Seguridad.TiposVencimiento (UPSERT)"""
        query = """
            MERGE Seguridad.TiposVencimiento AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS Source (Id, Codigo, Nombre, Descripcion, CreatedAt, CreatedBy, IsActive, IsDeleted)
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET 
                    Codigo = Source.Codigo,
                    Nombre = Source.Nombre,
                    Descripcion = Source.Descripcion,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, Codigo, Nombre, Descripcion, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.Codigo, Source.Nombre, Source.Descripcion, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        count = 0
        for item in datos:
            self.cursor.execute(query, 
                item.Id,
                item.Codigo or f"TV-{item.Id}",
                item.Nombre,
                item.Descripcion,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count
    
    def insertar_tipos_sub_indicador(self, datos: List[TiposSubIndicador]) -> int:
        """Inserta o Actualiza en Seguridad.TiposSubIndicador (UPSERT)"""
        query = """
            MERGE Seguridad.TiposSubIndicador AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS Source (Id, Codigo, Nombre, Descripcion, CreatedAt, CreatedBy, IsActive, IsDeleted)
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET 
                    Codigo = Source.Codigo,
                    Nombre = Source.Nombre,
                    Descripcion = Source.Descripcion,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, Codigo, Nombre, Descripcion, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.Codigo, Source.Nombre, Source.Descripcion, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.Codigo or f"TSI-{item.Id}",
                item.Nombre,
                item.Descripcion,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    def insertar_tipos_evaluacion(self, datos: List[TiposEvaluacion]) -> int:
        """Inserta o Actualiza en Seguridad.TiposEvaluacion (UPSERT)"""
        query = """
            MERGE Seguridad.TiposEvaluacion AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS Source (Id, Codigo, Nombre, Descripcion, CreatedAt, CreatedBy, IsActive, IsDeleted)
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET 
                    Codigo = Source.Codigo,
                    Nombre = Source.Nombre,
                    Descripcion = Source.Descripcion,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, Codigo, Nombre, Descripcion, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.Codigo, Source.Nombre, Source.Descripcion, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.Codigo or f"TE-{item.Id}",
                item.Nombre,
                item.Descripcion,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    def insertar_estados_archivo(self, datos: List[EstadosArchivo]) -> int:
        """Inserta o Actualiza en Seguridad.EstadosArchivo (UPSERT)"""
        query = """
            MERGE Seguridad.EstadosArchivo AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS Source (Id, Codigo, Nombre, Descripcion, CreatedAt, CreatedBy, IsActive, IsDeleted)
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET 
                    Codigo = Source.Codigo,
                    Nombre = Source.Nombre,
                    Descripcion = Source.Descripcion,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, Codigo, Nombre, Descripcion, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.Codigo, Source.Nombre, Source.Descripcion, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.Codigo or f"EA-{item.Id}",
                item.Nombre,
                item.Descripcion,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    # ============================================================
    # INDICADORES (Seguridad.Indicadores)
    # ============================================================
    
    def insertar_indicadores(self, datos: List[Indicador]) -> int:
        """Inserta o Actualiza en Seguridad.Indicadores (UPSERT)"""
        query = """
            MERGE Seguridad.Indicadores AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (
                Id, Codigo, Nombre, Descripcion, Orden, Peso, CreatedAt, CreatedBy, IsActive, IsDeleted
            )
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    Codigo = Source.Codigo,
                    Nombre = Source.Nombre,
                    Descripcion = Source.Descripcion,
                    Orden = Source.Orden,
                    Peso = Source.Peso,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, Codigo, Nombre, Descripcion, Orden, Peso, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.Codigo, Source.Nombre, Source.Descripcion, Source.Orden, Source.Peso, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.Codigo,
                item.Nombre,
                item.Descripcion,
                item.Orden or item.Id,
                item.Peso,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    # ============================================================
    # SUB INDICADORES (Seguridad.SubIndicadores)
    # ============================================================
    
    def insertar_sub_indicadores(self, datos: List[SubIndicador]) -> int:
        """Inserta o Actualiza en Seguridad.SubIndicadores (UPSERT)"""
        query = """
            MERGE Seguridad.SubIndicadores AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (
                Id, IndicadorId, TipoSubIndicadorId, TipoVencimientoId, Codigo, Nombre, Descripcion, 
                Orden, Peso, UnidadResponsable, CreatedAt, CreatedBy, IsActive, IsDeleted
            )
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    IndicadorId = Source.IndicadorId,
                    TipoSubIndicadorId = Source.TipoSubIndicadorId,
                    TipoVencimientoId = Source.TipoVencimientoId,
                    Codigo = Source.Codigo,
                    Nombre = Source.Nombre,
                    Descripcion = Source.Descripcion,
                    Orden = Source.Orden,
                    Peso = Source.Peso,
                    UnidadResponsable = Source.UnidadResponsable,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (
                    Id, IndicadorId, TipoSubIndicadorId, TipoVencimientoId, Codigo, Nombre, Descripcion, 
                    Orden, Peso, UnidadResponsable, CreatedAt, CreatedBy, IsActive, IsDeleted
                )
                VALUES (
                    Source.Id, Source.IndicadorId, Source.TipoSubIndicadorId, Source.TipoVencimientoId, Source.Codigo, Source.Nombre, Source.Descripcion, 
                    Source.Orden, Source.Peso, Source.UnidadResponsable, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted
                );
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.IndicadorId,
                item.TipoSubIndicadorId,
                item.TipoVencimientoId,
                item.Codigo,
                item.Nombre,
                item.Descripcion,
                item.Orden or item.Id,
                item.Peso,
                item.UnidadResponsable,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    # ============================================================
    # EVIDENCIAS (Seguridad.Evidencias)
    # ============================================================

    def insertar_evidencias(self, datos: List[EvidenciaDest]) -> int:
        """Inserta o Actualiza en Seguridad.Evidencias (UPSERT)"""
        query = """
            MERGE Seguridad.Evidencias AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (
                Id, Codigo, Nombre, Descripcion, Valor, AplicaVencimiento, CantidadDias, 
                FechaVencimiento, PreRequisitoId, CreatedAt, CreatedBy, IsActive, IsDeleted
            )
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    Codigo = Source.Codigo,
                    Nombre = Source.Nombre,
                    Descripcion = Source.Descripcion,
                    Valor = Source.Valor,
                    AplicaVencimiento = Source.AplicaVencimiento,
                    CantidadDias = Source.CantidadDias,
                    FechaVencimiento = Source.FechaVencimiento,
                    PreRequisitoId = Source.PreRequisitoId,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (
                    Id, Codigo, Nombre, Descripcion, Valor, AplicaVencimiento, CantidadDias, 
                    FechaVencimiento, PreRequisitoId, CreatedAt, CreatedBy, IsActive, IsDeleted
                )
                VALUES (
                    Source.Id, Source.Codigo, Source.Nombre, Source.Descripcion, Source.Valor, Source.AplicaVencimiento, Source.CantidadDias, 
                    Source.FechaVencimiento, Source.PreRequisitoId, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted
                );
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.Codigo,
                item.Nombre,
                item.Descripcion,
                item.Valor,
                item.AplicaVencimiento,
                item.CantidadDias,
                item.FechaVencimiento,
                item.PreRequisitoId,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    def insertar_fecha_vencimiento_evidencias(self, datos: List[FechaVencimientoSubIndicadorEvidencia]) -> int:
        """Inserta o Actualiza en Seguridad.FechasVencimientoSubIndicadorEvidencia"""
        query = """
            MERGE Seguridad.FechasVencimientoSubIndicadorEvidencia AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS Source (
                Id, TipoVencimientoId, FechaVencimiento, PeriodicidadDias, CreatedAt, CreatedBy, IsActive, IsDeleted
            )
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    TipoVencimientoId = Source.TipoVencimientoId,
                    FechaVencimiento = Source.FechaVencimiento,
                    PeriodicidadDias = Source.PeriodicidadDias,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, TipoVencimientoId, FechaVencimiento, PeriodicidadDias, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.TipoVencimientoId, Source.FechaVencimiento, Source.PeriodicidadDias, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.TipoVencimientoId,
                item.FechaVencimiento,
                item.PeriodicidadDias,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    def insertar_sub_indicador_evidencias(self, datos: List[SubIndicadorEvidencia]) -> int:
        """Inserta o Actualiza en Seguridad.SubIndicadorEvidencias"""
        query = """
            MERGE Seguridad.SubIndicadorEvidencias AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (
                Id, SubIndicadorId, EvidenciaId, FechaVenciento, TipoEvaluacionId, 
                FechaVencimientoSubIndicadorEvidenciaId, CreatedAt, CreatedBy, IsActive, IsDeleted
            )
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    SubIndicadorId = Source.SubIndicadorId,
                    EvidenciaId = Source.EvidenciaId,
                    FechaVenciento = Source.FechaVenciento,
                    TipoEvaluacionId = Source.TipoEvaluacionId,
                    FechaVencimientoSubIndicadorEvidenciaId = Source.FechaVencimientoSubIndicadorEvidenciaId,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (
                    Id, SubIndicadorId, EvidenciaId, FechaVenciento, TipoEvaluacionId, 
                    FechaVencimientoSubIndicadorEvidenciaId, CreatedAt, CreatedBy, IsActive, IsDeleted
                )
                VALUES (
                    Source.Id, Source.SubIndicadorId, Source.EvidenciaId, Source.FechaVenciento, Source.TipoEvaluacionId, 
                    Source.FechaVencimientoSubIndicadorEvidenciaId, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted
                );
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.SubIndicadorId,
                item.EvidenciaId,
                item.FechaVenciento,
                item.TipoEvaluacionId,
                item.FechaVencimientoSubIndicadorEvidenciaId,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    # ============================================================
    # ARCHIVOS (Seguridad.Archivos)
    # ============================================================

    def insertar_archivos(self, datos: List[ArchivoDest]) -> int:
        """Inserta o Actualiza en Seguridad.Archivos (UPSERT)"""
        query = """
            MERGE Seguridad.Archivos AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (
                Id, CoedomId, SubIndicadorEvidenciaId, NombreOriginal, ArchivoBinario, RowGuid, 
                EstadoArchivoId, TipoAlmacenamiento, RutaExterna, CreatedAt, CreatedBy, 
                UpdatedAt, UpdatedBy, IsActive, IsDeleted
            )
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    CoedomId = Source.CoedomId,
                    SubIndicadorEvidenciaId = Source.SubIndicadorEvidenciaId,
                    NombreOriginal = Source.NombreOriginal,
                    ArchivoBinario = Source.ArchivoBinario,
                    RowGuid = Source.RowGuid,
                    EstadoArchivoId = Source.EstadoArchivoId,
                    TipoAlmacenamiento = Source.TipoAlmacenamiento,
                    RutaExterna = Source.RutaExterna,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (
                    Id, CoedomId, SubIndicadorEvidenciaId, NombreOriginal, ArchivoBinario, RowGuid, 
                    EstadoArchivoId, TipoAlmacenamiento, RutaExterna, CreatedAt, CreatedBy, 
                    UpdatedAt, UpdatedBy, IsActive, IsDeleted
                )
                VALUES (
                    Source.Id, Source.CoedomId, Source.SubIndicadorEvidenciaId, Source.NombreOriginal, Source.ArchivoBinario, Source.RowGuid, 
                    Source.EstadoArchivoId, Source.TipoAlmacenamiento, Source.RutaExterna, Source.CreatedAt, Source.CreatedBy, 
                    Source.UpdatedAt, Source.UpdatedBy, Source.IsActive, Source.IsDeleted
                );
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.CoedomId or 0,
                item.SubIndicadorEvidenciaId,
                item.NombreOriginal,
                item.ArchivoBinario,
                item.RowGuid,
                item.EstadoArchivoId or 1,
                item.TipoAlmacenamiento or 1,
                item.RutaExterna,
                item.CreatedAt,
                item.CreatedBy,
                item.UpdatedAt,
                item.UpdatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    def obtener_ids_archivos_existentes(self) -> Set[int]:
        """Retorna un conjunto de todos los IDs de archivos actualmente existentes en la BD"""
        self.cursor.execute("SELECT Id FROM Seguridad.Archivos")
        return {row[0] for row in self.cursor.fetchall()}

    # ============================================================
    # PUNTUACIONES (Seguridad.Puntuaciones)
    # ============================================================

    def insertar_puntuacion(self, datos: List[PuntuacionDest]) -> int:
        """Inserta o Actualiza en Seguridad.Puntuaciones"""
        query = """
            MERGE Seguridad.Puntuaciones AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (
                Id, ArchivoEvidenciaId, PuntuadorUsuarioId, Calificacion, Observacion, 
                CreatedAt, CreatedBy, IsActive, IsDeleted
            )
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    ArchivoEvidenciaId = Source.ArchivoEvidenciaId,
                    PuntuadorUsuarioId = Source.PuntuadorUsuarioId,
                    Calificacion = Source.Calificacion,
                    Observacion = Source.Observacion,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (
                    Id, ArchivoEvidenciaId, PuntuadorUsuarioId, Calificacion, Observacion, 
                    CreatedAt, CreatedBy, IsActive, IsDeleted
                )
                VALUES (
                    Source.Id, Source.ArchivoEvidenciaId, Source.PuntuadorUsuarioId, Source.Calificacion, Source.Observacion, 
                    Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted
                );
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.ArchivoEvidenciaId,
                item.PuntuadorUsuarioId,
                item.Calificacion,
                item.Observacion,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    # ============================================================
    # REVISIONES (Seguridad.RevisionesEvidencia)
    # ============================================================

    def insertar_revision_evidencias(self, datos: List[RevisionEvidenciaDest]) -> int:
        """Inserta o Actualiza en Seguridad.RevisionesEvidencia"""
        query = """
            MERGE Seguridad.RevisionesEvidencia AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (
                Id, ArchivoEvidenciaId, FechaRevisionConcluida, UsuarioId, RevisionCoedomId, 
                EstadoDadoId, NivelRevisionEvidencia, CreatedAt, CreatedBy, IsActive, IsDeleted
            )
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    ArchivoEvidenciaId = Source.ArchivoEvidenciaId,
                    FechaRevisionConcluida = Source.FechaRevisionConcluida,
                    UsuarioId = Source.UsuarioId,
                    RevisionCoedomId = Source.RevisionCoedomId,
                    EstadoDadoId = Source.EstadoDadoId,
                    NivelRevisionEvidencia = Source.NivelRevisionEvidencia,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (
                    Id, ArchivoEvidenciaId, FechaRevisionConcluida, UsuarioId, RevisionCoedomId, 
                    EstadoDadoId, NivelRevisionEvidencia, CreatedAt, CreatedBy, IsActive, IsDeleted
                )
                VALUES (
                    Source.Id, Source.ArchivoEvidenciaId, Source.FechaRevisionConcluida, Source.UsuarioId, Source.RevisionCoedomId, 
                    Source.EstadoDadoId, Source.NivelRevisionEvidencia, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted
                );
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.ArchivoEvidenciaId,
                item.FechaRevisionConcluida,
                item.UsuarioId,
                item.RevisionCoedomId or 1,
                item.EstadoDadoId or 1,
                item.NivelRevisionEvidencia or 1,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    def insertar_comentario_revision(self, datos: List[ComentarioRevisionDest]) -> int:
        """Inserta o Actualiza en Seguridad.ComentariosRevisionEvidencia"""
        query = """
            MERGE Seguridad.ComentariosRevisionEvidencia AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS Source (
                Id, RevisionEvidenciaId, UsuarioId, Observaciones, CreatedAt, CreatedBy, IsActive, IsDeleted
            )
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    RevisionEvidenciaId = Source.RevisionEvidenciaId,
                    UsuarioId = Source.UsuarioId,
                    Observaciones = Source.Observaciones,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, RevisionEvidenciaId, UsuarioId, Observaciones, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.RevisionEvidenciaId, Source.UsuarioId, Source.Observaciones, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.RevisionEvidenciaId,
                item.UsuarioId,
                item.Observaciones,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    # ============================================================
    # NOTICIAS (Noticias.Noticia)
    # ============================================================

    def insertar_noticias(self, datos: List[NoticiaDest]) -> int:
        """Inserta o Actualiza en Noticias.Noticia"""
        query = """
            MERGE Noticias.Noticia AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (
                Id, Titulo, Descripcion, TipoNoticiaId, EsDestacada, Publicado, VisiblePublico, 
                CreatedAt, CreatedBy, IsActive, IsDeleted
            )
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    Titulo = Source.Titulo,
                    Descripcion = Source.Descripcion,
                    TipoNoticiaId = Source.TipoNoticiaId,
                    EsDestacada = Source.EsDestacada,
                    Publicado = Source.Publicado,
                    VisiblePublico = Source.VisiblePublico,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (
                    Id, Titulo, Descripcion, TipoNoticiaId, EsDestacada, Publicado, VisiblePublico, 
                    CreatedAt, CreatedBy, IsActive, IsDeleted
                )
                VALUES (
                    Source.Id, Source.Titulo, Source.Descripcion, Source.TipoNoticiaId, Source.EsDestacada, Source.Publicado, Source.VisiblePublico, 
                    Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted
                );
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.Titulo,
                item.Descripcion,
                item.TipoNoticiaId,
                item.EsDestacada,
                item.Publicado,
                item.VisiblePublico,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    # ============================================================
    # LIMPIEZA / RESET DE TABLAS EN BD DESTINO
    # ============================================================

    def limpiar_bitacora_historicos(self) -> int:
        """Limpia tablas históricas de Bitacora para evitar conflictos de FK al reiniciar datos"""
        count = 0
        try:
            self.cursor.execute("DELETE FROM Bitacora.RankingEvidenciasHistorico")
            count += self.cursor.rowcount
            self.cursor.execute("DELETE FROM Bitacora.RankingSubIndicadoresHistorico")
            count += self.cursor.rowcount
            self.cursor.execute("DELETE FROM Bitacora.RankingIndicadoresHistorico")
            count += self.cursor.rowcount
            self.cursor.execute("DELETE FROM Bitacora.RankingOrganismosHistorico")
            count += self.cursor.rowcount
            self.resetear_identidad('Bitacora', 'RankingEvidenciasHistorico')
            self.resetear_identidad('Bitacora', 'RankingSubIndicadoresHistorico')
            self.resetear_identidad('Bitacora', 'RankingIndicadoresHistorico')
            self.resetear_identidad('Bitacora', 'RankingOrganismosHistorico')
        except Exception as e:
            print(f"Aviso al limpiar Bitacora: {e}")
        return count

    def limpiar_auditoria_tickets(self) -> int:
        """Limpia Auditoria.Ticket para evitar conflictos de FK"""
        count = 0
        try:
            self.cursor.execute("DELETE FROM Auditoria.Ticket")
            count = self.cursor.rowcount
            self.resetear_identidad('Auditoria', 'Ticket')
        except Exception as e:
            print(f"Aviso al limpiar Auditoria: {e}")
        return count

    def limpiar_respuestas_revision(self) -> int:
        self.cursor.execute("DELETE FROM Seguridad.RespuestasRevision")
        count = self.cursor.rowcount
        self.resetear_identidad('Seguridad', 'RespuestasRevision')
        return count

    def limpiar_preguntas_revision(self) -> int:
        self.cursor.execute("DELETE FROM Seguridad.PreguntasRevision")
        count = self.cursor.rowcount
        self.resetear_identidad('Seguridad', 'PreguntasRevision')
        return count

    def limpiar_comentario_revision(self) -> int:
        self.cursor.execute("DELETE FROM Seguridad.ComentariosRevisionEvidencia")
        count = self.cursor.rowcount
        self.resetear_identidad('Seguridad', 'ComentariosRevisionEvidencia')
        return count

    def limpiar_revision_evidencias(self) -> int:
        self.cursor.execute("DELETE FROM Seguridad.RevisionesEvidencia")
        count = self.cursor.rowcount
        self.resetear_identidad('Seguridad', 'RevisionesEvidencia')
        return count

    def limpiar_puntuacion(self) -> int:
        self.cursor.execute("DELETE FROM Seguridad.Puntuaciones")
        count = self.cursor.rowcount
        self.resetear_identidad('Seguridad', 'Puntuaciones')
        return count

    def limpiar_archivos(self) -> int:
        self.cursor.execute("DELETE FROM Seguridad.Archivos")
        count = self.cursor.rowcount
        self.resetear_identidad('Seguridad', 'Archivos')
        return count

    def limpiar_sub_indicador_evidencias(self) -> int:
        self.cursor.execute("DELETE FROM Seguridad.SubIndicadorEvidencias")
        count = self.cursor.rowcount
        self.resetear_identidad('Seguridad', 'SubIndicadorEvidencias')
        return count

    def limpiar_fecha_vencimiento_evidencias(self) -> int:
        self.cursor.execute("DELETE FROM Seguridad.FechasVencimientoSubIndicadorEvidencia")
        count = self.cursor.rowcount
        self.resetear_identidad('Seguridad', 'FechasVencimientoSubIndicadorEvidencia')
        return count

    def limpiar_evidencias(self) -> int:
        self.deshabilitar_constraint('Seguridad', 'Evidencias', 'FK_Evidencias_Evidencias_PreRequisitoId')
        self.cursor.execute("DELETE FROM Seguridad.Evidencias")
        count = self.cursor.rowcount
        self.resetear_identidad('Seguridad', 'Evidencias')
        self.habilitar_constraint('Seguridad', 'Evidencias', 'FK_Evidencias_Evidencias_PreRequisitoId')
        return count

    def limpiar_sub_indicadores(self) -> int:
        self.cursor.execute("DELETE FROM Seguridad.SubIndicadores")
        count = self.cursor.rowcount
        self.resetear_identidad('Seguridad', 'SubIndicadores')
        return count

    def limpiar_indicadores(self) -> int:
        self.cursor.execute("DELETE FROM Seguridad.Indicadores")
        count = self.cursor.rowcount
        self.resetear_identidad('Seguridad', 'Indicadores')
        return count

    def asegurar_catalogos_defecto(self):
        """Asegura catálogos por defecto en Seguridad (TiposSubIndicador, TiposEvaluacion, EstadosArchivo)"""
        # TiposSubIndicador por defecto
        self.cursor.execute("SELECT COUNT(*) FROM Seguridad.TiposSubIndicador WHERE Id = 1")
        if self.cursor.fetchone()[0] == 0:
            self.habilitar_identity_insert('Seguridad', 'TiposSubIndicador')
            self.cursor.execute("""
                INSERT INTO Seguridad.TiposSubIndicador (Id, Codigo, Nombre, Descripcion, CreatedAt, IsActive, IsDeleted)
                VALUES (1, 'TSI-01', 'General', 'SubIndicador Estándar', GETDATE(), 1, 0)
            """)
            self.deshabilitar_identity_insert('Seguridad', 'TiposSubIndicador')

        # TiposEvaluacion por defecto (1: Manual, 2: Automática)
        self.cursor.execute("SELECT COUNT(*) FROM Seguridad.TiposEvaluacion WHERE Id = 1")
        if self.cursor.fetchone()[0] == 0:
            self.habilitar_identity_insert('Seguridad', 'TiposEvaluacion')
            self.cursor.execute("""
                INSERT INTO Seguridad.TiposEvaluacion (Id, Codigo, Nombre, Descripcion, CreatedAt, IsActive, IsDeleted)
                VALUES (1, 'MANUAL', 'Manual', 'Evaluación manual', GETDATE(), 1, 0)
            """)
            self.deshabilitar_identity_insert('Seguridad', 'TiposEvaluacion')

        self.cursor.execute("SELECT COUNT(*) FROM Seguridad.TiposEvaluacion WHERE Id = 2")
        if self.cursor.fetchone()[0] == 0:
            self.habilitar_identity_insert('Seguridad', 'TiposEvaluacion')
            self.cursor.execute("""
                INSERT INTO Seguridad.TiposEvaluacion (Id, Codigo, Nombre, Descripcion, CreatedAt, IsActive, IsDeleted)
                VALUES (2, 'AUTO', 'Automática', 'Evaluación automática', GETDATE(), 1, 0)
            """)
            self.deshabilitar_identity_insert('Seguridad', 'TiposEvaluacion')

        # EstadosArchivo por defecto (1: Cargado, 2: En Revision, 3: Aprobado)
        estados = [
            (1, 'CARGADO', 'Cargado', 'Archivo subido por la entidad'),
            (2, 'EN_REVISION', 'En Revisión', 'En proceso de evaluación'),
            (3, 'APROBADO', 'Aprobado', 'Evidencia aprobada y puntuada')
        ]
        for eid, cod, nom, desc in estados:
            self.cursor.execute("SELECT COUNT(*) FROM Seguridad.EstadosArchivo WHERE Id = ?", eid)
            if self.cursor.fetchone()[0] == 0:
                self.habilitar_identity_insert('Seguridad', 'EstadosArchivo')
                self.cursor.execute("""
                    INSERT INTO Seguridad.EstadosArchivo (Id, Codigo, Nombre, Descripcion, CreatedAt, IsActive, IsDeleted)
                    VALUES (?, ?, ?, ?, GETDATE(), 1, 0)
                """, eid, cod, nom, desc)
                self.deshabilitar_identity_insert('Seguridad', 'EstadosArchivo')

    # ============================================================
    # UTILIDADES
    # ============================================================
    
    def habilitar_identity_insert(self, schema: str, tabla: str):
        full_table = f"{schema}.{tabla}"
        self.cursor.execute(f"SET IDENTITY_INSERT {full_table} ON")
    
    def deshabilitar_identity_insert(self, schema: str, tabla: str):
        full_table = f"{schema}.{tabla}"
        self.cursor.execute(f"SET IDENTITY_INSERT {full_table} OFF")

    def deshabilitar_constraint(self, schema: str, tabla: str, constraint: str):
        full_table = f"{schema}.{tabla}"
        try:
            self.cursor.execute(f"ALTER TABLE {full_table} NOCHECK CONSTRAINT {constraint}")
        except Exception as e:
            print(f"Advertencia: No se pudo deshabilitar constraint {constraint} en {full_table}: {e}")

    def habilitar_constraint(self, schema: str, tabla: str, constraint: str):
        full_table = f"{schema}.{tabla}"
        try:
            self.cursor.execute(f"ALTER TABLE {full_table} WITH CHECK CHECK CONSTRAINT {constraint}")
        except Exception as e:
            print(f"Advertencia: No se pudo habilitar constraint {constraint} en {full_table}: {e}")

    def obtener_usuarios_existentes(self) -> Set[str]:
        """Obtiene el conjunto de GUIDs de usuarios existentes en Usuario.Usuarios"""
        try:
            self.cursor.execute("SELECT CAST(Id AS NVARCHAR(36)) FROM Usuario.Usuarios WHERE IsDeleted = 0")
            return {str(row[0]).upper() for row in self.cursor.fetchall() if row[0]}
        except Exception as e:
            print(f"Advertencia: No se pudieron leer usuarios existentes: {e}")
            return set()

    def obtener_primer_usuario_id(self) -> Optional[str]:
        """Obtiene el primer GUID de usuario disponible en Usuario.Usuarios"""
        try:
            self.cursor.execute("SELECT TOP 1 CAST(Id AS NVARCHAR(36)) FROM Usuario.Usuarios WHERE IsActive = 1 AND IsDeleted = 0")
            row = self.cursor.fetchone()
            if row and row[0]:
                return str(row[0])
            self.cursor.execute("SELECT TOP 1 CAST(Id AS NVARCHAR(36)) FROM Usuario.Usuarios")
            row = self.cursor.fetchone()
            if row and row[0]:
                return str(row[0])
        except Exception as e:
            print(f"Advertencia: Error al obtener usuario por defecto: {e}")
        return None

    def resetear_identidad(self, schema: str, tabla: str, seed: int = 0):
        full_table = f"{schema}.{tabla}"
        try:
            self.cursor.execute(f"DBCC CHECKIDENT ('{full_table}', RESEED, {seed})")
        except Exception as e:
            print(f"Advertencia: No se pudo resetear identidad para {full_table}: {e}")

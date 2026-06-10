from typing import List
from models.entities import TipoVencimiento, TiposSubIndicador, Indicador, SubIndicador, EvidenciaDest, SubIndicadorEvidencia, FechaVencimientoSubIndicadorEvidencia, PuntuacionDest, RevisionEvidenciaDest, ComentarioRevisionDest

class DestinoRepository:
    """
    Repositorio para ESCRIBIR datos en la BD DESTINO (SISMAP_EDUCACION_M)
    Esquema principal: Mantenimiento
    Solo operaciones INSERT, DELETE
    """
    
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
    
    # ============================================================
    # TIPO VENCIMIENTO (Mantenimiento.TipoVencimiento)
    # ============================================================
    
    def insertar_tipos_vencimiento(self, datos: List[TipoVencimiento]) -> int:
        """Inserta o Actualiza TipoVencimiento en destino (UPSERT)"""
        # Using MERGE to handle existing IDs (Constraint Violation Fix)
        query = """
            MERGE Mantenimiento.TipoVencimiento AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?)) AS Source (Id, Nombre, Descripcion, CreatedAt, CreatedBy, IsActive, IsDeleted)
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET 
                    Nombre = Source.Nombre,
                    Descripcion = Source.Descripcion,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, Nombre, Descripcion, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.Nombre, Source.Descripcion, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        
        count = 0
        for item in datos:
            self.cursor.execute(query, 
                item.Id,
                item.Nombre,
                item.Descripcion,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count
    
    def limpiar_tipos_vencimiento(self) -> int:
        """Elimina todos los TipoVencimiento"""
        self.cursor.execute("DELETE FROM Mantenimiento.TipoVencimiento")
        count = self.cursor.rowcount
        self.resetear_identidad('Mantenimiento', 'TipoVencimiento')
        return count
    
    # ============================================================
    # TIPOS SUB INDICADOR (Mantenimiento.TiposSubIndicador)
    # ============================================================
    
    def insertar_tipos_sub_indicador(self, datos: List[TiposSubIndicador]) -> int:
        """Inserta TiposSubIndicador en destino"""
        query = """
            INSERT INTO Mantenimiento.TiposSubIndicador (
                Id,
                Nombre,
                Descripcion,
                CreatedAt,
                CreatedBy,
                IsActive,
                IsDeleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.Nombre,
                item.Descripcion,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count
    
    def limpiar_tipos_sub_indicador(self) -> int:
        self.cursor.execute("DELETE FROM Mantenimiento.TiposSubIndicador")
        count = self.cursor.rowcount
        self.resetear_identidad('Mantenimiento', 'TiposSubIndicador')
        return count
    
    # ============================================================
    # INDICADORES (Mantenimiento.Indicadores)
    # ============================================================
    
    def insertar_indicadores(self, datos: List[Indicador]) -> int:
        """Inserta o Actualiza Indicadores en destino (UPSERT)"""
        # NOTA: TipoIndicadorId omitido - no existe en la BD destino actual.
        query = """
            MERGE Mantenimiento.Indicadores AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (Id, Codigo, Nombre, Descripcion, Peso, CreatedAt, CreatedBy, IsActive, IsDeleted)
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    Codigo = Source.Codigo,
                    Nombre = Source.Nombre,
                    Descripcion = Source.Descripcion,
                    Peso = Source.Peso,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, Codigo, Nombre, Descripcion, Peso, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.Codigo, Source.Nombre, Source.Descripcion, Source.Peso, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.Codigo,
                item.Nombre,
                item.Descripcion,
                item.Peso,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count
    
    def limpiar_indicadores(self) -> int:
        self.cursor.execute("""
            DELETE FROM Mantenimiento.Indicadores
            WHERE Id NOT IN (
                SELECT DISTINCT IndicadorId 
                FROM Mantenimiento.SubIndicadores
            )
        """)
        count = self.cursor.rowcount
        return count

    # ============================================================
    # SUB INDICADORES (Mantenimiento.SubIndicadores)
    # ============================================================
    
    def insertar_sub_indicadores(self, datos: List[SubIndicador]) -> int:
        """Inserta o Actualiza SubIndicadores en destino (UPSERT)"""
        query = """
            MERGE Mantenimiento.SubIndicadores AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (Id, IndicadorId, TipoSubIndicadorId, Codigo, Nombre, Descripcion, Peso, CreatedAt, CreatedBy, IsActive, IsDeleted)
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    IndicadorId = Source.IndicadorId,
                    TipoSubIndicadorId = Source.TipoSubIndicadorId,
                    Codigo = Source.Codigo,
                    Nombre = Source.Nombre,
                    Descripcion = Source.Descripcion,
                    Peso = Source.Peso,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, IndicadorId, TipoSubIndicadorId, Codigo, Nombre, Descripcion, Peso, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.IndicadorId, Source.TipoSubIndicadorId, Source.Codigo, Source.Nombre, Source.Descripcion, Source.Peso, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.IndicadorId,
                item.TipoSubIndicadorId,
                item.Codigo,
                item.Nombre,
                item.Descripcion,
                item.Peso,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    
    def limpiar_sub_indicadores(self) -> int:
        self.cursor.execute("""
            DELETE FROM Mantenimiento.SubIndicadores
            WHERE Id NOT IN (
                SELECT DISTINCT SubIndicadorId 
                FROM Evidencia.SubIndicadorEvidencias
            )
        """)
        count = self.cursor.rowcount
        return count
    
    # ============================================================
    # EVIDENCIAS (Evidencia Schema)
    # ============================================================

    def insertar_evidencias(self, datos: List[EvidenciaDest]) -> int:
        """Inserta o Actualiza en Evidencia.Evidencias (UPSERT)"""
        query = """
            MERGE Evidencia.Evidencias AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (Id, Nombre, Descripcion, Valor, PreRequisitoId, CreatedAt, CreatedBy, IsActive, IsDeleted, AplicaVencimiento, CantidadDias, FechaVencimiento, Codigo)
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    Nombre = Source.Nombre,
                    Descripcion = Source.Descripcion,
                    Valor = Source.Valor,
                    PreRequisitoId = Source.PreRequisitoId,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted,
                    AplicaVencimiento = Source.AplicaVencimiento,
                    CantidadDias = Source.CantidadDias,
                    FechaVencimiento = Source.FechaVencimiento,
                    Codigo = Source.Codigo
            WHEN NOT MATCHED THEN
                INSERT (Id, Nombre, Descripcion, Valor, PreRequisitoId, CreatedAt, CreatedBy, IsActive, IsDeleted, AplicaVencimiento, CantidadDias, FechaVencimiento, Codigo)
                VALUES (Source.Id, Source.Nombre, Source.Descripcion, Source.Valor, Source.PreRequisitoId, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted, Source.AplicaVencimiento, Source.CantidadDias, Source.FechaVencimiento, Source.Codigo);
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.Nombre,
                item.Descripcion,
                item.Valor,
                item.PreRequisitoId,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted,
                item.AplicaVencimiento,
                item.CantidadDias,
                item.FechaVencimiento,
                item.Codigo
            )
            count += 1
        return count
    
    def limpiar_evidencias(self) -> int:
        self.deshabilitar_constraint('Evidencia', 'Evidencias', 'FK_Evidencias_Evidencias_PreRequisitoId')
        self.cursor.execute("""
            WITH KeptEvidencias AS (
                SELECT Id, PreRequisitoId
                FROM Evidencia.Evidencias
                WHERE Id IN (SELECT DISTINCT EvidenciaId FROM Evidencia.SubIndicadorEvidencias)
                   OR Id IN (SELECT DISTINCT EvidenciaId FROM Evidencia.Archivos WHERE EvidenciaId IS NOT NULL)
                
                UNION ALL
                
                SELECT e.Id, e.PreRequisitoId
                FROM Evidencia.Evidencias e
                INNER JOIN KeptEvidencias k ON e.Id = k.PreRequisitoId
            )
            DELETE FROM Evidencia.Evidencias
            WHERE Id NOT IN (SELECT Id FROM KeptEvidencias)
        """)
        count = self.cursor.rowcount
        self.habilitar_constraint('Evidencia', 'Evidencias', 'FK_Evidencias_Evidencias_PreRequisitoId')
        return count

    def insertar_fecha_vencimiento_evidencias(self, datos: List[FechaVencimientoSubIndicadorEvidencia]) -> int:
        """Inserta o Actualiza en Evidencia.FechaVencimientoSubIndicadorEvidencias"""
        query = """
            MERGE Evidencia.FechaVencimientoSubIndicadorEvidencias AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS Source (Id, TipoVencimientoId, FechaVencimiento, PeriodicidadDias, CreatedAt, CreatedBy, IsActive, IsDeleted)
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

    def limpiar_fecha_vencimiento_evidencias(self) -> int:
        self.cursor.execute("""
            DELETE FROM Evidencia.FechaVencimientoSubIndicadorEvidencias
            WHERE Id NOT IN (
                SELECT DISTINCT FechaVencimientoSubIndicadorEvidenciaId 
                FROM Evidencia.SubIndicadorEvidencias
            )
        """)
        count = self.cursor.rowcount
        return count

    def insertar_sub_indicador_evidencias(self, datos: List[SubIndicadorEvidencia]) -> int:
        """Inserta o Actualiza en Evidencia.SubIndicadorEvidencias"""
        query = """
            MERGE Evidencia.SubIndicadorEvidencias AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (Id, SubIndicadorId, EvidenciaId, FechaVencimientoSubIndicadorEvidenciaId, TipoEvaluacionId, FechaVenciento, CreatedAt, CreatedBy, IsActive, IsDeleted)
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    SubIndicadorId = Source.SubIndicadorId,
                    EvidenciaId = Source.EvidenciaId,
                    FechaVencimientoSubIndicadorEvidenciaId = Source.FechaVencimientoSubIndicadorEvidenciaId,
                    TipoEvaluacionId = Source.TipoEvaluacionId,
                    FechaVenciento = Source.FechaVenciento,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, SubIndicadorId, EvidenciaId, FechaVencimientoSubIndicadorEvidenciaId, TipoEvaluacionId, FechaVenciento, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.SubIndicadorId, Source.EvidenciaId, Source.FechaVencimientoSubIndicadorEvidenciaId, Source.TipoEvaluacionId, Source.FechaVenciento, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.SubIndicadorId,
                item.EvidenciaId,
                item.FechaVencimientoSubIndicadorEvidenciaId,
                item.TipoEvaluacionId,
                item.FechaVenciento,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    def limpiar_sub_indicador_evidencias(self) -> int:
        self.cursor.execute("""
            DELETE FROM Evidencia.SubIndicadorEvidencias
            WHERE Id NOT IN (
                SELECT DISTINCT SubIndicadorEvidenciaId 
                FROM Evidencia.Archivos
            )
        """)
        count = self.cursor.rowcount
        return count

    # ============================================================
    # ARCHIVOS (Evidencia.Archivos)
    # ============================================================

    def insertar_archivos(self, datos: List['ArchivoDest']) -> int: # Forward ref or import if needed, but python is dynamic
        """Inserta o Actualiza en Evidencia.Archivos (UPSERT)"""
        # Note: CoedomId, SubIndicadorEvidenciaId, NombreOriginal, ArchivoBinario, EstadoArchivoId, RowGuid, TipoAlmacenamiento, RutaExterna
        # are required/important fields.
        
        query = """
            MERGE Evidencia.Archivos AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (
                Id, CoedomId, SubIndicadorEvidenciaId, NombreOriginal, ArchivoBinario, EstadoArchivoId, 
                EvidenciaId, CreatedAt, CreatedBy, UpdatedAt, UpdatedBy, IsActive, IsDeleted, 
                RowGuid, TipoAlmacenamiento, RutaExterna
            )
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    CoedomId = Source.CoedomId,
                    SubIndicadorEvidenciaId = Source.SubIndicadorEvidenciaId,
                    NombreOriginal = Source.NombreOriginal,
                    -- Update binary only if provided, else keep existing? 
                    -- Migration usually overwrites. Source has no binary, so we might receive empty.
                    -- If we want to preserve existing binary in DB, we'd need check. 
                    -- But this is full migration. Overwriting is standard.
                    ArchivoBinario = Source.ArchivoBinario,
                    EstadoArchivoId = Source.EstadoArchivoId,
                    EvidenciaId = Source.EvidenciaId,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted,
                    RowGuid = Source.RowGuid,
                    TipoAlmacenamiento = Source.TipoAlmacenamiento,
                    RutaExterna = Source.RutaExterna
            WHEN NOT MATCHED THEN
                INSERT (
                    Id, CoedomId, SubIndicadorEvidenciaId, NombreOriginal, ArchivoBinario, EstadoArchivoId, 
                    EvidenciaId, CreatedAt, CreatedBy, UpdatedAt, UpdatedBy, IsActive, IsDeleted, 
                    RowGuid, TipoAlmacenamiento, RutaExterna
                )
                VALUES (
                    Source.Id, Source.CoedomId, Source.SubIndicadorEvidenciaId, Source.NombreOriginal, Source.ArchivoBinario, Source.EstadoArchivoId,
                    Source.EvidenciaId, Source.CreatedAt, Source.CreatedBy, Source.UpdatedAt, Source.UpdatedBy, Source.IsActive, Source.IsDeleted,
                    Source.RowGuid, Source.TipoAlmacenamiento, Source.RutaExterna
                );
        """
        if datos:
             # Check if ANY item has CoedomId > 0
             for d in datos:
                 if d.CoedomId and d.CoedomId > 0:
                     msg = f"DEBUG DESTINO: Insertar Archivo VALID DETECTED CoedomId={d.CoedomId}"
                     print(msg)
                     # raise Exception(msg) # Removed validation crash

        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.CoedomId,
                item.SubIndicadorEvidenciaId,
                item.NombreOriginal,
                item.ArchivoBinario,
                item.EstadoArchivoId,
                item.EvidenciaId,
                item.CreatedAt,
                item.CreatedBy,
                item.UpdatedAt,
                item.UpdatedBy,
                item.IsActive,
                item.IsDeleted,
                item.RowGuid,
                item.TipoAlmacenamiento,
                item.RutaExterna
            )
            count += 1
        return count

    def limpiar_archivos(self) -> int:
        self.cursor.execute("""
            DELETE FROM Evidencia.Archivos
            WHERE Id NOT IN (
                SELECT DISTINCT ArchivoId 
                FROM Mantenimiento.ConfiguracionOrganismoExcepcion 
                WHERE ArchivoId IS NOT NULL
            )
            AND Id NOT IN (
                SELECT DISTINCT ArchivoId 
                FROM Auditoria.Ticket 
                WHERE ArchivoId IS NOT NULL
            )
            AND Id NOT IN (
                SELECT DISTINCT RevisionEvidenciaId 
                FROM Auditoria.Ticket 
                WHERE RevisionEvidenciaId IS NOT NULL
            )
        """)
        count = self.cursor.rowcount
        return count

    def obtener_ids_archivos_existentes(self) -> set:
        """Retorna un conjunto de todos los IDs de archivos actualmente existentes en la BD"""
        self.cursor.execute("SELECT Id FROM Evidencia.Archivos")
        return {row[0] for row in self.cursor.fetchall()}

    # ============================================================
    # PUNTUACION (Evidencia.Puntuacion)
    # ============================================================

    def insertar_puntuacion(self, datos: List[PuntuacionDest]) -> int:
        """Inserta o Actualiza en Evidencia.Puntuacion"""
        query = """
            MERGE Evidencia.Puntuacion AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS Source (Id, ArchivoEvidenciaId, PuntuadorUsuarioId, Calificacion, CreatedAt, CreatedBy, IsActive, IsDeleted)
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    ArchivoEvidenciaId = Source.ArchivoEvidenciaId,
                    PuntuadorUsuarioId = Source.PuntuadorUsuarioId,
                    Calificacion = Source.Calificacion,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, ArchivoEvidenciaId, PuntuadorUsuarioId, Calificacion, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.ArchivoEvidenciaId, Source.PuntuadorUsuarioId, Source.Calificacion, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.ArchivoEvidenciaId,
                item.PuntuadorUsuarioId,
                item.Calificacion,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    def limpiar_puntuacion(self) -> int:
        self.cursor.execute("DELETE FROM Evidencia.Puntuacion")
        count = self.cursor.rowcount
        self.resetear_identidad('Evidencia', 'Puntuacion')
        return count

    # ============================================================
    # REVISIONES (Evidencia.RevisionEvidencias)
    # ============================================================

    def insertar_revision_evidencias(self, datos: List[RevisionEvidenciaDest]) -> int:
        query = """
            MERGE Evidencia.RevisionEvidencias AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS Source (Id, ArchivoEvidenciaId, FechaRevisionConcluida, UsuarioId, EstadoDadoId, NivelRevisionEvidencia, RevisionCoedomId, CreatedAt, CreatedBy, IsActive, IsDeleted)
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    ArchivoEvidenciaId = Source.ArchivoEvidenciaId,
                    FechaRevisionConcluida = Source.FechaRevisionConcluida,
                    UsuarioId = Source.UsuarioId,
                    EstadoDadoId = Source.EstadoDadoId,
                    NivelRevisionEvidencia = Source.NivelRevisionEvidencia,
                    RevisionCoedomId = Source.RevisionCoedomId,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, ArchivoEvidenciaId, FechaRevisionConcluida, UsuarioId, EstadoDadoId, NivelRevisionEvidencia, RevisionCoedomId, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.ArchivoEvidenciaId, Source.FechaRevisionConcluida, Source.UsuarioId, Source.EstadoDadoId, Source.NivelRevisionEvidencia, Source.RevisionCoedomId, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.ArchivoEvidenciaId,
                item.FechaRevisionConcluida,
                item.UsuarioId,
                item.EstadoDadoId,
                item.NivelRevisionEvidencia,
                item.RevisionCoedomId,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    def limpiar_revision_evidencias(self) -> int:
        self.cursor.execute("DELETE FROM Evidencia.RevisionEvidencias")
        count = self.cursor.rowcount
        self.resetear_identidad('Evidencia', 'RevisionEvidencias')
        return count

    def insertar_comentario_revision(self, datos: List[ComentarioRevisionDest]) -> int:
        query = """
            MERGE Evidencia.ComentarioRevisionEvidencias AS Target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?)) AS Source (Id, RevisionEvidenciaId, Observaciones, UsuarioId, CreatedAt, CreatedBy, IsActive, IsDeleted)
            ON (Target.Id = Source.Id)
            WHEN MATCHED THEN
                UPDATE SET
                    RevisionEvidenciaId = Source.RevisionEvidenciaId,
                    Observaciones = Source.Observaciones,
                    UsuarioId = Source.UsuarioId,
                    UpdatedAt = GETDATE(),
                    UpdatedBy = 'MigrationScript_Update',
                    IsActive = Source.IsActive,
                    IsDeleted = Source.IsDeleted
            WHEN NOT MATCHED THEN
                INSERT (Id, RevisionEvidenciaId, Observaciones, UsuarioId, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (Source.Id, Source.RevisionEvidenciaId, Source.Observaciones, Source.UsuarioId, Source.CreatedAt, Source.CreatedBy, Source.IsActive, Source.IsDeleted);
        """
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.RevisionEvidenciaId,
                item.Observaciones,
                item.UsuarioId,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count

    def limpiar_comentario_revision(self) -> int:
        self.cursor.execute("DELETE FROM Evidencia.ComentarioRevisionEvidencias")
        count = self.cursor.rowcount
        self.resetear_identidad('Evidencia', 'ComentarioRevisionEvidencias')
        return count

    def asegurar_tipo_evaluacion_defecto(self):
        """Asegura que exista el TipoEvaluacion ID=1 (Automática)"""
        # Si no existe, insertarlo
        query = "SELECT COUNT(*) FROM Evidencia.TipoEvaluacion WHERE Id = 1"
        self.cursor.execute(query)
        if self.cursor.fetchone()[0] == 0:
            self.habilitar_identity_insert('Evidencia', 'TipoEvaluacion')
            self.cursor.execute("""
                INSERT INTO Evidencia.TipoEvaluacion (Id, Nombre, CreatedAt, IsActive, IsDeleted)
                VALUES (1, 'Automática', GETDATE(), 1, 0)
            """)
            self.deshabilitar_identity_insert('Evidencia', 'TipoEvaluacion')
    # UTILIDADES
    # ============================================================
    
    def habilitar_identity_insert(self, schema: str, tabla: str):
        """Habilita inserción de IDs explícitos"""
        full_table = f"{schema}.{tabla}"
        self.cursor.execute(f"SET IDENTITY_INSERT {full_table} ON")
    
    def deshabilitar_identity_insert(self, schema: str, tabla: str):
        """Deshabilita inserción de IDs explícitos"""
        full_table = f"{schema}.{tabla}"
        self.cursor.execute(f"SET IDENTITY_INSERT {full_table} OFF")

    def deshabilitar_constraint(self, schema: str, tabla: str, constraint: str):
        full_table = f"{schema}.{tabla}"
        self.cursor.execute(f"ALTER TABLE {full_table} NOCHECK CONSTRAINT {constraint}")

    def habilitar_constraint(self, schema: str, tabla: str, constraint: str):
        full_table = f"{schema}.{tabla}"
        self.cursor.execute(f"ALTER TABLE {full_table} WITH CHECK CHECK CONSTRAINT {constraint}")

    def limpiar_pregunta_revisiones(self) -> int:
        """Elimina registros de Evidencia.PreguntaRevisiones para evitar FK conflict"""
        self.cursor.execute("DELETE FROM Evidencia.PreguntaRevisiones")
        count = self.cursor.rowcount
        self.resetear_identidad('Evidencia', 'PreguntaRevisiones')
        return count

    def limpiar_respuestas_revisiones(self) -> int:
        """Elimina registros de Evidencia.RespuestasRevisiones para evitar FK conflict"""
        self.cursor.execute("DELETE FROM Evidencia.RespuestasRevisiones")
        count = self.cursor.rowcount
        self.resetear_identidad('Evidencia', 'RespuestasRevisiones')
        return count

    def resetear_identidad(self, schema: str, tabla: str, seed: int = 0):
        """Resetea el contador de identidad de la tabla"""
        full_table = f"{schema}.{tabla}"
        try:
            self.cursor.execute(f"DBCC CHECKIDENT ('{full_table}', RESEED, {seed})")
        except Exception as e:
            # Puede fallar si la tabla no tiene identity o permiso, loguear o ignorar
            print(f"Advertencia: No se pudo resetear identidad para {full_table}: {e}")

from typing import List
from models.entities import TipoVencimiento, TiposIndicador, Indicador, SubIndicador, EvidenciaDest, SubIndicadorEvidencia, FechaVencimientoSubIndicadorEvidencia

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
        """Inserta TipoVencimiento en destino"""
        query = """
            INSERT INTO Mantenimiento.TipoVencimiento (
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
    
    def limpiar_tipos_vencimiento(self) -> int:
        """Elimina todos los TipoVencimiento"""
        self.cursor.execute("DELETE FROM Mantenimiento.TipoVencimiento")
        count = self.cursor.rowcount
        self.resetear_identidad('Mantenimiento', 'TipoVencimiento')
        return count
    
    # ============================================================
    # TIPOS INDICADOR (Mantenimiento.TiposIndicador)
    # ============================================================
    
    def insertar_tipos_indicador(self, datos: List[TiposIndicador]) -> int:
        """Inserta TiposIndicador en destino"""
        query = """
            INSERT INTO Mantenimiento.TiposIndicador (
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
    
    def limpiar_tipos_indicador(self) -> int:
        self.cursor.execute("DELETE FROM Mantenimiento.TiposIndicador")
        count = self.cursor.rowcount
        self.resetear_identidad('Mantenimiento', 'TiposIndicador')
        return count
    
    # ============================================================
    # INDICADORES (Mantenimiento.Indicadores)
    # ============================================================
    
    def insertar_indicadores(self, datos: List[Indicador]) -> int:
        """Inserta Indicadores en destino"""
        query = """
            INSERT INTO Mantenimiento.Indicadores (
                Id,
                Codigo,
                Nombre,
                Descripcion,
                TipoIndicadorId,
                Peso,
                CreatedAt,
                CreatedBy,
                IsActive,
                IsDeleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.Codigo,
                item.Nombre,
                item.Descripcion,
                item.TipoIndicadorId,
                item.Peso,
                item.CreatedAt,
                item.CreatedBy,
                item.IsActive,
                item.IsDeleted
            )
            count += 1
        return count
    
    def limpiar_indicadores(self) -> int:
        self.cursor.execute("DELETE FROM Mantenimiento.Indicadores")
        count = self.cursor.rowcount
        self.resetear_identidad('Mantenimiento', 'Indicadores')
        return count

    # ============================================================
    # SUB INDICADORES (Mantenimiento.SubIndicadores)
    # ============================================================
    
    def insertar_sub_indicadores(self, datos: List[SubIndicador]) -> int:
        """Inserta SubIndicadores en destino"""
        query = """
            INSERT INTO Mantenimiento.SubIndicadores (
                Id,
                IndicadorId,
                Codigo,
                Nombre,
                Descripcion,
                Peso,
                CreatedAt,
                CreatedBy,
                IsActive,
                IsDeleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        count = 0
        for item in datos:
            self.cursor.execute(query,
                item.Id,
                item.IndicadorId,
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
        self.cursor.execute("DELETE FROM Mantenimiento.SubIndicadores")
        count = self.cursor.rowcount
        self.resetear_identidad('Mantenimiento', 'SubIndicadores')
        return count
    
    # ============================================================
    # EVIDENCIAS (Evidencia Schema)
    # ============================================================

    def insertar_evidencias(self, datos: List[EvidenciaDest]) -> int:
        """Inserta en Evidencia.Evidencias"""
        query = """
            INSERT INTO Evidencia.Evidencias (
                Id,
                Nombre,
                Descripcion,
                Valor,
                PreRequisitoId,
                CreatedAt,
                CreatedBy,
                IsActive,
                IsDeleted,
                AplicaVencimiento,
                CantidadDias,
                FechaVencimiento,
                Codigo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        self.cursor.execute("DELETE FROM Evidencia.Evidencias")
        count = self.cursor.rowcount
        self.resetear_identidad('Evidencia', 'Evidencias')
        return count

    def insertar_fecha_vencimiento_evidencias(self, datos: List[FechaVencimientoSubIndicadorEvidencia]) -> int:
        """Inserta en Evidencia.FechaVencimientoSubIndicadorEvidencias"""
        query = """
            INSERT INTO Evidencia.FechaVencimientoSubIndicadorEvidencias (
                Id,
                TipoVencimientoId,
                FechaVencimiento,
                PeriodicidadDias,
                CreatedAt,
                CreatedBy,
                IsActive,
                IsDeleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
        self.cursor.execute("DELETE FROM Evidencia.FechaVencimientoSubIndicadorEvidencias")
        count = self.cursor.rowcount
        self.resetear_identidad('Evidencia', 'FechaVencimientoSubIndicadorEvidencias')
        return count

    def insertar_sub_indicador_evidencias(self, datos: List[SubIndicadorEvidencia]) -> int:
        """Inserta en Evidencia.SubIndicadorEvidencias"""
        query = """
            INSERT INTO Evidencia.SubIndicadorEvidencias (
                Id,
                SubIndicadorId,
                EvidenciaId,
                FechaVencimientoSubIndicadorEvidenciaId,
                TipoEvaluacionId,
                FechaVenciento,
                CreatedAt,
                CreatedBy,
                IsActive,
                IsDeleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        self.cursor.execute("DELETE FROM Evidencia.SubIndicadorEvidencias")
        count = self.cursor.rowcount
        self.resetear_identidad('Evidencia', 'SubIndicadorEvidencias')
        return count

    def asegurar_tipo_evaluacion_defecto(self):
        """Asegura que exista TipoEvaluacion Id=1"""
        # Check if exists
        self.cursor.execute("SELECT COUNT(*) FROM Evidencia.TipoEvaluacion WHERE Id = 1")
        if self.cursor.fetchone()[0] == 0:
            query = """
                INSERT INTO Evidencia.TipoEvaluacion (
                    Id, Nombre, CreatedAt, CreatedBy, IsActive, IsDeleted
                ) VALUES (1, 'Evaluación Migrada', GETDATE(), 'MigrationScript', 1, 0)
            """
            self.habilitar_identity_insert('Evidencia', 'TipoEvaluacion')
            self.cursor.execute(query)
            self.deshabilitar_identity_insert('Evidencia', 'TipoEvaluacion')
            return True
        return False
    
    # ============================================================
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

    def resetear_identidad(self, schema: str, tabla: str, seed: int = 0):
        """Resetea el contador de identidad de la tabla"""
        full_table = f"{schema}.{tabla}"
        try:
            self.cursor.execute(f"DBCC CHECKIDENT ('{full_table}', RESEED, {seed})")
        except Exception as e:
            # Puede fallar si la tabla no tiene identity o permiso, loguear o ignorar
            print(f"Advertencia: No se pudo resetear identidad para {full_table}: {e}")

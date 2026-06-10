import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from repositories.fuente_repo import FuenteRepository
from repositories.destino_repo import DestinoRepository
from services.transformation_service import TransformationService
from models.entities import (
    TipoVencimiento, TiposSubIndicador, Indicador, Ibog, SubIndicador,
    EvidenciaSource, EvidenciaDest, SubIndicadorEvidencia, FechaVencimientoSubIndicadorEvidencia,
    CargaEvidenciaSource, PuntuacionDest, RevisionSource, RevisionEvidenciaDest, ComentarioRevisionDest
)
from utils.logger import setup_logger, MigrationStats


class MigrationService:
    """
    Servicio de migración ETL:
    1. Extract: Fuente -> JSON (Modelos Fuente)
    2. Transform: JSON -> Modelos Destino
    3. Load: Modelos Destino -> BD Destino
    """
    
    def __init__(self, conn_fuente, conn_destino):
        self.conn_fuente = conn_fuente
        self.conn_destino = conn_destino
        
        # Inicializar repositorios y servicios
        self.fuente = FuenteRepository(conn_fuente) if conn_fuente else None
        self.destino = DestinoRepository(conn_destino) if conn_destino else None
        self.transformer = TransformationService()
        
        self.logger = setup_logger("migracion")
        self.stats = MigrationStats()
        
        self.export_dir = Path(f"exports/migracion_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Carpeta de exportación: {self.export_dir}")
    
    # ============================================================
    # PASO 1: EXTRACCIÓN (E)
    # ============================================================
    
    def extraer_a_json(self, nombre: str, datos: List[Any]) -> Optional[str]:
        if not datos:
            self.logger.warning(f"No hay datos para extraer: {nombre}")
            return None
        
        archivo = self.export_dir / f"{nombre}.json"
        datos_dict = [item.to_dict() for item in datos]
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos_dict, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Extraído: {archivo} ({len(datos)} registros)")
        return str(archivo)

    def extraer_todo(self, sub_indicador_codigos: Optional[List[str]] = None) -> Dict[str, str]:
        self.logger.info("INICIANDO EXTRACCIÓN DE DATOS (FUENTE)")
        archivos = {}
        
        # 1. TipoVencimiento
        try:
            datos = self.fuente.obtener_tipos_vencimiento()
            archivos['tipos_vencimiento'] = self.extraer_a_json('tipos_vencimiento', datos)
            self.stats.registrar_tabla('TipoVencimiento', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo TipoVencimiento: {e}")
            
        # 2. TiposIndicador
        # try:
        #     datos = self.fuente.obtener_tipos_indicador()
        #     archivos['tipos_indicador'] = self.extraer_a_json('tipos_indicador', datos)
        #     self.stats.registrar_tabla('TiposIndicador', len(datos), 0, True)
        # except Exception as e:
        #     self.logger.error(f"Error extrayendo TiposIndicador: {e}")

        # 3. Indicadores (Desde Ibog)
        try:
            datos = self.fuente.obtener_indicadores_ibog()
            archivos['ibog'] = self.extraer_a_json('ibog', datos)
            self.stats.registrar_tabla('Ibog', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo Ibog: {e}")

        # 4. SubIndicadores
        try:
            datos = self.fuente.obtener_sub_indicadores()
            archivos['sub_indicadores'] = self.extraer_a_json('sub_indicadores', datos)
            self.stats.registrar_tabla('SubIndicadores', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo SubIndicadores: {e}")

        # 5. Evidencias (Filtrado opcional)
        try:
            datos = self.fuente.obtener_evidencias(sub_indicador_codigos)
            archivos['evidencias_source'] = self.extraer_a_json('evidencias_source', datos)
            self.stats.registrar_tabla('EvidenciasSource', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo Evidencias: {e}")
            
        # 6. Puntuaciones (Filtrado requerido si se usa, o vacio si no hay codigos)
        if sub_indicador_codigos:
            mapped_codigos = [self.transformer.map_to_source_code(c) for c in sub_indicador_codigos]
            try:
                datos = self.fuente.obtener_puntuaciones(mapped_codigos)
                archivos['puntuaciones'] = self.extraer_a_json('puntuaciones', datos)
                self.stats.registrar_tabla('Puntuaciones', len(datos), 0, True)
            except Exception as e:
                self.logger.error(f"Error extrayendo Puntuaciones: {e}")
                
            # 7. Revisiones (Filtrado requerido)
            try:
                datos = self.fuente.obtener_revisiones(mapped_codigos)
                archivos['revisiones'] = self.extraer_a_json('revisiones', datos)
                self.stats.registrar_tabla('Revisiones', len(datos), 0, True)
            except Exception as e:
                self.logger.error(f"Error extrayendo Revisiones: {e}")
                
        return archivos

    # ============================================================
    # PASO 2 & 3: TRANSFORMACIÓN Y CARGA (T + L)
    # ============================================================

    def cargar_desde_json(self, archivo: str, entity_class) -> List[Any]:
        if not archivo or not Path(archivo).exists():
            return []
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        # Handle instantiation safely
        if hasattr(entity_class, 'from_dict'):
            return [entity_class.from_dict(item) for item in datos]
        return [entity_class(**item) for item in datos]

    def cargar_todo(self, archivos: Dict[str, str], limpiar_antes: bool = False, puntuador_id: str = None) -> bool:
        self.logger.info("INICIANDO TRANSFORMACIÓN Y CARGA")
        
        try:
            if limpiar_antes:
                self.logger.info("Limpiando tablas destino...")
                # Order matters for foreign keys
                self.destino.limpiar_respuestas_revisiones() # Clean child first
                self.destino.limpiar_comentario_revision()
                self.destino.limpiar_revision_evidencias()
                self.destino.limpiar_puntuacion()
                self.destino.limpiar_pregunta_revisiones() # Clean child of SubIndicadorEvidencias
                self.destino.limpiar_archivos() # Clean child first
                self.destino.limpiar_sub_indicador_evidencias()
                self.destino.limpiar_fecha_vencimiento_evidencias()
                self.destino.limpiar_evidencias()
                
                self.destino.limpiar_sub_indicadores()
                self.destino.limpiar_indicadores()
                # limpiar_tipos_vencimiento() omitido: ConfiguracionOrganismoExcepcion
                # tiene FK a TipoVencimiento. No es necesario limpiar porque el insert usa MERGE (UPSERT).
                # self.destino.limpiar_tipos_vencimiento()
            
            existing_file_ids = self.destino.obtener_ids_archivos_existentes()
            
            # ... (Previous loads remain same) ...
            
            # 1. TipoVencimiento
            if archivos.get('tipos_vencimiento'):
                source_data = self.cargar_desde_json(archivos['tipos_vencimiento'], TipoVencimiento)
                # Note: transformation service now ignores source_data content and returns static list
                transformed_data = self.transformer.transformar_tipo_vencimiento(source_data)
                
                self.destino.habilitar_identity_insert('Mantenimiento', 'TipoVencimiento')
                count = self.destino.insertar_tipos_vencimiento(transformed_data)
                self.destino.deshabilitar_identity_insert('Mantenimiento', 'TipoVencimiento')
                
                self.logger.info(f"TipoVencimiento: {count} insertados")
            
            # 2. TiposSubIndicador
            # if archivos.get('tipos_sub_indicador'):
            #     source_data = self.cargar_desde_json(archivos['tipos_sub_indicador'], TiposSubIndicador)
            #     transformed_data = self.transformer.transformar_tipo_sub_indicador(source_data)
                
            #     self.destino.habilitar_identity_insert('Mantenimiento', 'TiposSubIndicador')
            #     count = self.destino.insertar_tipos_sub_indicador(transformed_data)
            #     self.destino.deshabilitar_identity_insert('Mantenimiento', 'TiposSubIndicador')
                
            #     self.logger.info(f"TiposSubIndicador: {count} insertados")
            
            # 3. Indicadores (De Ibog)
            if archivos.get('ibog'):
                source_data = self.cargar_desde_json(archivos['ibog'], Ibog)
                transformed_data = self.transformer.transformar_indicador(source_data)
                
                self.destino.habilitar_identity_insert('Mantenimiento', 'Indicadores')
                count = self.destino.insertar_indicadores(transformed_data)
                self.destino.deshabilitar_identity_insert('Mantenimiento', 'Indicadores')
                
                self.logger.info(f"Indicadores: {count} insertados")
            
            # 4. SubIndicadores
            if archivos.get('sub_indicadores'):
                source_data = self.cargar_desde_json(archivos['sub_indicadores'], SubIndicador)
                transformed_data = self.transformer.transformar_sub_indicador(source_data)
                
                self.destino.habilitar_identity_insert('Mantenimiento', 'SubIndicadores')
                count = self.destino.insertar_sub_indicadores(transformed_data)
                self.destino.deshabilitar_identity_insert('Mantenimiento', 'SubIndicadores')
                
                self.logger.info(f"SubIndicadores: {count} insertados")

            # 5. Evidencias
            if archivos.get('evidencias_source'):
                # Asegurar dependencias de diccionario
                self.destino.asegurar_tipo_evaluacion_defecto()
                
                source_data = self.cargar_desde_json(archivos['evidencias_source'], EvidenciaSource)
                evidencias, fechas, sub_evidencias, archivos_dest = self.transformer.transformar_evidencia(source_data)
                
                # Insertar Evidencias Base (Disable FK link to self for PreRequisito)
                self.destino.habilitar_identity_insert('Evidencia', 'Evidencias')
                self.destino.deshabilitar_constraint('Evidencia', 'Evidencias', 'FK_Evidencias_Evidencias_PreRequisitoId')
                
                c1 = self.destino.insertar_evidencias(evidencias)
                
                self.destino.habilitar_constraint('Evidencia', 'Evidencias', 'FK_Evidencias_Evidencias_PreRequisitoId')
                self.destino.deshabilitar_identity_insert('Evidencia', 'Evidencias')
                
                self.logger.info(f"Evidencias: {c1} insertadas")
                
                # Insertar Fechas
                self.destino.habilitar_identity_insert('Evidencia', 'FechaVencimientoSubIndicadorEvidencias')
                c2 = self.destino.insertar_fecha_vencimiento_evidencias(fechas)
                self.destino.deshabilitar_identity_insert('Evidencia', 'FechaVencimientoSubIndicadorEvidencias')
                
                self.logger.info(f"FechasVencimientoEvidencia: {c2} insertadas")
                
                # Insertar Pivot
                self.destino.habilitar_identity_insert('Evidencia', 'SubIndicadorEvidencias')
                c3 = self.destino.insertar_sub_indicador_evidencias(sub_evidencias)
                self.destino.deshabilitar_identity_insert('Evidencia', 'SubIndicadorEvidencias')
                
                self.logger.info(f"SubIndicadorEvidencias: {c3} insertadas")

                # Insertar Archivos
                self.destino.habilitar_identity_insert('Evidencia', 'Archivos')
                c4 = self.destino.insertar_archivos(archivos_dest)
                self.destino.deshabilitar_identity_insert('Evidencia', 'Archivos')
                
                self.logger.info(f"Archivos (Template): {c4} insertados")
                
                # Determine next file ID
                max_id = 0
                if archivos_dest:
                    max_id = max(a.Id for a in archivos_dest)
                next_file_id = max_id + 1

            # 6. Puntuaciones
            # 6. Puntuaciones (y Archivos de Usuario)
            if archivos.get('puntuaciones'):
                source_data = self.cargar_desde_json(archivos['puntuaciones'], CargaEvidenciaSource)
                
                self.logger.info(f"DEBUG: Source Data Length for Puntuaciones = {len(source_data)}")
                if source_data:
                    self.logger.info(f"DEBUG: Sample Source Item: {source_data[0]}")
                
                # Retrieve next_file_id if not set (e.g. if no ev files)
                if 'next_file_id' not in locals():
                    next_file_id = 1
                    
                scores, user_files = self.transformer.transformar_puntuacion(source_data, next_file_id, puntuador_id, existing_file_ids=existing_file_ids)
                
                # Insert User Files (Archivos)
                if user_files:
                    self.destino.habilitar_identity_insert('Evidencia', 'Archivos')
                    c_uf = self.destino.insertar_archivos(user_files)
                    self.destino.deshabilitar_identity_insert('Evidencia', 'Archivos')
                    self.logger.info(f"Archivos (Usuarios): {c_uf} insertados")
                
                # Insert Scores
                self.destino.habilitar_identity_insert('Evidencia', 'Puntuacion')
                count = self.destino.insertar_puntuacion(scores)
                self.destino.deshabilitar_identity_insert('Evidencia', 'Puntuacion')
                
                self.logger.info(f"Puntuaciones: {count} insertadas")
                
            # 7. Revisiones
            if archivos.get('revisiones'):
                source_data = self.cargar_desde_json(archivos['revisiones'], RevisionSource)
                revisions, comments = self.transformer.transformar_revision(source_data)
                
                self.destino.habilitar_identity_insert('Evidencia', 'RevisionEvidencias')
                c_rev = self.destino.insertar_revision_evidencias(revisions)
                self.destino.deshabilitar_identity_insert('Evidencia', 'RevisionEvidencias')
                
                self.destino.habilitar_identity_insert('Evidencia', 'ComentarioRevisionEvidencias')
                c_com = self.destino.insertar_comentario_revision(comments)
                self.destino.deshabilitar_identity_insert('Evidencia', 'ComentarioRevisionEvidencias')
                
                self.logger.info(f"Revisiones: {c_rev}, Comentarios: {c_com} insertados")


            self.conn_destino.commit()
            self.logger.info("✓ MIGRACIÓN EXITOSA")
            return True
            
        except Exception as e:
            self.conn_destino.rollback()
            self.logger.error(f"✗ ERROR EN CARGA: {e}")
            return False

    # ============================================================
    # EJECUCIÓN
    # ============================================================

    def ejecutar_migracion(self, sub_indicador_codigos: Optional[List[str]] = None, limpiar_antes: bool = False, confirmar: bool = True, puntuador_id: str = None) -> bool:
        archivos = self.extraer_todo(sub_indicador_codigos)
        if not any(archivos.values()):
            return False
            
        if confirmar:
            input("\nPresione Enter para cargar a destino (Ctrl+C para cancelar)...")
        
        return self.cargar_todo(archivos, limpiar_antes, puntuador_id)

    def solo_extraer(self) -> Dict[str, str]:
        self.extraer_todo()
        print(f"\n✓ Datos extraídos en: {self.export_dir}")
        return {}

    def solo_cargar(self, carpeta_export: str, limpiar_antes: bool = False) -> bool:
        export_path = Path(carpeta_export)
        archivos = {
            'tipos_vencimiento': str(export_path / 'tipos_vencimiento.json'),
            'tipos_sub_indicador': str(export_path / 'tipos_sub_indicador.json'),
            'ibog': str(export_path / 'ibog.json'),
            'sub_indicadores': str(export_path / 'sub_indicadores.json'),
        }
        return self.cargar_todo(archivos, limpiar_antes)

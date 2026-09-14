import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from repositories.fuente_repo import FuenteRepository
from repositories.destino_repo import DestinoRepository
from services.transformation_service import TransformationService
from models.entities import (
    TipoVencimiento, TiposSubIndicador, TiposEvaluacion, EstadosArchivo,
    Indicador, Ibog, SubIndicador, EvidenciaSource, EvidenciaDest, 
    SubIndicadorEvidencia, FechaVencimientoSubIndicadorEvidencia,
    CargaEvidenciaSource, PuntuacionDest, RevisionSource, RevisionEvidenciaDest, 
    ComentarioRevisionDest, NoticiaSource, NoticiaDest
)
from utils.logger import setup_logger, MigrationStats


class MigrationService:
    """
    Servicio de migración ETL para SISMAP Seguridad:
    1. Extract: SISMAPV1DB_SG -> JSON
    2. Transform: Modelos Fuente -> Modelos Destino (Esquemas Seguridad, Noticias)
    3. Load: Modelos Destino -> SISMAP_SEGURIDAD
    """
    
    def __init__(self, conn_fuente, conn_destino):
        self.conn_fuente = conn_fuente
        self.conn_destino = conn_destino
        
        self.fuente = FuenteRepository(conn_fuente) if conn_fuente else None
        self.destino = DestinoRepository(conn_destino) if conn_destino else None
        self.transformer = TransformationService()
        
        self.logger = setup_logger("migracion_seguridad")
        self.stats = MigrationStats()
        
        self.export_dir = Path(f"exports/migracion_seguridad_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
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
        self.logger.info("INICIANDO EXTRACCIÓN DE DATOS (SISMAPV1DB_SG)")
        archivos = {}
        
        # 1. TipoVencimiento
        try:
            datos = self.fuente.obtener_tipos_vencimiento()
            archivos['tipos_vencimiento'] = self.extraer_a_json('tipos_vencimiento', datos)
            self.stats.registrar_tabla('TipoVencimiento', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo TipoVencimiento: {e}")
            
        # 2. Indicadores (Desde Ibog)
        try:
            datos = self.fuente.obtener_indicadores_ibog()
            archivos['ibog'] = self.extraer_a_json('ibog', datos)
            self.stats.registrar_tabla('Ibog', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo Ibog: {e}")

        # 3. SubIndicadores
        try:
            datos = self.fuente.obtener_sub_indicadores()
            archivos['sub_indicadores'] = self.extraer_a_json('sub_indicadores', datos)
            self.stats.registrar_tabla('SubIndicadores', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo SubIndicadores: {e}")

        # 4. Evidencias
        try:
            datos = self.fuente.obtener_evidencias(sub_indicador_codigos)
            archivos['evidencias_source'] = self.extraer_a_json('evidencias_source', datos)
            self.stats.registrar_tabla('EvidenciasSource', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo Evidencias: {e}")
            
        # 5. Puntuaciones (CargaEvidencia)
        try:
            datos = self.fuente.obtener_puntuaciones(sub_indicador_codigos)
            archivos['puntuaciones'] = self.extraer_a_json('puntuaciones', datos)
            self.stats.registrar_tabla('Puntuaciones', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo Puntuaciones: {e}")
            
        # 6. Revisiones (RepositorioDeEnvio)
        try:
            datos = self.fuente.obtener_revisiones(sub_indicador_codigos)
            archivos['revisiones'] = self.extraer_a_json('revisiones', datos)
            self.stats.registrar_tabla('Revisiones', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo Revisiones: {e}")

        # 7. Noticias
        try:
            datos = self.fuente.obtener_noticias()
            archivos['noticias'] = self.extraer_a_json('noticias', datos)
            self.stats.registrar_tabla('Noticias', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo Noticias: {e}")
                
        return archivos

    # ============================================================
    # PASO 2 & 3: TRANSFORMACIÓN Y CARGA (T + L)
    # ============================================================

    def cargar_desde_json(self, archivo: str, entity_class) -> List[Any]:
        if not archivo or not Path(archivo).exists():
            return []
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        if hasattr(entity_class, 'from_dict'):
            return [entity_class.from_dict(item) for item in datos]
        return [entity_class(**item) for item in datos]

    def cargar_todo(self, archivos: Dict[str, str], limpiar_antes: bool = False, puntuador_id: str = None) -> bool:
        self.logger.info("INICIANDO TRANSFORMACIÓN Y CARGA EN SISMAP_SEGURIDAD")
        
        try:
            if limpiar_antes:
                self.logger.info("Limpiando tablas destino en esquema Seguridad, Bitacora y Auditoria...")
                self.destino.limpiar_bitacora_historicos()
                self.destino.limpiar_auditoria_tickets()
                self.destino.limpiar_respuestas_revision()
                self.destino.limpiar_preguntas_revision()
                self.destino.limpiar_comentario_revision()
                self.destino.limpiar_revision_evidencias()
                self.destino.limpiar_puntuacion()
                self.destino.limpiar_archivos()
                self.destino.limpiar_sub_indicador_evidencias()
                self.destino.limpiar_fecha_vencimiento_evidencias()
                self.destino.limpiar_evidencias()
                self.destino.limpiar_sub_indicadores()
                self.destino.limpiar_indicadores()

            # Asegurar catalogos por defecto
            self.destino.asegurar_catalogos_defecto()
            existing_file_ids = self.destino.obtener_ids_archivos_existentes()
            valid_users = self.destino.obtener_usuarios_existentes()
            fallback_user_guid = self.destino.obtener_primer_usuario_id()
            if fallback_user_guid:
                self.logger.info(f"Usuario por defecto para asignaciones: {fallback_user_guid}")
            
            # 1. TipoVencimiento
            if archivos.get('tipos_vencimiento'):
                source_data = self.cargar_desde_json(archivos['tipos_vencimiento'], TipoVencimiento)
                transformed_data = self.transformer.transformar_tipo_vencimiento(source_data)
                
                self.destino.habilitar_identity_insert('Seguridad', 'TiposVencimiento')
                count = self.destino.insertar_tipos_vencimiento(transformed_data)
                self.destino.deshabilitar_identity_insert('Seguridad', 'TiposVencimiento')
                
                self.logger.info(f"Seguridad.TiposVencimiento: {count} insertados")
            
            # 2. Indicadores (De Ibog)
            if archivos.get('ibog'):
                source_data = self.cargar_desde_json(archivos['ibog'], Ibog)
                transformed_data = self.transformer.transformar_indicador(source_data)
                
                self.destino.habilitar_identity_insert('Seguridad', 'Indicadores')
                count = self.destino.insertar_indicadores(transformed_data)
                self.destino.deshabilitar_identity_insert('Seguridad', 'Indicadores')
                
                self.logger.info(f"Seguridad.Indicadores: {count} insertados")
            
            # 3. SubIndicadores
            if archivos.get('sub_indicadores'):
                source_data = self.cargar_desde_json(archivos['sub_indicadores'], SubIndicador)
                transformed_data = self.transformer.transformar_sub_indicador(source_data)
                
                self.destino.habilitar_identity_insert('Seguridad', 'SubIndicadores')
                count = self.destino.insertar_sub_indicadores(transformed_data)
                self.destino.deshabilitar_identity_insert('Seguridad', 'SubIndicadores')
                
                self.logger.info(f"Seguridad.SubIndicadores: {count} insertados")

            # 4. Evidencias
            if archivos.get('evidencias_source'):
                source_data = self.cargar_desde_json(archivos['evidencias_source'], EvidenciaSource)
                evidencias, fechas, sub_evidencias = self.transformer.transformar_evidencia(source_data)
                
                self.destino.habilitar_identity_insert('Seguridad', 'Evidencias')
                self.destino.deshabilitar_constraint('Seguridad', 'Evidencias', 'FK_Evidencias_Evidencias_PreRequisitoId')
                c1 = self.destino.insertar_evidencias(evidencias)
                self.destino.habilitar_constraint('Seguridad', 'Evidencias', 'FK_Evidencias_Evidencias_PreRequisitoId')
                self.destino.deshabilitar_identity_insert('Seguridad', 'Evidencias')
                
                self.logger.info(f"Seguridad.Evidencias: {c1} insertadas")
                
                self.destino.habilitar_identity_insert('Seguridad', 'FechasVencimientoSubIndicadorEvidencia')
                c2 = self.destino.insertar_fecha_vencimiento_evidencias(fechas)
                self.destino.deshabilitar_identity_insert('Seguridad', 'FechasVencimientoSubIndicadorEvidencia')
                
                self.logger.info(f"Seguridad.FechasVencimientoSubIndicadorEvidencia: {c2} insertadas")
                
                self.destino.habilitar_identity_insert('Seguridad', 'SubIndicadorEvidencias')
                c3 = self.destino.insertar_sub_indicador_evidencias(sub_evidencias)
                self.destino.deshabilitar_identity_insert('Seguridad', 'SubIndicadorEvidencias')
                
                self.logger.info(f"Seguridad.SubIndicadorEvidencias: {c3} insertadas")

            # 5. Puntuaciones y Archivos
            if archivos.get('puntuaciones'):
                source_data = self.cargar_desde_json(archivos['puntuaciones'], CargaEvidenciaSource)
                scores, user_files = self.transformer.transformar_puntuacion(
                    source_data, start_file_id=1, puntuador_id=puntuador_id, 
                    existing_file_ids=existing_file_ids, valid_users=valid_users, 
                    fallback_user_guid=fallback_user_guid
                )
                
                if user_files:
                    self.destino.habilitar_identity_insert('Seguridad', 'Archivos')
                    c_uf = self.destino.insertar_archivos(user_files)
                    self.destino.deshabilitar_identity_insert('Seguridad', 'Archivos')
                    self.logger.info(f"Seguridad.Archivos: {c_uf} insertados")
                
                if scores:
                    self.destino.habilitar_identity_insert('Seguridad', 'Puntuaciones')
                    count = self.destino.insertar_puntuacion(scores)
                    self.destino.deshabilitar_identity_insert('Seguridad', 'Puntuaciones')
                    self.logger.info(f"Seguridad.Puntuaciones: {count} insertadas")
                
            # 6. Revisiones
            if archivos.get('revisiones'):
                source_data = self.cargar_desde_json(archivos['revisiones'], RevisionSource)
                revisions, comments = self.transformer.transformar_revision(
                    source_data, valid_users=valid_users, fallback_user_guid=fallback_user_guid
                )
                
                if revisions:
                    self.destino.habilitar_identity_insert('Seguridad', 'RevisionesEvidencia')
                    c_rev = self.destino.insertar_revision_evidencias(revisions)
                    self.destino.deshabilitar_identity_insert('Seguridad', 'RevisionesEvidencia')
                    self.logger.info(f"Seguridad.RevisionesEvidencia: {c_rev} insertadas")
                
                if comments:
                    self.destino.habilitar_identity_insert('Seguridad', 'ComentariosRevisionEvidencia')
                    c_com = self.destino.insertar_comentario_revision(comments)
                    self.destino.deshabilitar_identity_insert('Seguridad', 'ComentariosRevisionEvidencia')
                    self.logger.info(f"Seguridad.ComentariosRevisionEvidencia: {c_com} insertados")

            # 7. Noticias
            if archivos.get('noticias'):
                source_data = self.cargar_desde_json(archivos['noticias'], NoticiaSource)
                noticias = self.transformer.transformar_noticia(source_data)
                
                if noticias:
                    self.destino.habilitar_identity_insert('Noticias', 'Noticia')
                    c_not = self.destino.insertar_noticias(noticias)
                    self.destino.deshabilitar_identity_insert('Noticias', 'Noticia')
                    self.logger.info(f"Noticias.Noticia: {c_not} insertadas")

            # 8. Reconstruir caché si existen stored procedures
            self.reconstruir_cache()

            self.conn_destino.commit()
            self.logger.info("✓ MIGRACIÓN SISMAP SEGURIDAD EXITOSA")
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
            input("\nPresione Enter para cargar a destino SISMAP_SEGURIDAD (Ctrl+C para cancelar)...")
        
        return self.cargar_todo(archivos, limpiar_antes, puntuador_id)

    def solo_extraer(self) -> Dict[str, str]:
        self.extraer_todo()
        print(f"\n✓ Datos extraídos en: {self.export_dir}")
        return {}

    def solo_cargar(self, carpeta_export: str, limpiar_antes: bool = False) -> bool:
        export_path = Path(carpeta_export)
        archivos = {
            'tipos_vencimiento': str(export_path / 'tipos_vencimiento.json'),
            'ibog': str(export_path / 'ibog.json'),
            'sub_indicadores': str(export_path / 'sub_indicadores.json'),
            'evidencias_source': str(export_path / 'evidencias_source.json'),
            'puntuaciones': str(export_path / 'puntuaciones.json'),
            'revisiones': str(export_path / 'revisiones.json'),
            'noticias': str(export_path / 'noticias.json'),
        }
        return self.cargar_todo(archivos, limpiar_antes)

    def reconstruir_cache(self):
        cursor = self.conn_destino.cursor()
        orig_autocommit = self.conn_destino.autocommit
        self.conn_destino.autocommit = True
        
        try:
            self.logger.info("Ejecutando Stored Procedures de Caché y Ranking...")
            
            # 1. Ranking SubIndicador
            try:
                self.logger.info("Ejecutando Cache.sp_ActualizarRankingSubIndicador...")
                cursor.execute("EXEC Cache.sp_ActualizarRankingSubIndicador")
            except Exception as e:
                self.logger.warning(f"Aviso en Cache.sp_ActualizarRankingSubIndicador: {e}")
                
            # 2. Ranking Global
            try:
                self.logger.info("Ejecutando Cache.sp_ActualizarRankingGlobal...")
                cursor.execute("EXEC Cache.sp_ActualizarRankingGlobal")
            except Exception as e:
                self.logger.warning(f"Aviso en Cache.sp_ActualizarRankingGlobal: {e}")

            # 3. Procesar Ranking Mensual (Bitacora)
            try:
                self.logger.info("Ejecutando Bitacora.sp_ProcesarRankingMensual...")
                cursor.execute("EXEC Bitacora.sp_ProcesarRankingMensual")
            except Exception as e:
                self.logger.warning(f"Aviso en Bitacora.sp_ProcesarRankingMensual: {e}")

            self.logger.info("Reconstrucción de caché y ranking finalizada con éxito.")
        except Exception as e:
            self.logger.warning(f"Información al actualizar caché: {e}")
        finally:
            self.conn_destino.autocommit = orig_autocommit

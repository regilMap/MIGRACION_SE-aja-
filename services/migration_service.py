import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from repositories.fuente_repo import FuenteRepository
from repositories.destino_repo import DestinoRepository
from services.transformation_service import TransformationService
from models.entities import (
    TipoVencimiento, TiposIndicador, Indicador, Ibog, SubIndicador,
    EvidenciaSource, EvidenciaDest, SubIndicadorEvidencia, FechaVencimientoSubIndicadorEvidencia
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

    def extraer_todo(self) -> Dict[str, str]:
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
        try:
            datos = self.fuente.obtener_tipos_indicador()
            archivos['tipos_indicador'] = self.extraer_a_json('tipos_indicador', datos)
            self.stats.registrar_tabla('TiposIndicador', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo TiposIndicador: {e}")

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

        # 5. Evidencias
        try:
            datos = self.fuente.obtener_evidencias()
            archivos['evidencias_source'] = self.extraer_a_json('evidencias_source', datos)
            self.stats.registrar_tabla('EvidenciasSource', len(datos), 0, True)
        except Exception as e:
            self.logger.error(f"Error extrayendo Evidencias: {e}")

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

    def cargar_todo(self, archivos: Dict[str, str], limpiar_antes: bool = False) -> bool:
        self.logger.info("INICIANDO TRANSFORMACIÓN Y CARGA")
        
        try:
            if limpiar_antes:
                self.logger.info("Limpiando tablas destino...")
                # Order matters for foreign keys
                self.destino.limpiar_sub_indicador_evidencias()
                self.destino.limpiar_fecha_vencimiento_evidencias()
                self.destino.limpiar_evidencias()
                
                self.destino.limpiar_sub_indicadores()
                self.destino.limpiar_indicadores()
                self.destino.limpiar_tipos_indicador()
                self.destino.limpiar_tipos_vencimiento()
            
            # ... (Previous loads remain same) ...
            
            # 1. TipoVencimiento
            if archivos.get('tipos_vencimiento'):
                source_data = self.cargar_desde_json(archivos['tipos_vencimiento'], TipoVencimiento)
                transformed_data = self.transformer.transformar_tipo_vencimiento(source_data)
                
                self.destino.habilitar_identity_insert('Mantenimiento', 'TipoVencimiento')
                count = self.destino.insertar_tipos_vencimiento(transformed_data)
                self.destino.deshabilitar_identity_insert('Mantenimiento', 'TipoVencimiento')
                
                self.logger.info(f"TipoVencimiento: {count} insertados")
            
            # 2. TiposIndicador
            if archivos.get('tipos_indicador'):
                source_data = self.cargar_desde_json(archivos['tipos_indicador'], TiposIndicador)
                transformed_data = self.transformer.transformar_tipo_indicador(source_data)
                
                self.destino.habilitar_identity_insert('Mantenimiento', 'TiposIndicador')
                count = self.destino.insertar_tipos_indicador(transformed_data)
                self.destino.deshabilitar_identity_insert('Mantenimiento', 'TiposIndicador')
                
                self.logger.info(f"TiposIndicador: {count} insertados")
            
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
                evidencias, fechas, sub_evidencias = self.transformer.transformar_evidencia(source_data)
                
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

    def ejecutar_migracion(self, limpiar_antes: bool = False, confirmar: bool = True) -> bool:
        archivos = self.extraer_todo()
        if not any(archivos.values()):
            return False
            
        if confirmar:
            input("\nPresione Enter para cargar a destino (Ctrl+C para cancelar)...")
        
        return self.cargar_todo(archivos, limpiar_antes)

    def solo_extraer(self) -> Dict[str, str]:
        self.extraer_todo()
        print(f"\n✓ Datos extraídos en: {self.export_dir}")
        return {}

    def solo_cargar(self, carpeta_export: str, limpiar_antes: bool = False) -> bool:
        export_path = Path(carpeta_export)
        archivos = {
            'tipos_vencimiento': str(export_path / 'tipos_vencimiento.json'),
            'tipos_indicador': str(export_path / 'tipos_indicador.json'),
            'ibog': str(export_path / 'ibog.json'),
            'sub_indicadores': str(export_path / 'sub_indicadores.json'),
        }
        return self.cargar_todo(archivos, limpiar_antes)

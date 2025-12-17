import logging
from datetime import datetime
from pathlib import Path


def setup_logger(nombre: str = "migracion") -> logging.Logger:
    """Configura logger con salida a consola y archivo"""
    
    # Crear carpeta de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Nombre del archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{nombre}_{timestamp}.log"
    
    # Configurar logger
    logger = logging.getLogger(nombre)
    logger.setLevel(logging.DEBUG)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Handler archivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Agregar handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info(f"Log iniciado: {log_file}")
    
    return logger


class MigrationStats:
    """Estadísticas de migración"""
    
    def __init__(self):
        self.inicio = datetime.now()
        self.tablas = {}
        self.errores = []
    
    def registrar_tabla(self, nombre: str, extraidos: int, insertados: int, exito: bool):
        self.tablas[nombre] = {
            'extraidos': extraidos,
            'insertados': insertados,
            'exito': exito
        }
    
    def registrar_error(self, tabla: str, error: str):
        self.errores.append({
            'tabla': tabla,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
    
    def resumen(self) -> str:
        duracion = datetime.now() - self.inicio
        
        lineas = [
            "",
            "=" * 50,
            "RESUMEN DE MIGRACIÓN",
            "=" * 50,
            f"Duración: {duracion}",
            f"Tablas procesadas: {len(self.tablas)}",
            ""
        ]
        
        for tabla, stats in self.tablas.items():
            estado = "✓" if stats['exito'] else "✗"
            lineas.append(f"  {estado} {tabla}: {stats['extraidos']} → {stats['insertados']}")
        
        if self.errores:
            lineas.append("")
            lineas.append("ERRORES:")
            for err in self.errores:
                lineas.append(f"  - [{err['tabla']}] {err['error']}")
        
        lineas.append("=" * 50)
        
        return "\n".join(lineas)

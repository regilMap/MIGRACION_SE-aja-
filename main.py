#!/usr/bin/env python3
"""
Migración de datos: SISMAPV1DB_ED → SISMAP_EDUCACION_M

Uso:
    python main.py                    # Migración completa (extrae + carga)
    python main.py --solo-extraer     # Solo extrae a JSON
    python main.py --solo-cargar DIR  # Solo carga desde carpeta existente
    python main.py --limpiar          # Limpia tablas destino antes de cargar
"""

import sys
import argparse
from config.database import conectar_fuente, conectar_destino
from services.migration_service import MigrationService


def main():
    # Argumentos
    parser = argparse.ArgumentParser(description='Migración de base de datos')
    parser.add_argument('--solo-extraer', action='store_true', 
                        help='Solo extrae datos a JSON sin cargar')
    parser.add_argument('--solo-cargar', type=str, metavar='CARPETA',
                        help='Carga desde una carpeta de exportación existente')
    parser.add_argument('--limpiar', action='store_true',
                        help='Limpia tablas destino antes de cargar')
    parser.add_argument('--sin-confirmar', action='store_true',
                        help='No pide confirmación antes de cargar')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  MIGRACIÓN: SISMAPV1DB_ED → SISMAP_EDUCACION_M")
    print("=" * 60)
    
    # Conectar
    conn_fuente = None
    conn_destino = None
    
    # Solo cargar no necesita conexión fuente
    if not args.solo_cargar:
        conn_fuente = conectar_fuente()
        if not conn_fuente:
            print("✗ No se pudo conectar a BD FUENTE")
            return 1
    
    # Solo extraer no necesita conexión destino
    if not args.solo_extraer:
        conn_destino = conectar_destino()
        if not conn_destino:
            print("✗ No se pudo conectar a BD DESTINO")
            if conn_fuente:
                conn_fuente.close()
            return 1
    
    try:
        service = MigrationService(conn_fuente, conn_destino)
        
        if args.solo_extraer:
            # Solo extracción
            service.solo_extraer()
            
        elif args.solo_cargar:
            # Solo carga desde carpeta existente
            exito = service.solo_cargar(args.solo_cargar, args.limpiar)
            if not exito:
                return 1
                
        else:
            # Migración completa
            exito = service.ejecutar_migracion(
                limpiar_antes=args.limpiar,
                confirmar=not args.sin_confirmar
            )
            if not exito:
                return 1
        
        print("\n✓ Proceso completado")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n✗ Migración cancelada por el usuario")
        return 1
        
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        return 1
        
    finally:
        if conn_fuente:
            conn_fuente.close()
        if conn_destino:
            conn_destino.close()
        print("Conexiones cerradas")


if __name__ == "__main__":
    sys.exit(main())

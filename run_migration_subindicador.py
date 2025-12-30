import sys
import argparse
from typing import List
from config.database import conectar_fuente, conectar_destino
from services.migration_service import MigrationService

def main():
    parser = argparse.ArgumentParser(description='Ejecutar migracion por sub-indicador.')
    parser.add_argument('--codigos', nargs='+', help='Lista de codigos de sub-indicador (ej: 1.1 1.2)', required=True)
    parser.add_argument('--limpiar', action='store_true', help='Limpiar tablas destino antes de migrar (CUIDADO)')
    
    args = parser.parse_args()
    
    codigos = args.codigos
    print(f"Iniciando migracion para sub-indicadores: {codigos}")
    
    conn_fuente = conectar_fuente()
    conn_destino = conectar_destino()
    
    if not conn_fuente or not conn_destino:
        print("Error al conectar a bases de datos.")
        return

    try:
        # Fetch default user for Puntuacion
        cursor = conn_destino.cursor()
        cursor.execute("SELECT TOP 1 Id FROM Usuario.Usuarios")
        row = cursor.fetchone()
        if not row:
            print("ERROR: No se encontro ningun usuario en DESTINO (Usuario.Usuarios) para asignar scores.")
            return
        puntuador_id = str(row[0])
        print(f"Usando PuntuadorUsuarioId: {puntuador_id}")
        
        service = MigrationService(conn_fuente, conn_destino)
        # Pass codigos to execute
        success = service.ejecutar_migracion(
            sub_indicador_codigos=codigos, 
            limpiar_antes=args.limpiar, 
            confirmar=False,
            puntuador_id=puntuador_id
        )
        
        if success:
            print("Migracion finalizada con EXITO.")
        else:
            print("Migracion finalizada con ERRORES.")
            
    except Exception as e:
        print(f"Error fatal: {e}")
    finally:
        conn_fuente.close()
        conn_destino.close()

if __name__ == "__main__":
    main()

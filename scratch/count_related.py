import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino")
        return
    cursor = conn.cursor()
    try:
        tables = [
            'Mantenimiento.SubIndicadorRequisitos',
            'Mantenimiento.PreRequisitos',
            'Evidencia.RespuestasRevisiones',
            'Evidencia.PreguntaRevisiones',
            'Evidencia.TipoEvaluacion',
            'Mantenimiento.TiposSubIndicador',
            'Mantenimiento.Indicadores',
            'Mantenimiento.TipoVencimiento',
            'Mantenimiento.TipoIndicador'
        ]
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count} rows")
            except Exception as e:
                # Try finding without schema
                name_only = table.split('.')[-1]
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {name_only}")
                    count = cursor.fetchone()[0]
                    print(f"{name_only}: {count} rows")
                except Exception as ex:
                    print(f"Error counting {table}: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

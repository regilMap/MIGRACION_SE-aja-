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
            'Mantenimiento.ConfiguracionOrganismoExcepcion',
            'Evidencia.Archivos',
            'Evidencia.SubIndicadorEvidencias',
            'Evidencia.Evidencias',
            'Evidencia.Puntuacion',
            'Evidencia.RevisionEvidencias',
            'Evidencia.ComentarioRevisionEvidencias',
            'Evidencia.PreguntaRevisiones'
        ]
        
        # We also saw Ticket in FK, let's search where Ticket is
        cursor.execute("""
            SELECT s.name, t.name 
            FROM sys.tables t 
            INNER JOIN sys.schemas s ON t.schema_id = s.schema_id 
            WHERE t.name = 'Ticket'
        """)
        ticket_tables = cursor.fetchall()
        print(f"Ticket tables found: {ticket_tables}")
        for s, t in ticket_tables:
            tables.append(f"{s}.{t}")
            
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count} rows")
            except Exception as e:
                print(f"Error counting {table}: {e}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

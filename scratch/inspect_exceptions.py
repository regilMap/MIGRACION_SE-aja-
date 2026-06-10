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
        cursor.execute("SELECT COUNT(*) FROM Mantenimiento.ConfiguracionOrganismoExcepcion")
        count_ex = cursor.fetchone()[0]
        print(f"Total rows in Mantenimiento.ConfiguracionOrganismoExcepcion: {count_ex}")
        
        cursor.execute("SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'Mantenimiento' AND TABLE_NAME = 'ConfiguracionOrganismoExcepcion'")
        print("Columns in Mantenimiento.ConfiguracionOrganismoExcepcion:")
        for r in cursor.fetchall():
            print(r)
            
        cursor.execute("SELECT DISTINCT ArchivoId FROM Mantenimiento.ConfiguracionOrganismoExcepcion WHERE ArchivoId IS NOT NULL")
        archivo_ids = [r[0] for r in cursor.fetchall()]
        print(f"Distinct ArchivoId in exceptions: {archivo_ids}")
        
        if archivo_ids:
            # Check if these exist in Evidencia.Archivos
            ids_str = ",".join(str(i) for i in archivo_ids)
            cursor.execute(f"SELECT Id, NombreOriginal, CreatedAt FROM Evidencia.Archivos WHERE Id IN ({ids_str})")
            print("Referenced files in Evidencia.Archivos:")
            for r in cursor.fetchall():
                print(r)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar")
        return
    cursor = conn.cursor()
    try:
        # Verify file
        cursor.execute("""
            SELECT Id, CoedomId, SubIndicadorEvidenciaId, NombreOriginal, EstadoArchivoId, TipoAlmacenamiento, DATALENGTH(ArchivoBinario)
            FROM Evidencia.Archivos
            WHERE Id = 20166
        """)
        print("=== VERIFYING EVIDENCE FILE ===")
        file_row = cursor.fetchone()
        if file_row:
            print(f"File ID: {file_row[0]}")
            print(f"CoedomId: {file_row[1]}")
            print(f"SubIndicadorEvidenciaId: {file_row[2]}")
            print(f"NombreOriginal: {file_row[3]}")
            print(f"EstadoArchivoId: {file_row[4]}")
            print(f"TipoAlmacenamiento: {file_row[5]}")
            print(f"Binary length in DB: {file_row[6]} bytes")
        else:
            print("Error: File ID 20166 was not found in Evidencia.Archivos.")

        # Verify exceptions count
        cursor.execute("SELECT COUNT(*) FROM Mantenimiento.ConfiguracionOrganismoExcepcion WHERE ArchivoId = 20166")
        cnt = cursor.fetchone()[0]
        print(f"\n=== VERIFYING EXCEPTIONS ===")
        print(f"Total exceptions referencing file 20166: {cnt}")
        
        # Verify columns and sample rows
        cursor.execute("""
            SELECT TOP 5 Id, CoedomId, TipoEntidadId, EntidadId, Aplica, FechaVencimiento, FechaExtension, TipoVencimientoId, CreatedBy
            FROM Mantenimiento.ConfiguracionOrganismoExcepcion
            WHERE ArchivoId = 20166
        """)
        columns = [column[0] for column in cursor.description]
        print("\nSample Exceptions (first 5):")
        for r in cursor.fetchall():
            print(dict(zip(columns, r)))
            
        # Verify nullability of dates
        cursor.execute("""
            SELECT COUNT(*) FROM Mantenimiento.ConfiguracionOrganismoExcepcion 
            WHERE ArchivoId = 20166 AND (FechaVencimiento IS NOT NULL OR FechaExtension IS NOT NULL)
        """)
        non_null_dates = cursor.fetchone()[0]
        print(f"\nExceptions with non-null FechaVencimiento or FechaExtension: {non_null_dates}")

        # Verify how many exceptions are for Primario vs Secundario
        cursor.execute("""
            SELECT EntidadId, COUNT(*) 
            FROM Mantenimiento.ConfiguracionOrganismoExcepcion 
            WHERE ArchivoId = 20166 
            GROUP BY EntidadId
        """)
        print("\nExceptions count grouped by EntidadId (Sub-indicator):")
        for r in cursor.fetchall():
            # ID 5 is Np 7.01, 6 is Ns 7.02, 43 is Ns 7.01
            sub_id = r[0]
            count = r[1]
            if sub_id == 5:
                label = "Np 7.01 (Primario)"
            elif sub_id == 6:
                label = "Ns 7.02 (Secundario)"
            elif sub_id == 43:
                label = "Ns 7.01 (Secundario)"
            else:
                label = "Otro"
            print(f"  SubIndicator {sub_id} ({label}): {count} exceptions")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

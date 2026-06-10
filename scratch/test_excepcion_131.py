import sys
sys.path.append(r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)')
from config.database import conectar_destino

def test_excepcion_131():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar.")
        return

    try:
        cursor = conn.cursor()
        print("--- QUERY fn_DetalleEvidenciasPorIndicador(1, 25889) ---")
        cursor.execute("SELECT SubIndicadorEvidenciaId, NombreEvidencia, Valor, FechaVencimiento, VerificadoPor, Calificacion, Estado FROM dbo.fn_DetalleEvidenciasPorIndicador(1, 25889)")
        rows = cursor.fetchall()
        for r in rows:
            print(f"SieId: {r[0]} | Name: {r[1][:30]} | Valor: {r[2]} | Vence: {r[3]} | Estado: {r[6]}")

        print("\n--- QUERY ConfiguracionOrganismoExcepcion FOR COEDOM 25889 ---")
        cursor.execute("SELECT * FROM [Mantenimiento].[ConfiguracionOrganismoExcepcion] WHERE CoedomId = 25889")
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        for r in rows:
            print(dict(zip(columns, r)))

        print("\n--- QUERY Archivos FOR COEDOM 25889 AND 1.3.1 (SubIndicadorEvidenciaId = ?) ---")
        # Let's find SubIndicadorEvidenciaId for 1.3.1
        cursor.execute("""
            SELECT sie.Id, e.Nombre, sd.CodigoSubIndicador 
            FROM Evidencia.SubIndicadorEvidencias sie
            INNER JOIN Evidencia.Evidencias e ON e.Id = sie.EvidenciaId
            INNER JOIN Mantenimiento.SubIndicadores sd ON sd.Id = sie.SubIndicadorId
            WHERE sd.Codigo LIKE '01.3%' OR sd.Codigo LIKE '1.3%'
        """)
        sies = cursor.fetchall()
        sie_ids = []
        for s in sies:
            print(f"SieId: {s[0]} | EvName: {s[1]} | Code: {s[2]}")
            sie_ids.append(s[0])

        if sie_ids:
            sie_placeholders = ",".join(str(x) for x in sie_ids)
            cursor.execute(f"SELECT Id, SubIndicadorEvidenciaId, NombreOriginal, EstadoArchivoId, IsActive, IsDeleted FROM Evidencia.Archivos WHERE CoedomId = 25889 AND SubIndicadorEvidenciaId IN ({sie_placeholders})")
            archs = cursor.fetchall()
            print("\nArchivos encontrados:")
            for a in archs:
                print(f"ArchId: {a[0]} | SieId: {a[1]} | File: {a[2]} | EstadoId: {a[3]} | Active: {a[4]} | Deleted: {a[5]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_excepcion_131()

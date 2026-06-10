import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return
    cursor = conn.cursor()
    try:
        # Check files count for both CoedomIds
        for coedom in [26706, 26034]:
            print(f"\n--- Checking CoedomId {coedom} ---")
            
            # 1. Count of files in Evidencia.Archivos
            cursor.execute("SELECT COUNT(*) FROM Evidencia.Archivos WHERE CoedomId = ?", (coedom,))
            archivos_count = cursor.fetchone()[0]
            print(f"Total files in Evidencia.Archivos: {archivos_count}")
            
            if archivos_count > 0:
                # Group files by state name
                cursor.execute("""
                    SELECT ea.Nombre, COUNT(*) 
                    FROM Evidencia.Archivos a
                    INNER JOIN Mantenimiento.EstadoArchivos ea ON a.EstadoArchivoId = ea.Id
                    WHERE a.CoedomId = ?
                    GROUP BY ea.Nombre
                """, (coedom,))
                print("Files by status:")
                for row in cursor.fetchall():
                    print(f"  Status '{row[0]}': {row[1]}")
                
                # Check if there are any scores (Puntuacion) associated with these files
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM Evidencia.Puntuacion p
                    INNER JOIN Evidencia.Archivos a ON p.ArchivoEvidenciaId = a.Id
                    WHERE a.CoedomId = ?
                """, (coedom,))
                puntuaciones_count = cursor.fetchone()[0]
                print(f"Total ratings (Puntuacion) for these files: {puntuaciones_count}")
                
                if puntuaciones_count > 0:
                    cursor.execute("""
                        SELECT TOP 5 p.Id, p.ArchivoEvidenciaId, p.Calificacion, p.CreatedAt
                        FROM Evidencia.Puntuacion p
                        INNER JOIN Evidencia.Archivos a ON p.ArchivoEvidenciaId = a.Id
                        WHERE a.CoedomId = ?
                    """, (coedom,))
                    print("Sample scores:")
                    for row in cursor.fetchall():
                        print(f"  Id: {row[0]}, ArchivoId: {row[1]}, Calificacion: {row[2]}, CreatedAt: {row[3]}")
            
            # 2. Check if this organism has any records in Cache.ConfiguracionEntidad
            cursor.execute("SELECT COUNT(*) FROM Cache.ConfiguracionEntidad WHERE CoedomId = ?", (coedom,))
            config_count = cursor.fetchone()[0]
            print(f"Total configuration cache records (Cache.ConfiguracionEntidad): {config_count}")

            # 3. Check PesoDistribuidoSubIndicadores_Inline results for IndicadorId = 2
            cursor.execute("SELECT * FROM fn_PesoDistribuidoSubIndicadores_Inline() WHERE IndicadorId = 2 AND CoedomId = ?", (coedom,))
            pesos = cursor.fetchall()
            print(f"fn_PesoDistribuidoSubIndicadores_Inline(2, {coedom}) rows: {len(pesos)}")
            for p in pesos:
                print(f"  {p}")
                
            # 4. Check if the organism exists in the Organismo / Coedom table
            # Let's find out what table defines CoedomId. Let's search for columns.
            cursor.execute("""
                SELECT SCHEMA_NAME(t.schema_id) AS SchemaName, t.name AS TableName
                FROM sys.tables t
                INNER JOIN sys.columns c ON t.object_id = c.object_id
                WHERE c.name LIKE '%CoedomId%'
            """)
            print("Tables containing CoedomId:")
            tables_coedom = cursor.fetchall()
            for t in tables_coedom[:10]:
                print(f"  {t[0]}.{t[1]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

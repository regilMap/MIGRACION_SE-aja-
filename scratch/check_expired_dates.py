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
        # Check files that are currently expired (EstadoArchivoId = 13)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM Evidencia.Archivos 
            WHERE EstadoArchivoId = 13
        """)
        cnt = cursor.fetchone()[0]
        print(f"Total expired files (EstadoArchivoId = 13): {cnt}")
        
        # Check details of some expired files
        cursor.execute("""
            SELECT TOP 10 
                a.Id, 
                a.CoedomId, 
                a.NombreOriginal, 
                a.CreatedAt AS FechaSubida,
                se.FechaVenciento AS FechaVencimientoBase, 
                fv.FechaVencimiento AS FechaVencimientoFv,
                fv.TipoVencimientoId,
                up.FechaPuntuacion
            FROM Evidencia.Archivos a
            INNER JOIN Evidencia.SubIndicadorEvidencias se ON a.SubIndicadorEvidenciaId = se.Id
            LEFT JOIN Evidencia.FechaVencimientoSubIndicadorEvidencias fv ON se.FechaVencimientoSubIndicadorEvidenciaId = fv.Id
            CROSS APPLY (
                SELECT TOP 1 P.CreatedAt AS FechaPuntuacion
                FROM Evidencia.Puntuacion P
                WHERE P.ArchivoEvidenciaId = a.Id
                ORDER BY P.CreatedAt DESC
            ) UP
            WHERE a.EstadoArchivoId = 13
        """)
        columns = [column[0] for column in cursor.description]
        print("\nSample Expired Files (Top 10):")
        for r in cursor.fetchall():
            row_dict = dict(zip(columns, r))
            print(row_dict)
            
        # Get count by TipoVencimientoId
        cursor.execute("""
            SELECT fv.TipoVencimientoId, COUNT(*) 
            FROM Evidencia.Archivos a
            INNER JOIN Evidencia.SubIndicadorEvidencias se ON a.SubIndicadorEvidenciaId = se.Id
            LEFT JOIN Evidencia.FechaVencimientoSubIndicadorEvidencias fv ON se.FechaVencimientoSubIndicadorEvidenciaId = fv.Id
            WHERE a.EstadoArchivoId = 13
            GROUP BY fv.TipoVencimientoId
        """)
        print("\nExpired files count by TipoVencimientoId:")
        for r in cursor.fetchall():
            print(f"  TipoVencimientoId: {r[0]} -> {r[1]} files")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

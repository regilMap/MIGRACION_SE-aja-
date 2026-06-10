import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_fuente, conectar_destino

def main():
    conn_src = conectar_fuente()
    if conn_src:
        cursor_src = conn_src.cursor()
        try:
            print("\n=== SOURCE Puntuaciones for EvidenciaID = 77 ===")
            cursor_src.execute("SELECT TOP 10 * FROM CargaEvidencia WHERE EvidenciaID = 77")
            for r in cursor_src.fetchall():
                print(r)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn_src.close()
            
    conn_dst = conectar_destino()
    if conn_dst:
        cursor_dst = conn_dst.cursor()
        try:
            print("\n=== DESTINO Puntuaciones for EvidenciaID = 77 ===")
            cursor_dst.execute("""
                SELECT TOP 10 p.Id, p.ArchivoEvidenciaId, p.Calificacion, a.CoedomId, a.SubIndicadorEvidenciaId 
                FROM Evidencia.Puntuacion p
                INNER JOIN Evidencia.Archivos a ON p.ArchivoEvidenciaId = a.Id
                INNER JOIN Evidencia.SubIndicadorEvidencias se ON a.SubIndicadorEvidenciaId = se.Id
                WHERE se.EvidenciaId = 77
            """)
            for r in cursor_dst.fetchall():
                print(r)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn_dst.close()

if __name__ == '__main__':
    main()

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
        cursor.execute("""
            SELECT sie.Id, sie.SubIndicadorId, si.Codigo, si.Nombre, sie.EvidenciaId, e.Nombre 
            FROM Evidencia.SubIndicadorEvidencias sie
            INNER JOIN Mantenimiento.SubIndicadores si ON si.Id = sie.SubIndicadorId
            INNER JOIN Evidencia.Evidencias e ON e.Id = sie.EvidenciaId
            WHERE sie.SubIndicadorId IN (5, 6, 43)
        """)
        print("=== SubIndicadorEvidencias for 5, 6, 43 ===")
        for r in cursor.fetchall():
            print(f"SieId: {r[0]} | SubIndId: {r[1]} | SubIndCode: {r[2]} | SubIndName: {r[3][:30]} | EvId: {r[4]} | EvName: {r[5][:30]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

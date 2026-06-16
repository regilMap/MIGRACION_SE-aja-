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
        print("--- SUBINDICATORS FROM DB ---")
        cursor.execute("SELECT Id, Codigo, Nombre FROM Mantenimiento.SubIndicadores ORDER BY Codigo")
        subs = cursor.fetchall()
        for r in subs:
            print(f"Id: {r[0]} | Codigo: {r[1]} | Nombre: {r[2]}")
            
        print("\n--- EVIDENCES FROM DB ---")
        cursor.execute("""
            SELECT e.Id, e.Codigo, e.Nombre, sie.SubIndicadorId, s.Codigo as SubCodigo 
            FROM [Evidencia].[Evidencias] e
            JOIN [Evidencia].[SubIndicadorEvidencias] sie ON e.Id = sie.EvidenciaId
            JOIN Mantenimiento.SubIndicadores s ON sie.SubIndicadorId = s.Id
            WHERE sie.IsActive = 1 AND sie.IsDeleted = 0
            ORDER BY s.Codigo, e.Codigo
        """)
        evs = cursor.fetchall()
        for r in evs:
            print(f"Id: {r[0]} | Code: {r[1]} | Name: {r[2]} | SubId: {r[3]} | SubCode: {r[4]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

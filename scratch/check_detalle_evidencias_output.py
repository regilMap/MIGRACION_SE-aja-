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
        coedom_id = 26772
        cursor.execute("SELECT IndicadorId, Nombre FROM Mantenimiento.SubIndicadores WHERE Id = 5")
        sub_row = cursor.fetchone()
        if not sub_row:
            print("SubIndicador 5 no existe.")
            return
        indicador_id = sub_row[0]
        print(f"SubIndicador 5 belongs to IndicadorId: {indicador_id} ({sub_row[1]})")
        
        print(f"=== fn_DetalleEvidenciasPorIndicador({indicador_id}, {coedom_id}) ===")
        cursor.execute("""
            SELECT SubIndicadorId, SubIndicadorEvidenciaId, NombreEvidencia, Valor, FechaVencimiento, Estado
            FROM dbo.fn_DetalleEvidenciasPorIndicador(?, ?)
            WHERE SubIndicadorId = 5
        """, indicador_id, coedom_id)
        for r in cursor.fetchall():
            print(r)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()

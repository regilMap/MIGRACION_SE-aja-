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
        conn.autocommit = True
        
        # 1. Read and apply fn_DetalleEvidenciasPorIndicador_MODIFICADA.sql
        print("Applying fn_DetalleEvidenciasPorIndicador_MODIFICADA.sql...")
        with open("fn_DetalleEvidenciasPorIndicador_MODIFICADA.sql", "r", encoding="utf-8") as f:
            fn_sql = f.read()
            
        try:
            cursor.execute("DROP FUNCTION dbo.fn_DetalleEvidenciasPorIndicador")
            print("Dropped old function.")
        except Exception:
            pass
            
        cursor.execute(fn_sql)
        print("Function dbo.fn_DetalleEvidenciasPorIndicador updated successfully!")
        
        # 2. Check results
        print("\n=== VERIFYING fn_DetalleEvidenciasPorIndicador(1, 25889) ===")
        cursor.execute("""
            SELECT SubIndicadorEvidenciaId, NombreEvidencia, FechaVencimiento, Estado 
            FROM dbo.fn_DetalleEvidenciasPorIndicador(1, 25889)
        """)
        for r in cursor.fetchall():
            print(f"EvidenciaId: {r[0]}, Nombre: {r[1]}, Vencimiento: {r[2]}, Estado: {r[3]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

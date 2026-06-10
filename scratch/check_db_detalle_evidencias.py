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
        cursor.execute("SELECT OBJECT_DEFINITION(OBJECT_ID('dbo.fn_DetalleEvidenciasPorIndicador'))")
        row = cursor.fetchone()
        if row and row[0]:
            print("=== DB FUNCTION DEFINITION ===")
            print(row[0][:1000]) # Print first 1000 chars
            
            # Save to scratch to compare if needed
            with open("scratch/db_fn_DetalleEvidenciasPorIndicador.sql", "w", encoding="utf-8") as f:
                f.write(row[0])
            print("\nSaved full DB definition to scratch/db_fn_DetalleEvidenciasPorIndicador.sql")
        else:
            print("dbo.fn_DetalleEvidenciasPorIndicador not found in DB")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

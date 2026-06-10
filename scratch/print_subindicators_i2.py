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
        print("\n=== Subindicators for IndicadorId 2 (CoedomId 25903) ===")
        cursor.execute("SELECT * FROM fn_DetalleSubIndicadoresPorIndicador(2, 25903) ORDER BY SubIndicadorId")
        columns = [c[0] for c in cursor.description]
        print(", ".join(columns))
        for r in cursor.fetchall():
            print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

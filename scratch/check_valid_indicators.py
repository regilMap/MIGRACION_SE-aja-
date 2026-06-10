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
        cursor.execute("SELECT DISTINCT Id, Codigo, Nombre FROM dbo.fn_IndicadoresValidos_Inline()")
        print("Distinct valid indicators in fn_IndicadoresValidos_Inline():")
        for r in cursor.fetchall():
            print(r)
            
        cursor.execute("SELECT DISTINCT Id, Codigo FROM fn_PesoDistribuidoIndicadores_Inline()")
        print("\nDistinct indicators in fn_PesoDistribuidoIndicadores_Inline():")
        for r in cursor.fetchall():
            print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

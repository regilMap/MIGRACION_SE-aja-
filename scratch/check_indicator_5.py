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
        # Check subindicators of indicator 5
        print("\n=== SubIndicadores of Indicador 5 ===")
        cursor.execute("SELECT Id, IndicadorId, TipoSubIndicadorId, Codigo, Nombre, Peso FROM Mantenimiento.SubIndicadores WHERE IndicadorId = 5")
        for r in cursor.fetchall():
            print(r)
            
        print("\n=== All SubIndicadores related to Code '05' ===")
        cursor.execute("SELECT Id, IndicadorId, TipoSubIndicadorId, Codigo, Nombre, Peso FROM Mantenimiento.SubIndicadores WHERE Codigo LIKE '05%' OR Codigo LIKE '5%'")
        for r in cursor.fetchall():
            print(r)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

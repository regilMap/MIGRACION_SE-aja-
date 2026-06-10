import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_fuente, conectar_destino

def main():
    conn_src = conectar_fuente()
    if conn_src:
        cursor_src = conn_src.cursor()
        try:
            print("\n=== SOURCE (SISMAPV1DB_ED) ===")
            # Look up evidences for sub-indicator 03.3
            # We can find sub-indicators or evidences matching '03.3.1' or related to '03.3'
            cursor_src.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Evidencia'")
            cols = [r[0] for r in cursor_src.fetchall()]
            print(f"Evidencia columns: {cols}")
            
            # Let's search by Codigo in Evidencia or similar
            query = "SELECT * FROM Evidencia WHERE Codigo = '03.3.1' OR Codigo LIKE '03.3%'"
            try:
                cursor_src.execute(query)
                for r in cursor_src.fetchall():
                    print(r)
            except Exception as e:
                print(f"Error querying Evidencia: {e}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn_src.close()
            
    conn_dst = conectar_destino()
    if conn_dst:
        cursor_dst = conn_dst.cursor()
        try:
            print("\n=== DESTINO (SISMAP_EDUCACION_M2) ===")
            cursor_dst.execute("SELECT Id, Codigo, Nombre, Valor FROM Evidencia.Evidencias WHERE Codigo = '03.3.1' OR Codigo LIKE '03.3%'")
            for r in cursor_dst.fetchall():
                print(r)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn_dst.close()

if __name__ == '__main__':
    main()

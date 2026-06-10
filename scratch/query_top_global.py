import sys
sys.path.append(r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)')
from config.database import conectar_destino

def query_top_global():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar.")
        return

    try:
        cursor = conn.cursor()
        print("--- TOP 10 Cache.RankingGlobal ---")
        cursor.execute("""
            SELECT TOP 10 
                CoedomId,
                CodigoMINERD,    
                NombreOrganismo,       
                PuntajeTotal
            FROM [Cache].[RankingGlobal]
            ORDER BY PuntajeTotal DESC
        """)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        for idx, r in enumerate(rows):
            print(f"Index {idx} | {dict(zip(columns, r))}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    query_top_global()

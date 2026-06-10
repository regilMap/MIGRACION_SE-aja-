import sys
sys.path.append(r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)')
from config.database import conectar_destino

def query_ranking_details():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar.")
        return

    try:
        cursor = conn.cursor()
        print("--- TOP 10 Cache.RankingGlobal WITH RANKING COLUMN ---")
        cursor.execute("""
            SELECT TOP 10 
                CoedomId,
                CodigoMINERD,    
                NombreOrganismo,       
                PuntajeTotal,
                Ranking
            FROM [Cache].[RankingGlobal]
            ORDER BY PuntajeTotal DESC
        """)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        for idx, r in enumerate(rows):
            print(f"Index {idx} | {dict(zip(columns, r))}")

        print("\n--- DETALLES DE COMETA DE ESPERANZA (25889) ---")
        cursor.execute("""
            SELECT CoedomId, CodigoMINERD, NombreOrganismo, PuntajeTotal, Ranking
            FROM [Cache].[RankingGlobal]
            WHERE CoedomId = 25889
        """)
        row = cursor.fetchone()
        if row:
            print(dict(zip(columns, row)))
        else:
            print("No se encontró.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    query_ranking_details()

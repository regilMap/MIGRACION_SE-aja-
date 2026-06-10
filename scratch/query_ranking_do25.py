import sys
sys.path.append(r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)')
from config.database import conectar_destino

def query_ranking_do25():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar.")
        return

    try:
        cursor = conn.cursor()
        print("--- QUERY Cache.RankingGlobal JOINED WITH vOrganismosEducacionX FOR CODI_PROV = 'DO-25' ---")
        cursor.execute("""
            SELECT 
                rorg.[CoedomId],
                rorg.[CodigoMINERD],    
                rorg.[NombreOrganismo],       
                rorg.[PuntajeTotal],
                vorg.CodigoProvincia,
                vorg.NombreProvincia,
                vorg.REGIONAL,
                vorg.DISTRITO
            FROM [Cache].[RankingGlobal] rorg 
            INNER JOIN dbo.vOrganismosEducacionX vorg 
                ON vorg.OrganismoID = rorg.CoedomId
            WHERE vorg.Descripcion = 'Escuelas' 
              AND vorg.CodigoProvincia = 'DO-25'
            ORDER BY rorg.[PuntajeTotal] DESC
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
    query_ranking_do25()

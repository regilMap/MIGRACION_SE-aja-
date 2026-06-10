import sys
sys.path.append(r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)')
from config.database import conectar_destino

def query_ranking_provincia():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar.")
        return

    try:
        cursor = conn.cursor()
        print("--- GETTING PROVINCE CODE FOR COEDOM 25889 ---")
        cursor.execute("SELECT CodigoProvincia, Nombre FROM dbo.vOrganismosEducacion WHERE OrganismoID = 25889")
        row = cursor.fetchone()
        if not row:
            print("No se encontró el organismo.")
            return

        cod_prov, name = row
        print(f"CodigoProvincia: {cod_prov} | Nombre: {name}")

        print(f"\n--- QUERY Cache.RankingGlobal FOR PROVINCE {cod_prov} ---")
        cursor.execute("""
            SELECT 
                rorg.[CoedomId],
                rorg.[CodigoMINERD],    
                rorg.[NombreOrganismo],       
                rorg.[PuntajeTotal],
                rorg.[LastUpdated],
                vorg.CodigoProvincia
            FROM [Cache].[RankingGlobal] rorg 
            INNER JOIN dbo.vOrganismosEducacion vorg 
                ON vorg.OrganismoID = rorg.CoedomId
            WHERE vorg.Descripcion = 'Escuelas' 
              AND vorg.CodigoProvincia = ?
            ORDER BY rorg.[PuntajeTotal] DESC
        """, cod_prov)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        for idx, r in enumerate(rows):
            print(f"Index {idx} | {dict(zip(columns, r))}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    query_ranking_provincia()

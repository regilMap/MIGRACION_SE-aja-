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
        # Check mapping for a few rows in SigerdCoedom
        cursor.execute("SELECT TOP 10 REGIONAL, DISTRITO, CODIGO_MINERD, CODIGO_COEDOM, CENTRO FROM dbo.SigerdCoedom")
        sigerd_rows = cursor.fetchall()
        print("=== dbo.SigerdCoedom Samples ===")
        for r in sigerd_rows:
            print(f"Regional: {r[0]} | Distrito: {r[1]} | MinerdCode: {r[2]} | CoedomCode: {r[3]} | Centro: {r[4]}")
            
            # Look up in vOrganismosEducacionX by Codigo_Minerd
            minerd_clean = str(r[2]).strip()
            if minerd_clean.endswith(".0"):
                minerd_clean = minerd_clean[:-2]
            minerd_clean = minerd_clean.zfill(5)
            
            cursor.execute("SELECT OrganismoID, Nombre, Codigo_Minerd FROM dbo.vOrganismosEducacionX WHERE Codigo_Minerd = ? OR Codigo_Minerd = ?", (minerd_clean, r[2]))
            org_rows = cursor.fetchall()
            print(f"  -> Matches in vOrganismosEducacionX for '{minerd_clean}':")
            for org in org_rows:
                print(f"     OrganismoID: {org[0]} | Nombre: {org[1]} | Codigo_Minerd: {org[2]}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

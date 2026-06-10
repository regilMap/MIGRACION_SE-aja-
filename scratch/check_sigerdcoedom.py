import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return
    cursor = conn.cursor()
    try:
        # Check columns of dbo.SigerdCoedom
        cursor.execute("SELECT TOP 1 * FROM dbo.SigerdCoedom")
        columns = [column[0] for column in cursor.description]
        print("Columns in dbo.SigerdCoedom:")
        print(columns)
        
        # Check presence of 26706 and 26034
        for coedom in [26706, 26034]:
            cursor.execute("SELECT COUNT(*) FROM dbo.SigerdCoedom WHERE CODIGO_COEDOM = ?", (coedom,))
            cnt = cursor.fetchone()[0]
            print(f"CoedomId {coedom} count in dbo.SigerdCoedom: {cnt}")
            
            # Check presence in Cache.ConfiguracionEntidad
            cursor.execute("SELECT COUNT(*) FROM Cache.ConfiguracionEntidad WHERE CoedomId = ?", (coedom,))
            cache_cnt = cursor.fetchone()[0]
            print(f"CoedomId {coedom} count in Cache.ConfiguracionEntidad: {cache_cnt}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

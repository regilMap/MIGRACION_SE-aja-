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
        # Enable transactions/autocommit
        conn.autocommit = True

        # 1. Read and apply fn_AvanceSubIndicador_Optimized.sql
        print("Applying fn_AvanceSubIndicador_Optimized.sql...")
        with open("scratch/fn_AvanceSubIndicador_Optimized.sql", "r", encoding="utf-8") as f:
            fn_opt_sql = f.read()
        try:
            cursor.execute("DROP FUNCTION dbo.fn_AvanceSubIndicador_Optimized")
        except Exception:
            pass
        cursor.execute(fn_opt_sql)
        print("Function dbo.fn_AvanceSubIndicador_Optimized updated successfully!")
        
        # 2. Read and apply sp_ActualizarRankingSubIndicador.sql
        print("Applying sp_ActualizarRankingSubIndicador.sql...")
        with open("scratch/sp_ActualizarRankingSubIndicador.sql", "r", encoding="utf-8") as f:
            sp_sql = f.read()
        try:
            cursor.execute("DROP PROCEDURE Cache.sp_ActualizarRankingSubIndicador")
        except Exception:
            pass
        cursor.execute(sp_sql)
        print("Stored procedure Cache.sp_ActualizarRankingSubIndicador updated successfully!")

        # 3. Read and apply fn_RankingSubIndicadoresV2_Inline.sql
        print("Applying fn_RankingSubIndicadoresV2_Inline.sql...")
        with open("scratch/fn_RankingSubIndicadoresV2_Inline.sql", "r", encoding="utf-8") as f:
            fn_sql = f.read()
        try:
            cursor.execute("DROP FUNCTION dbo.fn_RankingSubIndicadoresV2_Inline")
        except Exception:
            pass
        cursor.execute(fn_sql)
        print("Function dbo.fn_RankingSubIndicadoresV2_Inline updated successfully!")

        # 4. Rebuild cache
        print("Executing Cache.sp_ActualizarRankingSubIndicador to rebuild cache...")
        cursor.execute("EXEC Cache.sp_ActualizarRankingSubIndicador")
        print("Cache rebuilt successfully!")

        # 5. Check results
        print("\n=== STATE COUNTS IN Cache.RankingSubIndicador AFTER UPDATE ===")
        cursor.execute("SELECT Estado, COUNT(*) FROM Cache.RankingSubIndicador GROUP BY Estado")
        for r in cursor.fetchall():
            print(r)
            
        print("\n=== SAMPLE RESULTS FROM fn_RankingSubIndicadores_Inline() ===")
        cursor.execute("SELECT TOP 10 * FROM dbo.fn_RankingSubIndicadores_Inline() ORDER BY NoAplica DESC, InactivoTemporal DESC")
        for r in cursor.fetchall():
            print(r)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

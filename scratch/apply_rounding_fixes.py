import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def run_ddl(cursor, sql, name):
    print(f"\n--- Applying DDL for {name} ---")
    
    # Let's try DROP with logging of errors
    if "FUNCTION" in name.upper():
        try:
            cursor.execute(f"DROP FUNCTION {name}")
            print(f"  Successfully dropped function {name}")
        except Exception as e:
            print(f"  Error dropping function {name}: {e}")
    elif "PROCEDURE" in name.upper():
        try:
            cursor.execute(f"DROP PROCEDURE {name}")
            print(f"  Successfully dropped procedure {name}")
        except Exception as e:
            print(f"  Error dropping procedure {name}: {e}")
            
    # Now run the creation SQL
    try:
        # Replace "CREATE FUNCTION" with "CREATE OR ALTER FUNCTION" to be safe
        # (Though some SQL scripts might have different spacing, using regex to replace is safer)
        sql_to_run = sql
        # Try to execute
        cursor.execute(sql_to_run)
        print(f"  Successfully executed definition for {name}")
        return True
    except Exception as e:
        print(f"  Error executing definition for {name}: {e}")
        return False

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return
    cursor = conn.cursor()
    try:
        conn.autocommit = True
        
        # 1. fn_PesoDistribuidoSubIndicadores_Inline
        path_fn_peso = "scratch/fn_PesoDistribuidoSubIndicadores_Inline.sql"
        with open(path_fn_peso, "r", encoding="utf-8") as f:
            sql_fn_peso = f.read()
        run_ddl(cursor, sql_fn_peso, "dbo.fn_PesoDistribuidoSubIndicadores_Inline")
        
        # 2. fn_DetalleSubIndicadoresPorIndicador
        path_fn_det_sub = "scratch/fn_DetalleSubIndicadoresPorIndicador.sql"
        with open(path_fn_det_sub, "r", encoding="utf-8") as f:
            sql_fn_det_sub = f.read()
        
        # Ensure we use CREATE OR ALTER FUNCTION
        sql_fn_det_sub = re.sub(r"CREATE\s+FUNCTION", "CREATE OR ALTER FUNCTION", sql_fn_det_sub, flags=re.IGNORECASE)
        run_ddl(cursor, sql_fn_det_sub, "dbo.fn_DetalleSubIndicadoresPorIndicador")
        
        # 3. fn_DetalleIndicadoresOrganismo
        path_fn_det_ind = "scratch/fn_DetalleIndicadoresOrganismo.sql"
        with open(path_fn_det_ind, "r", encoding="utf-8") as f:
            sql_fn_det_ind = f.read()
            
        sql_fn_det_ind = re.sub(r"CREATE\s+FUNCTION", "CREATE OR ALTER FUNCTION", sql_fn_det_ind, flags=re.IGNORECASE)
        run_ddl(cursor, sql_fn_det_ind, "dbo.fn_DetalleIndicadoresOrganismo")
        
        # 4. Cache.sp_ActualizarRankingGlobal
        path_sp_global = "sp_ActualizarRankingGlobal.sql"
        with open(path_sp_global, "r", encoding="utf-8") as f:
            sql_sp_global = f.read()
        run_ddl(cursor, sql_sp_global, "Cache.sp_ActualizarRankingGlobal")
        
        # 5. Execute Cache.sp_ActualizarRankingGlobal for 25903
        print("\n--- Executing Cache.sp_ActualizarRankingGlobal for 25903 ---")
        cursor.execute("EXEC Cache.sp_ActualizarRankingGlobal @CoedomId = 25903")
        print("Rebuilt global ranking cache for 25903.")
        
        # 6. Verify outputs from DB
        print("\n=== VERIFICATION: fn_DetalleIndicadoresOrganismo(25903) ===")
        cursor.execute("SELECT * FROM fn_DetalleIndicadoresOrganismo(25903) ORDER BY IndicadorId")
        columns = [c[0] for c in cursor.description]
        print(", ".join(columns))
        for row in cursor.fetchall():
            print(row)
            
    except Exception as e:
        print(f"Error during execution: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

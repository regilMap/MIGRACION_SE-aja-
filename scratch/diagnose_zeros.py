import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def run_query(cursor, query, title):
    print(f"\n==================================================")
    print(f"QUERY: {title}")
    print(f"==================================================")
    try:
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        print(", ".join(columns))
        rows = cursor.fetchall()
        print(f"Total rows: {len(rows)}")
        for r in rows[:10]: # print first 10 rows
            print(r)
        if len(rows) > 10:
            print("...")
    except Exception as e:
        print(f"Error running query: {e}")

def get_definition(cursor, name):
    print(f"\n==================================================")
    print(f"DEFINITION OF {name}")
    print(f"==================================================")
    try:
        cursor.execute(f"SELECT OBJECT_DEFINITION(OBJECT_ID('{name}'))")
        row = cursor.fetchone()
        if row and row[0]:
            print(row[0])
        else:
            # Maybe check in other schemas or system tables
            cursor.execute(f"SELECT OBJECT_DEFINITION(object_id) FROM sys.objects WHERE name = '{name}'")
            row = cursor.fetchone()
            if row and row[0]:
                print(row[0])
            else:
                print("Definition not found via OBJECT_DEFINITION.")
    except Exception as e:
        print(f"Error getting definition: {e}")

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino")
        return
    cursor = conn.cursor()
    try:
        # 1. Search for fn_DetalleIndicadoresOrganismo and other routines
        cursor.execute("""
            SELECT ROUTINE_SCHEMA, ROUTINE_NAME, ROUTINE_TYPE
            FROM INFORMATION_SCHEMA.ROUTINES
            WHERE ROUTINE_NAME LIKE '%DetalleIndicadoresOrganismo%'
               OR ROUTINE_NAME LIKE '%DetalleSubIndicadores%'
               OR ROUTINE_NAME LIKE '%DetalleEvidencias%'
        """)
        print("Matching routines in DB:")
        for r in cursor.fetchall():
            print(r)

        # Get definition of fn_DetalleIndicadoresOrganismo
        get_definition(cursor, 'dbo.fn_DetalleIndicadoresOrganismo')
        get_definition(cursor, 'fn_DetalleIndicadoresOrganismo')

        # Run user's queries
        run_query(cursor, "SELECT * FROM fn_DetalleIndicadoresOrganismo(26706) ORDER BY IndicadorId", "fn_DetalleIndicadoresOrganismo(26706)")
        run_query(cursor, "SELECT * FROM fn_DetalleIndicadoresOrganismo(26034) ORDER BY IndicadorId", "fn_DetalleIndicadoresOrganismo(26034)")
        run_query(cursor, "SELECT * FROM fn_DetalleSubIndicadoresPorIndicador(2, 26706) ORDER BY SubIndicadorId", "fn_DetalleSubIndicadoresPorIndicador(2, 26706)")
        run_query(cursor, "SELECT * FROM fn_DetalleEvidenciasPorIndicador(2, 26706) fnd ORDER BY fnd.SubIndicadorId", "fn_DetalleEvidenciasPorIndicador(2, 26706)")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

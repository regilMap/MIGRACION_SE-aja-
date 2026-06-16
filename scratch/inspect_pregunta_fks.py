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
        # Get all FKs related to PreguntaRevisiones or GrupoPreguntaRevisiones
        cursor.execute("""
            SELECT 
                fk.name AS ForeignKeyName,
                SCHEMA_NAME(tp.schema_id) + '.' + tp.name AS ParentTable,
                cp.name AS ParentColumn,
                SCHEMA_NAME(tr.schema_id) + '.' + tr.name AS ReferencedTable,
                cr.name AS ReferencedColumn
            FROM 
                sys.foreign_keys fk
            INNER JOIN 
                sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
            INNER JOIN 
                sys.tables tp ON fkc.parent_object_id = tp.object_id
            INNER JOIN 
                sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
            INNER JOIN 
                sys.tables tr ON fkc.referenced_object_id = tr.object_id
            INNER JOIN 
                sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
            WHERE
                tp.name LIKE '%Pregunta%' OR tr.name LIKE '%Pregunta%'
        """)
        print("Foreign Keys related to Preguntas:")
        rows = cursor.fetchall()
        for r in rows:
            print(f"FK: {r[0]} | Parent: {r[1]}({r[2]}) -> Ref: {r[3]}({r[4]})")
            
        print("\nChecking row counts for these tables:")
        tables = set()
        for r in rows:
            tables.add(r[1])
            tables.add(r[3])
        for t in sorted(tables):
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {t}")
                count = cursor.fetchone()[0]
                print(f"Table {t}: {count} rows")
            except Exception as ex:
                print(f"Could not count {t}: {ex}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

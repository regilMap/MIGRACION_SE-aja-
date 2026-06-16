import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        return
    cursor = conn.cursor()
    try:
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
                tr.name IN ('GrupoPreguntaRevisiones', 'PreguntaRevisiones', 'RespuestasRevisiones', 'ClasificacionGrupoPreguntaRevisiones')
        """)
        print("Foreign Keys referencing our target tables:")
        for r in cursor.fetchall():
            print(f"FK: {r[0]} | Parent: {r[1]}({r[2]}) -> Ref: {r[3]}({r[4]})")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

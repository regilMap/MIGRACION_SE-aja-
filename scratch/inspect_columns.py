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
        for table in ['Evidencia.GrupoPreguntaRevisiones', 'Evidencia.PreguntaRevisiones']:
            cursor.execute(f"""
                SELECT 
                    c.name AS ColumnName,
                    t.name AS DataType,
                    c.is_nullable AS IsNullable
                FROM 
                    sys.columns c
                INNER JOIN 
                    sys.types t ON c.user_type_id = t.user_type_id
                WHERE 
                    c.object_id = OBJECT_ID(?)
            """, table)
            print(f"\nColumns of {table}:")
            for r in cursor.fetchall():
                print(f"  {r[0]} ({r[1]}) - Nullable: {r[2]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

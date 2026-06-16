import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

conn = conectar_destino()
cur = conn.cursor()

# Find TipoPregunta table
cur.execute("""
    SELECT SCHEMA_NAME(schema_id) + '.' + name 
    FROM sys.tables
    WHERE name LIKE '%TipoPregunta%'
""")
print("Tables with TipoPregunta:", cur.fetchall())

# Try to get all data from TipoPregunta-like tables
for t in ['Evidencia.TipoPregunta', 'Evidencia.TipoPreguntaRevisiones', 'Evidencia.TiposPregunta']:
    try:
        cur.execute(f"SELECT * FROM {t}")
        print(f"\n{t} data:")
        for r in cur.fetchall():
            print(r)
    except Exception as e:
        print(f"  {t}: {e}")

conn.close()

from config.database import conectar_destino

conn = conectar_destino()
cursor = conn.cursor()

cursor.execute("""
    SELECT TABLE_SCHEMA, TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_SCHEMA, TABLE_NAME
""")

tables = cursor.fetchall()

print("\n==================================================")
print("   CONTEO DE TODAS LAS TABLAS EN SISMAP_SEGURIDAD ")
print("==================================================")

for schema, t in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM [{schema}].[{t}]")
        cnt = cursor.fetchone()[0]
        print(f"  [{schema}].[{t}]: {cnt} registros")
    except Exception as e:
        print(f"  [{schema}].[{t}]: Error ({e})")

conn.close()

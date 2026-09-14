from config.database import conectar_fuente

conn = conectar_fuente()
cursor = conn.cursor()

cursor.execute("""
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_NAME
""")

tables = [row[0] for row in cursor.fetchall()]

print("\n==================================================")
print("   CONTEO DE TODAS LAS TABLAS EN SISMAPV1DB_SG   ")
print("==================================================")

non_empty = []
for t in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM [dbo].[{t}]")
        cnt = cursor.fetchone()[0]
        if cnt > 0:
            print(f"  [+] dbo.{t}: {cnt} registros")
            non_empty.append((t, cnt))
        else:
            print(f"      dbo.{t}: 0 registros")
    except Exception as e:
        print(f"  [!] dbo.{t}: Error ({e})")

print("\n--- RESUMEN DE TABLAS CON DATOS ---")
for t, cnt in non_empty:
    print(f"  dbo.{t} -> {cnt}")

conn.close()

from config.database import conectar_fuente

conn = conectar_fuente()
cursor = conn.cursor()

print("\n--- dbo.ArchivoCargaEvidencia ---")
cursor.execute("SELECT * FROM dbo.ArchivoCargaEvidencia")
rows = cursor.fetchall()
cols = [column[0] for column in cursor.description]
print("Columns:", cols)
for r in rows:
    print("Row:", r)

print("\n--- dbo.MensajeEnvio ---")
cursor.execute("SELECT * FROM dbo.MensajeEnvio")
rows = cursor.fetchall()
cols = [column[0] for column in cursor.description]
print("Columns:", cols)
for r in rows:
    print("Row:", r)

print("\n--- dbo.Datos ---")
cursor.execute("SELECT TOP 5 * FROM dbo.Datos")
rows = cursor.fetchall()
cols = [column[0] for column in cursor.description]
print("Columns:", cols)
for r in rows:
    print("Row:", r)

print("\n--- dbo.SubIndicadorOrganismo ---")
cursor.execute("SELECT TOP 5 * FROM dbo.SubIndicadorOrganismo")
rows = cursor.fetchall()
cols = [column[0] for column in cursor.description]
print("Columns:", cols)
for r in rows:
    print("Row:", r)

conn.close()

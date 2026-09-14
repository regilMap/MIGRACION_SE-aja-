from config.database import conectar_fuente

conn = conectar_fuente()
cursor = conn.cursor()

tables = [
    "Ibog", "SubIndicadores", "Evidencia", "CargaEvidencia", 
    "ArchivoCargaEvidencia", "RepositorioDeEnvio", "Noticias"
]

print("\n--- CONTEO DE TABLAS EN SISMAPV1DB_SG ---")
for t in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM dbo.{t}")
        cnt = cursor.fetchone()[0]
        print(f"  dbo.{t}: {cnt} registros")
    except Exception as e:
        print(f"  dbo.{t}: Error ({e})")

conn.close()

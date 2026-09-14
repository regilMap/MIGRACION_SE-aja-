from config.database import conectar_destino

conn = conectar_destino()
cursor = conn.cursor()

tables = [
    ("Seguridad", "TiposVencimiento"),
    ("Seguridad", "Indicadores"),
    ("Seguridad", "SubIndicadores"),
    ("Seguridad", "Evidencias"),
    ("Seguridad", "FechasVencimientoSubIndicadorEvidencia"),
    ("Seguridad", "SubIndicadorEvidencias"),
    ("Seguridad", "Archivos"),
    ("Seguridad", "Puntuaciones"),
    ("Seguridad", "RevisionesEvidencia")
]

print("\n--- CONTEO DE TABLAS EN SISMAP_SEGURIDAD (DESTINO) ---")
for s, t in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {s}.{t}")
        cnt = cursor.fetchone()[0]
        print(f"  {s}.{t}: {cnt} registros")
    except Exception as e:
        print(f"  {s}.{t}: Error ({e})")

conn.close()

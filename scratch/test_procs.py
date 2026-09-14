from config.database import conectar_destino

conn = conectar_destino()
conn.autocommit = True
cursor = conn.cursor()

print("\n--- Ejecutando Cache.sp_ActualizarRankingSubIndicador ---")
try:
    cursor.execute("EXEC Cache.sp_ActualizarRankingSubIndicador")
    print("  [OK] Cache.sp_ActualizarRankingSubIndicador completado")
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n--- Ejecutando Cache.sp_ActualizarRankingGlobal ---")
try:
    cursor.execute("EXEC Cache.sp_ActualizarRankingGlobal")
    print("  [OK] Cache.sp_ActualizarRankingGlobal completado")
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n--- Ejecutando Bitacora.sp_ProcesarRankingMensual ---")
try:
    cursor.execute("EXEC Bitacora.sp_ProcesarRankingMensual")
    print("  [OK] Bitacora.sp_ProcesarRankingMensual completado")
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n--- Verificando conteos en tablas de Ranking/Cache ---")
tables = [
    ("Cache", "RankingGlobal"),
    ("Cache", "RankingSubIndicador"),
    ("Cache", "ConfiguracionEntidad"),
    ("Bitacora", "RankingOrganismosHistorico"),
    ("Bitacora", "RankingIndicadoresHistorico"),
    ("Bitacora", "RankingSubIndicadoresHistorico"),
    ("Bitacora", "RankingEvidenciasHistorico"),
    ("Seguridad", "Periodos")
]

for s, t in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {s}.{t}")
        cnt = cursor.fetchone()[0]
        print(f"  {s}.{t}: {cnt} registros")
    except Exception as e:
        print(f"  {s}.{t}: Error ({e})")

conn.close()

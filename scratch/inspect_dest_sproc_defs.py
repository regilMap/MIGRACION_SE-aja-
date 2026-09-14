from config.database import conectar_destino

conn = conectar_destino()
cursor = conn.cursor()

sprocs = [
    ("Cache", "sp_ActualizarRankingGlobal"),
    ("Cache", "sp_ActualizarRankingSubIndicador"),
    ("Bitacora", "sp_ProcesarRankingMensual"),
    ("dbo", "SP_ActualizarArchivosVencidos")
]

print("\n==================================================")
print("   DEFINICIONES DE STORED PROCEDURES EN DESTINO   ")
print("==================================================")

for schema, name in sprocs:
    print(f"\n--- [{schema}].[{name}] ---")
    try:
        cursor.execute(f"SELECT OBJECT_DEFINITION(OBJECT_ID('{schema}.{name}'))")
        definition = cursor.fetchone()[0]
        if definition:
            print(definition[:1500] + ("\n... (truncado)" if len(definition) > 1500 else ""))
        else:
            print("  No definition found")
    except Exception as e:
        print(f"  Error: {e}")

conn.close()

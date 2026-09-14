from config.database import conectar_fuente
from repositories.fuente_repo import FuenteRepository

conn = conectar_fuente()
repo = FuenteRepository(conn)
evs = repo.obtener_evidencias()

code_counts = {}
for e in evs:
    c = e.Codigo.strip() if e.Codigo else f"EV-{e.EvidenciaID}"
    if c not in code_counts:
        code_counts[c] = []
    code_counts[c].append(e)

print(f"Total evidencias en fuente: {len(evs)}")
for c, group in code_counts.items():
    if len(group) > 1:
        print(f"\nCodigo duplicado '{c}' ({len(group)} registros):")
        for item in group:
            print(f"  EvidenciaID: {item.EvidenciaID}, SubIndicadorID: {item.IndicadorID}, Nombre: {item.NombreArchivo or item.Descipcion}")

conn.close()

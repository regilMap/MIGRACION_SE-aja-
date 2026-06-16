import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino
sys.stdout.reconfigure(encoding='utf-8')

conn = conectar_destino()
cur = conn.cursor()

# Show all migrated PreguntaRevisiones with their evidencia code and valor
cur.execute("""
    SELECT 
        e.Codigo AS EvCod,
        pr.ValorPorcentual,
        LEFT(pr.TextoPregunta, 80) AS Texto
    FROM Evidencia.PreguntaRevisiones pr
    LEFT JOIN Evidencia.SubIndicadorEvidencias sie ON pr.SubIndicadorEvidenciaId = sie.Id
    LEFT JOIN Evidencia.Evidencias e ON sie.EvidenciaId = e.Id
    WHERE pr.CreatedBy = 'MIGRATION'
    ORDER BY e.Codigo, pr.Id
""")
rows = cur.fetchall()
print(f"Total migrated: {len(rows)}")
print()
prev = None
for cod, pct, texto in rows:
    if cod != prev:
        print(f"=== {cod} ===")
        prev = cod
    print(f"  Pct={pct} | {texto}")

conn.close()

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_fuente, conectar_destino
sys.stdout.reconfigure(encoding='utf-8')

print("=== SOURCE DB: All evidencias for sub-indicator 1.05 ===")
conn_f = conectar_fuente()
cur_f = conn_f.cursor()

# First check columns
cur_f.execute("SELECT TOP 1 * FROM dbo.Evidencia")
cols = [d[0] for d in cur_f.description]
print("Evidencia columns:", cols)

cur_f.execute("SELECT TOP 1 * FROM dbo.SubIndicadores")
cols2 = [d[0] for d in cur_f.description]
print("SubIndicadores columns:", cols2)

# Find evidencias for 1.05
cur_f.execute("""
    SELECT e.EvidenciaID, e.Codigo, e.NombreArchivo
    FROM dbo.Evidencia e
    JOIN dbo.SubIndicadores si ON e.IndicadorID = si.IndicadorID
    WHERE si.Codigo = '1.05'
    ORDER BY e.Codigo
""")
print("\nEvidencias for 1.05:")
for r in cur_f.fetchall():
    print(r)
conn_f.close()

print("\n=== DEST DB: SubIndicadorEvidencias for 1.05.x ===")
conn_d = conectar_destino()
cur_d = conn_d.cursor()
cur_d.execute("""
    SELECT se.Id, e.Id AS EvidId, e.Codigo, LEFT(e.Nombre, 60) AS Nombre
    FROM Evidencia.SubIndicadorEvidencias se
    JOIN Evidencia.Evidencias e ON se.EvidenciaId = e.Id
    WHERE e.Codigo LIKE '1.05%'
    ORDER BY e.Codigo
""")
print("SubIndicadorEvidencias for 1.05:")
for r in cur_d.fetchall():
    print(r)
conn_d.close()

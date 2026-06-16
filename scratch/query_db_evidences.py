import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.database import conectar_destino
    conn = conectar_destino()
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Codigo, Nombre, Descripcion, Valor FROM [Evidencia].[Evidencias] ORDER BY Codigo")
    rows = cursor.fetchall()
    
    output_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\db_evidencias_truth.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Total evidences in DB: {len(rows)}\n\n")
        for r in rows:
            f.write(f"Id: {r[0]} | Code: {r[1]} | Name: {r[2]} | Val: {r[4]}\n")
            
    print(f"Successfully dumped {len(rows)} evidences to db_evidencias_truth.txt")
except Exception as e:
    import traceback
    traceback.print_exc()

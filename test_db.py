import pandas as pd

try:
    from config.database import conectar_destino
    conn = conectar_destino()
    cursor = conn.cursor()
    cursor.execute("SELECT OrganismoID, Nombre, Codigo_Minerd FROM SISMAP_EDUCACION_M2.dbo.vOrganismosEducacionX WHERE Nombre LIKE '%Neiba%' OR Nombre LIKE '%Higuey%' OR Nombre LIKE '%Higüey%' OR Nombre LIKE '%Macorís Sur%' OR Nombre LIKE '%Macoris Sur%' OR Nombre LIKE '%Macorís Nor%' OR Nombre LIKE '%Macoris Nor%' OR Nombre LIKE '%Bisono%' OR Nombre LIKE '%Bisonó%' OR Nombre LIKE '%Sosua%' OR Nombre LIKE '%Sosúa%'")
    organismos = cursor.fetchall()
    print("MATCHES:")
    for o in organismos:
        print(f"{o[2]} | {o[1]} | {o[0]}")
except Exception as e:
    print(e)

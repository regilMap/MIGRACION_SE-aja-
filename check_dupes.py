import pyodbc

try:
    from config.database import conectar_destino
    conn = conectar_destino()
    cursor = conn.cursor()
    
    print("Buscando duplicados por correo...")
    cursor.execute("SELECT Correo, COUNT(*) FROM Usuario.Usuarios GROUP BY Correo HAVING COUNT(*) > 1")
    dupes = cursor.fetchall()
    
    if not dupes:
        print("No se encontraron correos duplicados.")
    else:
        print(f"Se encontraron {len(dupes)} correos con duplicados:")
        for d in dupes:
            print(f"Correo: {d[0]} | Cantidad: {d[1]}")
            
except Exception as e:
    print(e)

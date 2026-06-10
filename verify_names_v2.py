import pyodbc

try:
    from config.database import conectar_destino
    conn = conectar_destino()
    cursor = conn.cursor()
    
    print("--- Verificación de Nombres sin Prefijos ---")
    # Nombres que originalmente tenían Sr./Sra. en el Excel
    originales = ['Neuris Ramírez', 'Nina Almonte', 'Esmedin Eulogio Feliz Báez', 'Pilades Alberto Pérez Filpo', 'Samuel Guzmán Reyes']
    
    for full_name in originales:
        first_name = full_name.split(' ')[0]
        cursor.execute(f"SELECT Nombre, Apellido FROM Usuario.Usuarios WHERE Nombre = '{first_name}'")
        row = cursor.fetchone()
        if row:
            print(f"Original Excel: {full_name} -> DB (Limpio): {row[0]} {row[1]}")
    
    print("\n--- Buscando cualquier nombre que todavía tenga 'Sr' ---")
    cursor.execute("SELECT Nombre FROM Usuario.Usuarios WHERE Nombre LIKE 'Sr%' OR Nombre LIKE 'Sra%'")
    rows = cursor.fetchall()
    if not rows:
        print("No se encontraron nombres con 'Sr.' o 'Sra.' en la base de datos. ¡Todo está limpio!")
    else:
        for r in rows:
            print(f"Encontrado: {r[0]}")
            
except Exception as e:
    print(e)

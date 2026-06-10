import pyodbc

try:
    from config.database import conectar_destino
    conn = conectar_destino()
    cursor = conn.cursor()
    
    print("Verificando nombres en la base de datos...")
    # Buscamos algunos nombres que sabemos tenían Sr. o Sra. en el Excel
    nombres_a_buscar = ['Neuris%', 'Nina%', 'Esmedin%', 'Pilades%', 'Samuel%']
    
    for nombre in nombres_a_buscar:
        cursor.execute(f"SELECT Nombre, Apellido, Correo FROM Usuario.Usuarios WHERE Nombre LIKE '{nombre}'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"DB -> Nombre: {row[0]} | Apellido: {row[1]} | Correo: {row[2]}")
            
except Exception as e:
    print(f"Error: {e}")

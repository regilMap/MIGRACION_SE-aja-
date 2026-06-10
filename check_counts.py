import pyodbc

try:
    from config.database import conectar_destino
    conn = conectar_destino()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Usuario.Usuarios")
    u_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Usuario.UsuarioClaves")
    c_count = cursor.fetchone()[0]
    
    print(f"Balanse Global:")
    print(f"Usuarios: {u_count}")
    print(f"Claves: {c_count}")
    
    print("\n--- Listado de los primeros 5 usuarios ---")
    cursor.execute("SELECT TOP 5 Id, Correo, CreatedAt FROM Usuario.Usuarios ORDER BY CreatedAt DESC")
    for r in cursor.fetchall():
        print(r)
            
except Exception as e:
    print(e)

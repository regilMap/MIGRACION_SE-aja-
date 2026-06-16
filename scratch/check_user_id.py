import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar")
        return
    cursor = conn.cursor()
    try:
        user_id = '4011D474-7472-4FC4-9EE0-0C9B23AF1B17'
        cursor.execute("SELECT Id, Correo, Nombre, Apellido FROM Usuario.Usuarios WHERE Id = ?", user_id)
        row = cursor.fetchone()
        if row:
            print(f"User {user_id} found: Correo: {row[1]}, Nombre: {row[2]}, Apellido: {row[3]}")
        else:
            print(f"User {user_id} NOT found in Usuario.Usuarios.")
            
            # Find the user used in ConfiguracionGeneral as fallback
            cursor.execute("SELECT DISTINCT UsuarioConfiguracionId FROM Mantenimiento.ConfiguracionGeneral")
            print("Users in ConfiguracionGeneral:")
            for r in cursor.fetchall():
                print(r)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

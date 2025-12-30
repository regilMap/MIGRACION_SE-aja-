import pyodbc
import uuid
from datetime import datetime
from config.database import conectar_destino

def create_user():
    conn = conectar_destino()
    if not conn:
        return

    cursor = conn.cursor()
    try:
        # 1. Get Role
        cursor.execute("SELECT TOP 1 Id FROM Mantenimiento.Rol")
        rol_id = cursor.fetchone()[0]

        # 2. Get Cargo
        cursor.execute("SELECT TOP 1 Id FROM Mantenimiento.Cargo")
        cargo_id = cursor.fetchone()[0]

        # 3. Create Clave
        clave_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO Usuario.UsuarioClaves (Id, ClaveHasheada, CambioClave, CreatedAt, IsActive, IsDeleted)
            VALUES (?, 'HASH_DUMMY', 0, GETDATE(), 1, 0)
        """, clave_id)

        # 4. Create User
        user_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO Usuario.Usuarios 
            (Id, Nombre, Apellido, Genero, Telefono, Direccion, Correo, ClaveId, CargoId, RolId, CoedomId, CreatedAt, CreatedBy, IsActive, IsDeleted)
            VALUES (?, 'Migration', 'Admin', 1, '8090000000', 'Address', 'admin@migration.com', ?, ?, ?, 0, GETDATE(), 'MigrationScript', 1, 0)
        """, user_id, clave_id, cargo_id, rol_id)

        conn.commit()
        print(f"CREATED USER ID: {user_id}")
    
    except Exception as e:
        conn.rollback()
        print(f"Error creating user: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_user()

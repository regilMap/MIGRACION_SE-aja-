import pyodbc
import uuid
from datetime import datetime
from config.database import conectar_destino

def create_users():
    conn = conectar_destino()
    if not conn:
        return

    cursor = conn.cursor()
    
    # Common Cargo ID (assuming 1 for all based on input, or varying if specified)
    # Most users use CargoId 1.
    cursor.execute("SELECT TOP 1 Id FROM Mantenimiento.Cargo")
    default_cargo_id = cursor.fetchone()[0]

    # Users Data To Insert
    users_to_create = [
        {
            "id": "01K5HN14K8Y1WDAYY7CSZVHAWD", 
            "clave_hash": "$2b$10$FpamHWTWVKFmlstvwB/sN.t9.tPwrL8XOG5bvQ/wVIFIEejLAuU82",
            "nombre": "Admin", "apellido": "SISMAP", "genero": 0,
            "telefono": "809-111-0001", "direccion": "Oficina Regional 16",
            "correo": "admin.sismap@educacion.gob.do", 
            "rol_id": 1, "cargo_id": 1, "coedom_id": 98
        },
        {
            "id": "01KDT8CP5VEV0B9HQPQ8PHSZNS", 
            "clave_hash": "$2b$10$AsUgbRAlrBJ5POLXy2wzxe6mb822rNsTz4FIwTY7TfrBu0vJk.39u",
            "nombre": "Usuario Final Pruebas", "apellido": "Usuario Final Pruebas", "genero": 0,
            "telefono": "+18000000000", "direccion": "Ninguna direccion",
            "correo": "usuario.final@educacion.gob.do",
            "rol_id": 4, "cargo_id": 1, "coedom_id": 25231
        },
        {
            "id": "01KEYSWWXJCRAPWZJ7BJEN96CB",
            "clave_hash": "$2b$10$hQHZB4ZSIRi3y7WnlA.xbOLUyQIBebKVLTw/13ufW4TFmgoFINW7y",
            "nombre": "Usuario Final Pruebas 2", "apellido": "Usuario Final Pruebas 2", "genero": 1,
            "telefono": "+18000000000", "direccion": "n/a",
            "correo": "usuario.final.2@educacion.gob.do",
            "rol_id": 7, "cargo_id": 1, "coedom_id": 26706
        },
        {
            "id": "01KDDTV64CR81MW5Y0B6JAXDZA",
            "clave_hash": "$2b$10$35NOEGCE0o5NcS1PhDW0lOWSOsuolJ3mQfW5Zg9mZUZE64eVsL/92",
            "nombre": "Evaluador", "apellido": "Sebastian", "genero": 0,
            "telefono": "809-343-4302", "direccion": "holachgffghj",
            "correo": "sebastian.test@admin.com",
            "rol_id": 7, "cargo_id": 1, "coedom_id": 25316
        },
        {
            "id": "01KEYT26XB3WKY0BTBXVD30FY8", 
            "clave_hash": "$2b$10$hXEa0XLQk.RrY99QXa0GpO.yL1YxRRmUYm/VvBJzj5G2TpfBsJLlW",
            "nombre": "Usuario Revisor Distrital 1", "apellido": "Usuario Revisor Distrital 1", "genero": 0,
            "telefono": "+18000000000", "direccion": "n/a",
            "correo": "usuario.distrital@educacion.gob.do",
            "rol_id": 4, "cargo_id": 1, "coedom_id": 25254
        },
        {
            "id": "227fecb2-d3c4-44f5-8904-b4a1f296439a",
            "clave_hash": "HASH_DUMMY", # As provided
            "nombre": "Migration", "apellido": "Admin", "genero": 0,
            "telefono": "8090000000", "direccion": "Address",
            "correo": "admin@migration.com",
            "rol_id": 1, "cargo_id": 1, "coedom_id": 0 # Special case
        },
        {
            "id": str(uuid.uuid4()).upper(), # Generated ID
            "clave_hash": "$2b$10$hXEa0XLQk.RrY99QXa0GpO.yL1YxRRmUYm/VvBJzj5G2TpfBsJLlW", # Same as Revisor Distrital 1
            "nombre": "Usuario Puntuador 1", "apellido": "Usuario Puntuador 1", "genero": 1,
            "telefono": "+18000000000", "direccion": "n/a",
            "correo": "usuario.puntuador@educacion.gob.do",
            "rol_id": 2, "cargo_id": 1, "coedom_id": 98
        }
    ]

    try:
        for user_data in users_to_create:
            # Check if user already exists to avoid duplicates/errors if re-run
            cursor.execute("SELECT COUNT(*) FROM Usuario.Usuarios WHERE Correo = ?", user_data["correo"])
            exists = cursor.fetchone()[0]
            
            if exists > 0:
                print(f"User {user_data['correo']} already exists. Skipping.")
                continue

            # 1. Create Clave
            # If ID is provided as ULID-like, use it, else generate UUID?
            # Actually for ClaveId we can just generate a new UUID for each user, 
            # OR we should use the same Logic Key if we want consistency?
            # The input data has User ID. It doesn't explicitly have Clave ID in column 1 of first row, 
            # wait, the first column 01K5... is User.Id.
            # The ClaveId in the input table was 01K5HN14K8Y1WDAYY7CSZVHAWD for the first row? 
            # Looking at the input: 
            # Row 1: 01K5... (Id), $2b$10$... (Hash), ... 
            # The ClaveId column is not explicitly labeled in the comma text, 
            # but in the image or standard schema, Usuario has ClaveId FK.
            # I will generate a new UUID for ClaveId for each insertion to be safe and clean.
            
            clave_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO Usuario.UsuarioClaves (Id, ClaveHasheada, CambioClave, CreatedAt, IsActive, IsDeleted)
                VALUES (?, ?, 0, GETDATE(), 1, 0)
            """, clave_id, user_data['clave_hash'])

            # 2. Create User
            cursor.execute("""
                INSERT INTO Usuario.Usuarios 
                (Id, Nombre, Apellido, Genero, Telefono, Direccion, Correo, ClaveId, CargoId, RolId, CoedomId, CreatedAt, CreatedBy, IsActive, IsDeleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), 'MigrationScript', 1, 0)
            """, user_data['id'], user_data['nombre'], user_data['apellido'], user_data['genero'], 
                 user_data['telefono'], user_data['direccion'], user_data['correo'], 
                 clave_id, user_data['cargo_id'], user_data['rol_id'], user_data['coedom_id'])
            
            print(f"CREATED USER: {user_data['nombre']} ({user_data['correo']}) - ID: {user_data['id']}")

        conn.commit()
    
    except Exception as e:
        conn.rollback()
        print(f"Error creating users: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_users()

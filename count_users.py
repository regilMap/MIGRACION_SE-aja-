import re

with open("output_inserts.sql", "r", encoding="utf-8") as f:
    lines = f.readlines()

users = [line for line in lines if "INSERT INTO Usuario.Usuarios" in line]
print(f"Total Usuarios: {len(users)}")

roles = {
    "Regional (Rol 8)": 0,
    "Distrital/Nacional (Rol 4)": 0,
    "Puntuador (Rol 2)": 0,
    "Seguimiento (Rol 3)": 0
}

for u in users:
    # Look for the pattern of RolId which is the 10th column
    # The columns are: Id, Nombre, Apellido, Genero, Telefono, Direccion, Correo, ClaveId, CargoId, RolId, CoedomId, ...
    # Since they are positional, let's just split by comma but be careful with quotes
    # Actually, simpler: search for " 1, " followed by the role number then a comma
    if ", 8, " in u: roles["Regional (Rol 8)"] += 1
    elif ", 4, " in u: roles["Distrital/Nacional (Rol 4)"] += 1
    elif ", 2, " in u: roles["Puntuador (Rol 2)"] += 1
    elif ", 3, " in u: roles["Seguimiento (Rol 3)"] += 1

for name, count in roles.items():
    print(f"{name}: {count}")

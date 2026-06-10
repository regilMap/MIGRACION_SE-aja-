import sys
import os
sys.path.append(os.getcwd())
from config.database import conectar_destino

def find_user():
    conn = conectar_destino()
    cursor = conn.cursor()
    email = 'gabriela.javier@minerd.gob.do'
    cursor.execute("SELECT Id FROM Usuario.Usuarios WHERE Correo = ?", email)
    row = cursor.fetchone()
    if row:
        print(f"User found: {row[0]}")
    else:
        print("User NOT found in destination.")
    conn.close()

if __name__ == "__main__":
    find_user()

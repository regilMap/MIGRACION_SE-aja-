import sys
import os
sys.path.append(os.getcwd())
from config.database import conectar_fuente

def check_repositorio():
    conn = conectar_fuente()
    cursor = conn.cursor()
    
    filename = '638731018212129457-promocion--de-los-estudiantes-2024-2025-----SISMAP.pdf'
    query = "SELECT * FROM RepositorioDeEnvio WHERE Archivo = ?"
    cursor.execute(query, filename)
    row = cursor.fetchone()
    if row:
        print("FOUND the file in RepositorioDeEnvio!")
        cols = [column[0] for column in cursor.description]
        data = dict(zip(cols, row))
        print(data)
    else:
        print("File NOT FOUND in RepositorioDeEnvio.")
        
    conn.close()

if __name__ == "__main__":
    check_repositorio()

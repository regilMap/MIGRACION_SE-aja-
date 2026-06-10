import sys
import os
sys.path.append(os.getcwd())
from config.database import conectar_destino

def find_discarded_in_dest():
    conn = conectar_destino()
    cursor = conn.cursor()
    
    filename_part = '638731018212129457'
    query = "SELECT * FROM Evidencia.Archivos WHERE NombreOriginal LIKE ?"
    cursor.execute(query, f'%{filename_part}%')
    row = cursor.fetchone()
    if row:
        print("FOUND the discarded file in DESTINATION!")
        cols = [column[0] for column in cursor.description]
        print(dict(zip(cols, row)))
    else:
        print("Discarded file NOT FOUND in destination.")
        
    conn.close()

if __name__ == "__main__":
    find_discarded_in_dest()

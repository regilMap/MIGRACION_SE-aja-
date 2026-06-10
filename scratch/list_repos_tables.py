import sys
import os
sys.path.append(os.getcwd())
from config.database import conectar_fuente

def list_repos_tables():
    conn = conectar_fuente()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.tables WHERE name LIKE '%Repositorio%'")
    rows = cursor.fetchall()
    for r in rows:
        print(r[0])
    conn.close()

if __name__ == "__main__":
    list_repos_tables()

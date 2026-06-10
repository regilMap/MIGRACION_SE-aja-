import sys
import os
sys.path.append(os.getcwd())
from config.database import conectar_fuente

def compare_filenames():
    conn = conectar_fuente()
    cursor = conn.cursor()
    
    ace_id = 25327
    re_id = 30051
    
    cursor.execute("SELECT NombreArchivo FROM ArchivoCargaEvidencia WHERE ArchivoCargaEvidenciaID = ?", ace_id)
    name_ace = cursor.fetchone()[0]
    
    cursor.execute("SELECT Archivo FROM RepositorioDeEnvio WHERE RepositorioDeEnvioID = ?", re_id)
    name_re = cursor.fetchone()[0]
    
    print(f"ACE: '{name_ace}' (len: {len(name_ace)})")
    print(f"RE:  '{name_re}' (len: {len(name_re)})")
    print(f"Equal? {name_ace == name_re}")
    
    if name_ace != name_re:
        print("Mismatches:")
        for i, (c1, c2) in enumerate(zip(name_ace, name_re)):
            if c1 != c2:
                print(f"Pos {i}: '{c1}' (0x{ord(c1):02x}) vs '{c2}' (0x{ord(c2):02x})")
        if len(name_ace) != len(name_re):
            print(f"Lengths differ: {len(name_ace)} vs {len(name_re)}")
            
    conn.close()

if __name__ == "__main__":
    compare_filenames()

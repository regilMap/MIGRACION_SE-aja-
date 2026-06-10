import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino")
        return
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Id, CoedomId, SubIndicadorEvidenciaId, EvidenciaId, NombreOriginal FROM Evidencia.Archivos WHERE Id IN (17311, 17312, 17313, 17314, 17315, 17316, 17317)")
        print("Archivos references details:")
        for r in cursor.fetchall():
            print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

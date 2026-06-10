import sys
from config.database import conectar_fuente, conectar_destino

def main():
    print("Connecting to Source...")
    conn_fuente = conectar_fuente()
    if conn_fuente:
        cursor = conn_fuente.cursor()
        print("\n--- FUENTE: SubIndicadores containing 'migra' ---")
        cursor.execute("SELECT IndicadorID, Codigo, Descripcion, Estado FROM SubIndicadores WHERE Descripcion LIKE '%migra%' OR Codigo LIKE '%7%'")
        for r in cursor.fetchall():
            print(r)
            
        print("\n--- FUENTE: Evidencia containing 'migra' ---")
        cursor.execute("SELECT EvidenciaID, Codigo, Descipcion, Estado FROM Evidencia WHERE Descipcion LIKE '%migra%' OR Codigo LIKE '%7%'")
        for r in cursor.fetchall():
            print(r)
        conn_fuente.close()
        
    print("\nConnecting to Destination...")
    conn_destino = conectar_destino()
    if conn_destino:
        cursor = conn_destino.cursor()
        print("\n--- DESTINO: SubIndicadores containing 'migra' ---")
        try:
            cursor.execute("SELECT Id, Codigo, Nombre FROM Mantenimiento.SubIndicadores WHERE Nombre LIKE '%migra%' OR Codigo LIKE '%7%'")
            for r in cursor.fetchall():
                print(r)
        except Exception as e:
            print(e)
            
        print("\n--- DESTINO: Evidencias containing 'migra' ---")
        try:
            cursor.execute("SELECT Id, Codigo, Nombre FROM Evidencia.Evidencias WHERE Nombre LIKE '%migra%' OR Codigo LIKE '%7%'")
            for r in cursor.fetchall():
                print(r)
        except Exception as e:
            print(e)
        conn_destino.close()

if __name__ == '__main__':
    main()

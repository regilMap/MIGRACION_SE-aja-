from config.database import conectar_fuente

def main():
    conn = conectar_fuente()
    if conn:
        cursor = conn.cursor()
        print("Checking unique FechaVencimiento values in Evidencia:")
        cursor.execute("SELECT DISTINCT FechaVencimiento FROM Evidencia")
        for r in cursor.fetchall():
            print(r)
            
        print("\nChecking unique TipoVencimiento values in Evidencia:")
        cursor.execute("SELECT DISTINCT TipoVencimiento FROM Evidencia")
        for r in cursor.fetchall():
            print(r)
            
        print("\nChecking unique CantDias values in Evidencia:")
        cursor.execute("SELECT DISTINCT CantDias FROM Evidencia")
        for r in cursor.fetchall():
            print(r)
            
        conn.close()

if __name__ == '__main__':
    main()

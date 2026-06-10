from config.database import conectar_fuente

def main():
    conn = conectar_fuente()
    if conn:
        cursor = conn.cursor()
        print("Checking unique FechaVencimiento values in CargaEvidencia:")
        cursor.execute("SELECT DISTINCT FechaVencimiento FROM CargaEvidencia ORDER BY FechaVencimiento DESC")
        rows = cursor.fetchall()
        for r in rows[:30]:
            print(r)
        print(f"Total unique FechaVencimiento values: {len(rows)}")
        conn.close()

if __name__ == '__main__':
    main()

import sys
from config.database import conectar_fuente

def diagnose():
    conn = conectar_fuente()
    if not conn:
        print("Error connecting to source DB")
        return

    cursor = conn.cursor()

    # 1. Total Evidencias
    cursor.execute("SELECT COUNT(*) FROM Evidencia")
    total = cursor.fetchone()[0]
    print(f"Total rows in 'Evidencia' table: {total}")

    # 2. Total Evidencias joining SubIndicadores (orphans check)
    query_joined = """
        SELECT COUNT(*) 
        FROM Evidencia e
        JOIN SubIndicadores s ON e.IndicadorID = s.IndicadorID
    """
    cursor.execute(query_joined)
    total_joined = cursor.fetchone()[0]
    print(f"Total rows in 'Evidencia' matching a 'SubIndicador': {total_joined}")
    print(f"Orphaned Evidencias (No SubIndicador): {total - total_joined}")

    # 3. Counts by SubIndicador Code (Top 20)
    query_grouped = """
        SELECT s.Codigo, COUNT(*)
        FROM Evidencia e
        JOIN SubIndicadores s ON e.IndicadorID = s.IndicadorID
        GROUP BY s.Codigo
        ORDER BY COUNT(*) DESC
    """
    cursor.execute(query_grouped)
    rows = cursor.fetchall()
    
    print("\nTop 20 SubIndicadores by Evidencia Count:")
    for row in rows[:20]:
        print(f"Code: {row[0]}, Count: {row[1]}")

    # 4. Check specific sub-indicator if provided as arg (optional)
    if len(sys.argv) > 1:
        codes = sys.argv[1:]
        print(f"\nChecking specific codes: {codes}")
        placeholders = ','.join(['?'] * len(codes))
        query_specific = f"""
            SELECT COUNT(*) 
            FROM Evidencia e
            JOIN SubIndicadores s ON e.IndicadorID = s.IndicadorID
            WHERE s.Codigo IN ({placeholders})
        """
        cursor.execute(query_specific, codes)
        count_specific = cursor.fetchone()[0]
        print(f"Total for codes {codes}: {count_specific}")

    conn.close()

if __name__ == "__main__":
    diagnose()

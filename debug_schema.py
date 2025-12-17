import sys
from config.database import conectar_fuente

def print_separator(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def inspect_schema():
    conn = conectar_fuente()
    if not conn:
        print("No se pudo conectar a la fuente")
        return

    cursor = conn.cursor()

    # 1. List all tables
    print_separator("TABLAS EN LA BASE DE DATOS")
    cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES ORDER BY TABLE_NAME")
    tables = cursor.fetchall()
    for schema, table in tables:
        print(f"{schema}.{table}")

    # 2. Inspect TipoVencimiento columns
    print_separator("COLUMNAS DE TipoVencimiento")
    try:
        cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'TipoVencimiento' ORDER BY ORDINAL_POSITION")
        columns = cursor.fetchall()
        for col in columns:
            print(f"{col[0]} ({col[1]})")
    except Exception as e:
        print(f"Error: {e}")

    # 3. Check for Indicador-like tables
    print_separator("BUSCANDO TABLAS RELACIONADAS CON 'INDICADOR'")
    cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%Indicador%'")
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]}.{row[1]}")
        
        # List columns for these tables too
        print(f"  Columnas de {row[1]}:")
        cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{row[1]}'")
        cols = cursor.fetchall()
        print(f"  {', '.join([c[0] for c in cols])}")

    conn.close()

if __name__ == "__main__":
    inspect_schema()

import pyodbc
import traceback

try:
    from config.database import conectar_destino
    conn = conectar_destino()
    cursor = conn.cursor()
    
    print("Leyendo script SQL...")
    with open("output_inserts.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    # Separation by semicolon or simple execution of the whole block if possible
    # Given the format, it's safer to separate or use a transaction
    print("Iniciando ejecución de INSERTs...")
    
    # We split by semicolon to execute one by one and track progress
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
    
    count = 0
    conn.autocommit = False # Use transaction
    try:
        for stmt in statements:
            cursor.execute(stmt)
            count += 1
            if count % 20 == 0:
                print(f"Procesados {count} de {len(statements)} sentencias...")
        
        conn.commit()
        print(f"\n¡MIGRACIÓN EXITOSA! Se ejecutaron {count} sentencias correctamente.")
    except Exception as e:
        conn.rollback()
        print("\n[ERROR] Falló la ejecución. Se realizó ROLLBACK.")
        print(e)
        traceback.print_exc()

except Exception as e:
    print(f"Error de conexión: {e}")

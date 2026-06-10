import pyodbc

try:
    from config.database import conectar_destino
    conn = conectar_destino()
    cursor = conn.cursor()
    
    tables = [('Usuario', 'Usuarios'), ('Usuario', 'UsuarioClaves')]
    for schema, table in tables:
        print(f"\n--- Estructura de {schema}.{table} ---")
        try:
            cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}'")
            for row in cursor.fetchall():
                print(row)
        except Exception as e:
            print(f"Error leyendo {table}: {e}")
            
except Exception as e:
    print(f"Error de conexión: {e}")

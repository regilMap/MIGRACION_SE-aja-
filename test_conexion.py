from config.database import conectar_fuente, conectar_destino

print("Probando conexiones...")

# Probar fuente
conn_fuente = conectar_fuente()
if conn_fuente:
    cursor = conn_fuente.cursor()
    cursor.execute("SELECT TOP 5 * FROM TipoVencimiento")
    print("Datos de TipoVencimiento:")
    for row in cursor.fetchall():
        print(f"  {row}")
    conn_fuente.close()

# Probar destino
conn_destino = conectar_destino()
if conn_destino:
    print("Conexión destino OK")
    conn_destino.close()
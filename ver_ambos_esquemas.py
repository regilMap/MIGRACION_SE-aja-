from config.database import conectar_fuente, conectar_destino
import sys

def ver_tablas_y_columnas(cursor, nombre_bd, f):
    f.write(f"\n{'='*50}\n")
    f.write(f"  {nombre_bd}\n")
    f.write(f"{'='*50}\n")
    
    # Obtener tablas
    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """)
    tablas = cursor.fetchall()
    
    for esquema, tabla in tablas:
        f.write(f"\n[{esquema}.{tabla}]\n")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, esquema, tabla)
        for col in cursor.fetchall():
            null = "NULL" if col[2] == "YES" else "NOT NULL"
            f.write(f"    {col[0]} ({col[1]}) {null}\n")

with open('esquemas_completo.txt', 'w', encoding='utf-8') as f:
    # FUENTE
    conn_fuente = conectar_fuente()
    if conn_fuente:
        ver_tablas_y_columnas(conn_fuente.cursor(), "BD FUENTE - SISMAPV1DB_ED", f)
        conn_fuente.close()
    else:
        f.write("No se pudo conectar a la BD Fuente\n")

    # DESTINO
    conn_destino = conectar_destino()
    if conn_destino:
        ver_tablas_y_columnas(conn_destino.cursor(), "BD DESTINO - SISMAP_EDUCACION_M", f)
        conn_destino.close()
    else:
        f.write("No se pudo conectar a la BD Destino\n")

print("Schema dump finished.")

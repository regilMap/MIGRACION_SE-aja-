from config.database import conectar_destino

conn = conectar_destino()
cursor = conn.cursor()

cursor.execute("""
    SELECT ROUTINE_SCHEMA, ROUTINE_NAME, ROUTINE_TYPE
    FROM INFORMATION_SCHEMA.ROUTINES
    ORDER BY ROUTINE_SCHEMA, ROUTINE_NAME
""")

routines = cursor.fetchall()

print("\n==================================================")
print("   STORED PROCEDURES Y FUNCIONES EN DESTINO       ")
print("==================================================")

for schema, name, rtype in routines:
    print(f"  [{schema}].[{name}] ({rtype})")

conn.close()

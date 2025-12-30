import pyodbc
from config.database import conectar_destino

def verify_environment():
    print("--- VERIFICANDO CONEXIÓN ---")
    conn = conectar_destino()
    if not conn:
        print("FALLO AL CONECTAR")
        return

    cursor = conn.cursor()
    
    # 1. Verificar Servidor y Base de Datos
    cursor.execute("SELECT @@SERVERNAME, DB_NAME()")
    row = cursor.fetchone()
    print(f"\n[INFO] CONECTADO A:")
    print(f"   SERVIDOR: {row[0]}")
    print(f"   BASE DE DATOS: {row[1]}")
    
    # 2. Verificar Datos Recientes (Evidencia.Puntuacion)
    print(f"\n[INFO] BUSCANDO DATOS RECIENTES...")
    try:
        cursor.execute("SELECT TOP 5 Id, Calificacion, CreatedAt FROM Evidencia.Puntuacion ORDER BY CreatedAt DESC")
        rows = cursor.fetchall()
        
        if rows:
            print(f"   ENCONTRADAS {len(rows)} PUNTUACIONES RECIENTES:")
            for r in rows:
                print(f"   - ID: {r.Id} | Calif: {r.Calificacion} | Fecha: {r.CreatedAt}")
        else:
            print("   NO SE ENCONTRARON PUNTUACIONES.")
            
    except Exception as e:
        print(f"   ERROR LEYENDO TABLA: {e}")

    # 3. Verificar Flags
    print(f"\n[INFO] VERIFICANDO FLAGS (IsActive/IsDeleted)...")
    try:
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN IsActive = 1 THEN 1 ELSE 0 END) as Activos,
                SUM(CASE WHEN IsActive = 0 THEN 1 ELSE 0 END) as Inactivos,
                SUM(CASE WHEN IsDeleted = 1 THEN 1 ELSE 0 END) as Eliminados
            FROM Evidencia.Puntuacion
        """)
        row = cursor.fetchone()
        print(f"   ACTITVOS: {row[0]}")
        print(f"   INACTIVOS: {row[1]}")
        print(f"   ELIMINADOS: {row[2]}")
    except Exception as e:
        print(f"   ERROR: {e}")

    conn.close()

if __name__ == "__main__":
    verify_environment()

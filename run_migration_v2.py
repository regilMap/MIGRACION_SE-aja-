import pyodbc
import traceback
import sys

def run():
    try:
        from config.database import conectar_destino
        conn = conectar_destino()
        cursor = conn.cursor()
        
        print("Leyendo script SQL...")
        with open("output_inserts.sql", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        statements = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('--'):
                continue
            # Each line might have many statements? No, our generator did 1 per line but without trailing ; in the SQL generation logic?
            # Let's check the generator. It did append(f"INSERT ...;")
            if ';' in line:
                for s in line.split(';'):
                    if s.strip():
                        statements.append(s.strip())
            else:
                statements.append(line)

        print(f"Total de sentencias extraídas: {len(statements)}")
        
        success_count = 0
        error_count = 0
        
        for i, stmt in enumerate(statements):
            try:
                cursor.execute(stmt)
                # Commit every 10 to keep it stable
                if i % 10 == 0:
                    conn.commit()
                success_count += 1
                if success_count % 20 == 0:
                    print(f"Éxito: {success_count}...")
            except Exception as e:
                error_count += 1
                print(f"\n[ERROR en sentencia {i}]: {stmt}")
                print(f"Mensaje: {e}")
                # Optional: break if errors are critical
                if "deadlock" in str(e).lower() or "connection" in str(e).lower():
                    print("Error crítico de conexión. Abortando.")
                    break
        
        conn.commit()
        print(f"\nFinalizado.")
        print(f"Éxitos: {success_count}")
        print(f"Errores: {error_count}")

    except Exception as e:
        print(f"Error fatal: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run()

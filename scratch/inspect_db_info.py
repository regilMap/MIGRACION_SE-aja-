import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar")
        return
    cursor = conn.cursor()
    try:
        # Sub-indicators query
        cursor.execute("SELECT Id, Codigo, Nombre FROM Mantenimiento.SubIndicadores")
        print("=== SUBINDICADORES IN DB ===")
        sub_inds = cursor.fetchall()
        for s in sub_inds[:30]:
            print(f"Id: {s[0]} | Codigo: {s[1]} | Nombre: {s[2][:60]}")
        print(f"Total subindicators: {len(sub_inds)}")
        
        # Look for NP / NS pattern in DB sub-indicators
        np_subs = [s for s in sub_inds if "NP" in s[1].upper() or "NP" in s[2].upper()]
        ns_subs = [s for s in sub_inds if "NS" in s[1].upper() or "NS" in s[2].upper()]
        print(f"\nFound {len(np_subs)} subindicators with NP and {len(ns_subs)} with NS")
        for s in np_subs:
            print(f"NP Sub -> Id: {s[0]} | Codigo: {s[1]} | Nombre: {s[2][:60]}")
        for s in ns_subs:
            print(f"NS Sub -> Id: {s[0]} | Codigo: {s[1]} | Nombre: {s[2][:60]}")

        # TipoVencimiento check
        cursor.execute("SELECT Id, Nombre FROM Mantenimiento.TipoVencimiento")
        print("\n=== TIPO VENCIMIENTO ===")
        for r in cursor.fetchall():
            print(r)

        # Users check
        cursor.execute("SELECT TOP 5 Id, Correo, RolId FROM Usuario.Usuarios")
        print("\n=== USERS (Top 5) ===")
        for r in cursor.fetchall():
            print(r)

        # Check if PDF already exists in Evidencia.Archivos
        cursor.execute("SELECT Id, NombreOriginal FROM Evidencia.Archivos WHERE NombreOriginal LIKE '%Circular%'")
        print("\n=== EXISTING CIRCULAR ARCHIVOS ===")
        for r in cursor.fetchall():
            print(r)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino")
        return
    cursor = conn.cursor()
    try:
        print("=== EXCEPTIONS IN Mantenimiento.ConfiguracionOrganismoExcepcion ===")
        cursor.execute("""
            SELECT coe.Id, coe.CoedomId, te.Nombre as TipoEntidad, coe.EntidadId, coe.Aplica, 
                   coe.FechaVencimiento, coe.FechaExtension, coe.IsActive, coe.IsDeleted
            FROM Mantenimiento.ConfiguracionOrganismoExcepcion coe
            JOIN Mantenimiento.TipoEntidad te ON te.Id = coe.TipoEntidadId
        """)
        for r in cursor.fetchall():
            print(r)
            
        print("\n=== GENERAL CONFIG IN Mantenimiento.ConfiguracionGeneral ===")
        cursor.execute("""
            SELECT cg.Id, te.Nombre as TipoEntidad, cg.EntidadId, cg.Aplica, cg.IsActive, cg.IsDeleted
            FROM Mantenimiento.ConfiguracionGeneral cg
            JOIN Mantenimiento.TipoEntidad te ON te.Id = cg.TipoEntidadId
        """)
        for r in cursor.fetchall():
            print(r)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

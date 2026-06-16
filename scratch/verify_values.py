import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    conn = conectar_destino()
    if not conn:
        return
    cursor = conn.cursor()
    try:
        # Check PEC (1.01.2) type vencimiento
        cursor.execute("""
            SELECT 
                se.Id, 
                e.Codigo, 
                e.Nombre, 
                fv.TipoVencimientoId, 
                tv.Nombre AS TipoVencimientoNombre
            FROM 
                Evidencia.SubIndicadorEvidencias se
            INNER JOIN 
                Evidencia.Evidencias e ON se.EvidenciaId = e.Id
            INNER JOIN 
                Evidencia.FechaVencimientoSubIndicadorEvidencias fv ON se.FechaVencimientoSubIndicadorEvidenciaId = fv.Id
            INNER JOIN 
                Mantenimiento.TipoVencimiento tv ON fv.TipoVencimientoId = tv.Id
            WHERE 
                e.Codigo = '1.01.2'
        """)
        print("\nPEC (1.01.2) Expiration Type details:")
        for r in cursor.fetchall():
            print(f"  Id: {r[0]} | Codigo: {r[1]} | Nombre: {r[2]} | TipoVencimientoId: {r[3]} | TipoVencimientoNombre: {r[4]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

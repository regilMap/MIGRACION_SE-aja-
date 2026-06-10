import sys
sys.path.append(r'c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)')
from config.database import conectar_destino

def check_latest():
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar.")
        return

    try:
        cursor = conn.cursor()
        print("=== 1. ÚLTIMA EXCEPCIÓN CREADA EN Mantenimiento.ConfiguracionOrganismoExcepcion ===")
        cursor.execute("""
            SELECT TOP 1 Id, CoedomId, TipoEntidadId, EntidadId, Aplica, CreatedAt, CreatedBy
            FROM Mantenimiento.ConfiguracionOrganismoExcepcion
            ORDER BY CreatedAt DESC
        """)
        row = cursor.fetchone()
        if not row:
            print("No se encontró ninguna excepción.")
            return

        exc_id, coedom_id, tipo_entidad_id, entidad_id, aplica, created_at, created_by = row
        print(f"ID Excepción: {exc_id}")
        print(f"CoedomId: {coedom_id}")
        print(f"TipoEntidadId: {tipo_entidad_id} (1=Indicador, 2=SubIndicador, 3=Evidencia)")
        print(f"EntidadId: {entidad_id}")
        print(f"Aplica: {aplica}")
        print(f"Creado el: {created_at}")
        print(f"Creado por: {created_by}")

        print("\n=== 2. ESTADO EN EL CACHÉ (Cache.ConfiguracionEntidad) ===")
        cursor.execute("""
            SELECT TipoEntidad, EntidadId, CoedomId, TipoConfiguracion, AplicaFinal, FechaActualizacion
            FROM Cache.ConfiguracionEntidad
            WHERE CoedomId = ? AND EntidadId = ? AND TipoEntidadId = ?
        """, coedom_id, entidad_id, tipo_entidad_id)
        cache_row = cursor.fetchone()
        if cache_row:
            tipo, ent, coedom, tipo_cfg, aplica_final, fecha_act = cache_row
            print(f"TipoEntidad: {tipo}")
            print(f"EntidadId: {ent}")
            print(f"CoedomId: {coedom}")
            print(f"TipoConfiguracion: {tipo_cfg}")
            print(f"AplicaFinal: {aplica_final}")
            print(f"Fecha Actualización Caché: {fecha_act}")
        else:
            print("No se encontró registro en la tabla de caché para esta combinación.")

        print("\n=== 3. ESTADO EN EL RANKING GLOBAL (Cache.RankingGlobal) ===")
        cursor.execute("""
            SELECT CoedomId, NombreOrganismo, PuntajeTotal, LastUpdated
            FROM Cache.RankingGlobal
            WHERE CoedomId = ?
        """, coedom_id)
        rank_row = cursor.fetchone()
        if rank_row:
            coedom, nombre, puntaje, last_up = rank_row
            print(f"CoedomId: {coedom}")
            print(f"Nombre: {nombre}")
            print(f"Puntaje Total: {puntaje}")
            print(f"Última Actualización Ranking: {last_up}")
        else:
            print("No se encontró registro en la tabla de ranking para esta escuela.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_latest()

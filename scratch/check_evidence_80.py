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
        # Total preguntas en la tabla
        cursor.execute("SELECT COUNT(*) FROM Evidencia.PreguntaRevisiones")
        total = cursor.fetchone()[0]
        print(f"Total de preguntas en PreguntaRevisiones: {total}")

        # Cuantas tienen SubIndicadorEvidenciaId asignado
        cursor.execute("SELECT COUNT(*) FROM Evidencia.PreguntaRevisiones WHERE SubIndicadorEvidenciaId IS NOT NULL")
        con_sie = cursor.fetchone()[0]
        print(f"Con SubIndicadorEvidenciaId asignado: {con_sie}")

        # Cuantas SubIndicadorEvidencias automáticas TIENEN preguntas
        cursor.execute("""
            SELECT COUNT(DISTINCT se.Id)
            FROM Evidencia.SubIndicadorEvidencias se
            LEFT JOIN Evidencia.PreguntaRevisiones pr ON pr.SubIndicadorEvidenciaId = se.Id
            WHERE se.TipoEvaluacionId = 2 AND pr.Id IS NOT NULL
        """)
        con_preguntas = cursor.fetchone()[0]
        print(f"SubIndicadorEvidencias automáticas CON preguntas: {con_preguntas}")

        # Total automáticas
        cursor.execute("SELECT COUNT(*) FROM Evidencia.SubIndicadorEvidencias WHERE TipoEvaluacionId = 2")
        total_auto = cursor.fetchone()[0]
        print(f"Total SubIndicadorEvidencias automáticas: {total_auto}")

        # Lista las que SÍ tienen preguntas
        cursor.execute("""
            SELECT se.Id, se.EvidenciaId, COUNT(pr.Id) as NumPreguntas
            FROM Evidencia.SubIndicadorEvidencias se
            INNER JOIN Evidencia.PreguntaRevisiones pr ON pr.SubIndicadorEvidenciaId = se.Id
            WHERE se.TipoEvaluacionId = 2
            GROUP BY se.Id, se.EvidenciaId
            ORDER BY se.Id
        """)
        rows = cursor.fetchall()
        print(f"\nSubIndicadorEvidencias automáticas con preguntas ({len(rows)}):")
        for r in rows:
            print(f"  SubIndEvId={r[0]}, EvidenciaId={r[1]}, NumPreguntas={r[2]}")

        # Verificar: hay preguntas sin SubIndicadorEvidenciaId?
        cursor.execute("SELECT * FROM Evidencia.PreguntaRevisiones WHERE SubIndicadorEvidenciaId IS NULL")
        sin_sie = cursor.fetchall()
        cols = [c[0] for c in cursor.description]
        print(f"\nPreguntas sin SubIndicadorEvidenciaId: {len(sin_sie)}")
        for r in sin_sie[:5]:
            for c, v in zip(cols, r):
                print(f"  {c}: {v}")
            print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback; traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    main()

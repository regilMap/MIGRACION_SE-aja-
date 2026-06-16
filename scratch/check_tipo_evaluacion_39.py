import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conectar_destino

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    conn = conectar_destino()
    if not conn:
        print("No se pudo conectar a la base de datos destino")
        return
    cursor = conn.cursor()
    try:
        print("=== INFO DE LA EVIDENCIA 39 ===")
        cursor.execute("""
            SELECT Id, SubIndicadorId, TipoEvaluacionId, IsActive, IsDeleted
            FROM Evidencia.SubIndicadorEvidencias
            WHERE Id = 39
        """)
        columns = [column[0] for column in cursor.description]
        for r in cursor.fetchall():
            print(dict(zip(columns, r)))
            
        print("\n=== PREGUNTAS DE REVISIÓN PARA EVIDENCIA 39 ===")
        cursor.execute("""
            SELECT Id, TextoPregunta, TipoPreguntaId, GrupoPreguntaRevisionId, EsDefault, IsActive, IsDeleted
            FROM Evidencia.PreguntaRevisiones
            WHERE SubIndicadorEvidenciaId = 39 OR (EsDefault = 1 AND SubIndicadorEvidenciaId IS NULL)
        """)
        columns = [column[0] for column in cursor.description]
        for r in cursor.fetchall():
            d = dict(zip(columns, r))
            # Safely print text by replacing special characters if needed
            print(f"Id: {d['Id']}, Tipo: {d['TipoPreguntaId']}, Default: {d['EsDefault']}, Activo: {d['IsActive']}, Del: {d['IsDeleted']}")
            print(f"Texto: {d['TextoPregunta'].encode('utf-8', errors='replace').decode('utf-8')}")

        print("\n=== ULTIMO ARCHIVO ACTIVO ===")
        cursor.execute("""
            SELECT Id, NombreOriginal, EstadoArchivoId, CoedomId, SubIndicadorEvidenciaId, CreatedAt
            FROM Evidencia.Archivos
            WHERE CoedomId = 26706 AND SubIndicadorEvidenciaId = 39
            ORDER BY CreatedAt DESC
        """)
        columns = [column[0] for column in cursor.description]
        for r in cursor.fetchall():
            print(dict(zip(columns, r)))
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

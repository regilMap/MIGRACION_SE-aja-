"""
Script: migrate_criterios.py
Propósito: Migrar los Criterios de Verificación del Excel hacia
           Evidencia.PreguntaRevisiones en la BD destino.

Uso:
    python migrate_criterios.py
    python migrate_criterios.py --limpiar      (borra antes de insertar)
    python migrate_criterios.py --dry-run      (muestra lo que haría sin escribir)
"""
import sys
import os
import argparse
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config.database import conectar_destino

try:
    import openpyxl
except ImportError:
    print("ERROR: openpyxl no está instalado. Ejecuta: pip install openpyxl")
    sys.exit(1)

# ── Configuración ───────────────────────────────────────────────────────────
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "Criterios_Evaluacion_SISMAP_Updated.xlsx")
TIPO_PREGUNTA_ID = 1      # Tipo de pregunta: verificación estándar (Si/No)
CREADO_POR = "MIGRATION"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(description="Migrar criterios Excel → PreguntaRevisiones")
    p.add_argument("--limpiar", action="store_true",
                   help="Eliminar preguntas existentes en PreguntaRevisiones antes de insertar")
    p.add_argument("--dry-run", action="store_true",
                   help="Mostrar lo que haría sin escribir en la BD")
    return p.parse_args()


def cargar_excel(path: str) -> list[dict]:
    """Lee el Excel actualizado y devuelve lista de dicts con los criterios."""
    log.info(f"Leyendo Excel: {path}")
    wb = openpyxl.load_workbook(path)
    ws = wb.active

    rows = []
    skipped = 0
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        # Columnas: Ámbito|Indicador|Subindicador|SubCod|EvId|EvCod|EvNombre|EvPDF|Criterio|ValorPorcentual
        if len(row) < 10:
            continue
        ambito, indicador, subindicador, sub_cod, ev_id, ev_cod, ev_nombre, ev_pdf, criterio, valor_pct = row

        criterio = str(criterio).strip() if criterio else None
        ev_cod = str(ev_cod).strip() if ev_cod else None

        if not criterio or not ev_cod:
            skipped += 1
            continue

        rows.append({
            "ev_cod": ev_cod,
            "criterio": criterio,
            "valor_porcentual": float(valor_pct) if valor_pct is not None else None,
            "fila_excel": i,
        })

    log.info(f"  Filas leídas: {len(rows)} (omitidas vacías: {skipped})")
    return rows


def obtener_mapa_evidencias(conn) -> dict:
    """Construye mapa ev_cod → SubIndicadorEvidenciaId desde la BD destino."""
    cur = conn.cursor()
    cur.execute("""
        SELECT e.Codigo, se.Id AS SubIndicadorEvidenciaId
        FROM Evidencia.SubIndicadorEvidencias se
        JOIN Evidencia.Evidencias e ON se.EvidenciaId = e.Id
        ORDER BY e.Codigo
    """)
    mapa = {}
    for cod, sie_id in cur.fetchall():
        mapa[cod.strip()] = sie_id
    log.info(f"  Mapa de evidencias cargado: {len(mapa)} entradas")
    return mapa


def limpiar_tabla(conn, dry_run: bool):
    """Elimina todas las preguntas de PreguntaRevisiones (para re-migrar limpio)."""
    cur = conn.cursor()
    if dry_run:
        cur.execute("SELECT COUNT(*) FROM Evidencia.PreguntaRevisiones")
        n = cur.fetchone()[0]
        log.info(f"[DRY-RUN] Se eliminarían {n} registros de PreguntaRevisiones")
        return
    cur.execute("DELETE FROM Evidencia.PreguntaRevisiones WHERE CreatedBy = ?", CREADO_POR)
    deleted = cur.rowcount
    conn.commit()
    log.info(f"  Eliminados {deleted} registros previos de PreguntaRevisiones (CreatedBy={CREADO_POR})")


def migrar_criterios(conn, rows: list[dict], mapa_ev: dict, dry_run: bool):
    """Inserta cada criterio en Evidencia.PreguntaRevisiones."""
    cur = conn.cursor()
    now = datetime.now()

    insertados = 0
    sin_evidencia = []
    errores = []

    for r in rows:
        ev_cod = r["ev_cod"]
        sie_id = mapa_ev.get(ev_cod)

        if sie_id is None:
            sin_evidencia.append(ev_cod)

        if dry_run:
            log.debug(f"  [DRY-RUN] EvCod={ev_cod} SIE={sie_id} Pct={r['valor_porcentual']} | {r['criterio'][:60]}")
            insertados += 1
            continue

        try:
            cur.execute("""
                INSERT INTO Evidencia.PreguntaRevisiones
                    (TextoPregunta, EsDefault, CreatedAt, CreatedBy, IsActive, IsDeleted,
                     SubIndicadorEvidenciaId, TipoPreguntaId, ValorPorcentual, GrupoPreguntaRevisionId)
                VALUES (?, 1, ?, ?, 1, 0, ?, ?, ?, NULL)
            """, (
                r["criterio"],
                now,
                CREADO_POR,
                sie_id,
                TIPO_PREGUNTA_ID,
                r["valor_porcentual"],
            ))
            insertados += 1
        except Exception as e:
            errores.append({"fila": r["fila_excel"], "ev_cod": ev_cod, "error": str(e)})
            log.error(f"  ERROR fila {r['fila_excel']} ({ev_cod}): {e}")

    if not dry_run:
        conn.commit()

    return insertados, list(set(sin_evidencia)), errores


def main():
    args = parse_args()

    log.info("=" * 60)
    log.info("MIGRACIÓN: Criterios de Verificación → PreguntaRevisiones")
    if args.dry_run:
        log.info("  MODO: DRY-RUN (sin escritura en BD)")
    log.info("=" * 60)

    # 1. Leer Excel
    if not os.path.exists(EXCEL_PATH):
        log.error(f"Excel no encontrado: {EXCEL_PATH}")
        log.error("Ejecuta primero: python scratch/update_excel_valores.py")
        sys.exit(1)

    rows = cargar_excel(EXCEL_PATH)

    # 2. Conectar a BD
    conn = conectar_destino()

    # 3. Obtener mapa de evidencias
    mapa_ev = obtener_mapa_evidencias(conn)

    # 4. Limpiar si se solicitó
    if args.limpiar:
        log.info("Limpiando registros previos...")
        limpiar_tabla(conn, args.dry_run)

    # 5. Migrar criterios
    log.info(f"Insertando {len(rows)} criterios en PreguntaRevisiones...")
    insertados, sin_ev, errores = migrar_criterios(conn, rows, mapa_ev, args.dry_run)

    # 6. Resumen
    log.info("")
    log.info("=" * 60)
    log.info(f"RESUMEN:")
    log.info(f"  Criterios procesados : {len(rows)}")
    log.info(f"  Insertados           : {insertados}")
    log.info(f"  Con error            : {len(errores)}")
    log.info(f"  Sin evidencia en BD  : {len(sin_ev)}")
    if sin_ev:
        log.warning(f"  Códigos sin mapear   : {sorted(set(sin_ev))}")
    if errores:
        log.error("  Errores detallados:")
        for e in errores:
            log.error(f"    Fila {e['fila']} ({e['ev_cod']}): {e['error']}")

    # 7. Verificar conteo final en BD
    if not args.dry_run:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Evidencia.PreguntaRevisiones WHERE CreatedBy = ?", CREADO_POR)
        total_bd = cur.fetchone()[0]
        log.info(f"  Total en BD (CreatedBy=MIGRATION): {total_bd}")

    conn.close()
    log.info("Migración completada.")


if __name__ == "__main__":
    main()

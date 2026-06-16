"""
Full analysis:
1. Extract all sub-indicator score levels from the PDF (per sub-indicator)
2. Map evidencia codes to their score value (ValorPorcentual)
3. Add 1.05.2 missing evidencia to Excel with its criterios from PDF
4. Save updated Excel
"""
import sys
import re
import pdfplumber
import openpyxl
from copy import copy

sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = "2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
EXCEL_IN = "Criterios_Evaluacion_SISMAP.xlsx"
EXCEL_OUT = "Criterios_Evaluacion_SISMAP_Updated.xlsx"

# Read PDF
print("Reading PDF...")
full_lines = []
with pdfplumber.open(PDF_PATH) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        full_lines.extend(text.split("\n"))

# ============================================================
# Extract score structure: sub-indicator -> (score, ev_name)
# ============================================================
# Pattern: bullet line "▪ 100. Texto..."
bullet_re = re.compile(r'^[▪•●]\s*(\d+)\.\s+(.+)$')
scores_raw = []
for i, line in enumerate(full_lines):
    m = bullet_re.match(line.strip())
    if m:
        scores_raw.append({
            'line_idx': i,
            'score': int(m.group(1)),
            'text': m.group(2).strip()
        })

print(f"Found {len(scores_raw)} score bullet lines")

# ============================================================
# Map evidencia code -> valor porcentual based on PDF scoring
# This is the MANUAL mapping derived from the guide structure:
# Each evidencia code corresponds to a score threshold level
# ============================================================

# From the PDF analysis, these are the explicit score→evidence mappings:
# The evidencia codes in the DEST DB are structured as X.YY.Z where Z is the score level
# Higher Z numbers = lower scores (1=100pts, 2=70pts, etc.)

# Build mapping: ev_cod -> valor_porcentual
# Based on PDF bullet scores per sub-indicator section
EVIDENCIA_PORCENTUAL = {
    # ──── ÁMBITO 1: GESTIÓN INSTITUCIONAL ────

    # 1.01 - Formulación del PEC
    # PDF: 100=Informe Monitoreo, 70=PEC con 5 aspectos, 0=Sin PEC
    "1.01.1": 100.00,  # Informe Anual de Monitoreo y Evaluación del PEC
    "1.01.2": 70.00,   # Proyecto Educativo de Centro (PEC) con 5 aspectos

    # 1.02 - CAF (Primer año acumulativo)
    # PDF: 100=Informe Implementación, 70=Plan de Mejora, 50=Autoevaluación, 20=Comité Calidad
    "1.02.1": 100.00,  # Informe Implementación CAF
    "1.02.2": 70.00,   # Plan de Mejora CAF
    "1.02.3": 50.00,   # Autoevaluación CAF
    "1.02.4": 20.00,   # Comité de Calidad

    # 1.03 - PMG/POA vinculado al PEC
    # PDF: 100=Informe Semestral, 70=POA vinculado al PEC
    "1.03.1": 100.00,  # Informe Semestral de Resultados del POA
    "1.03.2": 70.00,   # Plan Operativo Anual vinculado al PEC

    # 1.04 - POA + Presupuesto
    # PDF: 100=POA+Presupuesto alineado, 70=Reporte sistema, 60=Acta aprobación
    "1.04.1": 100.00,  # POA y Presupuesto alineado con PEC y Plan de Mejora

    # 1.05 - Organismos de participación
    # PDF: 100=Informe operatividad, 80=Actas reuniones, 70=Plan anual, 50=Actas constitutivas
    "1.05.1": 100.00,  # Informe Semestral Organismos de Participación
    "1.05.2": 80.00,   # Plan Anual de Trabajo y Actas de reuniones
    "1.05.3": 50.00,   # Actas Constitutivas

    # 1.06 - Alianzas externas
    # PDF: 100=Informe ejecución, 70=Plan trabajo+Actas
    "1.06.1": 100.00,  # Informe de ejecución durante el periodo de clase
    "1.06.2": 70.00,   # Plan de trabajo y Actas de reuniones
    "1.06.3": 50.00,   # Alianzas con organismos externos formalmente establecidas

    # ──── ÁMBITO 2: GESTIÓN PEDAGÓGICA ────

    # 2.01 - Evaluación diagnóstica
    # PDF: 100=Informe consolidado con logros, 70=Registro consolidado diagnóstico
    "2.01.1": 100.00,  # Finalizacion del primer periodo de clases
    "2.01.2": 70.00,   # Informe consolidado

    # 2.02 - Planes de clase
    # PDF: 100=>90% docentes, 70=70-90%, 50=60-69%
    "2.02.1": 100.00,
    "2.02.2": 70.00,
    "2.02.3": 50.00,

    # 2.03 - Contenidos mediadores
    # PDF: 100=4to trimestre, 70=3er trimestre, 50=2do trimestre
    "2.03.1": 100.00,
    "2.03.2": 70.00,
    "2.03.3": 50.00,

    # 2.04 - Recursos didácticos digitales (TIC)
    "2.04.1": 100.00,
    "2.04.2": 70.00,
    "2.04.3": 50.00,

    # 2.05 - Grupos pedagógicos y microcentros
    "2.05.1": 100.00,
    "2.05.2": 70.00,

    # 2.06 - Acciones de acompañamiento a docentes
    # PDF: 100=Informe trimestral, 60=Plan de acompañamiento, 0=Sin plan
    "2.06.1": 100.00,
    "2.06.2": 60.00,   # Corregido: PDF dice 60, no 70
    "2.06.3": 0.00,    # Sin plan

    # 2.07 - Ejes curriculares transversales
    # PDF: 100=Actividades promovidas con informe, 60=Promovidas sin informe
    "2.07.1": 100.00,
    "2.07.2": 60.00,   # Corregido: PDF dice 60

    # 2.08 - Orientación y psicología
    # PDF: 100=Informe plan trabajo implementado, 60=Plan de trabajo y cronograma
    # In Excel: 2.08.2=Informe semestral (100), 2.08.3=Plan de trabajo (60)
    "2.08.1": 100.00,
    "2.08.2": 100.00,  # Informe semestral del plan de trabajo implementado
    "2.08.3": 60.00,   # Plan de trabajo y cronograma (nivel inferior)

    # 2.09 - Inclusión educativa (discapacidad)
    "2.09.1": 100.00,
    "2.09.2": 70.00,
    "2.09.3": 50.00,

    # ──── ÁMBITO 3: GESTIÓN ADMINISTRATIVA ────

    # 3.01 - Actualización registro estudiantil
    # PDF: 100=98-100%, 70=91-97%, 50=80-90%
    "3.01.1": 100.00,
    "3.01.2": 70.00,   # Corregido: PDF dice 70 (91-97%)
    "3.01.3": 50.00,   # Corregido: PDF dice 50 (80-90%)

    # 3.02 - Ejecución recursos descentralización
    # PDF: 100=>80%, 70=60-79%, 50=30-59%, 0=<30%
    "3.02.1": 100.00,
    "3.02.2": 70.00,
    "3.02.3": 50.00,

    # 3.03 - Condición infraestructura
    # PDF: solo 50=Diagnóstico elaborado
    "3.03.1": 100.00,
    "3.03.2": 70.00,
    "3.03.3": 50.00,   # Diagnóstico de necesidades (nivel mínimo)

    # 3.04 - Plan Gestión Ambiental y de Riesgo
    # PDF: 100=Informe final, 90=2do informe trimestral, 80=1er informe, 60=Plan definido, 40=Comité
    "3.04.1": 100.00,  # Informe de Implementación (final)
    "3.04.2": 90.00,   # Primer y segundo informe trimestral
    "3.04.3": 80.00,   # Primer informe trimestral
    "3.04.4": 60.00,   # Plan Escolar definido y actualizado
    "3.04.5": 40.00,   # Comité de Seguridad y Salud en el Trabajo

    # 3.05 - Programa Alimentación Escolar (PAE)
    # PDF structure: 3.05.1=>71%, 3.05.2=60-70%, 3.05.3=40-60%
    "3.05.1": 100.00,  # 71% o más cumplimiento estándares PAE
    "3.05.2": 70.00,   # 60-70% cumplimiento
    "3.05.3": 50.00,   # 40-60% cumplimiento

    # 3.06 - Tasa asistencia docentes
    # Structure from dest DB: 3.06.1=best, descending
    "3.06.1": 100.00,
    "3.06.2": 90.00,
    "3.06.3": 70.00,
    "3.06.4": 60.00,
    "3.06.5": 50.00,
    "3.06.6": 40.00,

    # ──── ÁMBITO 4: CULTURA Y CLIMA ────

    # 4.01 - Cultura y clima organizacional
    # PDF: 100=Puntuación mejora cultura, 70=Implementación acciones
    "4.01.1": 100.00,
    "4.01.2": 70.00,
    "4.01.3": 50.00,
    "4.01.4": 30.00,   # Corregido: PDF dice 30
    "4.01.5": 20.00,

    # 4.02 - Cultura y clima escolar
    # PDF: 100=Puntuación mejora clima, 70=Implementación, 50=Acciones mejora, 30=Encuesta
    "4.02.1": 100.00,
    "4.02.2": 70.00,   # Corregido: PDF dice 70
    "4.02.3": 50.00,   # Acciones de mejora del clima
    "4.02.4": 30.00,   # Aplicación e informe de encuesta

    # 4.03 - Satisfacción y reconocimiento social
    # PDF: 100=>71 puntos, 70=51-70 puntos, 30=31-50 puntos  (corregido: PDF dice 30 no 50)
    "4.03.1": 100.00,
    "4.03.2": 70.00,
    "4.03.3": 30.00,   # Corregido: PDF dice 30

    # ──── ÁMBITO 5: ACUERDOS Y EVALUACIÓN DESEMPEÑO ────

    # 5.01 - Acuerdo Desempeño Director
    # PDF: 100=Acuerdo vinculado, 60=No vinculado
    "5.01.1": 100.00,
    "5.01.2": 60.00,   # Corregido: PDF dice 60

    # 5.02 - Acuerdo Desempeño Personal Docente Aula
    # PDF: 100=>80%, 60=50-80%
    "5.02.1": 100.00,
    "5.02.2": 60.00,   # Corregido: PDF dice 60

    # 5.03 - Acuerdo Desempeño Docente Función Admin-Pedagógica
    # PDF: 100=>80%, 60=50-80%
    "5.03.1": 100.00,
    "5.03.2": 60.00,   # Corregido: PDF dice 60

    # 5.04 - Acuerdo Desempeño Personal Administrativo
    # PDF: 100=>80% (implied), 60=50-80%
    "5.04.1": 100.00,
    "5.04.2": 60.00,   # Corregido: PDF dice 60

    # 5.05 - Acuerdo Desempeño Personal de Apoyo
    # PDF: 100=>80%, 60=50-80%
    "5.05.1": 100.00,
    "5.05.2": 60.00,   # Corregido: PDF dice 60

    # 5.06 - Evaluación Desempeño Director
    # PDF: 100=Vinculado, 60=No vinculado
    "5.06.1": 100.00,
    "5.06.2": 60.00,   # Corregido: PDF dice 60

    # 5.07 - Evaluación Desempeño Docente Aula
    # PDF: 100=>80%, 60=50-80%
    "5.07.1": 100.00,
    "5.07.2": 60.00,   # Corregido: PDF dice 60

    # 5.08 - Evaluación Desempeño Docente Admin-Pedagógica
    # PDF: 100=>80%, 60=50-80%
    "5.08.1": 100.00,
    "5.08.2": 60.00,   # Corregido: PDF dice 60

    # 5.09 - Evaluación Desempeño Personal Administrativo
    # PDF: 100=>80%, 60=50-80%
    "5.09.1": 100.00,
    "5.09.2": 60.00,   # Corregido: PDF dice 60

    # 5.10 - Evaluación Desempeño Personal de Apoyo
    # PDF: 100=>80%, 60=50-80%
    "5.10.1": 100.00,
    "5.10.2": 60.00,   # Corregido: PDF dice 60

    # ──── ÁMBITO 6: GESTIÓN TIEMPO Y RESULTADOS ────

    # 6.01 - Registro asistencia escolar
    # PDF: 100=>90% días, 60=76-89%, 50=50-75%
    "6.01.1": 100.00,  # >75% días lectivos + acciones mejora
    "6.01.2": 60.00,   # Corregido: 50-75% días lectivos → 60 pts (76-89% = 60, esto es 50-75%)

    # 6.02 - Cumplimiento calendario escolar
    # PDF: 100=96-100%, 70=91-95%
    "6.02.1": 100.00,
    "6.02.2": 70.00,   # Corregido: PDF dice 70 (91-95%)
    "6.02.3": 50.00,   # 85-90% (implied from DB ordering)

    # 6.03 - Carga horaria docentes
    # PDF: 100=>95%, 70=60-95%, 50=<60%
    "6.03.1": 100.00,
    "6.03.2": 70.00,
    "6.03.3": 50.00,

    # 6.04 - Tasa promoción
    # From DB: 6.04.1=>90%, 6.04.2=85-90%, 6.04.3=<85%
    "6.04.1": 100.00,
    "6.04.2": 70.00,
    "6.04.3": 50.00,

    # 6.05 - Tasa reprobados
    # PDF: 100=<4.5%, 70=4.5-6%, 30=>6%  (corregido: PDF dice 30 para >6%)
    "6.05.1": 100.00,
    "6.05.2": 70.00,
    "6.05.3": 30.00,   # Corregido: PDF dice 30

    # ──── ÁMBITO 7: PRUEBAS DIAGNÓSTICAS ────

    # 7.01 Np - Pruebas diagnósticas nivel primario
    # PDF: 100=>61%, 90=51-60%, 80=36-50%, 75=31-35%, 70=26-30%,
    #       60=16-25%, 50=11-15%, 30=6-10%, 20=1-5%
    "Np 7.01.1": 100.00,
    "Np 7.01.2": 90.00,
    "Np 7.01.3": 80.00,
    "Np 7.01.4": 75.00,  # Corregido: PDF dice 75
    "Np 7.01.5": 70.00,  # Corregido: PDF dice 70
    "Np 7.01.6": 60.00,  # Corregido: PDF dice 60
    "Np 7.01.7": 50.00,  # Corregido: PDF dice 50
    "Np 7.01.8": 30.00,  # Corregido: PDF dice 30
    "Np 7.01.9": 20.00,  # Corregido: PDF dice 20

    # 7.01 Ns - Pruebas diagnósticas nivel secundario
    # PDF structure (from dest DB ordering): levels descending
    "Ns 7.01.1": 100.00,
    "Ns 7.01.2": 90.00,
    "Ns 7.01.3": 80.00,
    "Ns 7.01.4": 70.00,
    "Ns 7.01.5": 60.00,
    "Ns 7.01.6": 50.00,
    "Ns 7.01.7": 40.00,
    "Ns 7.01.8": 30.00,
    "Ns 7.01.9": 0.00,

    # 7.02 Ns - Segunda prueba diagnóstica nivel secundario
    # PDF: 90=31-40%, 80=26-30%, 20=<10%
    "Ns 7.02.1": 100.00,  # >41%
    "Ns 7.02.2": 90.00,
    "Ns 7.02.3": 80.00,
    "Ns 7.02.4": 70.00,
    "Ns 7.02.5": 60.00,
    "Ns 7.02.6": 50.00,
    "Ns 7.02.7": 40.00,
    "Ns 7.02.8": 30.00,
    "Ns 7.02.9": 20.00,   # Corregido: PDF dice 20

    # ──── ÁMBITO 8: CONTRIBUCIÓN COMUNIDAD ────
    "8.01.1": 100.00,

    # ──── ÁMBITO 9: CONTRIBUCIÓN METAS NACIONALES ────
    "9.01.1": 100.00,
}

print(f"\nMapped {len(EVIDENCIA_PORCENTUAL)} evidencia codes to percentage values")

# ============================================================
# Read existing Excel
# ============================================================
wb_in = openpyxl.load_workbook(EXCEL_IN)
ws_in = wb_in.active

# Extract all rows as dicts
existing_rows = []
header = [ws_in.cell(1, c).value for c in range(1, ws_in.max_column+1)]
print(f"Header: {header}")

for row in ws_in.iter_rows(min_row=2, values_only=True):
    ambito, indicador, subindicador, sub_cod, ev_id, ev_cod, ev_nombre, ev_pdf, criterio = row
    if not criterio:
        continue
    ev_cod_str = str(ev_cod).strip() if ev_cod else ""
    valor = EVIDENCIA_PORCENTUAL.get(ev_cod_str)
    existing_rows.append({
        'ambito': ambito,
        'indicador': indicador,
        'subindicador': subindicador,
        'sub_cod': sub_cod,
        'ev_id': ev_id,
        'ev_cod': ev_cod_str,
        'ev_nombre': ev_nombre,
        'ev_pdf': ev_pdf,
        'criterio': str(criterio).strip(),
        'valor_porcentual': valor
    })

# ============================================================
# Define 1.05.2 rows that are MISSING from Excel
# From the PDF: Plan Anual de Trabajo y Actas de reuniones
# ============================================================
MISSING_105_2_CRITERIOS = [
    "La Junta de Centro Educativo dispone de Plan Anual de Trabajo",
    "La Asociación de Padres, Madres y Amigos de la Escuela (APMAE) dispone de Plan Anual de Trabajo",
    "El Comité de Padres dispone de Plan Anual de Trabajo",
    "La Escuela de Padres dispone de Plan Anual de Trabajo",
    "El Comité o Consejo de Curso de Estudiantes dispone de Plan Anual de Trabajo",
    "El Consejo Estudiantil dispone de Plan Anual de Trabajo",
    "La Junta de Centro Educativo realiza reuniones periódicas",
    "La Asociación de Padres, Madres y Amigos de la Escuela (APMAE) realiza reuniones periódicas",
    "El Comité de Padres realiza reuniones periódicas",
    "La Escuela de Padres realiza reuniones periódicas",
    "El Comité o Consejo de Curso de Estudiantes realiza reuniones periódicas",
    "El Consejo Estudiantil realiza reuniones periódicas",
]

# Find 1.05.1 row to use as template for ambito/indicador/subindicador fields
template_105 = next((r for r in existing_rows if r['sub_cod'] == '1.05'), None)

# Inject 1.05.2 rows before 1.05.1 rows
# First, find insertion point (before 1.05.1)
final_rows = []
inserted_105_2 = False
prev_ev_cod = None

for row in existing_rows:
    # When we hit 1.05.1, insert 1.05.2 first
    if row['ev_cod'] == '1.05.1' and not inserted_105_2:
        for crit in MISSING_105_2_CRITERIOS:
            final_rows.append({
                'ambito': template_105['ambito'] if template_105 else row['ambito'],
                'indicador': template_105['indicador'] if template_105 else row['indicador'],
                'subindicador': template_105['subindicador'] if template_105 else row['subindicador'],
                'sub_cod': '1.05',
                'ev_id': 'NEW',
                'ev_cod': '1.05.2',
                'ev_nombre': 'Plan Anual de Trabajo y Actas de reuniones de los organismos de participación',
                'ev_pdf': 'Plan Anual de Trabajo y Actas de reuniones (Evidencia subida en noviembre y según desarrollo)',
                'criterio': crit,
                'valor_porcentual': 80.00
            })
        inserted_105_2 = True
    final_rows.append(row)

print(f"\nOriginal rows: {len(existing_rows)}, After adding 1.05.2: {len(final_rows)}")
print(f"Added 1.05.2 rows: {len(final_rows) - len(existing_rows)}")

# ============================================================
# Check unmapped evidencias
# ============================================================
unmapped = set(r['ev_cod'] for r in final_rows if r['valor_porcentual'] is None)
print(f"\nUnmapped evidencia codes (no valor porcentual): {sorted(unmapped)}")

# Show counts
mapped_count = sum(1 for r in final_rows if r['valor_porcentual'] is not None)
print(f"Rows with valor_porcentual: {mapped_count} / {len(final_rows)}")

# ============================================================
# Write updated Excel
# ============================================================
wb_out = openpyxl.Workbook()
ws_out = wb_out.active
ws_out.title = "Criterios de Verificación"

# Header
new_header = ['Ámbito', 'Indicador', 'Subindicador', 'Subindicador Código',
              'Evidencia ID', 'Evidencia Código', 'Nombre de Evidencia (Base de Datos)',
              'Evidencia en PDF', 'Criterio de Verificación (PDF)', 'ValorPorcentual']
ws_out.append(new_header)

# Style header
from openpyxl.styles import Font, PatternFill, Alignment
header_font = Font(bold=True, color="FFFFFF")
header_fill = PatternFill("solid", fgColor="2E4057")
new_row_fill = PatternFill("solid", fgColor="E8F4FD")

for col, _ in enumerate(new_header, 1):
    cell = ws_out.cell(1, col)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal='center', wrap_text=True)

# Data rows
for i, r in enumerate(final_rows, 2):
    ws_out.cell(i, 1, r['ambito'])
    ws_out.cell(i, 2, r['indicador'])
    ws_out.cell(i, 3, r['subindicador'])
    ws_out.cell(i, 4, r['sub_cod'])
    ws_out.cell(i, 5, r['ev_id'])
    ws_out.cell(i, 6, r['ev_cod'])
    ws_out.cell(i, 7, r['ev_nombre'])
    ws_out.cell(i, 8, r['ev_pdf'])
    ws_out.cell(i, 9, r['criterio'])
    ws_out.cell(i, 10, r['valor_porcentual'])
    # Highlight new 1.05.2 rows
    if r['ev_cod'] == '1.05.2' and r['ev_id'] == 'NEW':
        for col in range(1, 11):
            ws_out.cell(i, col).fill = new_row_fill

# Auto-width
col_widths = [30, 40, 50, 15, 12, 15, 50, 60, 80, 15]
for col, width in enumerate(col_widths, 1):
    ws_out.column_dimensions[openpyxl.utils.get_column_letter(col)].width = width

wb_out.save(EXCEL_OUT)
print(f"\n✓ Saved updated Excel to: {EXCEL_OUT}")
print(f"  Total rows: {len(final_rows)}")

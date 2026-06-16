"""
Script to:
1. Read the PDF guide and extract ValorPorcentual for each criterion
2. Read Criterios_Evaluacion_SISMAP.xlsx
3. Produce a mapping of criterio text -> porcentaje
4. Output the updated Excel with ValorPorcentual column added
"""
import sys
import re
import pdfplumber
import openpyxl
from openpyxl.styles import PatternFill, Font

sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = "2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
EXCEL_IN = "Criterios_Evaluacion_SISMAP.xlsx"
EXCEL_OUT = "Criterios_Evaluacion_SISMAP_Updated.xlsx"

# ============================================================
# STEP 1: Extract ALL text from PDF, page by page
# ============================================================
print("Reading PDF...")
all_pages = []
with pdfplumber.open(PDF_PATH) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        all_pages.append((i+1, text))

full_text = "\n".join(t for _, t in all_pages)
print(f"  Total pages: {len(all_pages)}, Total chars: {len(full_text)}")

# ============================================================
# STEP 2: Extract percentage values for each evidencia section
# ============================================================
# Strategy: find score lines like "▪ 70. Proyecto..." or "100. Informe..."
# and match to criterio table entries (Si/No table rows with percentages)

# Extract all lines
lines = full_text.split("\n")
print(f"  Total lines: {len(lines)}")

# Look for lines with percentage table entries
# Pattern: lines with "Si No" or "Cumple" and nearby percentage numbers
# The PDF tables look like: "1. Some criterion text  [Si] [No]"
# or percentage lines: "▪ 70. Proyecto Educativo..."

# Build a dict: criterio_text (lower) -> valor_porcentual
criterio_valor_map = {}

# ============================================================
# STEP 3: Read Excel and show current structure
# ============================================================
print("\nReading Excel...")
wb_in = openpyxl.load_workbook(EXCEL_IN)
ws_in = wb_in.active

rows = []
for row in ws_in.iter_rows(min_row=2, values_only=True):
    ambito, indicador, subindicador, sub_cod, ev_id, ev_cod, ev_nombre, ev_pdf, criterio = row
    if criterio:
        rows.append({
            'ambito': ambito,
            'indicador': indicador,
            'subindicador': subindicador,
            'sub_cod': sub_cod,
            'ev_id': ev_id,
            'ev_cod': ev_cod,
            'ev_nombre': ev_nombre,
            'ev_pdf': ev_pdf,
            'criterio': str(criterio).strip(),
            'valor_porcentual': None
        })

print(f"  Total criterios in Excel: {len(rows)}")

# Show unique evidencias
ev_ids = sorted(set(r['ev_id'] for r in rows))
print(f"  Unique evidencias: {ev_ids}")

# ============================================================
# STEP 4: Find percentage sections in PDF text
# ============================================================
# Search for percentage-table-like areas
# In the PDF, criterio tables appear as:
#   Evidencia   Criterios de verificación   Si  No
#   EvidName    criterio text               [x] [ ]
#
# Percentage scores appear separately as bullet points:
#   ▪ 70. [texto criterio]
#   or as columns in rating tables

# Let's find all lines with bullet+number pattern: ▪ XX. text
bullet_score_pattern = re.compile(r'[▪•●]\s*(\d+)\.\s+(.+)')
score_lines = []
for line in lines:
    m = bullet_score_pattern.match(line.strip())
    if m:
        score_lines.append((int(m.group(1)), m.group(2).strip()))

print(f"\n  Score bullet lines found: {len(score_lines)}")
for score, text in score_lines[:30]:
    print(f"    {score}: {text[:80]}")

# ============================================================
# STEP 5: Build criterio -> score mapping from PDF
# ============================================================
# The evidencia criterio pages show tables with "Si / No"
# Each criterio in those tables is a checkbox item
# We need to correlate the text of each criterio with a score

# Manual approach: search for "Criterios de verificación" sections
# and extract the Si/No table rows

# Find all "Criterios de verificación" section starts
crit_section_starts = [i for i, line in enumerate(lines) 
                        if 'criterios de verificación' in line.lower() 
                        or 'criterios de verificacion' in line.lower()]
print(f"\n  'Criterios de verificación' sections found: {len(crit_section_starts)}")

# Print a sample section
if crit_section_starts:
    for idx in crit_section_starts[:3]:
        print(f"\n  --- Section at line {idx} ---")
        for l in lines[idx:idx+30]:
            print(f"    {l}")


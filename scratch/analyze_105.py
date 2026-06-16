import sys
import re
import pdfplumber
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = "2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
EXCEL_IN = "Criterios_Evaluacion_SISMAP.xlsx"

# Read PDF
print("Reading PDF...")
all_text_by_page = []
with pdfplumber.open(PDF_PATH) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        all_text_by_page.append((i+1, text))

full_text = "\n".join(t for _, t in all_text_by_page)
lines = full_text.split("\n")

# ============================================================
# Find 1.05 section in PDF
# ============================================================
print("\n=== FINDING 1.05 SECTION ===")
for i, line in enumerate(lines):
    if '1.05' in line or '1.5' in line.lower():
        print(f"Line {i}: {line}")

print("\n=== PDF PAGES MENTIONING 1.05 ===")
for page_num, text in all_text_by_page:
    if '1.05' in text:
        print(f"\n-- Page {page_num} --")
        # Print relevant lines
        for line in text.split("\n"):
            if '1.05' in line or 'organismos' in line.lower() or 'participaci' in line.lower():
                print(f"  {line}")

# ============================================================
# Find score/percentage values for each sub-indicator
# ============================================================
print("\n=== SCORE LEVELS (bullet) for sub-indicator 1.05 ===")
in_105 = False
for i, line in enumerate(lines):
    if '1.05' in line:
        in_105 = True
    if in_105 and '1.06' in line:
        in_105 = False
    if in_105:
        print(f"  L{i}: {line}")

# ============================================================
# Find what sub-indicators are in Excel
# ============================================================
print("\n=== 1.05 SUB-INDICATORS IN EXCEL ===")
wb = openpyxl.load_workbook(EXCEL_IN)
ws = wb.active
for row in ws.iter_rows(min_row=2, values_only=True):
    _, _, subind, sub_cod, ev_id, ev_cod, ev_nombre, _, criterio = row
    if sub_cod and '1.05' in str(sub_cod):
        print(f"  Sub={sub_cod} | EvId={ev_id} | EvCod={ev_cod} | {ev_nombre[:60]}")
        print(f"    Criterio: {criterio}")

import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[32] # Page 33 (0-indexed 32)
tables = page.find_tables()
print(f"Tables found on Page 33: {len(tables.tables)}")
for idx, t in enumerate(tables.tables):
    data = t.extract()
    print(f"\nTable {idx + 1}:")
    for r_idx, r in enumerate(data):
        print(f"  Row {r_idx}: {[cell.strip() if cell else '' for cell in r]}")

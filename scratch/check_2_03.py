import fitz
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Let's import the extraction logic or run it locally
# We can copy the parser logic and see what it parses for page 33 (which is page 34 in 1-based, index 33)
pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[33]  # page 34
tables = page.find_tables()
print(f"Page 34 has {len(tables.tables)} tables.")
for idx, t in enumerate(tables.tables):
    rows = t.extract()
    print(f"Table {idx} rows count: {len(rows)}")
    header_row_idx = -1
    for r_idx, r in enumerate(rows):
        clean_row = [str(c).replace("\n", " ").strip() for c in r]
        row_str = " ".join(clean_row).lower()
        print(f"  Row {r_idx}: {row_str[:120]}")

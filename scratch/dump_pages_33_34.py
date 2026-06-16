import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

for p in [31, 32, 33, 34]:
    print(f"--- PAGE {p+1} ---")
    page = doc[p]
    print(page.get_text())
    
    # Also dump tables
    tables = page.find_tables()
    print(f"Found {len(tables.tables)} tables on page {p+1}")
    for idx, t in enumerate(tables.tables):
        print(f"Table {idx}:")
        rows = t.extract()
        for r in rows:
            print("  |  ".join([str(c).replace("\n", " ").strip() for c in r]))
    print("=" * 80)

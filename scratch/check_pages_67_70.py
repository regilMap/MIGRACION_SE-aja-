import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

for p in range(66, 70): # Pages 67 to 70 (0-indexed 66 to 69)
    print(f"--- PAGE {p+1} ---")
    page = doc[p]
    print(page.get_text())
    
    tables = page.find_tables()
    print(f"Found {len(tables.tables)} tables.")
    for idx, t in enumerate(tables.tables):
        rows = t.extract()
        for r in rows:
            print("  |  ".join([str(c).replace("\n", " ").strip() for c in r]))
        print("=" * 60)

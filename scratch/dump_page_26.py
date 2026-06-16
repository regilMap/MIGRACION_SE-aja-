import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[25] # Page 26 (0-indexed 25)
tables = page.find_tables()
print(f"Tables found: {len(tables.tables)}")
if tables.tables:
    t = tables.tables[0]
    data = t.extract()
    for r_idx, r in enumerate(data):
        print(f"Row {r_idx}: {[cell.strip() if cell else '' for cell in r]}")
else:
    print("No tables found")

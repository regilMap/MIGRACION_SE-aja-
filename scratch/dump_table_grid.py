import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[31] # Page 32
tables = page.find_tables()
if tables.tables:
    t = tables.tables[0]
    print(f"Table bbox: {t.bbox}")
    print(f"Col edges: {t.col_edges}")
    print(f"Row edges: {t.row_edges}")
else:
    print("No tables found")

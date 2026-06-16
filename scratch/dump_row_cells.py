import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[19] # Page 20
tables = page.find_tables()
if tables.tables:
    t = tables.tables[0]
    print("Row attributes:")
    row = t.rows[0]
    print(dir(row))
    print("Row cells:", row.cells)
    print("Row bbox:", row.bbox)
else:
    print("No tables found")

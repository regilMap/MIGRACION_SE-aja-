import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[19] # Page 20
tables = page.find_tables()
if tables.tables:
    table = tables.tables[0]
    data = table.extract()
    for r_idx, r in enumerate(data):
        print(f"Row {r_idx}:")
        for c_idx, cell in enumerate(r):
            if cell is not None and cell.strip():
                print(f"  Col {c_idx}: {repr(cell.strip())}")
else:
    print("No tables found")

import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[19] # Page 20
tables = page.find_tables()
if tables.tables:
    table = tables.tables[0]
    print(f"Table bbox: {table.bbox}")
    print(f"cols (length {len(table.cols)}): {table.cols}")
    print(f"rows (length {len(table.rows)}): {table.rows}")
else:
    print("No tables found")

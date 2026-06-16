import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[19] # Page 20
tables = page.find_tables()
if tables.tables:
    table = tables.tables[0]
    print(f"Table bbox: {table.bbox}")
    print(f"Col count: {table.col_count}, Row count: {table.row_count}")
    print("\nCells:")
    # table.cells is a list of cell objects or coordinates
    # Let's inspect some of them
    for idx, cell in enumerate(table.cells[:30]):
        if cell:
            print(f"Cell {idx}: bbox={cell}")
else:
    print("No tables found")

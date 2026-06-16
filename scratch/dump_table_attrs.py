import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[19] # Page 20
tables = page.find_tables()
if tables.tables:
    table = tables.tables[0]
    print(f"Directory: {dir(table)}")
    # Let's inspect some properties
    for attr in ['bbox', 'cells', 'col_count', 'row_count', 'rows']:
        if hasattr(table, attr):
            val = getattr(table, attr)
            print(f"{attr}: type={type(val)}, length/value={len(val) if hasattr(val, '__len__') else val}")
else:
    print("No tables found")

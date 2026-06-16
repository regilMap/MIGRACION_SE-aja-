import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[19] # Page 20
try:
    tables = page.find_tables()
    print("TableFinder attributes:", dir(tables))
    # In newer PyMuPDF, tables is a TableFinder. It has tables property or list.
    table_list = tables.tables
    print(f"Number of tables (via tables.tables): {len(table_list)}")
    for i, t in enumerate(table_list):
        print(f"Table {i+1} dir:", dir(t))
        data = t.extract()
        print(f"Table {i+1} rows: {len(data)}")
        for r_idx, r in enumerate(data[:10]):
            print(f"  Row {r_idx}: {r}")
except Exception as e:
    import traceback
    traceback.print_exc()

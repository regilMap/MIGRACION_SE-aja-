import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[31] # Page 32 (0-indexed 31)
tables = page.find_tables()
print(f"Tables found: {len(tables.tables)}")
for t_idx, t in enumerate(tables.tables):
    print(f"Table {t_idx+1}: bbox={t.bbox}, cols={t.col_count}, rows={t.row_count}")
    data = t.extract()
    for r_idx, r in enumerate(data):
        print(f"Row {r_idx}:")
        for c_idx, cell in enumerate(r):
            if cell is not None and cell.strip():
                print(f"  Col {c_idx}: {repr(cell.strip())}")

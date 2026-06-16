import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

print("Checking table bounding boxes:")
for page_num in range(len(doc)):
    page = doc[page_num]
    tables = page.find_tables()
    if tables.tables:
        for t_idx, t in enumerate(tables.tables):
            print(f"Page {page_num + 1}, Table {t_idx + 1}: bbox={t.bbox}, cols={t.col_count}, rows={t.row_count}")

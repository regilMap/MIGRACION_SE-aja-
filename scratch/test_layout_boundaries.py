import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

print("Page table column boundaries inspection:")
for page_num in range(18, 76):
    page = doc[page_num]
    tables = page.find_tables()
    if not tables.tables:
        continue
    for t_idx, t in enumerate(tables.tables):
        # Let's find unique column boundary coordinates
        # We can look at cells that have x0 and x1
        x0_coords = set()
        x1_coords = set()
        for cell in t.cells:
            if cell:
                x0_coords.add(round(cell[0], 2))
                x1_coords.add(round(cell[2], 2))
        
        # Sort them
        sorted_x0 = sorted(list(x0_coords))
        sorted_x1 = sorted(list(x1_coords))
        print(f"Page {page_num + 1} Table {t_idx + 1}: x0={sorted_x0} | x1={sorted_x1}")

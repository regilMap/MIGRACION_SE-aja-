import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[19] # Page 20
tables = page.find_tables()
if tables.tables:
    t = tables.tables[0]
    print(f"Table bbox: {t.bbox}")
    print("Extracting text from each unique cell bbox:")
    # Get unique bboxes from cells (t.cells contains a flat list of cell bboxes, some can be None)
    unique_cells = []
    seen = set()
    for cell in t.cells:
        if cell and cell not in seen:
            seen.add(cell)
            unique_cells.append(cell)
            
    # Sort cells by y0, then x0
    unique_cells.sort(key=lambda c: (c[1], c[0]))
    
    for idx, cell in enumerate(unique_cells):
        text = page.get_text("text", clip=cell).strip()
        cleaned_text = " ".join(text.split())
        print(f"Cell {idx+1}: bbox=({cell[0]:.1f}, {cell[1]:.1f}, {cell[2]:.1f}, {cell[3]:.1f}) | {repr(cleaned_text)}")
else:
    print("No tables found")

import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[19] # Page 20
try:
    tables = page.find_tables()
    print(f"Number of tables found: {len(tables)}")
    for i, table in enumerate(tables):
        print(f"Table {i+1}:")
        data = table.extract()
        for r in data[:5]:
            print("  ", r)
except Exception as e:
    print(f"Error extracting tables: {e}")

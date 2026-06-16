import fitz
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

queries = ["4.01", "4.02", "4.03", "8.01", "9.01"]
for q in queries:
    print(f"\nSearching for '{q}'...")
    found = False
    for i, page in enumerate(doc):
        text = page.get_text()
        if q in text:
            print(f"  Page {i+1} matches!")
            found = True
            # print a bit of text around the match
            idx = text.find(q)
            start = max(0, idx - 100)
            end = min(len(text), idx + 400)
            print(text[start:end])
            print("-" * 50)
    if not found:
        print(f"  No match found for '{q}' in PDF.")

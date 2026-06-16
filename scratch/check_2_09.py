import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

found = False
for page_num in range(len(doc)):
    text = doc[page_num].get_text("text")
    if "2.09" in text or "2.9" in text:
        print(f"--- Page {page_num + 1} contains '2.09' or '2.9' ---")
        print(text[:1500])
        found = True

if not found:
    print("Subindicator 2.09 was not found in the PDF.")

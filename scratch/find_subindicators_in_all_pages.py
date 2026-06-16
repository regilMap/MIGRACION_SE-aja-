import fitz
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

print("Searching all pages for Subindicator patterns...")
for i, page in enumerate(doc):
    text = page.get_text()
    # Find patterns like "Sub Indicador", "Subindicador", or matches to standard code patterns
    matches = re.findall(r'(?:sub\s*indicador|subindicador|indicador)\s*:?\s*([\d\.]+)', text, re.IGNORECASE)
    # Also find codes at the start of a line or in text
    code_matches = re.findall(r'\b([1-9]\.0[1-9]|[1-9]\.[1-9]\d?)\b', text)
    
    if matches or code_matches:
        print(f"Page {i+1}: sub_matches={matches}, code_matches={set(code_matches)}")

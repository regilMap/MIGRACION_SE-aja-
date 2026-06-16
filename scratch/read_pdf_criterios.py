import sys
import os
import re
import pdfplumber

sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = "2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    # Read all pages and search for percentage patterns near criterio keywords
    # Look for patterns like: "100", "70", "30", etc. associated with criterios
    # First, let's dump pages 1-40 to find the structure
    for page_num in range(min(40, len(pdf.pages))):
        text = pdf.pages[page_num].extract_text()
        if text and ('criterio' in text.lower() or '%' in text or '1.01' in text or '1.05' in text):
            print(f"\n=== PAGE {page_num+1} ===")
            print(text[:3000])

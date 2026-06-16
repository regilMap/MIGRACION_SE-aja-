import fitz # PyMuPDF
import sys

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"

try:
    doc = fitz.open(pdf_path)
    print(f"Total pages: {len(doc)}")
    
    # Print text from the first 5 pages to inspect the format
    for page_num in range(min(5, len(doc))):
        print(f"--- PAGE {page_num+1} ---")
        text = doc[page_num].get_text("text")
        print(text[:1500]) # Print first 1500 characters of each page
except Exception as e:
    print(f"Error: {e}")

import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

page = doc[31] # Page 32
blocks = page.get_text("blocks")
# Sort blocks by y0, then x0
blocks.sort(key=lambda b: (b[1], b[0]))

print("Blocks on Page 32 sorted by layout:")
for b in blocks:
    x0, y0, x1, y1, text, block_no, block_type = b
    cleaned_text = " ".join(text.split())
    if cleaned_text:
        print(f"BNo: {block_no} | bbox=({x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f}) | {cleaned_text}")

import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

output_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\extracted_tables.txt"

with open(output_path, "w", encoding="utf-8") as f:
    for page_num in range(18, 76): # Pages 19 to 76 (0-indexed 18 to 75)
        f.write(f"=================================================================\n")
        f.write(f"PAGE {page_num + 1}\n")
        f.write(f"=================================================================\n")
        text = doc[page_num].get_text("text")
        f.write(text)
        f.write("\n\n")

print(f"Dumped text from pages 19 to 76 to {output_path}")

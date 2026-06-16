import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\extracted_tables.txt"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Let's split by PAGE separator
pages = re.split(r"={10,}\s*PAGE \d+\s*={10,}", content)
page_numbers = re.findall(r"PAGE (\d+)", content)

print(f"Total pages parsed: {len(page_numbers)}")

for idx, page_text in enumerate(pages[1:]): # skip first split before first header
    page_num = page_numbers[idx]
    lines = [line.strip() for line in page_text.splitlines() if line.strip()]
    indicador_lines = [l for l in lines if "indicador" in l.lower()]
    evidencia_lines = [l for l in lines if "evidencia" in l.lower()]
    if indicador_lines or evidencia_lines:
        print(f"Page {page_num}:")
        print(f"  Indicador lines (first 2): {indicador_lines[:2]}")
        print(f"  Evidencia lines (first 2): {evidencia_lines[:2]}")

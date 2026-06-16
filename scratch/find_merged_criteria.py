import fitz
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

def clean_text(text):
    if not text:
        return ""
    text = str(text).replace("\r", " ").replace("\n", " ")
    return re.sub(r'\s+', ' ', text).strip()

def is_scoring_table(text):
    text_clean = re.sub(r'\s+', ' ', text).lower().strip()
    if "nivel de avance" in text_clean:
        return True
    if "objetivo logrado" in text_clean or "cierto avance" in text_clean or "poco avance" in text_clean or "sin avance" in text_clean:
        return True
    if re.search(r'(?:▪|o|○|\*|-)?\s*\b(100|95|90|85|80|75|70|65|60|50|40|30|20|10|0)\b(?:\s*[\.\+\%▪]|points|puntos|pto|pts)', text_clean):
        return True
    return False

active_table = None
current_subindicador = ""
active_sub_code = ""

print("Scanning for merged criteria cells...")

for page_num in range(18, 79):
    page = doc[page_num]
    tables = page.find_tables()
    if not tables.tables:
        continue
        
    for t_idx, t in enumerate(tables.tables):
        rows = t.extract()
        if not rows or len(rows) < 1:
            continue
            
        header_row_idx = -1
        
        # Subindicator check
        for r_idx, r in enumerate(rows):
            clean_row = [clean_text(cell) for cell in r]
            if any("sub" in cell.lower() and "indicador" in cell.lower() for cell in clean_row):
                for cell in clean_row:
                    if cell and not ("sub" in cell.lower() and "indicador" in cell.lower()) and cell.lower() != "cumple":
                        current_subindicador = cell
                        break
                        
        if current_subindicador:
            match_sub = re.match(r'^([\w\d\.\-]+)', current_subindicador)
            if match_sub:
                active_sub_code = match_sub.group(1).strip(" .")
                
        # Header check
        for r_idx, r in enumerate(rows):
            clean_row = [clean_text(cell) for cell in r]
            has_ev = False
            has_cr = False
            for i, cell in enumerate(clean_row):
                if "evidencia" in cell.lower() and not "criterio" in cell.lower():
                    has_ev = True
                elif "criterio" in cell.lower():
                    has_cr = True
            if has_ev and has_cr:
                header_row_idx = r_idx
                break
                
        if header_row_idx == -1:
            table_text = " ".join([" ".join([clean_text(c) for c in r]) for r in rows])
            if is_scoring_table(table_text):
                continue
            
        start_row = 0
        if header_row_idx != -1:
            start_row = header_row_idx + 1
            
        for r_idx in range(start_row, len(rows)):
            row = rows[r_idx]
            for cell in row:
                cell_text = clean_text(cell)
                # Search for score indicators inside the text, e.g. "80. ", "50. ", etc.
                match = re.search(r'\b(80|75|70|60|50|40|30|20|10)\.\s+[A-Z]', cell_text)
                if match:
                    print(f"Page {page_num+1} | Sub: {active_sub_code} | Merged Cell: {repr(cell_text)}")

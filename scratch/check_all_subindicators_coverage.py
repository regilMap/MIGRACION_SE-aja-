import fitz
import re
import sys
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
truth_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\db_evidencias_truth.txt"
doc = fitz.open(pdf_path)

def clean_text(text):
    if not text:
        return ""
    text = str(text).replace("\r", " ").replace("\n", " ")
    return re.sub(r'\s+', ' ', text).strip()

def is_new_item(text):
    text = text.strip()
    if not text:
        return False
    if text.startswith("("):
        return False
    if text.lower().startswith("nota"):
        return False
    if text.lower().startswith("evidencia subida"):
        return False
    if text.lower().startswith("evidencias subidas"):
        return False
    
    first_char = text[0]
    if first_char.isalpha() and first_char.islower():
        return False
    return True

def is_scoring_table(text):
    text_clean = re.sub(r'\s+', ' ', text).lower().strip()
    if "nivel de avance" in text_clean:
        return True
    if "objetivo logrado" in text_clean or "cierto avance" in text_clean or "poco avance" in text_clean or "sin avance" in text_clean:
        return True
    if re.search(r'(?:▪|o|○|\*|-)?\s*\b(100|95|90|85|80|75|70|65|60|50|40|30|20|10|0)\b(?:\s*[\.\+\%▪]|points|puntos|pto|pts)', text_clean):
        return True
    if re.search(r'\b(100|95|90|85|80|75|70|65|60|50|40|30|20|10|0)\b\s*(?:▪|o|○|\*|-)', text_clean):
        return True
    if re.search(r'\+\d+\s*(?:puntos|pts|pto)', text_clean):
        return True
    return False

SCORING_LABELS = {
    "objetivo", "logrado", "cierto", "avance", "poco", "sin", "nivel",
    "objetivo logrado", "cierto avance", "poco avance", "sin avance", "nivel de avance",
    "cumple", "si", "no", "criterio", "criterios", "verificación", "criterios de verificación"
}

def load_db_evidences(path):
    evidences = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("Id:"):
                continue
            parts = line.split(" | ")
            if len(parts) < 4:
                continue
            id_part = parts[0].replace("Id:", "").strip()
            code_part = parts[1].replace("Code:", "").strip()
            name_part = parts[2].replace("Name:", "").strip()
            val_part = parts[3].replace("Val:", "").strip()
            
            clean_name = name_part
            clean_name = clean_name.replace(code_part, "").strip()
            clean_name = re.sub(r'^[\d\.]+\s+', '', clean_name).strip()
            
            evidences.append({
                "id": int(id_part),
                "code": code_part,
                "name": clean_name,
                "full_name": name_part,
                "value": float(val_part)
            })
    return evidences

db_evidences = load_db_evidences(truth_path)

db_subs = set()
for ev in db_evidences:
    code = ev["code"]
    match = re.search(r'(\d+)\.(\d+)', code)
    if match:
        db_subs.add(f"{int(match.group(1))}.{int(match.group(2)):02d}")

db_by_sub = {}
for ev in db_evidences:
    code = ev["code"]
    match = re.search(r'(\d+)\.(\d+)', code)
    if match:
        sub_key = f"{int(match.group(1))}.{int(match.group(2)):02d}"
        sub_raw = f"{match.group(1)}.{match.group(2)}"
        
        for k in [sub_key, sub_raw]:
            if k not in db_by_sub:
                db_by_sub[k] = []
            if ev not in db_by_sub[k]:
                db_by_sub[k].append(ev)

extracted_tables = []
active_table = None

current_ambito = ""
current_indicador = ""
current_subindicador = ""
active_sub_code = ""
active_x_divide = 190.0

for page_num in range(18, 76):
    page = doc[page_num]
    tables = page.find_tables()
    if not tables.tables:
        continue
        
    for t_idx, t in enumerate(tables.tables):
        rows = t.extract()
        if not rows or len(rows) < 1:
            continue
            
        header_row_idx = -1
        
        for r_idx, r in enumerate(rows):
            clean_row = [clean_text(cell) for cell in r]
            row_str = " ".join(clean_row).lower()
            
            if "ámbito" in row_str or "ambito" in row_str:
                for cell in clean_row:
                    if "ámbito" in cell.lower() or "ambito" in cell.lower():
                        current_ambito = cell
                        break
            if any(cell.lower() == "indicador" for cell in clean_row):
                for cell in clean_row:
                    if cell and cell.lower() != "indicador":
                        current_indicador = cell
                        break
            if any("sub" in cell.lower() and "indicador" in cell.lower() for cell in clean_row):
                for cell in clean_row:
                    if cell and not ("sub" in cell.lower() and "indicador" in cell.lower()) and cell.lower() != "cumple":
                        current_subindicador = cell
                        break
                        
        for r_idx, r in enumerate(rows):
            clean_row = [clean_text(cell) for cell in r]
            has_ev = False
            has_cr = False
            ev_bbox = None
            cr_bbox = None
            for i, cell in enumerate(clean_row):
                cell_bbox = t.rows[r_idx].cells[i]
                if not cell_bbox:
                    continue
                if "evidencia" in cell.lower() and not "criterio" in cell.lower():
                    has_ev = True
                    ev_bbox = cell_bbox
                elif "criterio" in cell.lower():
                    has_cr = True
                    cr_bbox = cell_bbox
            if has_ev and has_cr:
                header_row_idx = r_idx
                active_x_divide = (ev_bbox[2] + cr_bbox[0]) / 2
                break
                
        if current_subindicador:
            match_sub = re.match(r'^(\d+\.\d+)', current_subindicador.strip())
            if match_sub:
                active_sub_code = match_sub.group(1).strip()
                # normalize to 1.01 style
                m2 = re.match(r'^(\d+)\.(\d+)', active_sub_code)
                if m2:
                    active_sub_code = f"{int(m2.group(1))}.{int(m2.group(2)):02d}"
                
        if header_row_idx == -1:
            table_text = " ".join([" ".join([clean_text(c) for c in r]) for r in rows])
            if is_scoring_table(table_text):
                active_table = None
                continue
            
        if header_row_idx == -1 and not active_table:
            continue
            
        start_row = 0
        if header_row_idx != -1:
            start_row = header_row_idx + 1
            active_table = {
                "ambito": current_ambito,
                "indicador": current_indicador,
                "subindicador": current_subindicador,
                "sub_code": active_sub_code,
                "pages": [page_num + 1],
                "rows": []
            }
            extracted_tables.append(active_table)
        else:
            if active_table:
                active_table["pages"].append(page_num + 1)
                
        for r_idx in range(start_row, len(rows)):
            row = rows[r_idx]
            row_cells = t.rows[r_idx].cells
            evidence_parts = []
            criteria_parts = []
            
            for c_idx, cell in enumerate(row):
                cell_text = clean_text(cell)
                if not cell_text:
                    continue
                cell_bbox = row_cells[c_idx]
                if not cell_bbox:
                    continue
                
                x0, y0, x1, y1 = cell_bbox
                x_mid = (x0 + x1) / 2
                
                if x_mid >= 380.0:
                    continue
                if cell_text.lower() in ["si", "no", "cumple", "s", "i"]:
                    continue
                    
                if x_mid < active_x_divide:
                    evidence_parts.append(cell_text)
                else:
                    criteria_parts.append(cell_text)
                    
            ev_str = " ".join(evidence_parts).strip()
            cr_str = " ".join(criteria_parts).strip()
            
            if not ev_str and not cr_str:
                continue
                
            if active_table:
                active_table["rows"].append((ev_str, cr_str))

extracted_subs = set(t["sub_code"] for t in extracted_tables)

print("DB SUBINDICATORS:")
print(sorted(list(db_subs)))
print("\nEXTRACTED SUBINDICATORS:")
print(sorted(list(extracted_subs)))

missing = db_subs - extracted_subs
print("\nMISSING SUBINDICATORS (in DB but not extracted):")
print(sorted(list(missing)))

extra = extracted_subs - db_subs
print("\nEXTRA SUBINDICATORS (extracted but not in DB):")
print(sorted(list(extra)))

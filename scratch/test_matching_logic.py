import fitz
import json
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
    text_clean = text.lower().strip()
    if "nivel de avance" in text_clean:
        return True
    if "objetivo logrado" in text_clean or "cierto avance" in text_clean or "poco avance" in text_clean or "sin avance" in text_clean:
        return True
    # Match bullet score: e.g. "▪ 100" or "▪ 70" or "+100 puntos"
    if re.search(r'▪\s*(?:100|95|90|85|80|75|70|65|60|50|40|30|20|10|0)\b', text_clean):
        return True
    if re.search(r'\+\d+\s*(?:puntos|pts|pto)', text_clean):
        return True
    return False

# Load DB evidences from baseline truth file
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
            
            # Clean database name by removing the code prefix (e.g. "1.01.2 " or "Np 7.01.2 ")
            clean_name = name_part
            clean_name = clean_name.replace(code_part, "").strip()
            
            # Additional cleanup of leading numbers/dots if still present
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
print(f"Loaded {len(db_evidences)} evidences from database baseline.")

# Group DB evidences by subindicator prefix for scoped matching
# e.g., "1.01" -> list of evidences
db_by_sub = {}
for ev in db_evidences:
    code = ev["code"]
    # Normalize code prefix: e.g. "Np 7.01.1" -> "7.01", "1.01.2" -> "1.01"
    match = re.search(r'(\d+)\.(\d+)', code)
    if match:
        sub_prefix = f"{int(match.group(1))}.{int(match.group(2)):02d}"  # e.g., "1.01"
        # If there's Np/Ns, we can keep track of it, but let's key by "1.01" or "7.01"
        sub_key = f"{match.group(1)}.{match.group(2)}" # e.g. "1.01" or "7.01"
        
        # Add both to dictionary
        if sub_key not in db_by_sub:
            db_by_sub[sub_key] = []
        db_by_sub[sub_key].append(ev)
        
        # Also key by formatted sub_prefix if different
        if sub_prefix != sub_key:
            if sub_prefix not in db_by_sub:
                db_by_sub[sub_prefix] = []
            db_by_sub[sub_prefix].append(ev)

# Extract Tables from PDF
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
        
        # Update metadata
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
                        
        # Get header index and calculate dynamic x-divide
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
            match_sub = re.match(r'^([\w\d\.\-]+)', current_subindicador)
            if match_sub:
                active_sub_code = match_sub.group(1).strip(" .")
                
        # Skip scoring tables
        table_text = " ".join([" ".join([clean_text(c) for c in r]) for r in rows])
        if header_row_idx == -1 and is_scoring_table(table_text):
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

# Reconstruct and match
def clean_ev_name_for_matching(name):
    # Remove things like "(Evidencia subida...)"
    name = re.split(r'\(Evidencia subida|\(Evidencias subidas', name, flags=re.IGNORECASE)[0].strip()
    name = re.split(r'Nota para el equipo|Nota:', name, flags=re.IGNORECASE)[0].strip()
    name = name.rstrip(".,;:- ")
    return name.lower().strip()

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

print(f"\nProcessing {len(extracted_tables)} extracted tables...")
matched_count = 0
unmatched_count = 0

for table in extracted_tables:
    grouped_items = []
    current_ev_name = ""
    current_ev_raw = ""
    current_criteria_list = []
    
    for ev_text, cr_text in table["rows"]:
        if ev_text:
            if is_new_item(ev_text):
                if current_ev_name or current_criteria_list:
                    grouped_items.append({
                        "evidence_name": current_ev_name.strip(),
                        "evidence_raw": current_ev_raw.strip(),
                        "criteria": current_criteria_list
                    })
                current_ev_name = ev_text
                current_ev_raw = ev_text
                current_criteria_list = []
            else:
                if current_ev_name:
                    current_ev_name += " " + ev_text
                else:
                    current_ev_name = ev_text
                current_ev_raw += "\n" + ev_text
                
        if cr_text:
            if is_new_item(cr_text):
                current_criteria_list.append(cr_text)
            else:
                if current_criteria_list:
                    current_criteria_list[-1] += " " + cr_text
                else:
                    current_criteria_list.append(cr_text)
                    
    if current_ev_name or current_criteria_list:
        grouped_items.append({
            "evidence_name": current_ev_name.strip(),
            "evidence_raw": current_ev_raw.strip(),
            "criteria": current_criteria_list
        })
        
    # Now match evidences for this table
    # Table sub_code e.g. "1.01"
    sub_code = table["sub_code"]
    # Normalize sub_code for database lookup (e.g. remove leading zeros in parts if db uses them)
    # E.g. "1.01" in PDF -> database has subindicator code "1.01"
    # E.g. "5.01" in PDF -> database has "5.01"
    norm_sub_code = sub_code
    
    candidates = db_by_sub.get(norm_sub_code, [])
    if not candidates:
        # Try fuzzy match of sub_code in keys
        for key in db_by_sub.keys():
            if norm_sub_code.replace("0", "") == key.replace("0", ""):
                candidates = db_by_sub[key]
                break
                
    print(f"\nSubindicador: {sub_code} (Found {len(candidates)} candidates in DB)")
    
    for item in grouped_items:
        pdf_ev_name = item["evidence_name"]
        pdf_clean = clean_ev_name_for_matching(pdf_ev_name)
        
        best_candidate = None
        best_score = 0.0
        
        for cand in candidates:
            cand_clean = clean_ev_name_for_matching(cand["name"])
            score = similarity(pdf_clean, cand_clean)
            if score > best_score:
                best_score = score
                best_candidate = cand
                
        if best_candidate and best_score > 0.45:
            print(f"  MATCHED: '{pdf_ev_name[:40]}...' -> Code: {best_candidate['code']} (ID: {best_candidate['id']}) [Score: {best_score:.2f}]")
            matched_count += 1
        else:
            print(f"  WARNING: UNMATCHED: '{pdf_ev_name[:40]}...' (Best score: {best_score:.2f} with '{best_candidate['name'][:40] if best_candidate else 'None'}...')")
            unmatched_count += 1

print(f"\nSummary: Total Matched = {matched_count}, Unmatched = {unmatched_count}")

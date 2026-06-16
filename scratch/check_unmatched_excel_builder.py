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
    text_clean = text.lower().strip()
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
            match_sub = re.match(r'^([\w\d\.\-]+)', current_subindicador)
            if match_sub:
                active_sub_code = match_sub.group(1).strip(" .")
                
        # Skip scoring tables and close active table if we hit one (only if no header is found on this page)
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

def clean_name_for_prefix(name):
    name = re.sub(r'^[A-Za-z\s]*\d+\.\d+\.\d+\s+', '', name)
    name = re.split(r'\(Evidencia subida|\(Evidencias subidas|Nota para|Nota:', name, flags=re.IGNORECASE)[0].strip()
    name = name.rstrip(".,;:- ")
    name = re.sub(r'[^\w\s]', ' ', name.lower())
    return " ".join(name.split())

def standard_heuristic_merge(table_rows):
    merged = []
    current_ev_name = ""
    current_ev_raw = ""
    current_criteria_list = []
    
    for ev_text, cr_text in table_rows:
        clean_ev_c = ev_text.lower().strip().rstrip(".,;:-")
        clean_cr_c = cr_text.lower().strip().rstrip(".,;:-")
        
        filtered_ev = "" if clean_ev_c in SCORING_LABELS else ev_text
        filtered_cr = "" if clean_cr_c in SCORING_LABELS else cr_text
        
        if not filtered_ev and not filtered_cr:
            continue
            
        if filtered_ev:
            if is_new_item(filtered_ev):
                if current_ev_name or current_criteria_list:
                    merged.append({
                        "evidence_name": current_ev_name.strip(),
                        "evidence_raw": current_ev_raw.strip(),
                        "criteria": current_criteria_list
                    })
                current_ev_name = filtered_ev
                current_ev_raw = filtered_ev
                current_criteria_list = []
            else:
                if current_ev_name:
                    current_ev_name += " " + filtered_ev
                else:
                    current_ev_name = filtered_ev
                current_ev_raw += "\n" + filtered_ev
                
        if filtered_cr:
            if is_new_item(filtered_cr):
                current_criteria_list.append(filtered_cr)
            else:
                if current_criteria_list:
                    current_criteria_list[-1] += " " + filtered_cr
                else:
                    current_criteria_list.append(filtered_cr)
                    
    if current_ev_name or current_criteria_list:
        merged.append({
            "evidence_name": current_ev_name.strip(),
            "evidence_raw": current_ev_raw.strip(),
            "criteria": current_criteria_list
        })
    return merged

def candidate_guided_merge(table_rows, candidates):
    if not candidates:
        return standard_heuristic_merge(table_rows)
        
    merged = []
    current_ev = ""
    current_ev_raw = ""
    current_criteria = []
    
    cand_names = [clean_name_for_prefix(c["name"]) for c in candidates]
    
    for ev_text, cr_text in table_rows:
        clean_ev_c = ev_text.lower().strip().rstrip(".,;:-")
        clean_cr_c = cr_text.lower().strip().rstrip(".,;:-")
        
        filtered_ev = "" if clean_ev_c in SCORING_LABELS else ev_text
        filtered_cr = "" if clean_cr_c in SCORING_LABELS else cr_text
        
        if not filtered_ev and not filtered_cr:
            continue
            
        if not filtered_ev:
            if filtered_cr:
                current_criteria.append(filtered_cr)
            continue
            
        if not current_ev:
            current_ev = filtered_ev
            current_ev_raw = filtered_ev
            if filtered_cr:
                current_criteria.append(filtered_cr)
            continue
            
        current_clean = clean_name_for_prefix(current_ev)
        combined_clean = clean_name_for_prefix(current_ev + " " + filtered_ev)
        
        is_continuation = False
        if not is_new_item(filtered_ev):
            is_continuation = True
        else:
            for cand in cand_names:
                if cand.startswith(current_clean) and len(cand) > len(current_clean):
                    if cand.startswith(combined_clean):
                        is_continuation = True
                        break
                        
        if is_continuation:
            current_ev += " " + filtered_ev
            current_ev_raw += "\n" + filtered_ev
            if filtered_cr:
                current_criteria.append(filtered_cr)
        else:
            merged.append({
                "evidence_name": current_ev.strip(),
                "evidence_raw": current_ev_raw.strip(),
                "criteria": current_criteria
            })
            current_ev = filtered_ev
            current_ev_raw = filtered_ev
            current_criteria = [filtered_cr] if filtered_cr else []
            
    if current_ev or current_criteria:
        merged.append({
            "evidence_name": current_ev.strip(),
            "evidence_raw": current_ev_raw.strip(),
            "criteria": current_criteria
        })
        
    return merged

MANUAL_MAPPING_OVERRIDES = {
    ("1.04", "presupuesto"): "1.04.1",
    ("1.04", "reporte"): "1.04.1",
    ("1.04", "acta"): "1.04.1",
    ("1.05", "informes"): "1.05.1",
    ("2.01", "instrumento"): "2.01.1",
    ("2.01", "informe"): "2.01.2",
    ("2.02", "planes"): "2.02.1",
    ("2.03", "informe"): "2.03.1",
    ("2.04", "planes"): "2.04.1",
    ("2.05", "informe"): "2.05.1",
    ("3.01", "registro"): "3.01.1",
    ("6.01", "reporte"): "6.01.1",
    ("7.01", "matriz"): "Np 7.01.1",
    ("7.02", "resultados"): "Ns 7.02.1"
}

def clean_name_for_matching(name):
    name = re.split(r'\(Evidencia subida|\(Evidencias subidas|Nota para', name, flags=re.IGNORECASE)[0].strip()
    name = name.rstrip(".,;:- ")
    return name.lower().strip()

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

flat_rows = []
for table in extracted_tables:
    sub_code = table["sub_code"]
    candidates = db_by_sub.get(sub_code, [])
    if not candidates:
        for key in db_by_sub.keys():
            if sub_code.replace("0", "") == key.replace("0", ""):
                candidates = db_by_sub[key]
                break
                
    grouped_items = candidate_guided_merge(table["rows"], candidates)
    
    for item in grouped_items:
        pdf_ev_name = item["evidence_name"]
        criteria_to_process = item["criteria"] if item["criteria"] else [""]
        for criterion in criteria_to_process:
            override_code = ""
            for (override_sub, kw), target_code in MANUAL_MAPPING_OVERRIDES.items():
                if sub_code == override_sub and kw in pdf_ev_name.lower():
                    override_code = target_code
                    break
            
            if sub_code == "5.01":
                if "no vinculado" in criterion.lower():
                    override_code = "5.01.2"
                else:
                    override_code = "5.01.1"
            elif sub_code == "5.06":
                if "no vinculado" in criterion.lower():
                    override_code = "5.06.2"
                else:
                    override_code = "5.06.1"
            
            best_cand = None
            if override_code:
                for cand in db_evidences:
                    if cand["code"] == override_code:
                        best_cand = cand
                        best_score = 1.0
                        break
            else:
                best_score = 0.0
                clean_ev = clean_name_for_matching(pdf_ev_name)
                clean_crit = clean_name_for_matching(criterion)
                for cand in candidates:
                    clean_cand = clean_name_for_matching(cand["name"])
                    score_ev = similarity(clean_ev, clean_cand)
                    score_crit = similarity(clean_crit, clean_cand)
                    
                    if clean_ev in clean_cand or clean_cand in clean_ev:
                        score_ev = max(score_ev, 0.7)
                    if clean_crit in clean_cand or clean_cand in clean_crit:
                        if len(clean_crit) > 10 and len(clean_cand) > 10:
                            score_crit = max(score_crit, 0.8)
                    
                    score = max(score_ev, score_crit)
                    if score > best_score:
                        best_score = score
                        best_cand = cand
            
            db_code = ""
            if best_cand and (best_score > 0.45 or override_code):
                db_code = best_cand["code"]
            
            flat_rows.append({
                "sub_code": sub_code,
                "pdf_evidence": pdf_ev_name,
                "pdf_criterion": criterion,
                "matched_code": db_code,
                "match_score": best_score
            })

unmatched = [r for r in flat_rows if not r["matched_code"]]
print(f"Total rows: {len(flat_rows)}")
print(f"Unmatched rows: {len(unmatched)}")
for i, r in enumerate(unmatched):
    print(f"{i+1}. Sub: {r['sub_code']} | Ev: {repr(r['pdf_evidence'])} | Crit: {repr(r['pdf_criterion'])}")

import fitz
import json
import re
import sys
import os
from difflib import SequenceMatcher
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

# Paths
pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
truth_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\db_evidencias_truth.txt"
excel_output_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\Criterios_Evaluacion_SISMAP.xlsx"

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
    # Match bullet score: e.g. "▪ 100" or "75 ▪" or "+100 puntos" or "100 ptos"
    if re.search(r'(?:▪|o|○|\*|-)?\s*\b(100|95|90|85|80|75|70|65|60|50|40|30|20|10|0)\b(?:\s*[\.\+\%▪]|points|puntos|pto|pts)', text_clean):
        return True
    if re.search(r'\b(100|95|90|85|80|75|70|65|60|50|40|30|20|10|0)\b\s*(?:▪|o|○|\*|-)', text_clean):
        return True
    if re.search(r'\+\d+\s*(?:puntos|pts|pto)', text_clean):
        return True
    return False

# Standalone scoring labels to filter out
SCORING_LABELS = {
    "objetivo", "logrado", "cierto", "avance", "poco", "sin", "nivel",
    "objetivo logrado", "cierto avance", "poco avance", "sin avance", "nivel de avance",
    "cumple", "si", "no", "criterio", "criterios", "verificación", "criterios de verificación"
}

# Manual overrides for tricky evidence matches
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
    ("3.02", "plan operativo"): "3.02.1",
    ("6.01", "reporte"): "6.01.1",
    ("7.01", "matriz"): "Np 7.01.1",
    ("7.02", "resultados"): "Ns 7.02.1"
}

# Load DB evidences
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

# Group DB evidences by subindicator prefix for scoped matching
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

# Extract Tables from PDF
extracted_tables = []
active_table = None

current_ambito = ""
current_indicador = ""
current_subindicador = ""
active_sub_code = ""
active_x_divide = 190.0

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
                if active_sub_code == "2.03":
                    if "80." in cr_str:
                        parts = re.split(r'\s*80\.\s*', cr_str)
                        if len(parts) == 2:
                            active_table["rows"].append((ev_str, parts[0].strip()))
                            active_table["rows"].append((ev_str, parts[1].strip()))
                        else:
                            active_table["rows"].append((ev_str, cr_str))
                    elif cr_str.startswith("50."):
                        clean_cr = re.sub(r'^50\.\s*', '', cr_str).strip()
                        active_table["rows"].append((ev_str, clean_cr))
                    else:
                        active_table["rows"].append((ev_str, cr_str))
                else:
                    active_table["rows"].append((ev_str, cr_str))

def clean_name_for_matching(name):
    name = re.split(r'\(Evidencia subida|\(Evidencias subidas|Nota para', name, flags=re.IGNORECASE)[0].strip()
    name = name.rstrip(".,;:- ")
    return name.lower().strip()

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def clean_name_for_prefix(name):
    name = re.sub(r'^[A-Za-z\s]*\d+\.\d+\.\d+\s+', '', name)
    name = re.split(r'\(Evidencia subida|\(Evidencias subidas|Nota para|Nota:', name, flags=re.IGNORECASE)[0].strip()
    name = name.rstrip(".,;:- ")
    name = re.sub(r'[^\w\s]', ' ', name.lower())
    return " ".join(name.split())

def candidate_guided_merge(table_rows, candidates):
    if not candidates:
        return standard_heuristic_merge(table_rows)
        
    merged = []
    current_ev = ""
    current_ev_raw = ""
    current_criteria = []
    
    cand_names = [clean_name_for_prefix(c["name"]) for c in candidates]
    
    for ev_text, cr_text in table_rows:
        # Filter out standalone scoring labels
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
            # Check manual overrides first
            override_code = ""
            
            # Simple overrides
            for (override_sub, kw), target_code in MANUAL_MAPPING_OVERRIDES.items():
                if sub_code == override_sub and kw in pdf_ev_name.lower():
                    override_code = target_code
                    break
            
            # Subindicator 2.03 specific overrides
            if sub_code == "2.03":
                if "4to" in criterion:
                    override_code = "2.03.1"
                elif "3er" in criterion or "segundo" in criterion:
                    override_code = "2.03.2"
                elif "primer" in criterion:
                    override_code = "2.03.3"
            
            # Subindicator-specific override conditions for Indicator 5 (5.01 to 5.10)
            elif sub_code.startswith("5."):
                match = re.search(r'5\.(\d+)', sub_code)
                if match:
                    sub_num = int(match.group(1))
                    if 1 <= sub_num <= 10:
                        crit_lower = criterion.lower()
                        if "no vinculado" in crit_lower or "entre 50" in crit_lower or "50 y" in crit_lower or "50% y" in crit_lower or "menos del 50" in crit_lower or "menos de 50" in crit_lower:
                            override_code = f"5.{sub_num:02d}.2"
                        else:
                            override_code = f"5.{sub_num:02d}.1"
                    
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
            db_id = ""
            db_name = ""
            
            if best_cand and (best_score > 0.45 or override_code):
                db_code = best_cand["code"]
                db_id = str(best_cand["id"])
                db_name = best_cand["name"]
                
            flat_rows.append({
                "ambito": table["ambito"],
                "indicador": table["indicador"],
                "subindicador": table["subindicador"],
                "sub_code": sub_code,
                "pdf_evidence": pdf_ev_name,
                "pdf_criterion": criterion,
                "matched_code": db_code,
                "db_ev_id": db_id,
                "db_ev_name": db_name,
                "match_score": best_score
            })

# Add manual rows for subindicators that do not have standard tables in the PDF
manual_rows = [
    # 4.01
    {
        "ambito": "SEGUNDO ÁMBITO. LIDERAZGO Y DESEMPEÑO DEL PERSONAL DIRECTIVO, DOCENTE, ADMINISTRATIVO Y DE APOYO",
        "indicador": "IBOG 4. Cultura organizacional y satisfacción",
        "subindicador": "4.01. Cultura del centro y clima organizacional del centro",
        "sub_code": "4.01",
        "pdf_evidence": "Puntuación vinculada a la mejora de la cultura y clima organizacional",
        "pdf_criterion": "El Índice de Valoración del Clima Organización es de 80 o más puntos al final de cada período de medición.",
        "matched_code": "4.01.1",
        "db_ev_id": "123",
        "db_ev_name": "Puntuación vinculada a la mejora de la cultura y clima organizacional"
    },
    {
        "ambito": "SEGUNDO ÁMBITO. LIDERAZGO Y DESEMPEÑO DEL PERSONAL DIRECTIVO, DOCENTE, ADMINISTRATIVO Y DE APOYO",
        "indicador": "IBOG 4. Cultura organizacional y satisfacción",
        "subindicador": "4.01. Cultura del centro y clima organizacional del centro",
        "sub_code": "4.01",
        "pdf_evidence": "Implementación de las acciones",
        "pdf_criterion": "El centro implementa las acciones de mejora vinculadas a la cultura y Clima Organizacional.",
        "matched_code": "4.01.2",
        "db_ev_id": "124",
        "db_ev_name": "Implementación de las acciones"
    },
    {
        "ambito": "SEGUNDO ÁMBITO. LIDERAZGO Y DESEMPEÑO DEL PERSONAL DIRECTIVO, DOCENTE, ADMINISTRATIVO Y DE APOYO",
        "indicador": "IBOG 4. Cultura organizacional y satisfacción",
        "subindicador": "4.01. Cultura del centro y clima organizacional del centro",
        "sub_code": "4.01",
        "pdf_evidence": "Acciones de mejora",
        "pdf_criterion": "El Centro Educativo ha definido acciones de mejora semestral para el clima organizacional.",
        "matched_code": "4.01.3",
        "db_ev_id": "125",
        "db_ev_name": "Acciones de mejora del clima escolar"
    },
    {
        "ambito": "SEGUNDO ÁMBITO. LIDERAZGO Y DESEMPEÑO DEL PERSONAL DIRECTIVO, DOCENTE, ADMINISTRATIVO Y DE APOYO",
        "indicador": "IBOG 4. Cultura organizacional y satisfacción",
        "subindicador": "4.01. Cultura del centro y clima organizacional del centro",
        "sub_code": "4.01",
        "pdf_evidence": "Informe de encuesta de clima",
        "pdf_criterion": "El Centro Educativo cuenta con encuesta de clima organizacional vigente para cada semestre.",
        "matched_code": "4.01.4",
        "db_ev_id": "126",
        "db_ev_name": "Informe de encuesta de clima"
    },
    {
        "ambito": "SEGUNDO ÁMBITO. LIDERAZGO Y DESEMPEÑO DEL PERSONAL DIRECTIVO, DOCENTE, ADMINISTRATIVO Y DE APOYO",
        "indicador": "IBOG 4. Cultura organizacional y satisfacción",
        "subindicador": "4.01. Cultura del centro y clima organizacional del centro",
        "sub_code": "4.01",
        "pdf_evidence": "Capacitación",
        "pdf_criterion": "El personal del Centro Educativo participa en las acciones de capacitación impartidas para la aplicación de detección del clima organizacional y en la definición de planes de acción para su mejora.",
        "matched_code": "4.01.5",
        "db_ev_id": "127",
        "db_ev_name": "Capacitación"
    },
    # 4.02
    {
        "ambito": "SEGUNDO ÁMBITO. LIDERAZGO Y DESEMPEÑO DEL PERSONAL DIRECTIVO, DOCENTE, ADMINISTRATIVO Y DE APOYO",
        "indicador": "IBOG 4. Cultura organizacional y satisfacción",
        "subindicador": "4.02. Cultura del centro y clima escolar",
        "sub_code": "4.02",
        "pdf_evidence": "Puntuación vinculada a la mejora de la cultura y clima escolar",
        "pdf_criterion": "El Índice de Valoración del Clima Escolar es de 80 o más puntos al final de cada periodo de medición.",
        "matched_code": "4.02.1",
        "db_ev_id": "128",
        "db_ev_name": "Puntuación vinculada a la mejora de la cultura y clima escolar"
    },
    {
        "ambito": "SEGUNDO ÁMBITO. LIDERAZGO Y DESEMPEÑO DEL PERSONAL DIRECTIVO, DOCENTE, ADMINISTRATIVO Y DE APOYO",
        "indicador": "IBOG 4. Cultura organizacional y satisfacción",
        "subindicador": "4.02. Cultura del centro y clima escolar",
        "sub_code": "4.02",
        "pdf_evidence": "Implementación de las acciones",
        "pdf_criterion": "El centro implementa las acciones de mejora vinculadas a la cultura y clima escolar.",
        "matched_code": "4.02.2",
        "db_ev_id": "129",
        "db_ev_name": "Implementación de las acciones"
    },
    {
        "ambito": "SEGUNDO ÁMBITO. LIDERAZGO Y DESEMPEÑO DEL PERSONAL DIRECTIVO, DOCENTE, ADMINISTRATIVO Y DE APOYO",
        "indicador": "IBOG 4. Cultura organizacional y satisfacción",
        "subindicador": "4.02. Cultura del centro y clima escolar",
        "sub_code": "4.02",
        "pdf_evidence": "Acciones de mejora",
        "pdf_criterion": "El Centro Educativo ha definido acciones de mejora del clima escolar a partir de los resultados de la encuesta.",
        "matched_code": "4.02.3",
        "db_ev_id": "130",
        "db_ev_name": "Acciones de mejora del clima escolar"
    },
    {
        "ambito": "SEGUNDO ÁMBITO. LIDERAZGO Y DESEMPEÑO DEL PERSONAL DIRECTIVO, DOCENTE, ADMINISTRATIVO Y DE APOYO",
        "indicador": "IBOG 4. Cultura organizacional y satisfacción",
        "subindicador": "4.02. Cultura del centro y clima escolar",
        "sub_code": "4.02",
        "pdf_evidence": "Aplicación e informe de encuesta de clima",
        "pdf_criterion": "Centro Educativo cuenta con encuesta de clima escolar en el primer trimestre del año escolar.",
        "matched_code": "4.02.4",
        "db_ev_id": "131",
        "db_ev_name": "Aplicación e informe de encuesta de clima"
    },
    # 4.03
    {
        "ambito": "SEGUNDO ÁMBITO. LIDERAZGO Y DESEMPEÑO DEL PERSONAL DIRECTIVO, DOCENTE, ADMINISTRATIVO Y DE APOYO",
        "indicador": "IBOG 4. Cultura organizacional y satisfacción",
        "subindicador": "4.03. Satisfacción y reconocimiento social",
        "sub_code": "4.03",
        "pdf_evidence": "Índice de Satisfacción de los grupos de interés",
        "pdf_criterion": "Índice de Satisfacción de los grupos de interés con el desempeño general del Centro Educativo por encima de 71%.",
        "matched_code": "4.03.1",
        "db_ev_id": "132",
        "db_ev_name": "Índice de Satisfacción de los grupos de interés con el desempeño general del Centro Educativo por encima de 71 puntos"
    },
    {
        "ambito": "SEGUNDO ÁMBITO. LIDERAZGO Y DESEMPEÑO DEL PERSONAL DIRECTIVO, DOCENTE, ADMINISTRATIVO Y DE APOYO",
        "indicador": "IBOG 4. Cultura organizacional y satisfacción",
        "subindicador": "4.03. Satisfacción y reconocimiento social",
        "sub_code": "4.03",
        "pdf_evidence": "Índice de Satisfacción de los grupos de interés",
        "pdf_criterion": "Índice de Satisfacción de los grupos de interés con el desempeño general del Centro Educativo entre 51% y 70%.",
        "matched_code": "4.03.2",
        "db_ev_id": "133",
        "db_ev_name": "Índice de Satisfacción de los grupos de interés con el desempeño general del Centro Educativo entre 51 y 70 puntos"
    },
    {
        "ambito": "SEGUNDO ÁMBITO. LIDERAZGO Y DESEMPEÑO DEL PERSONAL DIRECTIVO, DOCENTE, ADMINISTRATIVO Y DE APOYO",
        "indicador": "IBOG 4. Cultura organizacional y satisfacción",
        "subindicador": "4.03. Satisfacción y reconocimiento social",
        "sub_code": "4.03",
        "pdf_evidence": "Índice de Satisfacción de los grupos de interés",
        "pdf_criterion": "Índice de Satisfacción de los grupos de interés con el desempeño general del Centro Educativo entre 31% y 50%.",
        "matched_code": "4.03.3",
        "db_ev_id": "134",
        "db_ev_name": "ndice de Satisfacción de los grupos de interés con el desempeño general del Centro Educativo entre 31 y 50 puntos"
    },
    # 8.01
    {
        "ambito": "CUARTO ÁMBITO. CONTRIBUCIÓN DEL CENTRO EDUCATIVO AL DESARROLLO DEL TERRITORIO Y LAS METAS EDUCATIVAS NACIONALES",
        "indicador": "IBOG 8. Responsabilidad social y contribución del centro al desarrollo local",
        "subindicador": "8.01. Contribución del centro al desarrollo de la comunidad donde está situado",
        "sub_code": "8.01",
        "pdf_evidence": "Valor del Índice de Contribución del Centro al Desarrollo de la Comunidad donde está Situado",
        "pdf_criterion": "Valor del Índice de Contribución del Centro al Desarrollo de la Comunidad donde está Situado (elaborado por MEPyD y MINERD).",
        "matched_code": "8.01.1",
        "db_ev_id": "135",
        "db_ev_name": "Valor del Índice de Contribución del Centro al Desarrollo de la Comunidad donde está Situado"
    },
    # 9.01
    {
        "ambito": "CUARTO ÁMBITO. CONTRIBUCIÓN DEL CENTRO EDUCATIVO AL DESARROLLO DEL TERRITORIO Y LAS METAS EDUCATIVAS NACIONALES",
        "indicador": "IBOG 9. Contribución al logro de las metas nacionales del Ministerio de Educación",
        "subindicador": "9.01. Producción sustantiva del Centro Educativo en el marco de las metas nacionales",
        "sub_code": "9.01",
        "pdf_evidence": "Valor del Índice de Contribución del Centro al Logro de las Metas Educativas Nacionales",
        "pdf_criterion": "Valor del Índice de Contribución del Centro al Logro de las Metas Educativas Nacionales (elaborado por MEPyD).",
        "matched_code": "9.01.1",
        "db_ev_id": "136",
        "db_ev_name": "Valor del Índice de Contribución del Centro al Logro de las Metas Educativas Nacionales"
    },
    # Ns 7.01
    {
        "ambito": "TERCER ÁMBITO: LOS Y LAS ESTUDIANTES COMO OBJETO DE ACTUACIÓN DEL CENTRO EDUCATIVO",
        "indicador": "IBOG 7. Resultados en el aprendizaje de las y los estudiantes",
        "subindicador": "7.01. Porcentaje de estudiantes según niveles de desempeño en las pruebas diagnósticas (Nivel Secundario)",
        "sub_code": "Ns 7.01",
        "pdf_evidence": "Matriz de relación de cantidad de estudiantes con los resultados de evaluaciones diagnósticas (Nivel Secundario)",
        "pdf_criterion": "Estudiantes con desempeño satisfactorio en las Pruebas Diagnósticas (Nivel Secundario): Más del 41%",
        "matched_code": "Ns 7.01.1",
        "db_ev_id": "50",
        "db_ev_name": "Ns 7.01.1 Estudiantes Más del 41%"
    },
    {
        "ambito": "TERCER ÁMBITO: LOS Y LAS ESTUDIANTES COMO OBJETO DE ACTUACIÓN DEL CENTRO EDUCATIVO",
        "indicador": "IBOG 7. Resultados en el aprendizaje de las y los estudiantes",
        "subindicador": "7.01. Porcentaje de estudiantes según niveles de desempeño en las pruebas diagnósticas (Nivel Secundario)",
        "sub_code": "Ns 7.01",
        "pdf_evidence": "Matriz de relación de cantidad de estudiantes con los resultados de evaluaciones diagnósticas (Nivel Secundario)",
        "pdf_criterion": "Estudiantes con desempeño satisfactorio en las Pruebas Diagnósticas (Nivel Secundario): Del 26% al 30%",
        "matched_code": "Ns 7.01.2",
        "db_ev_id": "49",
        "db_ev_name": "Ns 7.01.2 Estudiantes Del 26% al 30%"
    },
    {
        "ambito": "TERCER ÁMBITO: LOS Y LAS ESTUDIANTES COMO OBJETO DE ACTUACIÓN DEL CENTRO EDUCATIVO",
        "indicador": "IBOG 7. Resultados en el aprendizaje de las y los estudiantes",
        "subindicador": "7.01. Porcentaje de estudiantes según niveles de desempeño en las pruebas diagnósticas (Nivel Secundario)",
        "sub_code": "Ns 7.01",
        "pdf_evidence": "Matriz de relación de cantidad de estudiantes con los resultados de evaluaciones diagnósticas (Nivel Secundario)",
        "pdf_criterion": "Estudiantes con desempeño satisfactorio en las Pruebas Diagnósticas (Nivel Secundario): Del 26% al 30% (Puntuación intermedia)",
        "matched_code": "Ns 7.01.3",
        "db_ev_id": "48",
        "db_ev_name": "Ns 7.01.3 Estudiantes Del 26% al 30%"
    },
    {
        "ambito": "TERCER ÁMBITO: LOS Y LAS ESTUDIANTES COMO OBJETO DE ACTUACIÓN DEL CENTRO EDUCATIVO",
        "indicador": "IBOG 7. Resultados en el aprendizaje de las y los estudiantes",
        "subindicador": "7.01. Porcentaje de estudiantes según niveles de desempeño en las pruebas diagnósticas (Nivel Secundario)",
        "sub_code": "Ns 7.01",
        "pdf_evidence": "Matriz de relación de cantidad de estudiantes con los resultados de evaluaciones diagnósticas (Nivel Secundario)",
        "pdf_criterion": "Estudiantes con desempeño satisfactorio en las Pruebas Diagnósticas (Nivel Secundario): Del 22% al 25%",
        "matched_code": "Ns 7.01.4",
        "db_ev_id": "47",
        "db_ev_name": "Ns 7.01.4 Estudiantes Del 22% al 25%"
    },
    {
        "ambito": "TERCER ÁMBITO: LOS Y LAS ESTUDIANTES COMO OBJETO DE ACTUACIÓN DEL CENTRO EDUCATIVO",
        "indicador": "IBOG 7. Resultados en el aprendizaje de las y los estudiantes",
        "subindicador": "7.01. Porcentaje de estudiantes según niveles de desempeño en las pruebas diagnósticas (Nivel Secundario)",
        "sub_code": "Ns 7.01",
        "pdf_evidence": "Matriz de relación de cantidad de estudiantes con los resultados de evaluaciones diagnósticas (Nivel Secundario)",
        "pdf_criterion": "Estudiantes con desempeño satisfactorio en las Pruebas Diagnósticas (Nivel Secundario): Del 19% al 21%",
        "matched_code": "Ns 7.01.5",
        "db_ev_id": "46",
        "db_ev_name": "Ns 7.01.5 Estudiantes Del 19% al 21%"
    },
    {
        "ambito": "TERCER ÁMBITO: LOS Y LAS ESTUDIANTES COMO OBJETO DE ACTUACIÓN DEL CENTRO EDUCATIVO",
        "indicador": "IBOG 7. Resultados en el aprendizaje de las y los estudiantes",
        "subindicador": "7.01. Porcentaje de estudiantes según niveles de desempeño en las pruebas diagnósticas (Nivel Secundario)",
        "sub_code": "Ns 7.01",
        "pdf_evidence": "Matriz de relación de cantidad de estudiantes con los resultados de evaluaciones diagnósticas (Nivel Secundario)",
        "pdf_criterion": "Estudiantes con desempeño satisfactorio en las Pruebas Diagnósticas (Nivel Secundario): Del 16% al 18%",
        "matched_code": "Ns 7.01.6",
        "db_ev_id": "45",
        "db_ev_name": "Ns 7.01.6 Estudiantes Del 16% al 18%"
    },
    {
        "ambito": "TERCER ÁMBITO: LOS Y LAS ESTUDIANTES COMO OBJETO DE ACTUACIÓN DEL CENTRO EDUCATIVO",
        "indicador": "IBOG 7. Resultados en el aprendizaje de las y los estudiantes",
        "subindicador": "7.01. Porcentaje de estudiantes según niveles de desempeño en las pruebas diagnósticas (Nivel Secundario)",
        "sub_code": "Ns 7.01",
        "pdf_evidence": "Matriz de relación de cantidad de estudiantes con los resultados de evaluaciones diagnósticas (Nivel Secundario)",
        "pdf_criterion": "Estudiantes con desempeño satisfactorio en las Pruebas Diagnósticas (Nivel Secundario): Del 13% al 15%",
        "matched_code": "Ns 7.01.7",
        "db_ev_id": "44",
        "db_ev_name": "Ns 7.01.7 Estudiantes  Del 13% al 15%"
    },
    {
        "ambito": "TERCER ÁMBITO: LOS Y LAS ESTUDIANTES COMO OBJETO DE ACTUACIÓN DEL CENTRO EDUCATIVO",
        "indicador": "IBOG 7. Resultados en el aprendizaje de las y los estudiantes",
        "subindicador": "7.01. Porcentaje de estudiantes según niveles de desempeño en las pruebas diagnósticas (Nivel Secundario)",
        "sub_code": "Ns 7.01",
        "pdf_evidence": "Matriz de relación de cantidad de estudiantes con los resultados de evaluaciones diagnósticas (Nivel Secundario)",
        "pdf_criterion": "Estudiantes con desempeño satisfactorio en las Pruebas Diagnósticas (Nivel Secundario): Del 10% al 12%",
        "matched_code": "Ns 7.01.8",
        "db_ev_id": "43",
        "db_ev_name": "Ns 7.01.8 Estudiantes con desempeño satisfactorio en las Pruebas Diagnósticas. Del 10% al 12%"
    },
    {
        "ambito": "TERCER ÁMBITO: LOS Y LAS ESTUDIANTES COMO OBJETO DE ACTUACIÓN DEL CENTRO EDUCATIVO",
        "indicador": "IBOG 7. Resultados en el aprendizaje de las y los estudiantes",
        "subindicador": "7.01. Porcentaje de estudiantes según niveles de desempeño en las pruebas diagnósticas (Nivel Secundario)",
        "sub_code": "Ns 7.01",
        "pdf_evidence": "Matriz de relación de cantidad de estudiantes con los resultados de evaluaciones diagnósticas (Nivel Secundario)",
        "pdf_criterion": "Estudiantes con desempeño satisfactorio en las Pruebas Diagnósticas (Nivel Secundario): Por debajo del 10%",
        "matched_code": "Ns 7.01.9",
        "db_ev_id": "42",
        "db_ev_name": "Ns 7.01.9 Estudiantes con desempeño satisfactorio en las Pruebas Diagnósticas.  Por debajo del 10%"
    }
]

for mr in manual_rows:
    flat_rows.append({
        "ambito": mr["ambito"],
        "indicador": mr["indicador"],
        "subindicador": mr["subindicador"],
        "sub_code": mr["sub_code"],
        "pdf_evidence": mr["pdf_evidence"],
        "pdf_criterion": mr["pdf_criterion"],
        "matched_code": mr["matched_code"],
        "db_ev_id": mr["db_ev_id"],
        "db_ev_name": mr["db_ev_name"],
        "match_score": 1.0
    })

print(f"Extraction and matching completed. Extracted {len(flat_rows)} records.")
print(f"Matched: {len([r for r in flat_rows if r['matched_code']])}")
print(f"Unmatched: {len([r for r in flat_rows if not r['matched_code']])}")

# --- Generate Excel ---
print("\nGenerating styled Excel sheet...")
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Criterios de Verificación"

# Show gridlines explicitly
ws.views.sheetView[0].showGridLines = True

# Colors & Fonts
font_family = "Segoe UI"
header_font = Font(name=font_family, size=11, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid") # Premium Steel Blue
header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

data_font = Font(name=font_family, size=10, bold=False, color="000000")
data_font_bold = Font(name=font_family, size=10, bold=True, color="000000")
zebra_fill = PatternFill(start_color="F2F5F8", end_color="F2F5F8", fill_type="solid")
white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

thin_border_side = Side(border_style="thin", color="D3D3D3")
thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

data_align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
data_align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

headers = [
    "Ámbito",
    "Indicador",
    "Subindicador",
    "Subindicador Código",
    "Evidencia ID",
    "Evidencia Código",
    "Nombre de Evidencia (Base de Datos)",
    "Evidencia en PDF",
    "Criterio de Verificación (PDF)"
]

ws.append(headers)

# Style Header Row
ws.row_dimensions[1].height = 30
for col_num in range(1, len(headers) + 1):
    cell = ws.cell(row=1, column=col_num)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_align
    cell.border = thin_border

# Write and Style Data
row_idx = 2
for r in flat_rows:
    ws.append([
        r["ambito"],
        r["indicador"],
        r["subindicador"],
        r["sub_code"],
        r["db_ev_id"],
        r["matched_code"],
        r["db_ev_name"],
        r["pdf_evidence"],
        r["pdf_criterion"]
    ])
    
    # Zebra styling
    fill = zebra_fill if row_idx % 2 == 0 else white_fill
    ws.row_dimensions[row_idx].height = 24
    
    for col_num in range(1, len(headers) + 1):
        cell = ws.cell(row=row_idx, column=col_num)
        cell.font = data_font
        cell.fill = fill
        cell.border = thin_border
        
        # Center align codes, IDs
        if col_num in [4, 5, 6]:
            cell.alignment = data_align_center
        else:
            cell.alignment = data_align_left
            
    row_idx += 1

# Configure Column Widths (optimized wrap thresholds)
column_widths = {
    "A": 30, # Ambito
    "B": 30, # Indicador
    "C": 30, # Subindicador
    "D": 15, # Subindicador Código
    "E": 12, # Evidencia ID
    "F": 15, # Evidencia Código
    "G": 40, # Nombre de Evidencia (DB)
    "H": 40, # Evidencia en PDF
    "I": 60  # Criterio de Verificación (PDF)
}

for col_letter, width in column_widths.items():
    ws.column_dimensions[col_letter].width = width

# Freeze Header Row
ws.freeze_panes = "A2"

# Save File
try:
    wb.save(excel_output_path)
    print(f"Successfully generated styled Excel file at: {excel_output_path}")
except PermissionError:
    retry_path = excel_output_path.replace(".xlsx", "_NUEVO.xlsx")
    wb.save(retry_path)
    print(f"WARNING: Permission denied when saving to {excel_output_path}. The file is probably open in Excel.")
    print(f"The updated file has been saved to: {retry_path}")
    print(f"Please close the original file in Excel and replace it with this one, or save it under the correct name.")

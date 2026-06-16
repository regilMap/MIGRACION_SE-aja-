import fitz
import json
import re
import sys
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding='utf-8')

# Paths
pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
json_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\exports\migracion_20260129_124821\evidencias_source.json"

# Load database evidences
with open(json_path, 'r', encoding='utf-8') as f:
    db_data = json.load(f)

# Helper to format code
def format_code(code):
    if not code:
        return ""
    code = code.strip()
    match = re.match(r'^([A-Za-z]+)?\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?(.*)$', code)
    if not match:
        return code
    
    prefix, ind_part, sub_part, ev_part, rest = match.groups()
    try:
        indicator = int(ind_part)
    except ValueError:
        return code

    if sub_part is None:
        res = f"{indicator}"
    else:
        try:
            subindicator = int(sub_part)
            res = f"{indicator}.{subindicator:02d}"
        except ValueError:
            res = f"{indicator}.{sub_part}"
            
        if ev_part is not None:
            res = f"{res}.{ev_part}"
            
    prefix_str = f"{prefix} " if prefix else ""
    return f"{prefix_str}{res}{rest}"

# Format all database entries
db_evidences = []
for item in db_data:
    raw_code = item.get("Codigo", "") or ""
    if raw_code == '07.2' or raw_code.startswith('07.2.'):
        raw_code = 'Ns ' + raw_code
    
    clean_code = format_code(raw_code)
    name = item.get("NombreArchivo", "") or ""
    db_evidences.append({
        "id": item.get("EvidenciaID"),
        "raw_code": raw_code,
        "code": clean_code,
        "name": name.strip(),
        "criterio": (item.get("Criterio", "") or "").strip()
    })

# Clean PDF text helpers
def clean_pdf_text(text):
    if not text:
        return ""
    # Remove carriage returns and normalize spaces
    text = str(text).replace("\r", " ").replace("\n", " ")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_evidence_name(raw_text):
    # Heuristic: The evidence name is usually before parentheses (Evidencia subida...) or Nota...
    text = clean_pdf_text(raw_text)
    # Remove "Nota para..."
    text = re.split(r'Nota para el equipo|Nota:', text, flags=re.IGNORECASE)[0].strip()
    # Remove "(Evidencia subida..."
    text = re.split(r'\(Evidencia subida|\(Evidencias subidas', text, flags=re.IGNORECASE)[0].strip()
    # Remove trailing/leading punctuation
    text = text.rstrip(".,;:- ")
    return text

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# Load PDF
doc = fitz.open(pdf_path)

# Extract tables
pdf_tables = []
for page_num in range(len(doc)):
    page = doc[page_num]
    tables = page.find_tables()
    if not tables.tables:
        continue
    for t in tables.tables:
        rows = t.extract()
        if not rows or len(rows) < 2:
            continue
            
        # We find columns
        ev_col = -1
        cr_col = -1
        sub_indicador_val = ""
        indicador_val = ""
        ambito_val = ""
        
        # Analyze rows
        table_rows = []
        current_evidence_raw = ""
        
        for row in rows:
            clean_row = [clean_pdf_text(cell) for cell in row]
            row_str = " ".join(clean_row).lower()
            
            # Subindicador header
            if any("sub" in cell.lower() and "indicador" in cell.lower() for cell in clean_row):
                for cell in clean_row:
                    if cell and not ("sub" in cell.lower() and "indicador" in cell.lower()) and cell.lower() != "cumple":
                        sub_indicador_val = cell
                        break
                continue
                
            # Indicador header
            if any(cell.lower() == "indicador" for cell in clean_row):
                for cell in clean_row:
                    if cell and cell.lower() != "indicador":
                        indicador_val = cell
                        break
                continue
                
            # Ámbito header
            if "ámbito" in row_str or "ambito" in row_str:
                for cell in clean_row:
                    if "ámbito" in cell.lower() or "ambito" in cell.lower():
                        ambito_val = cell
                        break
                continue
                
            # Headers row
            if any(cell.lower() == "evidencia" for cell in clean_row) and any("criterio" in cell.lower() for cell in clean_row):
                for i, cell in enumerate(clean_row):
                    if cell.lower() == "evidencia":
                        ev_col = i
                    elif "criterio" in cell.lower():
                        cr_col = i
                continue
                
            # Content rows
            if ev_col != -1 and cr_col != -1:
                ev_text = clean_row[ev_col] if ev_col < len(clean_row) else ""
                cr_text = clean_row[cr_col] if cr_col < len(clean_row) else ""
                
                if not ev_text and not cr_text:
                    continue
                if cr_text.lower() in ["si", "no", "cumple", "criterios de verificación", "criterios"]:
                    continue
                    
                if ev_text:
                    current_evidence_raw = ev_text
                    
                if cr_text:
                    table_rows.append({
                        "raw_evidence": current_evidence_raw,
                        "raw_criterion": cr_text
                    })
                    
        if table_rows:
            pdf_tables.append({
                "page": page_num + 1,
                "ambito": sub_indicador_val or indicador_val or ambito_val, # Fallback path
                "indicador": indicador_val,
                "subindicador": sub_indicador_val,
                "rows": table_rows
            })

# Let's match extracted rows with database evidences
matches = []
unmatched = []

for table in pdf_tables:
    sub_code = ""
    # Extract subindicator number, e.g. "1.01" from "1.01. Formulación de..."
    match_sub = re.match(r'^([\w\d\.]+)', table["subindicador"])
    if match_sub:
        sub_code = match_sub.group(1).strip(" .")
        
    print(f"\nSubindicador in PDF: {table['subindicador']} (Extracted Code: {sub_code})")
    
    # Filter DB evidences that belong to this subindicator
    # E.g. if sub_code is "1.01", database subindicator code in map_to_source_code would be "01.1"
    # Let's find db subindicator code using mapping rules
    db_sub_prefix = ""
    if sub_code:
        # We can map it using the same mapping rules
        # Let's do a loose check: if db_ev code starts with sub_code formatted, or has similar prefix
        # E.g. Np 7.01 -> database code has Np 07.1
        # Let's translate sub_code to database style
        pass
        
    # Group rows by raw_evidence name on this page to reconstruct evidence + criteria list
    grouped_evidences = {}
    for r in table["rows"]:
        ev_name = extract_evidence_name(r["raw_evidence"])
        if ev_name not in grouped_evidences:
            grouped_evidences[ev_name] = {
                "raw_name": r["raw_evidence"],
                "criteria": []
            }
        grouped_evidences[ev_name]["criteria"].append(r["raw_criterion"])
        
    for ev_name, info in grouped_evidences.items():
        print(f"  PDF Evidence: {repr(ev_name)}")
        print(f"    Criteria count: {len(info['criteria'])}")
        
        # Match with database
        best_match = None
        best_score = 0.0
        
        for db_ev in db_evidences:
            # First check: does the database code match the subindicator?
            # E.g. if PDF is 1.01.X, and db code is 1.01.X or 01.1.X
            # Let's compute similarity of the evidence name
            score = similarity(ev_name, db_ev["name"])
            
            # Let's also check if subindicator matches (to prevent cross-indicator false matches)
            # If the database code contains the indicator and subindicator numbers:
            # E.g. db_ev["code"] = "1.01.2", sub_code = "1.01" -> matches!
            # db_ev["code"] = "Np 7.01.3", sub_code = "Np 7.01" or "Np 7.01" in sub_code
            db_ev_code = db_ev["code"]
            sub_match = False
            
            # Simple check:
            if sub_code:
                # E.g. sub_code = "1.01" -> check if "1.01" in db_ev_code
                # E.g. sub_code = "Np 7.01" -> check if "Np 7.01" in db_ev_code
                # We normalize both:
                norm_sub_code = sub_code.lower().replace(" ", "").replace("0", "")
                norm_db_code = db_ev_code.lower().replace(" ", "").replace("0", "")
                if norm_sub_code in norm_db_code or norm_db_code in norm_sub_code:
                    sub_match = True
            else:
                sub_match = True
                
            if sub_match:
                if score > best_score:
                    best_score = score
                    best_match = db_ev
                    
        if best_match and best_score > 0.5:
            print(f"    -> MATCHED to Code: {best_match['code']} (Score: {best_score:.2f}) | {best_match['name']}")
            matches.append({
                "pdf_sub": table["subindicador"],
                "pdf_ev_name": ev_name,
                "db_code": best_match["code"],
                "db_name": best_match["name"],
                "criteria": info["criteria"]
            })
        else:
            print(f"    -> WARNING: UNMATCHED (Best Score: {best_score:.2f} to {best_match['name'] if best_match else 'None'})")
            unmatched.append({
                "pdf_sub": table["subindicador"],
                "pdf_ev_name": ev_name,
                "criteria": info["criteria"]
            })

print(f"\nMATCHED: {len(matches)}, UNMATCHED: {len(unmatched)}")

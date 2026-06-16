import fitz
import json
import re
import sys
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
json_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\exports\migracion_20260129_124821\evidencias_source.json"

with open(json_path, 'r', encoding='utf-8') as f:
    db_data = json.load(f)

# Expected database evidences for subindicator 2.01 (database code 02.1)
expected_db = []
for item in db_data:
    code = item.get("Codigo", "") or ""
    if code.startswith("02.1."):
        expected_db.append({
            "code": code,
            "name": item.get("NombreArchivo", "").strip(),
            "id": item.get("EvidenciaID")
        })

print("Expected database evidences for 02.1:")
for db_ev in expected_db:
    print(f"  {db_ev['code']}: {db_ev['name']}")

def clean_text(text):
    if not text:
        return ""
    text = str(text).replace("\r", " ").replace("\n", " ")
    return re.sub(r'\s+', ' ', text).strip()

def get_best_match(cell_text, expected_evidences):
    if not cell_text or len(cell_text) < 5:
        return None, 0.0
        
    best_ev = None
    best_score = 0.0
    
    # We clean cell text by removing parentheticals
    clean_cell = re.split(r'\(Evidencia subida|\(Evidencias subidas|Nota para', cell_text, flags=re.IGNORECASE)[0].strip()
    clean_cell = clean_cell.rstrip(".,;:- ")
    
    for ev in expected_evidences:
        # Check similarity
        score = SequenceMatcher(None, clean_cell.lower(), ev["name"].lower()).ratio()
        
        # Check if one is substring of other (for prefix matching)
        if clean_cell.lower() in ev["name"].lower() and len(clean_cell) > 10:
            score = max(score, len(clean_cell) / len(ev["name"]))
        if ev["name"].lower() in clean_cell.lower() and len(ev["name"]) > 10:
            score = max(score, len(ev["name"]) / len(clean_cell))
            
        if score > best_score:
            best_score = score
            best_ev = ev
            
    return best_ev, best_score

doc = fitz.open(pdf_path)
page = doc[31] # Page 32
tables = page.find_tables()
if tables.tables:
    t = tables.tables[0]
    rows = t.extract()
    
    current_ev = None
    extracted_items = []
    
    # Identify columns
    ev_col = -1
    cr_col = -1
    for r_idx, r in enumerate(rows):
        clean_row = [clean_text(cell) for cell in r]
        if any(cell.lower() == "evidencia" for cell in clean_row) and any("criterio" in cell.lower() for cell in clean_row):
            for i, cell in enumerate(clean_row):
                if cell.lower() == "evidencia":
                    ev_col = i
                elif "criterio" in cell.lower():
                    cr_col = i
            break
            
    print(f"\nUsing columns: Evidencia={ev_col}, Criterios={cr_col}")
    
    # Process rows below header
    for r_idx in range(ev_col + 1 if ev_col != -1 else 0, len(rows)):
        row = rows[r_idx]
        ev_cell = clean_text(row[ev_col]) if ev_col < len(row) else ""
        cr_cell = clean_text(row[cr_col]) if cr_col < len(row) else ""
        
        if not ev_cell and not cr_cell:
            continue
        if cr_cell.lower() in ["si", "no", "cumple", "criterios de verificación"]:
            continue
            
        # Try to match new evidence if cell is not empty
        if ev_cell:
            matched_ev, score = get_best_match(ev_cell, expected_db)
            if score > 0.5:
                current_ev = matched_ev
                print(f"Row {r_idx}: Matched left cell {repr(ev_cell[:30])} to {current_ev['code']} (Score: {score:.2f})")
            else:
                print(f"Row {r_idx}: Left cell {repr(ev_cell[:30])} did NOT match (Best Score: {score:.2f} for {matched_ev['code'] if matched_ev else 'None'})")
                
        if cr_cell and current_ev:
            extracted_items.append({
                "code": current_ev["code"],
                "evidence": current_ev["name"],
                "criterion": cr_cell
            })
            print(f"  Added criterion: {repr(cr_cell[:50])}")

    print("\nResulting extraction:")
    for idx, item in enumerate(extracted_items):
        print(f"  {idx+1}. Code: {item['code']} | Ev: {item['evidence'][:30]}... | Cr: {item['criterion']}")
else:
    print("No tables found")

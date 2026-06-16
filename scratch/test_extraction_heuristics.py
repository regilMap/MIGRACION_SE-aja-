import fitz
import json
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

extracted_tables = []
current_ambito = ""
current_indicador = ""
current_subindicador = ""

active_ev_col = -1
active_cr_col = -1
active_sub_code = ""

for page_num in range(18, 75):
    page = doc[page_num]
    tables = page.find_tables()
    
    if not tables.tables:
        continue
        
    for t_idx, t in enumerate(tables.tables):
        rows = t.extract()
        if not rows or len(rows) < 2:
            continue
            
        # 1. Scan rows to find headers and identify rows before header
        header_row_idx = -1
        page_ev_col = -1
        page_cr_col = -1
        
        for r_idx, r in enumerate(rows):
            clean_row = [clean_text(cell) for cell in r]
            has_ev = False
            has_cr = False
            for i, cell in enumerate(clean_row):
                if "evidencia" in cell.lower():
                    page_ev_col = i
                    has_ev = True
                elif "criterio" in cell.lower():
                    page_cr_col = i
                    has_cr = True
            if has_ev and has_cr:
                header_row_idx = r_idx
                active_ev_col = page_ev_col
                active_cr_col = page_cr_col
                break
                
        # 2. Extract metadata from rows (even before header)
        for r_idx, r in enumerate(rows):
            clean_row = [clean_text(cell) for cell in r]
            row_str = " ".join(clean_row).lower()
            
            # Check for Ámbito header
            if "ámbito" in row_str or "ambito" in row_str:
                for cell in clean_row:
                    if "ámbito" in cell.lower() or "ambito" in cell.lower():
                        current_ambito = cell
                        break
                
            # Check for Indicador header
            if any(cell.lower() == "indicador" for cell in clean_row):
                for cell in clean_row:
                    if cell and cell.lower() != "indicador":
                        current_indicador = cell
                        break
                
            # Check for Sub Indicador header
            if any("sub" in cell.lower() and "indicador" in cell.lower() for cell in clean_row):
                for cell in clean_row:
                    if cell and not ("sub" in cell.lower() and "indicador" in cell.lower()) and cell.lower() != "cumple":
                        current_subindicador = cell
                        break
                        
        # Determine starting row for content
        start_row = 0
        if header_row_idx != -1:
            start_row = header_row_idx + 1
            # Update subindicator code
            match_sub = re.match(r'^([\w\d\.]+)', current_subindicador)
            active_sub_code = match_sub.group(1).strip(" .") if match_sub else ""
            
        ev_col = active_ev_col
        cr_col = active_cr_col
        
        if ev_col == -1 or cr_col == -1:
            continue # No header found yet and no active columns
            
        table_rows = []
        for r_idx in range(start_row, len(rows)):
            row = rows[r_idx]
            ev_text = clean_text(row[ev_col]) if ev_col < len(row) else ""
            cr_text = clean_text(row[cr_col]) if cr_col < len(row) else ""
            
            # Skip rows with purely checkbox data
            if cr_text.lower() in ["si", "no", "cumple", "s", "i"]:
                continue
            if not ev_text and not cr_text:
                continue
                
            table_rows.append((ev_text, cr_text))
            
        if table_rows:
            # Reconstruct evidences and criteria using our heuristics
            grouped_items = []
            
            current_ev_name = ""
            current_ev_raw = ""
            current_criteria_list = []
            
            for ev_text, cr_text in table_rows:
                # 1. Handle evidence cell
                if ev_text:
                    if is_new_item(ev_text):
                        # Commit previous evidence if it exists
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
                        
                # 2. Handle criteria cell
                if cr_text:
                    if is_new_item(cr_text):
                        current_criteria_list.append(cr_text)
                    else:
                        if current_criteria_list:
                            current_criteria_list[-1] += " " + cr_text
                        else:
                            current_criteria_list.append(cr_text)
                            
            # Commit the last evidence
            if current_ev_name or current_criteria_list:
                grouped_items.append({
                    "evidence_name": current_ev_name.strip(),
                    "evidence_raw": current_ev_raw.strip(),
                    "criteria": current_criteria_list
                })
                
            if grouped_items:
                extracted_tables.append({
                    "page": page_num + 1,
                    "ambito": current_ambito,
                    "indicador": current_indicador,
                    "subindicador": current_subindicador,
                    "sub_code": active_sub_code,
                    "items": grouped_items
                })

# Save text log of results
log_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\extraction_heuristics_results.txt"
with open(log_path, "w", encoding="utf-8") as f:
    f.write(f"Extracted {len(extracted_tables)} tables.\n\n")
    for table in extracted_tables:
        f.write(f"=================================================================\n")
        f.write(f"PAGE {table['page']} | Subindicador: {table['sub_code']} - {table['subindicador']}\n")
        f.write(f"=================================================================\n")
        f.write(f"Ámbito: {table['ambito']}\n")
        f.write(f"Indicador: {table['indicador']}\n")
        for idx, item in enumerate(table["items"]):
            f.write(f"  Evidencia {idx+1}: {item['evidence_name']}\n")
            f.write(f"    Raw: {repr(item['evidence_raw'])}\n")
            for c_idx, cr in enumerate(item["criteria"]):
                f.write(f"      Criterio {c_idx+1}: {cr}\n")
        f.write("\n")

print(f"Heuristics extraction completed. Found {len(extracted_tables)} tables.")
print(f"Results written to {log_path}")

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
active_table = None

# We'll keep track of active table metadata to handle continuations
current_ambito = ""
current_indicador = ""
current_subindicador = ""
active_sub_code = ""
active_x_divide = 190.0  # default divide

for page_num in range(18, 76): # Pages 19 to 76 (0-indexed 18 to 75)
    page = doc[page_num]
    tables = page.find_tables()
    
    if not tables.tables:
        continue
        
    for t_idx, t in enumerate(tables.tables):
        rows = t.extract()
        if not rows or len(rows) < 1:
            continue
            
        # 1. Scan rows to find headers and metadata
        header_row_idx = -1
        page_ev_col = -1
        page_cr_col = -1
        
        # We also look for metadata on the page or inside the table
        page_text = page.get_text("text")
        
        # Check metadata from rows
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
                # Calculate divide
                x1_ev = ev_bbox[2]
                x0_cr = cr_bbox[0]
                active_x_divide = (x1_ev + x0_cr) / 2
                break
                
        # Determine subindicator code if we have a new one
        if current_subindicador:
            match_sub = re.match(r'^([\w\d\.\-]+)', current_subindicador)
            if match_sub:
                active_sub_code = match_sub.group(1).strip(" .")
                
        # Skip this table if it is a scoring table
        # We can identify scoring tables by checking if the page text or table rows contain keywords like
        # "nivel de avance", "objetivo logrado", "cierto avance", "satisfactorio", etc.
        # But wait! A valid evidence table on page 20 has "nivel de avance" tables on page 21.
        # If the table has a header containing "evidencia" and "criterio", it is DEFINITELY a valid table.
        # If it doesn't have a header:
        #   - If it is at the top of the page (row 0 contains continuation data), it could be a continuation.
        #   - But we must check if it contains scoring terms.
        is_scoring_table = False
        table_text = " ".join([" ".join([clean_text(c) for c in r]) for r in rows]).lower()
        if "nivel de avance" in table_text or "objetivo logrado" in table_text or "cierto avance" in table_text:
            is_scoring_table = True
            
        if is_scoring_table:
            # Skip this table!
            continue
            
        # If no header was found on this page and we don't have an active table, skip it
        if header_row_idx == -1 and not active_table:
            continue
            
        start_row = 0
        if header_row_idx != -1:
            start_row = header_row_idx + 1
            # We are starting a new subindicator table!
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
            # Continuation table!
            if active_table:
                active_table["pages"].append(page_num + 1)
                
        # Process rows
        for r_idx in range(start_row, len(rows)):
            row = rows[r_idx]
            row_cells = t.rows[r_idx].cells
            
            # We group the text cells based on x-coordinates
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
                
                # Checkbox columns: skip
                if x_mid >= 380.0:
                    continue
                # Also skip checkbox labels
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

# Print summary
print(f"Extracted {len(extracted_tables)} indicator tables.")
for idx, t in enumerate(extracted_tables):
    print(f"Table {idx+1}: Pages {t['pages']} | Code: {t['sub_code']} | Raw Rows: {len(t['rows'])}")
    
# Reconstruct using heuristics per table
reconstructed_tables = []
for table in extracted_tables:
    grouped_items = []
    current_ev_name = ""
    current_ev_raw = ""
    current_criteria_list = []
    
    for ev_text, cr_text in table["rows"]:
        # Handle evidence cell
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
                
        # Handle criteria cell
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
        
    reconstructed_tables.append({
        "pages": table["pages"],
        "ambito": table["ambito"],
        "indicador": table["indicador"],
        "subindicador": table["subindicador"],
        "sub_code": table["sub_code"],
        "items": grouped_items
    })

# Write to log
with open(r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\extraction_results_v2.txt", "w", encoding="utf-8") as f:
    f.write(f"Extracted {len(reconstructed_tables)} tables.\n\n")
    for table in reconstructed_tables:
        f.write(f"=================================================================\n")
        f.write(f"PAGES {table['pages']} | Subindicador: {table['sub_code']} - {table['subindicador']}\n")
        f.write(f"=================================================================\n")
        f.write(f"Ámbito: {table['ambito']}\n")
        f.write(f"Indicador: {table['indicador']}\n")
        for idx, item in enumerate(table["items"]):
            f.write(f"  Evidencia {idx+1}: {item['evidence_name']}\n")
            f.write(f"    Raw: {repr(item['evidence_raw'])}\n")
            for c_idx, cr in enumerate(item["criteria"]):
                f.write(f"      Criterio {c_idx+1}: {cr}\n")
        f.write("\n")

print("Finished. Log written to scratch/extraction_results_v2.txt")

import fitz
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

extracted_tables = []

def clean_text(text):
    if not text:
        return ""
    text = str(text).replace("\r", " ").replace("\n", " ")
    return re.sub(r'\s+', ' ', text).strip()

# We will scan pages 19 to 76 (0-indexed 18 to 75)
current_ambito = ""
current_indicador = ""
current_subindicador = ""

# Track columns across pages for same subindicator
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
            
        page_ev_col = -1
        page_cr_col = -1
        
        # 1. Detect headers and metadata in table rows
        table_rows = []
        
        for r_idx, r in enumerate(rows):
            clean_row = [clean_text(cell) for cell in r]
            row_str = " ".join(clean_row).lower()
            
            # Check for Ámbito header
            if "ámbito" in row_str or "ambito" in row_str:
                for cell in clean_row:
                    if "ámbito" in cell.lower() or "ambito" in cell.lower():
                        current_ambito = cell
                        break
                continue
                
            # Check for Indicador header
            if any(cell.lower() == "indicador" for cell in clean_row):
                for cell in clean_row:
                    if cell and cell.lower() != "indicador":
                        current_indicador = cell
                        break
                continue
                
            # Check for Sub Indicador header
            if any("sub" in cell.lower() and "indicador" in cell.lower() for cell in clean_row):
                for cell in clean_row:
                    if cell and not ("sub" in cell.lower() and "indicador" in cell.lower()) and cell.lower() != "cumple":
                        current_subindicador = cell
                        break
                continue
                
            # Detect column indices for Evidencia and Criterios de verificación
            is_header_row = False
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
                is_header_row = True
                active_ev_col = page_ev_col
                active_cr_col = page_cr_col
                # Update subindicator code context
                match_sub = re.match(r'^([\w\d\.]+)', current_subindicador)
                active_sub_code = match_sub.group(1).strip(" .") if match_sub else ""
                continue
                
            # If we don't find the header row, but we have active columns, we use them
            ev_col = page_ev_col if page_ev_col != -1 else active_ev_col
            cr_col = page_cr_col if page_cr_col != -1 else active_cr_col
            
            if ev_col != -1 and cr_col != -1:
                ev_text = clean_row[ev_col] if ev_col < len(clean_row) else ""
                cr_text = clean_row[cr_col] if cr_col < len(clean_row) else ""
                
                # Clean up specific garbage in criteria column
                if cr_text.lower() in ["si", "no", "cumple", "criterios de verificación", "criterios", "s", "i"]:
                    continue
                if not ev_text and not cr_text:
                    continue
                    
                table_rows.append({
                    "left_raw": ev_text,
                    "right_raw": cr_text
                })
                
        if table_rows:
            # Reconstruct evidence items
            reconstructed_items = []
            current_evidence = ""
            
            for item in table_rows:
                left = item["left_raw"]
                right = item["right_raw"]
                
                # Skip header repetitions inside rows
                if "evidencia" in left.lower() and "criterio" in right.lower():
                    continue
                if left.lower() in ["sub indicador", "indicador", "cumple"]:
                    continue
                    
                if left:
                    current_evidence = left
                if right:
                    reconstructed_items.append({
                        "raw_evidence": current_evidence,
                        "criterion": right
                    })
                    
            if reconstructed_items:
                extracted_tables.append({
                    "page": page_num + 1,
                    "ambito": current_ambito,
                    "indicador": current_indicador,
                    "subindicador": current_subindicador,
                    "sub_code": active_sub_code,
                    "items": reconstructed_items
                })

# Save to JSON
output_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\extracted_tables_v2.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(extracted_tables, f, ensure_ascii=False, indent=2)

# Save text log
log_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\extraction_results_v2.txt"
with open(log_path, "w", encoding="utf-8") as f:
    f.write(f"Extracted {len(extracted_tables)} tables from PDF.\n\n")
    for table in extracted_tables:
        f.write(f"=================================================================\n")
        f.write(f"PAGE {table['page']} | Subindicador: {table['sub_code']} - {table['subindicador']}\n")
        f.write(f"=================================================================\n")
        f.write(f"Ámbito: {table['ambito']}\n")
        f.write(f"Indicador: {table['indicador']}\n")
        for idx, item in enumerate(table["items"]):
            f.write(f"  Item {idx+1}:\n")
            f.write(f"    Raw Ev: {item['raw_evidence']}\n")
            f.write(f"    Criterion: {item['criterion']}\n")
        f.write("\n")

print(f"Extraction completed. Found {len(extracted_tables)} tables.")
print(f"Results written to {log_path} and {output_path}")

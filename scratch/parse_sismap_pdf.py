import fitz
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

extracted_data = []

def clean_text(text):
    if not text:
        return ""
    # Remove leading/trailing spaces and newlines, collapse multiple spaces
    text = str(text).replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return " ".join(lines)

def parse_pdf():
    current_ambito = ""
    current_indicador = ""
    current_subindicador = ""
    
    # We loop through all pages in the document
    for page_num in range(len(doc)):
        page = doc[page_num]
        tables = page.find_tables()
        table_list = tables.tables
        
        if not table_list:
            continue
            
        for t in table_list:
            rows = t.extract()
            if not rows or len(rows) < 2:
                continue
                
            # Let's inspect the rows to find where indicator/subindicator headers are,
            # and then extract evidence & criteria rows.
            # We want to identify the columns for Evidence and Criteria.
            # In the table:
            # Row 0 or 1 might be Ámbito: e.g. "IBOG PRIMER ÁMBITO..."
            # Row 2 might be Indicador: cell 1="Indicador", cell 3="IBOG 1. ..."
            # Row 3 might be Sub Indicador: cell 0="Sub Indicador", cell 3="1.01. ..."
            # Row 4 might be Headers: cell 1="Evidencia", cell 3="Criterios de verificación"
            
            # Let's write a stateful row-by-row parser for this table
            evidence_col_idx = -1
            criteria_col_idx = -1
            
            # Temporary storage for this table
            table_evidences = []
            current_evidence = ""
            
            for r_idx, row in enumerate(rows):
                # Clean row elements
                clean_row = [clean_text(cell) for cell in row]
                
                # Check for Ámbito header
                row_str = " ".join(clean_row).lower()
                if "ámbito" in row_str or "ambito" in row_str:
                    # Find which cell contains the ámbito text
                    for cell in clean_row:
                        if "ámbito" in cell.lower() or "ambito" in cell.lower():
                            current_ambito = cell
                            break
                    continue
                
                # Check for Indicador row
                if any(cell.lower() == "indicador" for cell in clean_row):
                    # The indicator name is usually in a column after "Indicador"
                    idx = -1
                    for i, cell in enumerate(clean_row):
                        if cell.lower() == "indicador":
                            idx = i
                            break
                    if idx != -1 and idx + 1 < len(clean_row):
                        # Find the first non-empty cell after "Indicador"
                        for j in range(idx + 1, len(clean_row)):
                            if clean_row[j]:
                                current_indicador = clean_row[j]
                                break
                    continue
                
                # Check for Sub Indicador row
                if any("sub" in cell.lower() and "indicador" in cell.lower() for cell in clean_row):
                    idx = -1
                    for i, cell in enumerate(clean_row):
                        if "sub" in cell.lower() and "indicador" in cell.lower():
                            idx = i
                            break
                    if idx != -1 and idx + 1 < len(clean_row):
                        for j in range(idx + 1, len(clean_row)):
                            if clean_row[j]:
                                current_subindicador = clean_row[j]
                                break
                    continue
                
                # Check for table headers (Evidencia and Criterios de verificación)
                if any(cell.lower() == "evidencia" for cell in clean_row) and any("criterio" in cell.lower() for cell in clean_row):
                    for i, cell in enumerate(clean_row):
                        if cell.lower() == "evidencia":
                            evidence_col_idx = i
                        elif "criterio" in cell.lower():
                            criteria_col_idx = i
                    continue
                
                # If we have identified the columns, we parse the rows as evidence & criteria
                if evidence_col_idx != -1 and criteria_col_idx != -1:
                    ev_cell = clean_row[evidence_col_idx] if evidence_col_idx < len(clean_row) else ""
                    cr_cell = clean_row[criteria_col_idx] if criteria_col_idx < len(clean_row) else ""
                    
                    # Skip rows that are empty or contain only "si", "no", "cumple"
                    if not ev_cell and not cr_cell:
                        continue
                    if cr_cell.lower() in ["si", "no", "cumple", "criterios de verificación", "criterios"]:
                        continue
                        
                    # If the evidence cell is not empty, update current_evidence
                    if ev_cell:
                        current_evidence = ev_cell
                        
                    if cr_cell:
                        table_evidences.append({
                            "evidence_raw": current_evidence,
                            "criterion": cr_cell
                        })
            
            # Add table data to extracted_data
            if table_evidences:
                extracted_data.append({
                    "page": page_num + 1,
                    "ambito": current_ambito,
                    "indicador": current_indicador,
                    "subindicador": current_subindicador,
                    "items": table_evidences
                })

parse_pdf()
print(f"Extracted {len(extracted_data)} subindicator tables from PDF.")

# Let's save to JSON so we can look at it
json_output_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\extracted_raw_tables.json"
with open(json_output_path, "w", encoding="utf-8") as f:
    json.dump(extracted_data, f, ensure_ascii=False, indent=2)

print(f"Saved raw data to {json_output_path}")

# Let's print out the first 2 subindicator details
for table in extracted_data[:2]:
    print(f"\nPage: {table['page']}")
    print(f"Ámbito: {table['ambito']}")
    print(f"Indicador: {table['indicador']}")
    print(f"Sub Indicador: {table['subindicador']}")
    for idx, item in enumerate(table['items'][:5]):
        print(f"  Item {idx+1}:")
        print(f"    Raw Evidence: {item['evidence_raw']}")
        print(f"    Criterion: {item['criterion']}")

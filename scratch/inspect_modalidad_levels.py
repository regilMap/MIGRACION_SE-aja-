import pandas as pd
import re

file_path = "Centros modalidad  Primario - Secundario.xlsx"
xl = pd.ExcelFile(file_path)

def clean_code(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s.endswith('.0'):
        s = s[:-2]
    s = re.sub(r'\D', '', s)
    if s:
        return s.zfill(5)
    return None

all_centers = {}

for sheet in xl.sheet_names:
    print(f"\n--- Processing sheet: {sheet} ---")
    df = xl.parse(sheet, header=None)
    
    # Let's find header rows
    header_rows = []
    for idx, row in df.iterrows():
        vals = [str(x).strip().upper() for x in row.fillna("").tolist()]
        if any("SIGERD" in v or "CODIGO" in v or "CÓDIGO" in v for v in vals):
            header_rows.append(idx)
            print(f"  Header found at row {idx}: {row.dropna().tolist()[:10]}")
            
    if not header_rows:
        print("  No headers containing SIGERD or CODIGO found.")
        continue
        
    for h_idx in header_rows:
        # Load sub-dataframe starting after the header row
        header_vals = df.iloc[h_idx].tolist()
        
        # We might have side-by-side tables (like in Matriz (2))
        # Let's split header_vals into potential tables
        # Find where "No." or similar starts or just map by indices
        # Let's check indices of headers with SIGERD/CODIGO
        sigerd_indices = [i for i, v in enumerate(header_vals) if v and ("SIGERD" in str(v).upper() or "CODIGO" in str(v).upper() or "CÓDIGO" in str(v).upper())]
        print(f"  SIGERD columns at indices: {sigerd_indices}")
        
        for sig_col_idx in sigerd_indices:
            # Let's find the corresponding NIVEL column for this SIGERD column.
            # Usually, the NIVEL column is next to it, or within a few columns to the right.
            nivel_col_idx = None
            for offset in range(1, 4):
                curr_idx = sig_col_idx + offset
                if curr_idx < len(header_vals):
                    val = str(header_vals[curr_idx]).strip().upper()
                    if "NIVEL" in val:
                        nivel_col_idx = curr_idx
                        break
            if nivel_col_idx is None:
                # Fallback: search anywhere to the right of sig_col_idx up to the next sig_col_idx or end
                limit = len(header_vals)
                for next_sig in sigerd_indices:
                    if next_sig > sig_col_idx:
                        limit = next_sig
                        break
                for curr_idx in range(sig_col_idx + 1, limit):
                    val = str(header_vals[curr_idx]).strip().upper()
                    if "NIVEL" in val:
                        nivel_col_idx = curr_idx
                        break
            
            print(f"  Mapping: SIGERD at col {sig_col_idx} -> NIVEL at col {nivel_col_idx}")
            
            # Now extract data
            for r_idx in range(h_idx + 1, len(df)):
                # If the row has NaN for SIGERD, skip or stop
                raw_code = df.iloc[r_idx, sig_col_idx]
                code = clean_code(raw_code)
                if not code:
                    continue
                # Stop if it looks like a header or footer
                if "TOTAL" in str(df.iloc[r_idx, sig_col_idx - 1]).upper() or "TOTAL" in str(df.iloc[r_idx, sig_col_idx]).upper():
                    break
                
                # Get nivel
                nivel = ""
                if nivel_col_idx is not None:
                    nivel = str(df.iloc[r_idx, nivel_col_idx]).strip()
                
                # Get name
                # Name is usually to the left of SIGERD
                name = ""
                for offset in range(1, 3):
                    curr_idx = sig_col_idx - offset
                    if curr_idx >= 0:
                        val = str(header_vals[curr_idx]).strip().upper()
                        if "NOMBRE" in val or "INSTANCIA" in val or "CENTRO" in val:
                            name = str(df.iloc[r_idx, curr_idx]).strip()
                            break
                if not name and sig_col_idx > 0:
                    name = str(df.iloc[r_idx, sig_col_idx - 1]).strip()
                
                if code not in all_centers:
                    all_centers[code] = []
                all_centers[code].append((sheet, name, nivel))

print(f"\nTotal unique SIGERD codes extracted: {len(all_centers)}")

# Print unique levels found
all_levels = set()
for code, occs in all_centers.items():
    for occ in occs:
        all_levels.add(occ[2])
print("\nAll unique LEVEL values in Excel:", all_levels)

# Check a few samples
print("\nSamples:")
for code in list(all_centers.keys())[:10]:
    print(f"Code {code}: {all_centers[code]}")

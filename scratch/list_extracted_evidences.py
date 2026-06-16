import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

log_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\scratch\extraction_results_v2.txt"

with open(log_path, "r", encoding="utf-8") as f:
    content = f.read()

# Parse the file to get all evidences
tables = content.split("=================================================================")
print(f"Total blocks: {len(tables)}")

evidences = []
for t in tables:
    if "Subindicador:" not in t:
        continue
    # Extract subindicator code
    sub_code_match = re.search(r'Subindicador:\s*([\w\d\.\-]+)', t)
    sub_code = sub_code_match.group(1) if sub_code_match else "Unknown"
    
    # Find all Evidencia lines
    ev_matches = re.findall(r'Evidencia \d+:\s*(.*)', t)
    for ev in ev_matches:
        evidences.append((sub_code, ev.strip()))

print(f"Total extracted evidences in log: {len(evidences)}")
print("\nList of extracted evidences:")
for idx, (sub, ev) in enumerate(evidences):
    print(f"{idx+1}. Sub: {sub} | Evidencia: {ev}")

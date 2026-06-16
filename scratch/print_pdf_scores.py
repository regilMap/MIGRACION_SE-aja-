"""
Extract and print all bullet score lines from the PDF by sub-indicator section.
This lets us verify that the porcentual mapping is correct.
"""
import sys, re, pdfplumber
sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = "2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"

full_lines = []
with pdfplumber.open(PDF_PATH) as pdf:
    for page in pdf.pages:
        text = page.extract_text() or ""
        full_lines.extend(text.split("\n"))

# Find sub-indicator headings and their score bullets
sub_ind_re = re.compile(r'^(\d+\.\d+)\.\s+')
bullet_re = re.compile(r'^[▪•●]\s*(\d+)\.\s+(.+)$')

current_si = None
for i, line in enumerate(full_lines):
    stripped = line.strip()
    # Sub-indicator heading
    m_si = sub_ind_re.match(stripped)
    if m_si:
        # Only valid sub-indicators (not versión, etc.)
        code = m_si.group(1)
        if len(code) <= 5:  # e.g. "1.01" not long text
            current_si = code
            # print header
            print(f"\n>>> SUB-INDICATOR {code}: {stripped[:60]}")
            continue
    # Score bullet
    m_b = bullet_re.match(stripped)
    if m_b and current_si:
        print(f"  [{current_si}] Score={m_b.group(1)}: {m_b.group(2)[:70]}")

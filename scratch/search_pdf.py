import fitz

pdf_path = r"c:\Users\regil.batista\Desktop\MIGRACION_SE(aja)\2.1 Guía Actualizada SISMAP 21-05-2026 (1).pdf"
doc = fitz.open(pdf_path)

headers = [
    "Evidencias requeridas y criterios de verificación",
    "Evidencias requeridas y criterios",
    "IBOG PRIMER ÁMBITO",
    "Criterios de verificación",
    "Sub Indicador",
    "Evidencia"
]

results = []
for page_num in range(len(doc)):
    text = doc[page_num].get_text("text")
    found = []
    for h in headers:
        if h.lower() in text.lower():
            found.append(h)
    if found:
        results.append((page_num + 1, found))

print("Matches found by page:")
for page_num, matches in results:
    print(f"Page {page_num}: {', '.join(matches)}")

import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook("Criterios_Evaluacion_SISMAP_Updated.xlsx")
ws = wb.active
for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
    ev_cod = str(row[5]).strip()
    criterio = str(row[8]).strip()
    pct = row[9]
    print(f"Fila {i} | Cod={ev_cod} | Pct={pct} | {criterio}")

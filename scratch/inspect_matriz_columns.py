import pandas as pd

file_path = "Centros modalidad  Primario - Secundario.xlsx"
xl = pd.ExcelFile(file_path)
df = xl.parse("Matriz", header=None)

print("Matriz Sheet Shape:", df.shape)
for r in range(15):
    print(f"Row {r}: {df.iloc[r].tolist()[:10]}")


import pandas as pd
from pathlib import Path

def inspect_excel():
    f = Path("data/exports/contactos_municipales.xlsx")
    if not f.exists():
        print("File not found.")
        return

    try:
        df = pd.read_excel(f)
        print("COLUMNS FOUND:")
        print(list(df.columns))
        print("\nFIRST ROW EXAMPLE:")
        print(df.iloc[0].to_dict())
    except Exception as e:
        print(f"Error reading excel: {e}")

if __name__ == "__main__":
    inspect_excel()

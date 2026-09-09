import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from config import RAW_DATA_DIR

path = RAW_DATA_DIR / "npa.xlsx"

df = pd.read_excel(path, sheet_name="Report 1", header=None, skiprows=11, engine="openpyxl")
df = df.dropna(how="all").reset_index(drop=True)

print(f"Raw shape: {df.shape}")
print(f"\nFirst 15 rows, first 12 cols:")
print(df.iloc[:15, :12].to_string())
print(f"\nAll unique values in col 0:")
print(df.iloc[:, 0].dropna().unique())
print(f"\nAll unique values in col 1 (if exists):")
if df.shape[1] > 1:
    print(df.iloc[:, 1].dropna().unique()[:20])
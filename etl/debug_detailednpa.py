# etl/debug_npa_detailed.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from config import RAW_DATA_DIR

path = RAW_DATA_DIR / "npa_detailed.xlsx"
df = pd.read_excel(path, sheet_name="Report 1", header=None, skiprows=7, engine="openpyxl")
df = df.dropna(how="all").reset_index(drop=True)

print(f"Raw shape: {df.shape}")
print(f"\nFirst 20 rows, first 7 cols:")
print(df.iloc[:20, :7].to_string())
print(f"\nUnique col 0 values:")
print(df.iloc[:, 0].dropna().unique()[:10])
print(f"\nUnique col 1 values (first 20):")
print(df.iloc[:, 1].dropna().unique()[:20])
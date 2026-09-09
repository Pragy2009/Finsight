# etl/debug_npa_full.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from config import RAW_DATA_DIR

path = RAW_DATA_DIR / "npa.xlsx"
df = pd.read_excel(path, sheet_name="Report 1", header=None, skiprows=11, engine="openpyxl")
df = df.dropna(how="all").reset_index(drop=True)

pd.set_option('display.max_rows', 200)
print(f"Total rows: {len(df)}")
print(f"\nFull col 1 (year) and col 0 values, row by row:")
for i in range(len(df)):
    col0 = df.iloc[i, 0]
    col1 = df.iloc[i, 1]
    print(f"row {i:3d}: col0={repr(col0)}, col1={repr(col1)}")
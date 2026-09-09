# etl/debug_subtotals.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from config import RAW_DATA_DIR

path = RAW_DATA_DIR / "npa_detailed.xlsx"
df = pd.read_excel(path, sheet_name="Report 1", header=None, skiprows=7, engine="openpyxl")
df = df.dropna(how="all").reset_index(drop=True)
df = df.iloc[:, 1:6]
df.columns = ["year", "bank_name", "gross_npa", "gross_advances", "gross_npa_ratio_pct"]
df["year"] = pd.to_numeric(df["year"], errors="coerce").ffill()
df["bank_name"] = df["bank_name"].astype(str).str.strip()
df = df[df["bank_name"].str.len() > 2]
df = df[df["bank_name"] != "nan"]

print(f"Total rows before subtotal filter: {len(df)}")
print(f"\nAll unique bank_name values (first 60):")
for i, name in enumerate(df["bank_name"].unique()[:60]):
    print(f"  {i:3d}: {repr(name)}")
print(f"\nAll unique bank_name values (60 onwards):")
for i, name in enumerate(df["bank_name"].unique()[60:]):
    print(f"  {i+60:3d}: {repr(name)}")
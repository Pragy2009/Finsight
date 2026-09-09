# etl/debug_sectoral2.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from config import RAW_DATA_DIR

path = RAW_DATA_DIR / "sectoral_credit.xlsx"

df_raw = pd.read_excel(path, sheet_name=0, header=None, engine="openpyxl")
print(f"Total columns in file: {df_raw.shape[1]}")
print(f"Total rows in file: {df_raw.shape[0]}")

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)

print("\nRow 6 (date header), ALL columns:")
print(df_raw.iloc[6].to_dict())

print("\nRow 7 (Non-food Credit totals), ALL columns:")
print(df_raw.iloc[7].to_dict())

print("\nRow 9 (Agriculture), ALL columns:")
print(df_raw.iloc[9].to_dict())
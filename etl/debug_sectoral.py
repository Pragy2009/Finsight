# etl/debug_sectoral.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from config import RAW_DATA_DIR

path = RAW_DATA_DIR / "sectoral_credit.xlsx"

# Read raw with no skip to see everything from row 0
df_raw = pd.read_excel(path, sheet_name=0, header=None, engine="openpyxl")

print("Rows 0-10, all columns:")
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
print(df_raw.iloc[0:10, 0:14].to_string())
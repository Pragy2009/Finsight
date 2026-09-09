"""
Test runner for ETL ingestion module.
Run from project root: python etl/test_ingest.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.ingest import load_all

def test_all():
    datasets = load_all()
    print("\n── Ingestion Results ──────────────────────")
    for name, df in datasets.items():
        print(f"\n{name}:")
        print(f"  Shape     : {df.shape}")
        print(f"  Columns   : {list(df.columns)}")
        print(f"  First row : {df.iloc[0].to_dict()}")
        null_counts = df.isnull().sum()
        if null_counts.any():
            print(f"  Nulls     : {null_counts[null_counts > 0].to_dict()}")

if __name__ == "__main__":
    test_all()
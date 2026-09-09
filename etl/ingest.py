"""
ETL Ingestion Module — FinSight
Loads all raw DBIE Excel files into cleaned pandas DataFrames.
Each loader is specific to one file's layout.
No column names are assumed — all derived from actual file inspection.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Optional

from config import RAW_DATA_DIR
from logger import get_logger

logger = get_logger(__name__)


# ── 1. BALANCE SHEET ────────────────────────────────────────────────────────

def load_balance_sheet() -> pd.DataFrame:
    """
    Loads: balance_sheet.xlsx
    Layout: Title row 2, multi-row merged headers rows 5-7,
            column numbers row 8, data from row 9.
    """
    path = RAW_DATA_DIR / "balance_sheet.xlsx"
    _validate_file(path)

    logger.info("Loading balance_sheet.xlsx")

    df = pd.read_excel(
        path,
        sheet_name="Report 1",
        header=None,
        skiprows=8,
        engine="openpyxl"
    )

    df = df.dropna(how="all").reset_index(drop=True)
    df = df.dropna(axis=1, how="all")

    df.columns = [
        "year",
        "capital",
        "reserves_surplus",
        "deposits",
        "borrowings",
        "other_liabilities_provisions",
        "cash_balances_rbi",
        "balances_call_short_notice",
        "investments",
        "loans_advances",
        "fixed_assets",
        "other_assets",
        "total_liabilities_assets"
    ]

    df["year"] = df["year"].astype(str).str.strip()
    df = df[df["year"].str.match(r"^\d{4}-\d{2,4}$", na=False)]

    numeric_cols = [c for c in df.columns if c != "year"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=["total_liabilities_assets"])

    df = df.reset_index(drop=True)
    logger.info(f"balance_sheet loaded: {len(df)} rows, {len(df.columns)} columns")
    return df


# ── 2. NPA TIME SERIES ──────────────────────────────────────────────────────

def load_npa() -> pd.DataFrame:
    """
    Loads: npa.xlsx
    Only the first block (rows 0-27) is the SCB aggregate time series.
    Everything after 'Public Sector Banks' label is a different bank-group section.
    """
    path = RAW_DATA_DIR / "npa.xlsx"
    _validate_file(path)
    logger.info("Loading npa.xlsx")

    df = pd.read_excel(
        path, sheet_name="Report 1",
        header=None, skiprows=11, engine="openpyxl"
    )

    df = df.dropna(how="all").reset_index(drop=True)
    df = df.iloc[:, 1:10]

    df.columns = [
        "year", "gross_advances", "net_advances",
        "gross_npa_amount", "gross_npa_pct_gross_advances",
        "gross_npa_pct_total_assets", "net_npa_amount",
        "net_npa_pct_net_advances", "net_npa_pct_total_assets"
    ]

    df["year"] = df["year"].astype(str).str.strip()

    # Find where the first section ends — first row that is NOT a valid year format
    # marks the start of "Public Sector Banks" and subsequent sections
    valid_year_mask = df["year"].str.match(r"^\d{4}-\d{2,4}$", na=False)

    # Take only the CONTIGUOUS block from the top (SCB aggregate)
    # Stop at first False after the initial True run
    first_invalid_idx = None
    for i, is_valid in enumerate(valid_year_mask):
        if not is_valid:
            first_invalid_idx = i
            break

    if first_invalid_idx is not None:
        df = df.iloc[:first_invalid_idx]
    else:
        df = df[valid_year_mask]

    numeric_cols = [c for c in df.columns if c != "year"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=["gross_npa_amount"])
    df = df.reset_index(drop=True)

    logger.info(f"npa loaded: {len(df)} rows (SCB aggregate only)")
    return df


# ── 3. NPA DETAILED (BANK-WISE CROSS SECTION) ───────────────────────────────

def load_npa_detailed() -> pd.DataFrame:
    """
    Loads: npa_detailed.xlsx
    Col 0: blank spacer. Col 1: year (sparse int). Col 2: bank_name.
    Cols 3-5: NPA metrics. Multi-year stacked, individual banks only.
    """
    path = RAW_DATA_DIR / "npa_detailed.xlsx"
    _validate_file(path)
    logger.info("Loading npa_detailed.xlsx")

    df = pd.read_excel(
        path, sheet_name="Report 1",
        header=None, skiprows=7, engine="openpyxl"
    )

    df = df.dropna(how="all").reset_index(drop=True)

    df = df.iloc[:, 1:6]

    df.columns = [
        "year", "bank_name",
        "gross_npa", "gross_advances", "gross_npa_ratio_pct"
    ]

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["year"] = df["year"].ffill()
    df["year"] = df["year"].astype("Int64").astype(str)

    df["bank_name"] = df["bank_name"].astype(str).str.strip()
    df = df[df["bank_name"].str.len() > 2]
    df = df[df["bank_name"] != "nan"]

    # Drop only confirmed aggregate/subtotal rows — exact match, verified from actual file
    subtotal_exact = {
        "PUBLIC SECTOR BANKS",
        "PRIVATE SECTOR BANKS",
        "FOREIGN BANKS",
        "SMALL FINANCE BANKS",
        "ALL SCHEDULED COMMERCIAL BANKS",
        "NATIONALISED BANKS",
        "STATE BANK OF INDIA AND ITS ASSOCIATES",
    }
    df = df[~df["bank_name"].str.upper().isin(subtotal_exact)]

    numeric_cols = ["gross_npa", "gross_advances", "gross_npa_ratio_pct"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=["gross_npa"])
    df = df.reset_index(drop=True)

    logger.info(f"npa_detailed loaded: {len(df)} rows")
    return df


# ── 4. CRAR DISTRIBUTION ────────────────────────────────────────────────────

def load_car() -> pd.DataFrame:
    """
    Loads: car.xlsx
    Layout: Title row 2, unit row 4, headers rows 5-6, data from row 8.
    3 CRAR bands per year, year column sparse.
    """
    path = RAW_DATA_DIR / "car.xlsx"
    _validate_file(path)
    logger.info("Loading car.xlsx")

    df = pd.read_excel(
        path,
        sheet_name="Report 1",
        header=None,
        skiprows=7,
        engine="openpyxl"
    )

    df = df.dropna(how="all").reset_index(drop=True)
    df = df.dropna(axis=1, how="all")

    df.columns = [
        "year",
        "crar_band",
        "state_bank_group",
        "nationalised_banks",
        "old_private_sector_banks",
        "new_private_sector_banks",
        "foreign_banks_india",
        "scheduled_commercial_banks",
        "other_public_sector_bank",
        "capital_adequacy_ratio_pct"
    ]

    df["year"] = df["year"].replace("", np.nan)
    df["year"] = df["year"].ffill()
    df["year"] = df["year"].astype(str).str.strip()
    df = df[df["year"].str.match(r"^\d{4}-\d{2,4}$", na=False)]

    df["crar_band"] = df["crar_band"].astype(str).str.strip()

    numeric_cols = [c for c in df.columns if c not in ["year", "crar_band"]]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    df = df.reset_index(drop=True)

    logger.info(f"car loaded: {len(df)} rows")
    return df


# ── 5. SECTORAL CREDIT ──────────────────────────────────────────────────────

def load_sectoral_credit() -> pd.DataFrame:
    """
    Loads: sectoral_credit.xlsx
    Col 2: sr_no. Col 3: sector. Cols 4-11: dates (8 years, 2019-2026).
    """
    path = RAW_DATA_DIR / "sectoral_credit.xlsx"
    _validate_file(path)
    logger.info("Loading sectoral_credit.xlsx")

    # Read date header row (row index 6, 0-indexed)
    header_df = pd.read_excel(
        path, sheet_name=0, header=None,
        skiprows=6, nrows=1, engine="openpyxl"
    )
    header_row = header_df.iloc[0].tolist()

    # Dates start at column index 4
    date_columns = []
    for val in header_row[4:]:
        if pd.notna(val):
            date_columns.append(str(val).strip())

    logger.debug(f"Detected date columns: {date_columns}")

    df = pd.read_excel(
        path, sheet_name=0, header=None,
        skiprows=7, engine="openpyxl"
    )
    df = df.dropna(how="all").reset_index(drop=True)

    n_dates = len(date_columns)
    df = df.iloc[:, 2:4 + n_dates]
    df.columns = ["sr_no", "sector"] + date_columns

    df["sector"] = df["sector"].astype(str).str.strip()
    df = df[df["sector"].notna()]
    df = df[df["sector"] != "nan"]
    df = df[df["sector"].str.len() > 1]
    df = df[~df["sector"].str.startswith("(")]

    df_long = df.melt(
        id_vars=["sr_no", "sector"],
        value_vars=date_columns,
        var_name="date",
        value_name="amount_crore"
    )

    df_long["amount_crore"] = (
        df_long["amount_crore"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("(", "-", regex=False)
        .str.replace(")", "", regex=False)
    )
    df_long["amount_crore"] = pd.to_numeric(df_long["amount_crore"], errors="coerce")
    df_long = df_long.dropna(subset=["amount_crore"])
    df_long = df_long.reset_index(drop=True)

    logger.info(f"sectoral_credit loaded: {len(df_long)} rows (long format)")
    return df_long


# ── UTILITY ─────────────────────────────────────────────────────────────────

def _validate_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Required data file not found: {path}\n"
            f"Download from RBI DBIE and place in data/raw/"
        )


def load_all() -> dict:
    logger.info("Loading all datasets...")
    datasets = {
        "balance_sheet":  load_balance_sheet(),
        "npa":            load_npa(),
        "npa_detailed":   load_npa_detailed(),
        "car":            load_car(),
        "sectoral_credit": load_sectoral_credit(),
    }
    logger.info("All datasets loaded successfully.")
    return datasets
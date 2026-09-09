"""
Central configuration for FinSight.
All paths and constants live here.
"""
from pathlib import Path

# Root directory
ROOT_DIR = Path(__file__).parent

# Data paths
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

# Output paths
OUTPUTS_DIR = ROOT_DIR / "outputs"
LOGS_DIR = ROOT_DIR / "logs"
DB_PATH = ROOT_DIR / "db" / "finsight.db"

# Report templates
TEMPLATES_DIR = ROOT_DIR / "reports" / "templates"
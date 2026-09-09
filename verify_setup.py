"""Run this to confirm Phase 1 setup is complete."""
from pathlib import Path
import sys

required_dirs = [
    "data/raw", "data/processed", "etl", "analysis",
    "dashboard", "reports/templates", "scheduler", "db",
    "outputs", "logs"
]

required_files = [
    "config.py", "logger.py", "requirements.txt"
]

print("Checking directories...")
all_ok = True
for d in required_dirs:
    exists = Path(d).exists()
    status = "✅" if exists else "❌"
    print(f"  {status} {d}")
    if not exists:
        all_ok = False

print("\nChecking files...")
for f in required_files:
    exists = Path(f).exists()
    status = "✅" if exists else "❌"
    print(f"  {status} {f}")
    if not exists:
        all_ok = False

print("\nChecking packages...")
packages = ["pandas", "numpy", "dash", "plotly",
            "scipy", "statsmodels", "fpdf", "apscheduler"]
for pkg in packages:
    try:
        __import__(pkg)
        print(f"  ✅ {pkg}")
    except ImportError:
        print(f"  ❌ {pkg} — run: pip install -r requirements.txt")
        all_ok = False

if all_ok:
    print("\n✅ Phase 1 complete. Ready for Phase 2.")
else:
    print("\n❌ Fix the above issues before continuing.")
    sys.exit(1)
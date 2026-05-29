"""Central configuration for the revenue analytics pipeline.

Keeping paths and column names in one place means the rest of the code never
hard-codes a filename. To run against the real export instead of the bundled
sample, point INPUT_CSV at your own file (and keep that file out of git).
"""

from pathlib import Path

# --- Project paths -----------------------------------------------------------
# PROJECT_ROOT resolves to the repo root regardless of where you run from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Default input is the synthetic sample so the project runs out of the box.
# Override with the REVENUE_INPUT_CSV environment variable to use real data.
import os

INPUT_CSV = Path(
    os.environ.get("REVENUE_INPUT_CSV", DATA_DIR / "sample" / "sample_sales.csv")
)

# --- Forecast settings -------------------------------------------------------
FORECAST_MONTHS = 14  # how many months ahead Prophet projects

# --- Domain values -----------------------------------------------------------
# Rows whose Item is one of these are treated as damage/loss, not sales.
DAMAGE_ITEMS = ("Damaged", "Lost")

# Number of rows kept in each "top N" ranking table.
TOP_N = 10

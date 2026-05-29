"""Loading and cleaning the raw sales export.

The raw NetSuite CSV has human-friendly column names with spaces and
parentheses (e.g. "Amount (Tax)", "Shipping State/Province") and string-typed
money columns. This module normalises all of that into a tidy DataFrame the
rest of the pipeline can rely on.
"""

import pandas as pd


def load_data(file_path):
    """Read the raw CSV into a DataFrame.

    latin1 encoding is used because the NetSuite export contains a few
    non-UTF-8 characters (e.g. accented customer names) that crash the
    default utf-8 reader.
    """
    return pd.read_csv(file_path, encoding="latin1")


# Money columns that arrive as strings and must be coerced to numbers.
_NUMERIC_COLS = [
    "Item_Rate",
    "Amount_Tax",
    "Amount_Shipping",
    "Amount_Transaction_Total",
    "Amount_Discount",
    "Amount",
]


def _normalise_columns(df):
    """Strip whitespace and remove spaces/parentheses from column names.

    "Amount (Tax)" -> "Amount_Tax", "Shipping State/Province" ->
    "Shipping_State/Province". Done once so every later step can use stable,
    predictable column names.
    """
    df.columns = (
        df.columns.str.strip()
        .str.replace(" ", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )
    return df


def clean_data(df):
    """Return a cleaned sales DataFrame ready for aggregation.

    Steps: parse dates, derive year/month/day, coerce money columns to
    numeric, drop discount and rate-less rows, and label missing shipping
    locations as "Headquarters".
    """
    # Date string -> datetime, then break out parts we group on later.
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month
    df["day"] = df["Date"].dt.day

    # Fill blank numeric cells with 0 before any maths.
    numeric_cells = df.select_dtypes(include="number")
    df[numeric_cells.columns] = numeric_cells.fillna(0)

    df = _normalise_columns(df)

    # Trim stray whitespace inside string cells (e.g. " Acme " -> "Acme").
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    # Some money columns are stored as text; coerce them to real numbers.
    for col in _NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Discount line items are adjustments, not sales -> drop them.
    is_discount = df["Item"].str.contains("Discount", case=False, na=False)
    df = df[~is_discount]

    # A null Item_Rate means the row has no priced product -> drop it.
    df = df.dropna(subset=["Item_Rate"])

    # Orders with no shipping location are internal/HQ activity.
    df["Shipping_State/Province"] = df["Shipping_State/Province"].fillna("Headquarters")

    return df


def separate_sales_and_damage(df):
    """Split cleaned rows into real sales vs. damaged/lost inventory.

    Returns (sales_df, damage_df). Damage is analysed separately so it never
    inflates revenue numbers.
    """
    from .config import DAMAGE_ITEMS

    damage_df = df[df["Item"].isin(DAMAGE_ITEMS)]
    sales_df = df[~df["Item"].isin(DAMAGE_ITEMS)]
    return sales_df, damage_df

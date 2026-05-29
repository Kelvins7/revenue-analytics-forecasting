"""Generate a synthetic sales export that mimics the real NetSuite schema.

This produces data/sample/sample_sales.csv with the SAME columns and quirks as
the real export (spaces/parentheses in headers, money stored as text, discount
and damaged/lost line items) -- but every value is randomly generated. No real
company data is used or required.

Run once with:  python generate_sample_data.py
"""

import random
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

OUT = Path(__file__).resolve().parent / "data" / "sample" / "sample_sales.csv"

# Fictional dimensions -------------------------------------------------------
BRANDS = ["Aurora", "Northwind", "Crestline", "Vanta"]
CATEGORIES = ["Beverages", "Snacks", "Household", "Personal Care"]
CUSTOMERS = [
    "Maple Grocers", "Riverside Market", "Summit Foods", "Harbor Wholesale",
    "Pine Street Deli", "Oakwood Retail", "Lakeside Provisions", "Cedar Mart",
    "Birch & Co", "Willow Distributors",
]
STATES = ["NJ", "NY", "PA", "CT", "MA", "DE", "MD"]
ITEMS = ["Spring Water 24pk", "Trail Mix", "Dish Soap", "Hand Lotion", "Cola 12pk"]


def _month_starts(start_year=2022, end_year=2025):
    return pd.date_range(f"{start_year}-01-01", f"{end_year}-12-01", freq="MS")


def build_rows():
    rows = []
    doc = 1000
    for month in _month_starts():
        # Seasonal lift: a gentle yearly bump peaking mid-year, plus growth.
        season = 1.0 + 0.25 * np.sin((month.month / 12) * 2 * np.pi)
        growth = 1.0 + 0.04 * (month.year - 2022)

        # A random handful of orders each month.
        for _ in range(np.random.randint(18, 30)):
            doc += 1
            brand = random.choice(BRANDS)
            qty = int(np.random.randint(5, 120))
            rate = round(np.random.uniform(3.0, 45.0), 2)
            base = round(qty * rate * season * growth, 2)
            tax = round(base * 0.06, 2)
            shipping = round(np.random.uniform(0, 50), 2)

            rows.append({
                "Date": month.strftime("%m/%d/%Y"),
                "Document Number": f"SO{doc}",
                "Name": random.choice(CUSTOMERS),
                "Item": random.choice(ITEMS),
                "Brand": brand,
                "Category": random.choice(CATEGORIES),
                "Quantity": qty,
                "Item Rate": rate,
                "Amount (Tax)": tax,
                "Amount (Shipping)": shipping,
                "Amount (Transaction Total)": round(base + tax + shipping, 2),
                "Amount (Discount)": 0,
                "Amount": base,
                "Shipping State/Province": random.choice(STATES),
            })

        # Occasional discount line (should be dropped by clean_data).
        if np.random.rand() < 0.5:
            doc += 1
            rows.append({
                "Date": month.strftime("%m/%d/%Y"),
                "Document Number": f"SO{doc}",
                "Name": random.choice(CUSTOMERS),
                "Item": "Volume Discount",
                "Brand": random.choice(BRANDS),
                "Category": random.choice(CATEGORIES),
                "Quantity": 1,
                "Item Rate": -round(np.random.uniform(20, 200), 2),
                "Amount (Tax)": 0,
                "Amount (Shipping)": 0,
                "Amount (Transaction Total)": 0,
                "Amount (Discount)": round(np.random.uniform(20, 200), 2),
                "Amount": -round(np.random.uniform(20, 200), 2),
                "Shipping State/Province": random.choice(STATES),
            })

        # Occasional damaged/lost line (routed to the damage report).
        if np.random.rand() < 0.6:
            doc += 1
            rows.append({
                "Date": month.strftime("%m/%d/%Y"),
                "Document Number": f"SO{doc}",
                "Name": random.choice(CUSTOMERS),
                "Item": random.choice(["Damaged", "Lost"]),
                "Brand": random.choice(BRANDS),
                "Category": random.choice(CATEGORIES),
                "Quantity": int(np.random.randint(1, 10)),
                "Item Rate": round(np.random.uniform(3.0, 45.0), 2),
                "Amount (Tax)": 0,
                "Amount (Shipping)": 0,
                "Amount (Transaction Total)": 0,
                "Amount (Discount)": 0,
                "Amount": round(np.random.uniform(50, 800), 2),
                "Shipping State/Province": random.choice(STATES + [None]),
            })

    return rows


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(build_rows())
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df):,} synthetic rows to {OUT}")


if __name__ == "__main__":
    main()

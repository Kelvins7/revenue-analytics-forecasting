"""Generate the chart set from the aggregated views.

Every chart is saved as a PNG into the outputs/ directory. The script is
designed to run headless (no plt.show()), so it produces the full image set
in one pass -- handy for a scheduled/automated report.
"""

import matplotlib

matplotlib.use("Agg")  # headless backend: render to file, never pop a window.

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

from .config import OUTPUT_DIR

# Reusable formatter that renders the y-axis as currency, e.g. $1,250.
_DOLLARS = ticker.StrMethodFormatter("${x:,.0f}")


def _month_start(df):
    """Build a month-start datetime column from year + month for plotting."""
    return pd.to_datetime(
        df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2) + "-01"
    )


def _save(fig_name):
    """Save the current figure into outputs/ and close it to free memory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT_DIR / fig_name, dpi=300, bbox_inches="tight")
    plt.close()


def _company_monthly_revenue(views):
    monthly = views["grouped_month"].copy()
    monthly["date"] = _month_start(monthly)
    monthly = monthly.sort_values("date")

    plt.figure(figsize=(12, 6))
    plt.plot(monthly["date"], monthly["Amount"], marker="o")
    plt.title("Company Monthly Revenue")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.grid(True)
    plt.gca().yaxis.set_major_formatter(_DOLLARS)
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    _save("Company_Monthly_Revenue.png")


def _company_yearly_revenue(views):
    yearly = views["grouped_year"].copy().sort_values("year")
    plt.figure(figsize=(12, 6))
    plt.plot(yearly["year"], yearly["Amount"], marker="o")
    plt.title("Company Yearly Revenue")
    plt.xlabel("Year")
    plt.ylabel("Revenue")
    plt.grid(True)
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_formatter(_DOLLARS)
    plt.tight_layout()
    _save("Company_Yearly_Revenue.png")


def _company_yearly_damages(damage_views):
    d_yearly = damage_views["grouped_year"].copy()
    d_yearly["year"] = d_yearly["year"].astype(int)
    plt.figure(figsize=(8, 6))
    plt.plot(d_yearly["year"], d_yearly["Amount"], marker="o")
    plt.title("Company Yearly Damages")
    plt.xlabel("Year")
    plt.ylabel("Damages")
    plt.grid(True)
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_formatter(_DOLLARS)
    plt.tight_layout()
    _save("Company_Yearly_Damages.png")


def _brand_monthly_revenue(views):
    brand_monthly = views["grouped_brand"].copy()
    brand_monthly["date"] = _month_start(brand_monthly)
    brand_monthly = brand_monthly.sort_values(["Brand", "date"])

    plt.figure(figsize=(12, 6))
    for brand in brand_monthly["Brand"].unique():
        brand_data = brand_monthly[brand_monthly["Brand"] == brand]
        plt.plot(brand_data["date"], brand_data["Amount"], marker="o", label=brand)
    plt.title("Brand Monthly Revenue")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.grid(True)
    plt.gca().yaxis.set_major_formatter(_DOLLARS)
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.legend(title="Brand")
    plt.xticks(rotation=45)
    plt.tight_layout()
    _save("Brand_Monthly_Revenue.png")


def _brand_yearly_revenue(views):
    pivot_brand = views["brand_yearly"].copy().pivot(
        index="year", columns="Brand", values="Amount"
    )
    pivot_brand.plot(kind="bar", figsize=(10, 6))
    plt.title("Brand Yearly Revenue")
    plt.xlabel("Year")
    plt.ylabel("Revenue")
    plt.grid(True)
    plt.gca().yaxis.set_major_formatter(_DOLLARS)
    plt.xticks(rotation=45)
    plt.tight_layout()
    _save("Brand_Yearly_Revenue.png")


def _quantity_by_state(views):
    state_q = views["states_q"].copy().sort_values("Quantity")
    state_col = [c for c in state_q.columns if c != "Quantity"][0]
    plt.figure(figsize=(12, 8))
    plt.barh(state_q[state_col], state_q["Quantity"])
    plt.title("Quantity Distribution by State")
    plt.xlabel("Quantity")
    plt.ylabel("State")
    plt.grid(True, axis="x")
    plt.tight_layout()
    _save("Quantity_Distribution_by_State.png")


def _revenue_by_state(views):
    state_a = views["states_a"].copy().sort_values("Amount")
    state_col = [c for c in state_a.columns if c != "Amount"][0]
    plt.figure(figsize=(12, 8))
    plt.barh(state_a[state_col], state_a["Amount"])
    plt.title("Revenue Distribution by State")
    plt.xlabel("Revenue")
    plt.ylabel("State")
    plt.grid(True, axis="x")
    plt.gca().xaxis.set_major_formatter(_DOLLARS)
    plt.tight_layout()
    _save("Revenue_Distribution_by_State.png")


def _top_customer_yearly_revenue(views):
    customer_year = views["customer_groups_amount"].copy()
    top_customers = (
        customer_year.groupby("Name")["Amount"].sum().sort_values(ascending=False).head(10).index
    )
    customer_year = customer_year.sort_values(["Name", "year"])
    customer_year["year"] = customer_year["year"].astype(int)

    plt.figure(figsize=(12, 6))
    for customer in top_customers:
        data = customer_year[customer_year["Name"] == customer]
        plt.plot(data["year"], data["Amount"], marker="o", label=customer)
    plt.title("Top Customer Yearly Revenue")
    plt.xlabel("Year")
    plt.ylabel("Revenue")
    plt.grid(True, axis="x")
    plt.gca().yaxis.set_major_formatter(_DOLLARS)
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    _save("Top_customer_yearly_revenue.png")


def _category_monthly_revenue(views):
    category_monthly = views["category_month"].copy()
    category_monthly["date"] = _month_start(category_monthly)
    category_monthly = category_monthly.sort_values(["Category", "date"])

    plt.figure(figsize=(12, 6))
    for category in category_monthly["Category"].dropna().unique():
        category_data = category_monthly[category_monthly["Category"] == category]
        plt.plot(category_data["date"], category_data["Amount"], marker="o", label=category)
    plt.title("Category Monthly Revenue")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.grid(True)
    plt.gca().yaxis.set_major_formatter(_DOLLARS)
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.legend(title="Category")
    plt.xticks(rotation=45)
    plt.tight_layout()
    _save("Category_Monthly_Revenue.png")


def _category_yearly_revenue(views):
    category_year = views["category_year"].copy()
    category_year["year"] = category_year["year"].astype(int)
    category_year = category_year.sort_values(["Category", "Name", "year"])

    # Rank customers within each category so we only plot the top few per line.
    ranked = (
        category_year.groupby(["Category", "Name"])["Amount"]
        .sum()
        .reset_index()
        .sort_values(["Category", "Amount"], ascending=[True, False])
    )

    plt.figure(figsize=(12, 6))
    for category in category_year["Category"].dropna().unique():
        top_names = ranked[ranked["Category"] == category].head(5)["Name"]
        data = category_year[
            (category_year["Category"] == category) & (category_year["Name"].isin(top_names))
        ]
        for customer in data["Name"].unique():
            c_data = data[data["Name"] == customer]
            plt.plot(
                c_data["year"], c_data["Amount"], marker="o", label=f"{customer} ({category})"
            )
    plt.title("Category Yearly Revenue")
    plt.xlabel("Year")
    plt.ylabel("Revenue")
    plt.grid(True)
    plt.gca().yaxis.set_major_formatter(_DOLLARS)
    plt.xticks(rotation=45)
    plt.tight_layout()
    _save("Category_Yearly_Revenue.png")


def create_charts(views, damage_views):
    """Generate and save every chart for sales and damage data."""
    _company_monthly_revenue(views)
    _company_yearly_revenue(views)
    _company_yearly_damages(damage_views)
    _brand_monthly_revenue(views)
    _brand_yearly_revenue(views)
    _quantity_by_state(views)
    _revenue_by_state(views)
    _top_customer_yearly_revenue(views)
    _category_monthly_revenue(views)
    _category_yearly_revenue(views)

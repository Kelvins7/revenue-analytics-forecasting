"""Aggregate cleaned rows into the 14 summary views used downstream.

Each value in the returned dict is a small DataFrame answering one business
question (revenue by brand/month, by state, by customer, by category, etc.).
Charts, rankings and the forecast all read from these views.
"""


def aggregate_views(df):
    """Build and return all summary views keyed by name."""
    # --- Revenue by brand --------------------------------------------------
    grouped_brand = df.groupby(["year", "month", "Brand"])["Amount"].sum().reset_index()
    brand_yearly = df.groupby(["year", "Brand"])["Amount"].sum().reset_index()

    # --- Company-wide revenue ---------------------------------------------
    grouped_month = df.groupby(["year", "month"])["Amount"].sum().reset_index()
    grouped_month["Brand"] = "brand_Monthly Total"

    grouped_year = df.groupby(["year"])["Amount"].sum().reset_index()
    grouped_year["Brand"] = "Yearly Total"

    # --- Revenue & quantity by shipping state -----------------------------
    states_a = df.groupby(["Shipping_State/Province"])["Amount"].sum().reset_index()
    state_a_yearly = (
        df.groupby(["Shipping_State/Province", "year"])["Amount"].sum().reset_index()
    )
    states_q = df.groupby(["Shipping_State/Province"])["Quantity"].sum().reset_index()
    state_q_yearly = (
        df.groupby(["Shipping_State/Province", "year"])["Quantity"].sum().reset_index()
    )

    # --- Customer (Name) breakdowns ---------------------------------------
    customer_groups = df.groupby(["Name", "Brand", "year"])["Quantity"].sum().reset_index()
    customer_overall = df.groupby(["Name", "Brand"])["Quantity"].sum().reset_index()
    customer_groups_amount = (
        df.groupby(["Name", "Brand", "year"])["Amount"].sum().reset_index()
    )
    customer_overall_amount = (
        df.groupby(["Name", "Brand"])["Amount"].sum().reset_index()
    )

    # --- Category breakdowns ----------------------------------------------
    category_month = (
        df.groupby(["year", "month", "Name", "Category"])["Amount"].sum().reset_index()
    )
    category_year = (
        df.groupby(["year", "Name", "Category"])["Amount"].sum().reset_index()
    )

    return {
        "grouped_brand": grouped_brand,
        "brand_yearly": brand_yearly,
        "grouped_month": grouped_month,
        "grouped_year": grouped_year,
        "customer_groups": customer_groups,
        "customer_overall": customer_overall,
        "customer_groups_amount": customer_groups_amount,
        "customer_overall_amount": customer_overall_amount,
        "state_a_yearly": state_a_yearly,
        "states_a": states_a,
        "states_q": states_q,
        "state_q_yearly": state_q_yearly,
        "category_year": category_year,
        "category_month": category_month,
    }

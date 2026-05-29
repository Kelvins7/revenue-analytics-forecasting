"""Rank the aggregated views into 'top N' / 'bottom N' tables.

Pure sorting and slicing on the views from aggregate.py -- no new data is
computed here, it just surfaces the highest and lowest performers.
"""

from .config import TOP_N


def _top(df, column, ascending=False, n=TOP_N):
    """Return the n rows with the highest (or lowest) value in `column`."""
    return df.sort_values(column, ascending=ascending).head(n)


def rank_views(views):
    """Return a dict of ranking tables derived from the aggregated views."""
    return {
        "top_months_brands": _top(views["grouped_brand"], "Amount"),
        "lowest_months_brands": _top(views["grouped_brand"], "Amount", ascending=True),
        "top_years_brand": _top(views["brand_yearly"], "Amount"),
        "lowest_years_brand": _top(views["brand_yearly"], "Amount", ascending=True),
        "top_years": _top(views["grouped_year"], "Amount"),
        "lowest_years": _top(views["grouped_year"], "Amount", ascending=True),
        "top_months": _top(views["grouped_month"], "Amount"),
        "lowest_months": _top(views["grouped_month"], "Amount", ascending=True),
        "top_customer_q_yearly": _top(views["customer_groups"], "Quantity"),
        "top_customer_a_yearly": _top(views["customer_groups_amount"], "Amount"),
        "top_customer_a_overall": _top(views["customer_overall_amount"], "Amount"),
        "top_state_a_yearly": _top(views["state_a_yearly"], "Amount"),
        "top_states_a": _top(views["states_a"], "Amount"),
        "top_states_q": _top(views["states_q"], "Quantity"),
        "top_state_q_yearly": _top(views["state_q_yearly"], "Quantity"),
        "top_category_yearly": _top(views["category_year"], "Amount"),
        "top_category_month": _top(views["category_month"], "Amount"),
    }

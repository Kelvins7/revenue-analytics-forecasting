"""Write a single human-readable results.txt summarising the whole run.

Contains the forecast tail, every ranking table, and the raw grouped views
for both sales and damage data -- a quick artefact to skim without rerunning.
"""

from .config import OUTPUT_DIR

_FORECAST_COLS = ["ds", "yhat", "yhat_lower", "yhat_upper"]


def save_results(views, forecast, rankings, damage_views):
    """Dump forecast, rankings and grouped data to outputs/results.txt."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "results.txt"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("==================== FORECAST ======================\n\n")
        forecast_tail = forecast.tail(12)
        f.write(forecast_tail[_FORECAST_COLS].to_string(index=False))

        f.write("\n\n\n================== ANALYSIS RESULTS ===============\n\n")
        for name, table in rankings.items():
            f.write(f"\n{name}:\n{table}\n\n")

        f.write("\n================== GROUPED DATA ===============\n\n")
        for name, view in views.items():
            f.write(f"\n{name}\n{view.to_string()}\n\n")

        f.write("================== DAMAGED DATA ===============\n\n")
        for name, view in damage_views.items():
            f.write(f"\n{name}\n{view.to_string()}\n\n")

    return out_path

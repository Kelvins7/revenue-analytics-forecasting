"""Revenue Analytics & Forecasting System -- entry point.

Pipeline: load -> clean -> split sales/damage -> aggregate -> rank ->
chart -> forecast -> write results. Run with:

    python main.py

By default it reads the bundled synthetic sample (data/sample/sample_sales.csv).
Set REVENUE_INPUT_CSV to point at a real export instead.
"""

from src.aggregate import aggregate_views
from src.analyze import rank_views
from src.config import INPUT_CSV, OUTPUT_DIR
from src.forecast import build_forecast, save_forecast_plots
from src.load_clean import clean_data, load_data, separate_sales_and_damage
from src.results import save_results
from src.visualize import create_charts


def main():
    print(f"Loading data from: {INPUT_CSV}")
    df = load_data(INPUT_CSV)
    df = clean_data(df)

    sales_df, damage_df = separate_sales_and_damage(df)

    sales_views = aggregate_views(sales_df)
    damage_views = aggregate_views(damage_df)

    rankings = rank_views(sales_views)

    print("Building charts...")
    create_charts(sales_views, damage_views)

    print("Fitting forecast model...")
    model, forecast = build_forecast(sales_views)
    save_forecast_plots(model, forecast)

    results_path = save_results(sales_views, forecast, rankings, damage_views)
    print(f"Done. Charts and results written to: {OUTPUT_DIR}")
    print(f"Summary: {results_path}")


if __name__ == "__main__":
    main()

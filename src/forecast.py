"""Monthly revenue forecasting with Prophet.

Takes the company monthly-revenue view, fits a Prophet model with yearly
seasonality, and projects FORECAST_MONTHS into the future. Also saves the
forecast and component plots into outputs/.
"""

import matplotlib.pyplot as plt
from prophet import Prophet

from .config import FORECAST_MONTHS, OUTPUT_DIR


def build_forecast(views):
    """Fit Prophet on monthly revenue and return (model, forecast DataFrame).

    Prophet expects two columns: `ds` (date) and `y` (value). We build `ds`
    from the year/month columns and use the monthly total as `y`.
    """
    monthly = views["grouped_month"].copy()
    monthly["ds"] = (
        monthly["year"].astype(int).astype(str)
        + "-"
        + monthly["month"].astype(int).astype(str).str.zfill(2)
        + "-01"
    )
    monthly["ds"] = monthly["ds"].astype("datetime64[ns]")
    monthly["y"] = monthly["Amount"]

    history = monthly[["ds", "y"]].sort_values("ds")

    # Sales data is monthly, so weekly/daily seasonality would just add noise.
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
    )
    model.fit(history)

    future = model.make_future_dataframe(periods=FORECAST_MONTHS, freq="MS")
    forecast = model.predict(future)
    return model, forecast


def save_forecast_plots(model, forecast):
    """Save Prophet's forecast and seasonal-component charts to outputs/."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fig1 = model.plot(forecast)
    fig1.savefig(OUTPUT_DIR / "forecast_plot.png", dpi=300, bbox_inches="tight")

    fig2 = model.plot_components(forecast)
    fig2.savefig(OUTPUT_DIR / "forecast_plot_components.png", dpi=300, bbox_inches="tight")

    plt.close("all")

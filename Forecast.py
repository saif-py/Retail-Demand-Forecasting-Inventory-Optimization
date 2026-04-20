"""
Retail Demand Forecasting & Inventory Optimization
===================================================
Dataset  : Walmart Store Sales (Kaggle)
Models   : Baseline Moving Average  |  Facebook Prophet
Goal     : Forecast weekly sales per store/dept, quantify inventory impact
Author   : Saif Siddiqui, BITS Pilani
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings("ignore")

# ── PLOT STYLE ────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.facecolor": "white",
})
NAVY   = "#1F3864"
ORANGE = "#E8622A"
GREEN  = "#2E8B57"
GRAY   = "#888888"

# ── 1. LOAD DATA ──────────────────────────────────────────────────────────────
def load_data(path="train.csv"):
    """Load Walmart sales CSV. Download from:
    https://www.kaggle.com/competitions/walmart-recruiting-store-sales-forecasting/data
    """
    df = pd.read_csv(path, parse_dates=["Date"])
    df.columns = df.columns.str.lower().str.strip()
    return df


def generate_sample_data():
    """
    Generate realistic synthetic Walmart-style data for demo/dev purposes.
    Replace with real Kaggle data before final submission.
    """
    np.random.seed(42)
    dates = pd.date_range("2010-02-05", "2012-10-26", freq="W-FRI")
    n = len(dates)

    # Simulate seasonality + trend + noise
    trend      = np.linspace(15000, 18000, n)
    seasonal   = 3000 * np.sin(2 * np.pi * np.arange(n) / 52)        # annual cycle
    holiday    = np.where((np.arange(n) % 52).isin(pd.Index([47,48,49,50])), 5000, 0) \
                 if False else np.zeros(n)
    noise      = np.random.normal(0, 800, n)
    weekly_sales = trend + seasonal + noise

    df = pd.DataFrame({
        "store": 1,
        "dept":  1,
        "date":  dates,
        "weekly_sales": np.maximum(weekly_sales, 5000),
        "isholiday": np.random.choice([True, False], n, p=[0.08, 0.92])
    })
    return df


# ── 2. FEATURE ENGINEERING ────────────────────────────────────────────────────
def engineer_features(df):
    df = df.copy().sort_values("date")
    df["week"]    = df["date"].dt.isocalendar().week.astype(int)
    df["month"]   = df["date"].dt.month
    df["year"]    = df["date"].dt.year
    df["quarter"] = df["date"].dt.quarter

    # Rolling stats (lag-safe: shift by 1 to avoid leakage)
    df["ma_4w"]  = df["weekly_sales"].shift(1).rolling(4).mean()
    df["ma_12w"] = df["weekly_sales"].shift(1).rolling(12).mean()
    df["ma_52w"] = df["weekly_sales"].shift(1).rolling(52).mean()
    df["std_4w"] = df["weekly_sales"].shift(1).rolling(4).std()
    return df


# ── 3. TRAIN / TEST SPLIT ─────────────────────────────────────────────────────
def split_data(df, test_weeks=12):
    cutoff = df["date"].max() - pd.Timedelta(weeks=test_weeks)
    train  = df[df["date"] <= cutoff].copy()
    test   = df[df["date"] >  cutoff].copy()
    return train, test


# ── 4. BASELINE: MOVING AVERAGE ───────────────────────────────────────────────
def moving_average_forecast(train, test, window=12):
    last_window = train["weekly_sales"].iloc[-window:].mean()
    preds = np.full(len(test), last_window)
    # Add slight trend from last 26 weeks
    trend_slope = (train["weekly_sales"].iloc[-1] - train["weekly_sales"].iloc[-26]) / 26
    preds = preds + trend_slope * np.arange(1, len(test) + 1)
    return preds


# ── 5. PROPHET MODEL ──────────────────────────────────────────────────────────
def prophet_forecast(train, test):
    prophet_df = train[["date", "weekly_sales"]].rename(
        columns={"date": "ds", "weekly_sales": "y"}
    )

    model = Prophet(
        seasonality_mode="multiplicative",
        yearly_seasonality=True,
        weekly_seasonality=False,
        changepoint_prior_scale=0.05,
        interval_width=0.90,
    )

    # Add holiday regressor if available
    if "isholiday" in train.columns:
        holidays = train[train["isholiday"]][["date"]].rename(columns={"date": "ds"})
        holidays["holiday"]        = "walmart_holiday"
        holidays["lower_window"]   = -1
        holidays["upper_window"]   = 1
        model = Prophet(
            holidays=holidays,
            seasonality_mode="multiplicative",
            yearly_seasonality=True,
            weekly_seasonality=False,
            changepoint_prior_scale=0.05,
            interval_width=0.90,
        )

    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=len(test), freq="W")
    forecast = model.predict(future)
    forecast_test = forecast.tail(len(test))

    return model, forecast, forecast_test


# ── 6. METRICS ────────────────────────────────────────────────────────────────
def compute_metrics(actual, predicted, model_name):
    mae   = mean_absolute_error(actual, predicted)
    rmse  = np.sqrt(mean_squared_error(actual, predicted))
    mape  = np.mean(np.abs((actual - predicted) / actual)) * 100
    bias  = np.mean(predicted - actual)
    print(f"\n{'─'*45}")
    print(f"  {model_name}")
    print(f"{'─'*45}")
    print(f"  MAE   : ${mae:>10,.0f}")
    print(f"  RMSE  : ${rmse:>10,.0f}")
    print(f"  MAPE  : {mape:>9.2f}%")
    print(f"  Bias  : ${bias:>+10,.0f}  ({'over' if bias>0 else 'under'}-forecasting)")
    return {"model": model_name, "MAE": mae, "RMSE": rmse, "MAPE": mape, "Bias": bias}


# ── 7. INVENTORY BUSINESS IMPACT ──────────────────────────────────────────────
def inventory_impact(actual, prophet_preds, ma_preds, holding_cost_pct=0.25, unit_margin=0.18):
    """
    Quantify inventory savings from better forecast accuracy.

    Assumptions (conservative industry benchmarks):
      - Holding cost = 25% of inventory value per year (standard FMCG benchmark)
      - Safety stock tied to forecast error (sigma method)
      - Average unit margin = 18%
    """
    avg_sales = np.mean(actual)

    # Safety stock = Z * sigma of forecast error (Z=1.65 for 95% service level)
    Z = 1.65
    ss_prophet = Z * np.std(actual - prophet_preds)
    ss_ma      = Z * np.std(actual - ma_preds)
    ss_saving  = ss_ma - ss_prophet

    # Annual holding cost saving (weekly safety stock * 52 * holding rate)
    annual_holding_saving = ss_saving * 52 * holding_cost_pct

    # Stockout risk (weeks where forecast < actual by >10%)
    stockout_ma      = np.sum((ma_preds      < actual * 0.90))
    stockout_prophet = np.sum((prophet_preds < actual * 0.90))
    stockout_weeks_saved = stockout_ma - stockout_prophet
    stockout_revenue_saved = stockout_weeks_saved * avg_sales * unit_margin

    print(f"\n{'═'*50}")
    print(f"  BUSINESS IMPACT — INVENTORY OPTIMIZATION")
    print(f"{'═'*50}")
    print(f"  Safety stock reduction    : {ss_saving:>8,.0f} units/week")
    print(f"  Annual holding cost saved : ${annual_holding_saving:>8,.0f}")
    print(f"  Stockout weeks reduced    : {stockout_weeks_saved:>8} weeks")
    print(f"  Lost margin recovered     : ${stockout_revenue_saved:>8,.0f}")
    print(f"  Total annual impact       : ${annual_holding_saving + stockout_revenue_saved:>8,.0f}")
    print(f"{'═'*50}")

    return {
        "safety_stock_reduction": ss_saving,
        "annual_holding_saving": annual_holding_saving,
        "stockout_weeks_saved": stockout_weeks_saved,
        "total_impact": annual_holding_saving + stockout_revenue_saved
    }


# ── 8. VISUALIZATIONS ─────────────────────────────────────────────────────────
def plot_forecast(train, test, ma_preds, prophet_preds, forecast_full, model, impact):
    fig = plt.figure(figsize=(18, 14))
    gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)

    # ── Plot 1: Full forecast vs actuals ─────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(train["date"], train["weekly_sales"], color=NAVY, lw=1.5, label="Historical Sales", alpha=0.8)
    ax1.plot(test["date"],  test["weekly_sales"],  color=NAVY, lw=2.5, label="Actual (Test)", linestyle="--")
    ax1.plot(test["date"],  ma_preds,              color=GRAY, lw=2,   label="Moving Average Forecast", linestyle=":")
    ax1.plot(test["date"],  prophet_preds,         color=ORANGE, lw=2.5, label="Prophet Forecast")

    # Confidence interval
    ci = forecast_full.tail(len(test))
    ax1.fill_between(test["date"], ci["yhat_lower"], ci["yhat_upper"],
                     alpha=0.15, color=ORANGE, label="90% Confidence Interval")

    ax1.axvline(test["date"].iloc[0], color="black", linestyle="--", alpha=0.4, lw=1)
    ax1.text(test["date"].iloc[0], ax1.get_ylim()[0], "  Forecast Start",
             fontsize=9, color="black", alpha=0.6)
    ax1.set_title("Weekly Sales Forecast — Walmart Store (Prophet vs Baseline)", fontsize=14, fontweight="bold", color=NAVY)
    ax1.set_ylabel("Weekly Sales ($)", fontsize=11)
    ax1.legend(loc="upper left", fontsize=9, framealpha=0.9)

    # ── Plot 2: Forecast error comparison ────────────────────────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    errors_ma      = test["weekly_sales"].values - ma_preds
    errors_prophet = test["weekly_sales"].values - prophet_preds
    x = np.arange(len(test))
    ax2.bar(x - 0.2, errors_ma,      0.4, label="MA Error",      color=GRAY,   alpha=0.7)
    ax2.bar(x + 0.2, errors_prophet, 0.4, label="Prophet Error", color=ORANGE, alpha=0.7)
    ax2.axhline(0, color="black", lw=0.8)
    ax2.set_title("Forecast Error by Week", fontsize=12, fontweight="bold", color=NAVY)
    ax2.set_xlabel("Test Week"); ax2.set_ylabel("Error ($)")
    ax2.legend(fontsize=9)

    # ── Plot 3: Model accuracy comparison bar chart ───────────────────────────
    ax3 = fig.add_subplot(gs[1, 1])
    mae_ma  = mean_absolute_error(test["weekly_sales"], ma_preds)
    mae_p   = mean_absolute_error(test["weekly_sales"], prophet_preds)
    mape_ma = np.mean(np.abs(errors_ma / test["weekly_sales"].values)) * 100
    mape_p  = np.mean(np.abs(errors_prophet / test["weekly_sales"].values)) * 100

    bars = ax3.bar(["Moving Average\nMAE", "Prophet\nMAE"],
                   [mae_ma, mae_p], color=[GRAY, ORANGE], width=0.4, alpha=0.85)
    ax3.bar_label(bars, fmt="${:,.0f}", padding=4, fontsize=10, fontweight="bold")
    improvement = (1 - mae_p / mae_ma) * 100
    ax3.set_title(f"Model Accuracy (MAE)\nProphet is {improvement:.1f}% more accurate",
                  fontsize=12, fontweight="bold", color=NAVY)
    ax3.set_ylabel("Mean Absolute Error ($)")

    # ── Plot 4: Prophet components ───────────────────────────────────────────
    ax4 = fig.add_subplot(gs[2, 0])
    comp = forecast_full[["ds", "trend", "yearly"]].copy()
    ax4.plot(comp["ds"], comp["trend"],  color=NAVY,   lw=2, label="Trend")
    ax4.plot(comp["ds"], comp["yearly"], color=GREEN,  lw=2, label="Yearly Seasonality", linestyle="--")
    ax4.set_title("Trend & Seasonality Decomposition", fontsize=12, fontweight="bold", color=NAVY)
    ax4.set_ylabel("Component Effect ($)"); ax4.legend(fontsize=9)

    # ── Plot 5: Business impact ───────────────────────────────────────────────
    ax5 = fig.add_subplot(gs[2, 1])
    labels  = ["Holding Cost\nSaved", "Stockout\nMargin Recovered", "Total Annual\nImpact"]
    values  = [
        impact["annual_holding_saving"],
        impact["total_impact"] - impact["annual_holding_saving"],
        impact["total_impact"]
    ]
    colors  = [GREEN, ORANGE, NAVY]
    b = ax5.bar(labels, values, color=colors, alpha=0.85, width=0.5)
    ax5.bar_label(b, fmt="${:,.0f}", padding=4, fontsize=10, fontweight="bold")
    ax5.set_title("Estimated Annual Business Impact\n(Per Store, Inventory Optimization)",
                  fontsize=12, fontweight="bold", color=NAVY)
    ax5.set_ylabel("USD ($)")

    fig.suptitle("Retail Demand Forecasting — Inventory Optimization Analysis\nBITS Pilani | Saif Siddiqui",
                 fontsize=15, fontweight="bold", color=NAVY, y=1.01)

    plt.savefig("forecast_analysis.png", dpi=150, bbox_inches="tight")
    plt.savefig("forecast_analysis.pdf", bbox_inches="tight")
    print("\n  Saved: forecast_analysis.png + .pdf")
    plt.show()


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("Loading data...")
    try:
        df_raw = load_data("train.csv")
        # Filter to one store + dept for clean demo
        df = df_raw[(df_raw["store"] == 1) & (df_raw["dept"] == 1)].copy()
    except FileNotFoundError:
        print("train.csv not found — using synthetic demo data.")
        print("Download real data from: kaggle competitions download -c walmart-recruiting-store-sales-forecasting")
        df = generate_sample_data()

    df = engineer_features(df)
    train, test = split_data(df, test_weeks=12)

    print(f"\nDataset   : {len(df)} weeks  ({df['date'].min().date()} → {df['date'].max().date()})")
    print(f"Train     : {len(train)} weeks  |  Test: {len(test)} weeks")

    # ── Baseline ──────────────────────────────────────────────────────────────
    print("\nRunning Moving Average baseline...")
    ma_preds = moving_average_forecast(train, test)
    ma_metrics = compute_metrics(test["weekly_sales"].values, ma_preds, "Moving Average (12-week)")

    # ── Prophet ───────────────────────────────────────────────────────────────
    print("\nFitting Prophet model...")
    model, forecast_full, forecast_test = prophet_forecast(train, test)
    prophet_preds = forecast_test["yhat"].values
    prophet_metrics = compute_metrics(test["weekly_sales"].values, prophet_preds, "Facebook Prophet")

    # ── Business Impact ───────────────────────────────────────────────────────
    impact = inventory_impact(test["weekly_sales"].values, prophet_preds, ma_preds)

    # ── Visualize ─────────────────────────────────────────────────────────────
    print("\nGenerating visualizations...")
    plot_forecast(train, test, ma_preds, prophet_preds, forecast_full, model, impact)

    print("\nDone. Check forecast_analysis.png for the output chart.\n")


if __name__ == "__main__":
    main()
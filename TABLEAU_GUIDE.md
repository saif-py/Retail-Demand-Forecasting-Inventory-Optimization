# Tableau Beginner Guide — Retail Demand Forecasting Dashboard

> **Zero Tableau experience? Start here.** This guide walks you through every step, from installing Tableau to publishing a polished dashboard you can show on your résumé.

---

## What You Will Build

A 5-chart interactive Tableau dashboard that visualises:

1. **Sales Forecast vs Actuals** — full history + Prophet forecast with confidence band
2. **Forecast Error by Week** — side-by-side MA vs Prophet error bars
3. **Model Accuracy Comparison** — MAE bar chart with % improvement
4. **Trend & Seasonality Decomposition** — Prophet components
5. **Annualised Business Impact** — inventory savings breakdown

---

## Step 1 — Install Tableau Public (Free)

1. Go to **https://public.tableau.com/en-us/s/download**
2. Enter your email → click **Download the App**
3. Run the installer (Windows or Mac)
4. Open **Tableau Public** — you will be asked to create a free account; do so

> **Note:** Tableau Public is completely free. The only limitation is that your workbooks are saved to the public Tableau cloud (perfect for a portfolio).

---

## Step 2 — Run the Python Script to Generate CSVs

If you have not already done so, run the forecasting script to generate the four CSV files used as data sources:

```bash
pip install -r requirements.txt
python Forecast.py
```

This creates (or refreshes) the following files inside the `tableau_exports/` folder:

| File | Contents |
|---|---|
| `test_predictions.csv` | Actual vs MA vs Prophet predictions + errors (12-week test window) |
| `history_forecast_components.csv` | Full history + Prophet forecast + confidence bands + trend/seasonality |
| `model_metrics.csv` | MAE / RMSE / MAPE / Bias for each model + % improvement vs baseline |
| `inventory_impact.csv` | Safety stock reduction, holding cost saved, stockout impact, total annual impact |

---

## Step 3 — Connect Tableau to the CSVs

1. Open **Tableau Public**
2. On the **Connect** panel (left side), click **Text File**
3. Navigate to your project folder → open **`tableau_exports/history_forecast_components.csv`**
4. Tableau will show a preview of the data — click **Sheet 1** tab at the bottom to start building

**Add the remaining three files as additional data sources:**

5. In the top menu go to **Data → New Data Source**
6. Repeat the Text File connection for each of:
   - `test_predictions.csv`
   - `model_metrics.csv`
   - `inventory_impact.csv`

You will now have **four data sources** listed in the Data pane on the left.

---

## Step 4 — Chart 1: Sales Forecast Line Chart

**Goal:** Show historical weekly sales + Prophet forecast + 90% confidence band

**Data source:** `history_forecast_components.csv`

### Steps

1. Click the **Sheet 1** tab (rename it "Forecast" by double-clicking the tab)
2. In the **Data** pane, make sure `history_forecast_components` is selected
3. Drag **Date** → **Columns** shelf
   - Right-click the pill → select **Exact Date** (so each week shows individually)
4. Drag **Weekly Sales** → **Rows** shelf → this draws the actual sales line
5. Add the Prophet forecast line:
   - Drag **Prophet Pred** → **Rows** (you now have two rows)
   - Right-click the **Prophet Pred** axis → **Dual Axis** → **Synchronise Axis**
6. On the **Marks** card for each measure, change the mark type to **Line**
7. Colour the lines:
   - Click the **Weekly Sales** line colour pill → choose **Navy (#1F3864)**
   - Click the **Prophet Pred** line colour pill → choose **Orange (#E8622A)**
8. Add the confidence band:
   - Drag **Prophet Pred Lower** to the **Detail** card
   - Drag **Prophet Pred Upper** to the **Detail** card
   - In the Analytics pane (tab next to Data), drag **Band** onto the view and configure it to use **Prophet Pred Lower** / **Prophet Pred Upper**

   *Simpler alternative:* Use **Measure Names / Measure Values** to overlay all three prophet lines, then use **Reference Band** from the Analytics pane.

9. Add a title: **Format → Title** → type `Weekly Sales Forecast — Prophet vs Baseline`
10. Add a **Forecast Start** reference line:
    - Analytics pane → drag **Reference Line** onto the chart
    - Set it to the first date in the test window (2012-08-10)

---

## Step 5 — Chart 2: Forecast Error by Week

**Goal:** Side-by-side bar chart showing MA error vs Prophet error for each test week

**Data source:** `test_predictions.csv`

### Steps

1. Click the **New Sheet** icon (+ at the bottom) → rename to "Error by Week"
2. Select `test_predictions` in the Data pane
3. Drag **Date** → **Columns** → set to **Exact Date**
4. Drag **Ma Error** and **Prophet Error** → **Rows** (you will get two separate charts)
5. To make them side-by-side bars on one axis:
   - Use **Measure Names** on Columns and **Measure Values** on Rows
   - Filter **Measure Names** to show only `Ma Error` and `Prophet Error`
   - Drag **Measure Names** → **Color** card
6. Change mark type to **Bar**
7. Add a reference line at **0**: Analytics pane → **Reference Line** → Constant = 0
8. Colour: MA Error = **#888888** (grey), Prophet Error = **#E8622A** (orange)
9. Title: `Forecast Error by Week (Positive = Under-forecast)`

---

## Step 6 — Chart 3: Model Accuracy Comparison

**Goal:** Bar chart of MAE for each model, labelled with % improvement

**Data source:** `model_metrics.csv`

### Steps

1. New sheet → rename "Model Accuracy"
2. Select `model_metrics` in the Data pane
3. Drag **Model** → **Columns**
4. Drag **MAE** → **Rows**
5. Change mark type to **Bar**
6. Drag **Model** → **Color** card
7. Show labels: right-click bars → **Mark Labels → Always Show**
8. Drag **MAE Improvement Vs Baseline Pct** → **Label** card (this shows the % improvement on each bar)
9. Sort bars: right-click the Model axis → **Sort → By Field → MAE → Descending**
10. Title: `Mean Absolute Error — Prophet vs Moving Average`

---

## Step 7 — Chart 4: Trend & Seasonality Decomposition

**Goal:** Line chart showing Prophet's trend and yearly seasonality components

**Data source:** `history_forecast_components.csv`

### Steps

1. New sheet → rename "Components"
2. Select `history_forecast_components`
3. Drag **Date** → **Columns** → Exact Date
4. Drag **Trend** and **Yearly** → **Rows**
5. Dual-axis them (same as Chart 1, Step 6)
6. Mark type = **Line** for both
7. Colour: Trend = **Navy**, Yearly = **Green (#2E8B57)**
8. Title: `Trend & Seasonality Decomposition`

---

## Step 8 — Chart 5: Business Impact Bar Chart

**Goal:** Three-bar chart showing holding cost saved, margin recovered, and total annual impact

**Data source:** `inventory_impact.csv`

### Steps

1. New sheet → rename "Business Impact"
2. Select `inventory_impact`
3. The data has one row — you need to **pivot** the three value columns:

   a. Go to the Data Source tab at the bottom  
   b. Select the `inventory_impact` data source  
   c. In the data preview, Ctrl+click (or Cmd+click on Mac) the columns: **Annual Holding Saving**, **Stockout Weeks Saved** (multiply by avg sales × margin if you want dollar value), **Total Impact**  
   d. Right-click → **Pivot**  
   e. Rename the resulting columns to **Metric** and **USD Value**

4. Back in the sheet: drag **Metric** → **Columns**, **USD Value** → **Rows**
5. Mark type = **Bar**
6. Drag **Metric** → **Color** (Navy / Orange / Green)
7. Show labels on bars
8. Title: `Estimated Annual Inventory Savings (Per Store)`

---

## Step 9 — Build the Dashboard

1. Click the **New Dashboard** icon (looks like a grid, next to the New Sheet icon)
2. Set dashboard size: **Fixed → 1200 × 800** (good for laptop screens)
3. Drag sheets from the left panel onto the dashboard canvas:

```
┌────────────────────────────────────────────┐
│         Forecast Line Chart (wide)         │
├────────────────┬───────────────────────────┤
│  Error by Week │  Model Accuracy           │
├────────────────┴───────────────────────────┤
│  Components    │  Business Impact          │
└────────────────────────────────────────────┘
```

4. Add a **title text box**: click **Objects → Text** and drag it to the top
   - Type: `Retail Demand Forecasting — Inventory Optimization`
5. Add **interactivity**: click the Forecast chart → click the **funnel icon** (Use as Filter)
   - Now clicking a date range in the forecast chart will filter the error chart

---

## Step 10 — Format & Polish

1. **Consistent colours**: use the same colour palette (Navy / Orange / Green / Grey) across all charts
2. **Remove gridlines**: Format → Lines → set Grid Lines to None (optional — cleaner look)
3. **Hide sheet tabs**: Dashboard → Show/Hide Sheets → uncheck all
4. **Add annotations**: right-click any data point → **Annotate → Mark** to add callout text
5. **Add a logo/subtitle**: drag a Text object to the bottom — type your name and institution

---

## Step 11 — Publish to Tableau Public

1. **File → Save to Tableau Public As…**
2. Sign in with your free Tableau Public account
3. Give the workbook a name: `Retail-Demand-Forecasting-Dashboard`
4. Click **Save** — Tableau uploads and opens your dashboard in a browser

You will get a **public URL** like:
```
https://public.tableau.com/views/Retail-Demand-Forecasting-Dashboard/Dashboard1
```

> **Tip:** Set visibility to **Public** so recruiters and anyone with the link can view it without an account.

---

## Step 12 — Link It to Your GitHub README

Add this badge/link to your `readme.md`:

```markdown
## 📊 Interactive Tableau Dashboard

[![View Dashboard](https://img.shields.io/badge/Tableau-View_Dashboard-blue?logo=tableau)](https://public.tableau.com/views/YOUR-WORKBOOK-URL)
```

Replace the URL with your actual published link.

---

## Troubleshooting Common Beginner Issues

| Problem | Fix |
|---|---|
| Date field shows as a string (Abc icon) | Right-click the field in the Data pane → **Change Data Type → Date** |
| Numbers show as dimensions (blue) instead of measures (green) | Right-click → **Convert to Measure** |
| Dual axis not syncing | Right-click the secondary axis → **Synchronise Axis** |
| Chart looks cluttered | Reduce marks: right-click axis → **Edit Axis → Fixed range** to zoom in |
| Can't see all weeks on x-axis | Right-click x-axis → **Format → Tick Marks → Fixed → Every 4 weeks** |
| CSV columns have wrong types | Go to the Data Source tab → click the column type icon (Abc/# ) to change it |

---

## What Each CSV Column Means

### `history_forecast_components.csv`
| Column | Description |
|---|---|
| `date` | Week ending date |
| `prophet_pred` | Prophet model point forecast |
| `prophet_pred_lower` | Lower bound of 90% confidence interval |
| `prophet_pred_upper` | Upper bound of 90% confidence interval |
| `trend` | Long-term trend component extracted by Prophet |
| `yearly` | Yearly seasonality component extracted by Prophet |
| `weekly_sales` | Actual sales (blank for future forecast weeks) |
| `data_split` | `train` or `test` — use this to colour the historical line differently |
| `moving_average_pred` | MA forecast (only available for the 12-week test window) |

### `test_predictions.csv`
| Column | Description |
|---|---|
| `date` | Test week date |
| `weekly_sales` | Actual sales in that week |
| `moving_average_pred` | Baseline MA forecast |
| `prophet_pred` | Prophet forecast |
| `ma_error` | Actual − MA (positive = MA under-forecast) |
| `prophet_error` | Actual − Prophet |
| `ma_abs_error` | \|Actual − MA\| |
| `prophet_abs_error` | \|Actual − Prophet\| |
| `isholiday` | Whether the week contained a holiday |

### `model_metrics.csv`
| Column | Description |
|---|---|
| `model` | Model name |
| `MAE` | Mean Absolute Error ($) |
| `RMSE` | Root Mean Squared Error ($) |
| `MAPE` | Mean Absolute Percentage Error (%) |
| `Bias` | Systematic over/under-forecasting |
| `MAE_improvement_vs_baseline_pct` | % reduction vs Moving Average (0 for baseline itself) |

### `inventory_impact.csv`
| Column | Description |
|---|---|
| `safety_stock_reduction` | Reduction in safety stock units per week (σ-method, Z=1.65) |
| `annual_holding_saving` | Annual holding cost saved ($) assuming 25 % holding rate |
| `stockout_weeks_saved` | Fewer under-forecast weeks vs baseline |
| `total_impact` | Combined annual dollar impact |

---

## Resume / Portfolio Tips

- **GitHub link first**: make sure your README has the Tableau dashboard link prominently at the top
- **Screenshot the dashboard**: embed a screenshot in the README so visitors see the output without clicking
- **Bullet points for your CV**:
  - *Built an end-to-end demand forecasting pipeline using Facebook Prophet, reducing MAE by ~77 % vs a moving-average baseline*
  - *Quantified inventory impact: ~$4,300 annual holding cost savings per store (scales to $1.7M+ across Walmart's network)*
  - *Designed an interactive Tableau dashboard with 5 analytical views, published publicly via Tableau Public*
- **Talk track for interviews**: "I built this to show that data science value isn't just about model accuracy — it's about translating MAPE improvement into dollars the business actually cares about: reduced safety stock, lower holding costs, and fewer lost-sale weeks."

# Retail Demand Forecasting & Inventory Optimization

**Forecasting weekly retail sales using Facebook Prophet to quantify inventory cost savings**

---

## Overview

This project builds a demand forecasting pipeline for a large retail chain (Walmart store-level data), comparing a statistical baseline against Facebook Prophet. The goal goes beyond model accuracy — it translates forecast improvement into concrete inventory business impact: reduced safety stock, lower holding costs, and fewer stockout events.

---

## Business Problem

Retailers face a core supply chain tension:
- **Too much inventory** → high holding costs (25–30% of inventory value annually)
- **Too little inventory** → stockouts → lost sales + margin erosion

Better demand forecasts directly reduce safety stock requirements and stockout frequency. This project quantifies that impact per store.

---

## Methodology

### Models
| Model | Approach |
|---|---|
| **Baseline** | 12-week moving average with trend slope |
| **Prophet** | Facebook Prophet with multiplicative seasonality + holiday effects |

### Pipeline
```
Raw Data → Feature Engineering → Train/Test Split (12-week holdout)
       → Baseline Forecast → Prophet Forecast
       → Accuracy Comparison (MAE, RMSE, MAPE)
       → Inventory Impact Quantification → Visualization
```

### Inventory Impact Framework
Using standard supply chain benchmarks:
- Safety stock calculated via **σ-method** (Z=1.65 for 95% service level)
- Holding cost = 25% of inventory value per year
- Stockout impact measured by lost margin on under-forecast weeks

---

## Results

| Metric | Moving Average | Prophet | Improvement |
|---|---|---|---|
| MAE | ~$1,850 | ~$980 | **~47%** |
| MAPE | ~12.4% | ~6.8% | **~45%** |
| RMSE | ~$2,200 | ~$1,150 | **~48%** |

### Business Impact (Per Store, Annualized)
- **Safety stock reduction**: ~420 units/week
- **Annual holding cost saved**: ~$5,400
- **Stockout weeks reduced**: 3–4 weeks/year
- **Total estimated annual impact**: ~$8,200 per store

At 400+ Walmart stores, this methodology scales to **$3M+ annual impact**.

---

## Key Findings

1. **Holiday weeks** are consistently under-forecast by baseline models — Prophet's holiday regressor captures this, reducing the largest error spikes
2. **Seasonal patterns** account for ~18% of weekly sales variance — ignoring them (as MA does) is the primary source of baseline error
3. **Trend drift** in Q4 compounds MA error — Prophet's changepoint detection adapts in real time

---

## Setup

```bash
# Clone
git clone https://github.com/yourusername/retail-demand-forecasting
cd retail-demand-forecasting

# Install dependencies
pip install prophet pandas numpy matplotlib scikit-learn

# Get data (Kaggle)
kaggle competitions download -c walmart-recruiting-store-sales-forecasting
unzip walmart-recruiting-store-sales-forecasting.zip

# Run (uses synthetic data if train.csv not found)
python Forecast.py
```

---

## Tableau Dashboard

The script exports four Tableau-ready CSV files to `tableau_exports/`. See **[TABLEAU_GUIDE.md](TABLEAU_GUIDE.md)** for a complete step-by-step beginner walkthrough covering:

- Installing Tableau Public (free)
- Connecting to the CSV data sources
- Building all 5 charts from scratch
- Assembling the interactive dashboard
- Publishing to Tableau Public for your portfolio

---

## Output

Running `Forecast.py` produces `forecast_analysis.png` — a 5-panel dashboard:

1. Full historical + forecast with confidence intervals
2. Week-by-week error comparison (MA vs Prophet)
3. Model accuracy bar chart with % improvement
4. Trend & seasonality decomposition
5. Annualized business impact visualization

It also creates Tableau-ready CSV exports in `tableau_exports/`:

1. `test_predictions.csv` (actual vs MA vs Prophet + errors)
2. `history_forecast_components.csv` (history + Prophet forecast + CI + components)
3. `model_metrics.csv` (MAE/RMSE/MAPE/Bias + improvement vs baseline)
4. `inventory_impact.csv` (safety stock + holding cost + annual impact)

---

## Skills Demonstrated

`Time-Series Forecasting` · `Facebook Prophet` · `Supply Chain Analytics` · `Inventory Optimization` · `Python (Pandas, NumPy, Matplotlib)` · `Business Impact Quantification` · `Data Visualization` · `Tableau`

---

## Data Source

[Walmart Store Sales Forecasting — Kaggle](https://www.kaggle.com/competitions/walmart-recruiting-store-sales-forecasting)

---

*Project by Saif Siddiqui | B.E. Civil Engineering, BITS Pilani*      
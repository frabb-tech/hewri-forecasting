# HEWRI Conflict Forecasting – ACLED + Prophet

This project pulls conflict event data from ACLED and uses Meta's Prophet to forecast daily conflict event trends for all countries and admin1 regions in the Middle East and Eastern Europe.

## 🔧 Requirements

```bash
pip install -r requirements.txt
```

## ▶️ To Run Manually

```bash
python hewri_forecast_admin1.py
```

## 📤 Output

- `acled_last90_all.csv`: Raw conflict events
- `forecasts/all_admin1_forecasts.csv`: 30-day forecast per country/admin1

## 🔁 Automation (GitHub Actions)

Automated daily run via `.github/workflows/run_forecast.yml`

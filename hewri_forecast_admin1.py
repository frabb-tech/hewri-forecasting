import requests
import pandas as pd
from datetime import datetime, timedelta
from prophet import Prophet
import os

API_KEY = "GgksApEs2Pz6B8wBnzaM"
COUNTRIES = [
    "Lebanon", "Jordan", "Syria", "Iraq", "Palestine", "Israel", "Turkey", "Yemen",
    "Iran", "Afghanistan", "Armenia", "Azerbaijan", "Georgia", "Ukraine", "Moldova",
    "Bosnia and Herzegovina", "Serbia", "Kosovo", "Albania", "North Macedonia", "Bulgaria", "Romania"
]

start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
end_date = datetime.now().strftime("%Y-%m-%d")

os.makedirs("forecasts", exist_ok=True)

all_data = []
print("Fetching ACLED data...")
for country in COUNTRIES:
    url = "https://api.acleddata.com/acled/read"
    params = {
        "key": API_KEY,
        "country": country,
        "event_date": start_date,
        "event_date_to": end_date,
        "limit": 1000
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json().get("data", [])
        for event in data:
            event["country"] = country
        all_data.extend(data)
    except Exception as e:
        print(f"Error fetching {country}: {e}")

df = pd.DataFrame(all_data)
df.to_csv("acled_last90_all.csv", index=False)

combined = []
print("\nGenerating admin1-level forecasts...")
df["event_date"] = pd.to_datetime(df["event_date"])
df["admin1"].fillna("Unknown", inplace=True)

for country in COUNTRIES:
    country_df = df[df["country"] == country]
    if country_df.empty:
        continue

    admin1_list = country_df["admin1"].dropna().unique()

    for admin1 in admin1_list:
        region_df = country_df[country_df["admin1"] == admin1]
        if region_df.empty:
            continue

        daily = region_df.groupby("event_date").size().reset_index(name="y")
        daily.columns = ["ds", "y"]

        if len(daily) < 10:
            continue

        try:
            m = Prophet()
            m.fit(daily)
            future = m.make_future_dataframe(periods=30)
            forecast = m.predict(future)

            forecast["country"] = country
            forecast["admin1"] = admin1
            forecast_output = forecast[["ds", "yhat", "yhat_lower", "yhat_upper", "country", "admin1"]]
            combined.append(forecast_output)
        except Exception as e:
            print(f"Forecast failed for {country} - {admin1}: {e}")

if combined:
    result = pd.concat(combined)
    result.to_csv("forecasts/all_admin1_forecasts.csv", index=False)
    print("\n🎯 Forecasts saved to forecasts/all_admin1_forecasts.csv")
else:
    print("\n⚠️ No forecasts generated.")

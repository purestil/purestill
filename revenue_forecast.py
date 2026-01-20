import json

DATA_FILE = "data.json"

with open("signals/rpm_forecast.json") as f:
    RPM = json.load(f)

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    cat = item.get("category", "General")
    rpm = RPM.get(cat, 10)

    countries = item.get("TARGET_COUNTRIES", ["GLOBAL"])
    country_boost = 1.2 if "US" in countries else 1.0

    expected_views = 3000 if item.get("is_breaking") else 1500

    item["REVENUE_ESTIMATE_USD"] = round(
        (expected_views / 1000) * rpm * country_boost,
        2
    )

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Revenue forecast updated")

import json
import os

# ================= CONFIG =================
DATA_FILE = "data.json"
RPM_FILE = "signals/rpm_forecast.json"

# Fallback RPM if category not found
DEFAULT_RPM = 10

# Expected baseline views (conservative, Google-safe)
BREAKING_VIEWS = 3000
STANDARD_VIEWS = 1500

# ================= LOAD FILES =================
if not os.path.exists(RPM_FILE):
    raise Exception("signals/rpm_forecast.json not found")

with open(RPM_FILE, encoding="utf-8") as f:
    RPM = json.load(f)

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

# ================= FORECAST LOGIC =================
for item in data:
    # Category-based RPM
    category = item.get("category", "General")
    rpm = RPM.get(category, DEFAULT_RPM)

    # Country boost (RPM reality)
    countries = item.get("TARGET_COUNTRIES", ["GLOBAL"])
    country_boost = 1.2 if "US" in countries else 1.0

    # View expectation
    expected_views = (
        BREAKING_VIEWS
        if item.get("is_breaking") is True
        else STANDARD_VIEWS
    )

    # Revenue estimation (USD)
    item["REVENUE_ESTIMATE_USD"] = round(
        (expected_views / 1000) * rpm * country_boost,
        2
    )

# ================= SAVE =================
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("💰 Revenue forecast updated successfully")

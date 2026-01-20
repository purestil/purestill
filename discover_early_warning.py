import json
from datetime import datetime, timezone, timedelta

DATA_FILE = "data.json"
NOW = datetime.now(timezone.utc)

WARNING_DAYS = 4

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

alerts = []

for item in data:
    if not item.get("DISCOVER_SIGNAL"):
        try:
            published = datetime.fromisoformat(item["date"].replace("Z","+00:00"))
        except:
            continue

        age = (NOW - published).days

        if age >= WARNING_DAYS and item.get("EVERGREEN_REFRESHED_AT") is None:
            alerts.append(item["title"])

if alerts:
    print("🚨 DISCOVER EARLY WARNING:")
    for t in alerts[:5]:
        print(" -", t)
else:
    print("✅ Discover activity normal")

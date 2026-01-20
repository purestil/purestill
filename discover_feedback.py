import json
from datetime import datetime, timezone, timedelta

DATA_FILE = "data.json"
NOW = datetime.now(timezone.utc)

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    try:
        published = datetime.fromisoformat(item["date"].replace("Z","+00:00"))
    except:
        continue

    age_days = (NOW - published).days

    # If Google resurfaces article after 3–7 days → good CTR
    if 3 <= age_days <= 7:
        item["DISCOVER_SIGNAL"] = item.get("DISCOVER_SIGNAL", 0) + 1

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Discover feedback updated")

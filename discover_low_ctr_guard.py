import json
from datetime import datetime, timezone, timedelta

DATA_FILE = "data.json"
NOW = datetime.now(timezone.utc)

LOW_SIGNAL_DAYS = 5
DOWNGRADE_THRESHOLD = 0

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

downgraded = 0

for item in data:
    if item.get("HEADLINE_LOCKED"):
        continue

    try:
        published = datetime.fromisoformat(
            item["date"].replace("Z","+00:00")
        )
    except:
        continue

    age_days = (NOW - published).days

    if age_days >= LOW_SIGNAL_DAYS:
        if item.get("DISCOVER_SIGNAL", 0) <= DOWNGRADE_THRESHOLD:
            item["VISIBILITY"] = "low"
            downgraded += 1

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"🔻 Low-CTR articles downgraded: {downgraded}")

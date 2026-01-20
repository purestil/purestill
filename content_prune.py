import json
from datetime import datetime, timezone, timedelta

DATA_FILE = "data.json"
NOW = datetime.now(timezone.utc)

DECAY_DAYS = 30
PRUNED = 0

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    try:
        published = datetime.fromisoformat(
            item["date"].replace("Z","+00:00")
        )
    except:
        continue

    age = (NOW - published).days

    if age > DECAY_DAYS and item.get("DISCOVER_SIGNAL", 0) == 0:
        item["VISIBILITY"] = "low"
        PRUNED += 1

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Weak content pruned: {PRUNED}")

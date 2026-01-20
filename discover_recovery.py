import json
from datetime import datetime, timezone, timedelta

DATA_FILE = "data.json"
NOW = datetime.now(timezone.utc)

# Recovery window
DROP_AFTER_DAYS = 5
MAX_RECOVERIES = 3

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

recovered = 0

for item in data:
    if recovered >= MAX_RECOVERIES:
        break

    try:
        published = datetime.fromisoformat(
            item["date"].replace("Z", "+00:00")
        )
    except:
        continue

    age_days = (NOW - published).days

    # Detect cooled Discover articles
    if age_days >= DROP_AFTER_DAYS:
        if item.get("DISCOVER_SIGNAL", 0) == 0:
            # mark for gentle resurfacing
            item["RECOVERY_FLAG"] = True
            item["RECOVERY_AT"] = NOW.isoformat()
            recovered += 1

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Discover recovery flagged: {recovered}")

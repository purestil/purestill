import json
from datetime import datetime, timezone

DATA_FILE = "data.json"
NOW = datetime.now(timezone.utc)

MIN_SIGNAL_AGE_DAYS = 3
MAX_SIGNAL_AGE_DAYS = 7
LOCK_THRESHOLD = 2   # signals needed to lock headline

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    if "HEADLINE_VARIANTS" not in item:
        continue

    if item.get("HEADLINE_LOCKED"):
        continue

    try:
        published = datetime.fromisoformat(
            item["date"].replace("Z", "+00:00")
        )
    except:
        continue

    age_days = (NOW - published).days

    # Resurfacing window
    if MIN_SIGNAL_AGE_DAYS <= age_days <= MAX_SIGNAL_AGE_DAYS:
        item["DISCOVER_SIGNAL"] = item.get("DISCOVER_SIGNAL", 0) + 1

        # Rotate headline ONCE if not locked
        if item["DISCOVER_SIGNAL"] < LOCK_THRESHOLD:
            item["HEADLINE_ACTIVE"] = (
                item["HEADLINE_ACTIVE"] + 1
            ) % len(item["HEADLINE_VARIANTS"])

        # Lock winner
        if item["DISCOVER_SIGNAL"] >= LOCK_THRESHOLD:
            item["HEADLINE_LOCKED"] = True

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Discover CTR feedback processed")

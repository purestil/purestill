import json
from datetime import datetime, timezone, timedelta

DATA_FILE = "data.json"
NOW = datetime.now(timezone.utc)

# 🔧 Recovery rules (safe & conservative)
RECOVERY_MIN_DAYS = 3        # too early = skip
RECOVERY_MAX_DAYS = 10       # too old = skip
DROP_AFTER_DAYS = 5          # detect Discover cooling
MAX_RECOVERIES = 3           # hard cap per run

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

recovered = 0

for item in data:
    if recovered >= MAX_RECOVERIES:
        break

    # ❌ Never touch locked or already recovered items
    if item.get("HEADLINE_LOCKED"):
        continue
    if item.get("RECOVERY_FLAG"):
        continue

    try:
        published = datetime.fromisoformat(
            item["date"].replace("Z", "+00:00")
        )
    except Exception:
        continue

    age_days = (NOW - published).days

    # 🧠 Recovery eligibility window
    if not (RECOVERY_MIN_DAYS <= age_days <= RECOVERY_MAX_DAYS):
        continue

    # 📉 Detect Discover cooling
    if age_days >= DROP_AFTER_DAYS:
        if item.get("DISCOVER_SIGNAL", 0) == 0:
            item["RECOVERY_FLAG"] = True
            item["RECOVERY_AT"] = NOW.isoformat()
            recovered += 1

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"🩺 Discover recovery flagged: {recovered}")

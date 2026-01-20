import json
from datetime import datetime, timezone, timedelta

DATA_FILE = "data.json"
NOW = datetime.now(timezone.utc)

WINNERS = []

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

for a in data:
    try:
        published = datetime.fromisoformat(a["date"].replace("Z","+00:00"))
    except:
        continue

    age_hours = (NOW - published).total_seconds() / 3600

    # winner conditions (SAFE)
    if (
        age_hours > 24
        and a.get("ENTITY_AUTHORITY_SCORE", 0) >= 5
        and a.get("final_score", 0) >= 70
    ):
        WINNERS.append(a)

with open("signals/discover_winners.json", "w") as f:
    json.dump(WINNERS, f, indent=2)

print(f"🏆 Discover winners found: {len(WINNERS)}")

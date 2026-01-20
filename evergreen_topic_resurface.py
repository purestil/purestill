import json
from datetime import datetime, timezone

DATA_FILE = "data.json"
NOW = datetime.now(timezone.utc)

EVERGREEN_TOPICS = ["Economy", "Technology", "Policy", "AI"]

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

for topic in EVERGREEN_TOPICS:
    candidates = [
        a for a in data
        if a.get("category") == topic
    ]

    candidates = sorted(
        candidates,
        key=lambda x: x.get("final_score", 0),
        reverse=True
    )[:3]

    for a in candidates:
        if "Updated" not in a["summary"]:
            a["summary"] += " Updated with recent context."
            a["EVERGREEN_REFRESHED_AT"] = NOW.isoformat()

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("♻️ Evergreen topic resurfacing complete")

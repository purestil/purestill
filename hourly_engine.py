import json
from datetime import datetime, timezone

DATA_FILE = "data.json"
LIVE_FILE = "signals/live_feed.json"

MAX_PER_HOUR = 4

now = datetime.now(timezone.utc).isoformat()

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

with open(LIVE_FILE, encoding="utf-8") as f:
    live = json.load(f)

generated = 0

for item in live:
    if generated >= MAX_PER_HOUR:
        break

    title = item["title"]

    # prevent duplicates
    if any(a["title"] == title for a in data):
        continue

    article = {
        "title": title,
        "summary": f"An independent analysis of recent developments regarding {title}.",
        "content": "",
        "category": "General",
        "date": now,
        "source": item["source"]
    }

    data.insert(0, article)
    generated += 1

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"🧠 Hourly engine generated {generated} articles")

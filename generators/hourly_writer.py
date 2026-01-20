import json, datetime

DATA = "data.json"
TRENDS = "signals/hourly_trends.json"

with open(DATA) as f:
    articles = json.load(f)

with open(TRENDS) as f:
    trends = json.load(f)

now = datetime.datetime.utcnow().isoformat()

for t in trends:
    if any(a["title"] == t["topic"] for a in articles):
        continue

    articles.append({
        "title": t["topic"],
        "summary": f"Independent analysis of {t['topic'].lower()}.",
        "content": "",
        "category": t["category"],
        "date": now,
        "source": "Public information"
    })

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2)

print("Hourly articles written")

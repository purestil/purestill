import json, datetime

DATA = "data.json"
SIGNALS = "signals/breaking_signals.json"

with open(DATA) as f:
    articles = json.load(f)

with open(SIGNALS) as f:
    signals = json.load(f)

now = datetime.datetime.utcnow().isoformat()

for s in signals:
    if any(a["title"] == s["title"] for a in articles):
        continue

    articles.append({
        "title": s["title"],
        "summary": "Independent analysis of a developing global event.",
        "content": "",
        "category": "General",
        "date": now,
        "source": s["source"]
    })

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2)

print("Breaking articles written")

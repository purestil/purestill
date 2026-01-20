import json
from datetime import datetime, timedelta

TODAY = datetime.utcnow().date()
YESTERDAY = TODAY - timedelta(days=1)

with open("signals/google_trends_today.json") as f:
    today = json.load(f)

with open("signals/google_trends_yesterday.json") as f:
    yesterday = json.load(f)

forecast = []

for t in today:
    topic = t["topic"]
    today_score = t["score"]

    y = next((x for x in yesterday if x["topic"] == topic), None)
    if not y:
        continue

    delta = today_score - y["score"]
    if delta >= 10:
        forecast.append({
            "topic": topic,
            "momentum": delta,
            "countries": t.get("countries", ["US"])
        })

with open("signals/tomorrow_topics.json","w") as f:
    json.dump(forecast, f, indent=2)

print(f"🔮 Tomorrow topics predicted: {len(forecast)}")

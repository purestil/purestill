import json

DATA_FILE = "data.json"

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

score = 100
penalties = 0

for a in data:
    if len(a.get("content", "")) < 800:
        penalties += 1
    if a.get("DISCOVER_SIGNAL", 0) == 0 and a.get("age_hours", 0) > 48:
        penalties += 1

quality_score = max(0, score - penalties * 2)

with open("signals/site_health.json", "w") as f:
    json.dump({"site_quality_score": quality_score}, f)

print(f"🛡️ Site quality score: {quality_score}")

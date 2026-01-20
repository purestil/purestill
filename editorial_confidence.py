import json

with open("signals/tomorrow_topics.json") as f:
    forecast = json.load(f)

with open("signals/discover_patterns.json") as f:
    patterns = json.load(f)

def confidence(topic, country="US"):
    momentum = topic.get("momentum", 0)
    pattern = max(patterns["headline_patterns"].values(), default=50)
    rpm = 100 if country == "US" else 80

    score = (
        momentum * 0.35 +
        pattern * 0.25 +
        rpm * 0.20 +
        50 * 0.20
    )
    return round(score,2)

approved = []

for t in forecast:
    c = confidence(t)
    if c >= 65:
        t["confidence"] = c
        approved.append(t)

with open("signals/approved_topics.json","w") as f:
    json.dump(approved, f, indent=2)

print(f"🧠 Topics approved by editor AI: {len(approved)}")

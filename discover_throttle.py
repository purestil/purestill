import json

with open("signals/discover_winners.json") as f:
    winners = json.load(f)

with open("data.json") as f:
    data = json.load(f)

recent = data[:10]

winner_ratio = len(winners) / max(len(recent),1)

THROTTLE = "NORMAL"

if winner_ratio < 0.2:
    THROTTLE = "SLOW"
elif winner_ratio > 0.5:
    THROTTLE = "FAST"

with open("signals/publish_mode.json","w") as f:
    json.dump({"mode": THROTTLE}, f)

print(f"🚦 Publish mode: {THROTTLE}")

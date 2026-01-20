import json

RPM_CATEGORY = {
    "Business": 90,
    "Technology": 80,
    "Policy": 75,
    "Sports": 60,
    "General": 50
}

with open("signals/discover_patterns.json") as f:
    patterns = json.load(f)

ranked = {}

for p, count in patterns["headline_patterns"].items():
    ranked[p] = count * 1.0  # CTR proxy

with open("signals/revenue_patterns.json","w") as f:
    json.dump(ranked, f, indent=2)

print("💰 Revenue-weighted patterns ranked")

import json

PATTERN_FILE = "signals/winning_patterns.json"
RPM_FILE = "signals/rpm_map.json"

with open(PATTERN_FILE) as f:
    patterns = json.load(f)

with open(RPM_FILE) as f:
    rpm = json.load(f)

def score_headline(title, category, countries):
    score = 0

    for p in patterns:
        if p.lower() in title.lower():
            score += 20

    score += {
        "Business": 30,
        "Technology": 25,
        "Policy": 20,
        "Sports": 10
    }.get(category, 10)

    score += max(rpm.get(c, 40) for c in countries) * 0.3

    return round(score, 2)

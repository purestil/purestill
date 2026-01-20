import json
import re

with open("signals/discover_patterns.json") as f:
    patterns = json.load(f)

RPM_MAP = {
    "US": 100, "UK": 95, "CA": 90, "AU": 85,
    "EU": 70, "IN": 40
}

def length_score(title):
    l = len(title)
    return 100 if 55 <= l <= 75 else 60

def intent_score(title):
    t = title.lower()
    if any(k in t for k in ["explained", "what it means", "why"]):
        return 90
    if any(k in t for k in ["update", "today"]):
        return 80
    return 60

def clarity_score(title):
    return 90 if ":" in title or "?" not in title else 70

def predict(title, country="US"):
    pattern_rate = max(patterns["headline_patterns"].values(), default=50)
    score = (
        pattern_rate * 0.35
        + intent_score(title) * 0.25
        + length_score(title) * 0.15
        + RPM_MAP.get(country, 60) * 0.15
        + clarity_score(title) * 0.10
    )
    return round(score, 2)

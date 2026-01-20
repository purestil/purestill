import json
import re
from collections import Counter

with open("signals/discover_winners.json", encoding="utf-8") as f:
    winners = json.load(f)

headline_patterns = Counter()
section_patterns = Counter()

for a in winners:
    title = a["title"].lower()

    # headline pattern detection
    if "what it means" in title:
        headline_patterns["WHAT_IT_MEANS"] += 1
    elif "explained" in title:
        headline_patterns["EXPLAINED"] += 1
    elif "why" in title:
        headline_patterns["WHY"] += 1
    else:
        headline_patterns["STRAIGHT_NEWS"] += 1

    # content structure
    content = a.get("content","").lower()
    if "why this matters" in content:
        section_patterns["WHY_THIS_MATTERS"] += 1
    if "what happens next" in content:
        section_patterns["WHAT_NEXT"] += 1

patterns = {
    "headline_patterns": headline_patterns,
    "section_patterns": section_patterns
}

with open("signals/discover_patterns.json", "w") as f:
    json.dump(patterns, f, indent=2, default=int)

print("🧬 Discover patterns extracted")

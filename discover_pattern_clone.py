import json
from collections import Counter

DATA_FILE = "data.json"
OUT_FILE = "signals/winning_patterns.json"

patterns = Counter()

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    if item.get("HEADLINE_LOCKED") and item.get("DISCOVER_SIGNAL", 0) >= 2:
        title = item["HEADLINE_VARIANTS"][item["HEADLINE_ACTIVE"]]
        if ":" in title:
            pattern = title.split(":")[1].strip()
            patterns[pattern] += 1

top_patterns = [p for p, _ in patterns.most_common(5)]

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(top_patterns, f, indent=2)

print("🧬 Discover winning patterns extracted")

import json
import re
from collections import defaultdict

DATA_FILE = "data.json"

ENTITY_PATTERNS = {
    "Federal Reserve": ["federal reserve", "fed"],
    "Artificial Intelligence": ["ai", "artificial intelligence"],
    "Stock Market": ["stock", "market", "shares"],
    "Government Policy": ["policy", "government", "law", "regulation"]
}

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

entity_scores = defaultdict(int)

for article in data:
    text = (article.get("title","") + " " + article.get("summary","")).lower()

    for entity, keywords in ENTITY_PATTERNS.items():
        if any(k in text for k in keywords):
            entity_scores[entity] += 1
            article.setdefault("ENTITIES", []).append(entity)

# normalize authority score
for article in data:
    score = 0
    for e in article.get("ENTITIES", []):
        score += entity_scores.get(e, 0)

    article["ENTITY_AUTHORITY_SCORE"] = score

with open("signals/entity_authority.json", "w") as f:
    json.dump(entity_scores, f, indent=2)

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("🧠 Entity authority updated")

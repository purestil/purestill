import json
import random

with open("signals/discover_patterns.json", encoding="utf-8") as f:
    patterns = json.load(f)

headline_modes = list(patterns["headline_patterns"].keys())

def apply_headline_pattern(title):
    mode = random.choice(headline_modes)

    if mode == "WHAT_IT_MEANS":
        return f"{title}: What It Means"
    if mode == "EXPLAINED":
        return f"{title} Explained"
    if mode == "WHY":
        return f"Why {title} Matters Now"

    return title  # straight fallback

def apply_structure(content):
    if "Why This Matters" not in content:
        content += "\n<h2>Why This Matters</h2><p>This development has broader implications.</p>"
    if "What Happens Next" not in content:
        content += "\n<h2>What Happens Next</h2><p>Observers are watching upcoming signals.</p>"
    return content

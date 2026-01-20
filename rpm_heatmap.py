import json
from collections import defaultdict

DATA_FILE = "data.json"

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

heatmap = defaultdict(int)

for a in data:
    for c in a.get("TARGET_COUNTRIES", ["GLOBAL"]):
        key = f"{c}_{a.get('category','General')}"
        heatmap[key] += 1

with open("signals/rpm_heatmap.json", "w") as f:
    json.dump(heatmap, f, indent=2)

print("🔥 RPM heatmap built")

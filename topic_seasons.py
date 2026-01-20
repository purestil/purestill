import json
from datetime import datetime
from collections import defaultdict

with open("data.json") as f:
    data = json.load(f)

seasons = defaultdict(lambda: defaultdict(int))

for a in data:
    if a.get("DISCOVER_SIGNAL", 0) < 2:
        continue

    try:
        dt = datetime.fromisoformat(a["date"].replace("Z","+00:00"))
    except:
        continue

    week = dt.isocalendar()[1]
    topic = a.get("category","General")

    seasons[week][topic] += 1

season_map = {}

for week, topics in seasons.items():
    top = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3]
    season_map[str(week)] = [t[0] for t in top]

with open("signals/topic_seasons.json","w") as f:
    json.dump(season_map, f, indent=2)

print("📆 Topic seasons generated")

import json, os
from datetime import datetime, timezone

DISCOVER_FILE = "signals/discover_signals.json"
LIVE_FILE = "signals/live_feed.json"
TOPICS_FILE = "signals/topics_feed.json"

os.makedirs("signals", exist_ok=True)

now = datetime.now(timezone.utc)

live_count = 0
topic_strength = {}

if os.path.exists(LIVE_FILE):
    with open(LIVE_FILE, encoding="utf-8") as f:
        live_items = json.load(f)
        live_count = len(live_items)

if os.path.exists(TOPICS_FILE):
    with open(TOPICS_FILE, encoding="utf-8") as f:
        topics = json.load(f)
        for topic, items in topics.items():
            topic_strength[topic] = len(items)

discover_signals = {
    "publisher": "PureStill",
    "last_update": now.isoformat(),
    "discover_ready": True,
    "signals": {
        "freshness": "high",
        "update_velocity": "hourly",
        "mobile_optimized": True,
        "visual_intrusive_ads": False,
        "content_type": "news_analysis",
        "clickbait": False
    },
    "metrics": {
        "live_items": live_count,
        "topic_strength": topic_strength,
        "priority_topics": sorted(
            topic_strength,
            key=topic_strength.get,
            reverse=True
        )[:3]
    }
}

with open(DISCOVER_FILE, "w", encoding="utf-8") as f:
    json.dump(discover_signals, f, indent=2)

print("🧭 Discover signals updated")

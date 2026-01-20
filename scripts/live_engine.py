import json, os, hashlib
from datetime import datetime, timezone, timedelta
import feedparser

# ================= CONFIG =================

LIVE_FILE = "signals/live_feed.json"
SEEN_FILE = "signals/live_seen.json"
TOPICS_FILE = "signals/topics_feed.json"

LIVE_TTL_HOURS = 2          # live expires after 2 hours
MAX_PER_RUN = 10            # safety cap per run

# 🔝 Tier-1 sources (high RPM)
FEEDS = [
    ("https://feeds.reuters.com/reuters/topNews", "Reuters", 3),
    ("https://apnews.com/rss", "AP", 2),
    ("https://www.bbc.co.uk/news/rss.xml", "BBC", 2),
]

# 🧠 Topic detection
TOPIC_KEYWORDS = {
    "AI": ["ai", "artificial intelligence", "machine learning"],
    "Markets": ["stocks", "markets", "inflation", "rates", "wall street"],
    "Policy": ["government", "policy", "law", "election", "senate"],
    "Technology": ["technology", "tech", "software", "chip"],
    "World": []
}

BREAKING_KEYWORDS = ["breaking", "crisis", "surge", "record", "emergency"]

now = datetime.now(timezone.utc)

os.makedirs("signals", exist_ok=True)

# ================= HELPERS =================

def detect_topic(title: str) -> str:
    t = title.lower()
    for topic, keys in TOPIC_KEYWORDS.items():
        if any(k in t for k in keys):
            return topic
    return "World"

def score_item(minutes_ago: int, title: str, tier_weight: int) -> int:
    score = tier_weight * 20

    if minutes_ago <= 15:
        score += 40
    elif minutes_ago <= 60:
        score += 25
    elif minutes_ago <= 180:
        score += 10

    if any(k in title.lower() for k in BREAKING_KEYWORDS):
        score += 15

    return score

# ================= LOAD STATE =================

live_items = []
seen = set()

if os.path.exists(LIVE_FILE):
    with open(LIVE_FILE, encoding="utf-8") as f:
        live_items = json.load(f)

if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, encoding="utf-8") as f:
        seen = set(json.load(f))

# ================= EXPIRE OLD =================

fresh = []
for item in live_items:
    expires = datetime.fromisoformat(item["expires_at"])
    if expires > now:
        fresh.append(item)

live_items = fresh

# ================= FETCH FEEDS =================

added = 0
topics = {k: [] for k in TOPIC_KEYWORDS}

for feed_url, source, tier_weight in FEEDS:
    if added >= MAX_PER_RUN:
        break

    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:10]:
        if added >= MAX_PER_RUN:
            break

        title = entry.get("title", "").strip()
        link = entry.get("link", "")

        if not title or not link:
            continue

        uid = hashlib.md5((title + source).lower().encode()).hexdigest()
        if uid in seen:
            continue

        # published time
        if hasattr(entry, "published_parsed"):
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            minutes_ago = int((now - published).total_seconds() / 60)
        else:
            minutes_ago = 0

        topic = detect_topic(title)
        priority = score_item(minutes_ago, title, tier_weight)

        item = {
            "id": uid,
            "title": title,
            "url": link,
            "source": source,
            "topic": topic,
            "priority": priority,
            "minutes_ago": minutes_ago,
            "timestamp": now.isoformat(),
            "expires_at": (now + timedelta(hours=LIVE_TTL_HOURS)).isoformat()
        }

        live_items.insert(0, item)
        topics[topic].append(item)

        seen.add(uid)
        added += 1

# ================= SORT & TRIM =================

# Sort live items by priority
live_items = sorted(live_items, key=lambda x: x["priority"], reverse=True)

# Keep feed compact
live_items = live_items[:30]

# ================= SAVE =================

with open(LIVE_FILE, "w", encoding="utf-8") as f:
    json.dump(live_items, f, indent=2)

with open(SEEN_FILE, "w", encoding="utf-8") as f:
    json.dump(list(seen), f)

with open(TOPICS_FILE, "w", encoding="utf-8") as f:
    json.dump(topics, f, indent=2)

print(f"🔴 Live engine added {added} updates | {len(live_items)} active")

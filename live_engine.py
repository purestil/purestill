import json, os, hashlib
from datetime import datetime, timezone, timedelta
import feedparser

LIVE_FILE = "signals/live_feed.json"
SEEN_FILE = "signals/live_seen.json"

LIVE_TTL_HOURS = 2          # live expires after 2 hours
MAX_PER_RUN = 10            # safety cap per run

FEEDS = [
    ("https://feeds.reuters.com/reuters/topNews", "Reuters"),
    ("https://apnews.com/rss", "AP"),
    ("https://www.bbc.co.uk/news/rss.xml", "BBC"),
]

now = datetime.now(timezone.utc)

os.makedirs("signals", exist_ok=True)

# ---------- load state ----------
live_items = []
seen = set()

if os.path.exists(LIVE_FILE):
    with open(LIVE_FILE, encoding="utf-8") as f:
        live_items = json.load(f)

if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, encoding="utf-8") as f:
        seen = set(json.load(f))

# ---------- expire old ----------
fresh = []
for item in live_items:
    expires = datetime.fromisoformat(item["expires_at"])
    if expires > now:
        fresh.append(item)

live_items = fresh

# ---------- fetch feeds ----------
added = 0

for feed_url, source in FEEDS:
    if added >= MAX_PER_RUN:
        break

    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:10]:
        if added >= MAX_PER_RUN:
            break

        title = entry.get("title", "").strip()
        if not title:
            continue

        uid = hashlib.md5(title.lower().encode()).hexdigest()
        if uid in seen:
            continue

        item = {
            "id": uid,
            "title": title,
            "source": source,
            "timestamp": now.isoformat(),
            "expires_at": (now + timedelta(hours=LIVE_TTL_HOURS)).isoformat()
        }

        live_items.insert(0, item)
        seen.add(uid)
        added += 1

# ---------- save ----------
with open(LIVE_FILE, "w", encoding="utf-8") as f:
    json.dump(live_items, f, indent=2)

with open(SEEN_FILE, "w", encoding="utf-8") as f:
    json.dump(list(seen), f)

print(f"🔴 Live engine added {added} updates")

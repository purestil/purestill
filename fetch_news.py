import feedparser
import json
import os
from datetime import datetime, timezone

# ================= CONFIG =================
DATA_FILE = "data.json"
FEEDS_FILE = "feeds.txt"

MAX_ITEMS_PER_FEED = 3      # 2–3 per feed
MAX_ITEMS_PER_RUN = 20      # total per day (safe range 15–25)

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ================= LOAD EXISTING DATA =================
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

existing_links = {item.get("source") for item in data}
existing_today = sum(1 for item in data if item.get("date") == TODAY)

# ================= LOAD FEEDS WITH WEIGHTS =================
feeds = []
with open(FEEDS_FILE, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = [p.strip() for p in line.split("|")]
        url = parts[0]
        weight = int(parts[1]) if len(parts) > 1 else 1
        feeds.append((url, weight))

# Highest priority first (Gov > Media > Tech > Google News)
feeds.sort(key=lambda x: x[1], reverse=True)

new_items_added = 0
paused_feeds = []

# ================= CATEGORY DETECTION =================
def detect_category(title):
    t = title.lower()
    if any(k in t for k in ["inflation", "jobs", "labor", "gdp", "economy"]):
        return "Economy"
    if any(k in t for k in ["technology", "ai", "chip", "software", "tech"]):
        return "Technology"
    if any(k in t for k in ["market", "stocks", "bonds", "earnings"]):
        return "Markets"
    if any(k in t for k in ["policy", "regulation", "law", "government"]):
        return "Policy"
    return "General"

# ================= FETCH LOOP =================
for feed_url, weight in feeds:
    if new_items_added >= MAX_ITEMS_PER_RUN:
        break

    feed = feedparser.parse(feed_url)

    # ---------- AUTO-PAUSE ON ERROR ----------
    if getattr(feed, "bozo", False):
        paused_feeds.append(feed_url)
        print(f"⚠️ Feed error, skipped: {feed_url}")
        continue

    if not feed.entries:
        paused_feeds.append(feed_url)
        print(f"⚠️ Empty feed, skipped: {feed_url}")
        continue
    # ----------------------------------------

    feed_count = 0

    for entry in feed.entries:
        if new_items_added >= MAX_ITEMS_PER_RUN:
            break
        if feed_count >= MAX_ITEMS_PER_FEED:
            break
        if existing_today + new_items_added >= MAX_ITEMS_PER_RUN:
            break

        link = entry.get("link")
        title = entry.get("title", "").strip()

        if not link or not title:
            continue
        if link in existing_links:
            continue

        summary = (
            f"An independent analysis based on recent public information regarding "
            f"{title}. The summary highlights context, implications, and relevance "
            f"for the United States."
        )

        item = {
            "title": title,
            "summary": summary,
            "content": "",              # expanded later by generate_pages.py
            "category": detect_category(title),
            "date": TODAY,
            "source": link
        }

        data.insert(0, item)
        existing_links.add(link)
        new_items_added += 1
        feed_count += 1

# ================= SAVE UPDATED DATA =================
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

# ================= REPORT =================
print(f"fetch_news.py finished → added {new_items_added} new articles ({TODAY})")

if paused_feeds:
    print("⏸️ Feeds paused this run:")
    for f in paused_feeds:
        print(f" - {f}")

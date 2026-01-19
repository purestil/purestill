import feedparser
import json
import os
from datetime import datetime, timezone

# ================= CONFIG =================
DATA_FILE = "data.json"
FEEDS_FILE = "feeds.txt"

MAX_ITEMS_PER_FEED = 3      # 2–3 items per feed
MAX_ITEMS_PER_RUN = 20      # total 15–25 per day (safe default)

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ================= LOAD EXISTING DATA =================
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

existing_links = {item.get("source") for item in data}
existing_today = sum(1 for item in data if item.get("date") == TODAY)

# ================= LOAD FEEDS =================
with open(FEEDS_FILE, encoding="utf-8") as f:
    feeds = [line.strip() for line in f if line.strip() and not line.startswith("#")]

new_items_added = 0

# ================= CATEGORY DETECTION =================
def detect_category(title):
    t = title.lower()
    if any(k in t for k in ["inflation", "jobs", "gdp", "economy", "labor"]):
        return "Economy"
    if any(k in t for k in ["technology", "ai", "software", "chip", "tech"]):
        return "Technology"
    if any(k in t for k in ["market", "stocks", "bonds", "earnings"]):
        return "Markets"
    if any(k in t for k in ["policy", "regulation", "law", "government"]):
        return "Policy"
    return "General"

# ================= FETCH LOOP =================
for feed_url in feeds:
    if new_items_added >= MAX_ITEMS_PER_RUN:
        break

    feed = feedparser.parse(feed_url)
    feed_count = 0

    for entry in feed.entries:
        if new_items_added >= MAX_ITEMS_PER_RUN:
            break
        if feed_count >= MAX_ITEMS_PER_FEED:
            break

        link = entry.get("link")
        title = entry.get("title", "").strip()

        if not link or not title:
            continue
        if link in existing_links:
            continue
        if existing_today + new_items_added >= MAX_ITEMS_PER_RUN:
            break

        summary_text = (
            f"An independent analysis based on recent public information regarding "
            f"{title}. The article examines context, implications, and broader relevance "
            f"for the United States."
        )

        item = {
            "title": title,
            "summary": summary_text,
            "content": "",  # expanded later by generate_pages.py
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

print(f"fetch_news.py complete → added {new_items_added} new articles ({TODAY})")

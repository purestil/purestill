import feedparser
import json
import os
from datetime import datetime, timezone

# ================= CONFIG =================
DATA_FILE = "data.json"
FEEDS_FILE = "feeds.txt"

MAX_ITEMS_PER_FEED = 3        # max per feed per run
MAX_ITEMS_PER_RUN = 20        # total per run (safe: 15–25)

NOW = datetime.now(timezone.utc)
TODAY = NOW.strftime("%Y-%m-%d")

# ================= LOAD EXISTING DATA =================
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print("⚠️ data.json invalid, resetting to empty list")
            data = []
    except Exception as e:
        print("⚠️ Failed to read data.json, resetting:", e)
        data = []
else:
    data = []

existing_links = {
    item.get("source")
    for item in data
    if isinstance(item, dict)
}

existing_today = sum(
    1 for item in data
    if isinstance(item, dict)
    and str(item.get("date", "")).startswith(TODAY)
)

# ================= LOAD FEEDS =================
if not os.path.exists(FEEDS_FILE):
    raise Exception("feeds.txt not found in repo root")

feeds = []
with open(FEEDS_FILE, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = [p.strip() for p in line.split("|")]
        url = parts[0]
        weight = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
        feeds.append((url, weight))

# Higher weight first (gov / Reuters > others)
feeds.sort(key=lambda x: x[1], reverse=True)

# ================= CATEGORY DETECTION =================
def detect_category(title: str) -> str:
    t = title.lower()

    if any(k in t for k in ["inflation", "jobs", "labor", "gdp", "economy", "growth"]):
        return "Economy"
    if any(k in t for k in ["market", "stocks", "shares", "bonds", "earnings"]):
        return "Business"
    if any(k in t for k in ["technology", "tech", "ai", "chip", "software"]):
        return "Technology"
    if any(k in t for k in ["policy", "regulation", "law", "government", "court"]):
        return "Policy"

    return "General"

# ================= FETCH LOOP =================
new_items_added = 0
paused_feeds = []

for feed_url, weight in feeds:
    if new_items_added >= MAX_ITEMS_PER_RUN:
        break

    print(f"🔍 Fetching: {feed_url}")
    feed = feedparser.parse(feed_url)

    # ---- FEED SAFETY CHECKS ----
    if getattr(feed, "bozo", False):
        paused_feeds.append(feed_url)
        print("⚠️ Feed parse error, skipped")
        continue

    if not getattr(feed, "entries", []):
        paused_feeds.append(feed_url)
        print("⚠️ Empty feed, skipped")
        continue
    # ----------------------------

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

        # ✅ Original summary (copyright-safe)
        summary = (
            f"An independent analysis based on recent public information regarding "
            f"{title}. This summary highlights context, implications, and relevance "
            f"for the United States."
        )

        item = {
            "title": title,
            "summary": summary,
            "content": "",                  # expanded later by generate_pages.py
            "category": detect_category(title),
            "date": NOW.isoformat(),         # FULL ISO (critical)
            "source": link,

            # 🔥 NEW FIELDS (used by homepage logic)
            "IS_BREAKING": True,             # all fresh feed items start as breaking
            "PUBLISH_GROUP": "breaking"
        }

        data.insert(0, item)
        existing_links.add(link)
        new_items_added += 1
        feed_count += 1

# ================= SAVE UPDATED DATA =================
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# ================= REPORT =================
print("✅ fetch_news.py finished")
print(f"➕ New articles added: {new_items_added}")
print(f"📅 Date (UTC): {TODAY}")

if paused_feeds:
    print("⏸️ Feeds paused this run:")
    for f in paused_feeds:
        print(f" - {f}")

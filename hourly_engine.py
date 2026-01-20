print("🧠 Starting PureStill Hourly Engine…")

import json
import os
from datetime import datetime, timezone

# ================= CONFIG =================
DATA_FILE = "data.json"
LIVE_FILE = "signals/live_feed.json"

MAX_PER_HOUR = 4          # HARD LIMIT (Discover-safe)

NOW = datetime.now(timezone.utc).isoformat()

# ================= SAFETY CHECKS =================
if not os.path.exists(DATA_FILE):
    raise Exception("❌ data.json not found")

if not os.path.exists(LIVE_FILE):
    print("⚠️ No live_feed.json found — skipping hourly generation")
    exit()

# ================= LOAD DATA =================
with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

with open(LIVE_FILE, encoding="utf-8") as f:
    live = json.load(f)

if not isinstance(data, list):
    raise Exception("❌ data.json must be a list")

if not isinstance(live, list):
    raise Exception("❌ live_feed.json must be a list")

existing_titles = {a.get("TITLE") for a in data if isinstance(a, dict)}
generated = 0

# ================= HOURLY PROMOTION LOGIC =================
for item in live:
    if generated >= MAX_PER_HOUR:
        break

    title = item.get("title", "").strip()
    source = item.get("source", "Unknown")

    if not title:
        continue

    # 🚫 DUPLICATE GUARD
    if title in existing_titles:
        continue

    article = {
        # 🔑 CORE FIELDS (PURESTILL STANDARD)
        "TITLE": title,
        "SUMMARY": f"An independent analysis of recent developments regarding {title}.",
        "CONTENT": "",   # expanded later by generate_pages.py
        "CATEGORY": "General",
        "SOURCE": source,
        "DATE": NOW,

        # 🌍 INTELLIGENCE FIELDS
        "COUNTRY": "GLOBAL",
        "IS_BREAKING": False,          # hourly ≠ live
        "VISIBILITY": "normal",

        # 🧪 DISCOVER / HEADLINE SYSTEM
        "HEADLINE_VARIANTS": [
            title,
            f"{title}: What It Means",
            f"{title} Explained"
        ],
        "HEADLINE_ACTIVE": 0,
        "DISCOVER_SIGNAL": 0
    }

    data.insert(0, article)
    existing_titles.add(title)
    generated += 1

# ================= SAVE =================
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Hourly engine generated {generated} articles")

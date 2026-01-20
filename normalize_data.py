print("🔧 Normalizing PureStill data.json…")

import json
import hashlib
from datetime import datetime, timezone, timedelta

DATA_FILE = "data.json"

NOW = datetime.now(timezone.utc)

# =========================
# CONFIG (LOCKED RULES)
# =========================

BREAKING_TTL_HOURS = 2          # auto demote breaking after 2h
MAX_BREAKING_ALLOWED = 3        # safety guard
DEFAULT_COUNTRY = "GLOBAL"

CATEGORY_MAP = {
    "policy": "Policy",
    "politics": "Policy",
    "government": "Policy",
    "economy": "Economy",
    "business": "Business",
    "technology": "Technology",
    "tech": "Technology",
    "ai": "AI",
    "sports": "Sports"
}

# =========================
# HELPERS
# =========================

def iso(dt):
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")

def normalize_date(d):
    try:
        dt = datetime.fromisoformat(d.replace("Z", "+00:00"))
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return iso(dt)
    except:
        return iso(NOW)

def normalize_category(cat):
    if not cat:
        return "General"
    key = str(cat).lower().strip()
    return CATEGORY_MAP.get(key, cat.title())

def fingerprint(title):
    return hashlib.md5(title.lower().encode()).hexdigest()

def default_headlines(title):
    return [
        title,
        f"{title}: what it means",
        f"Explained: {title}"
    ]

# =========================
# LOAD DATA
# =========================

with open(DATA_FILE, encoding="utf-8") as f:
    raw = json.load(f)

if not isinstance(raw, list):
    raise Exception("❌ data.json must be a list")

normalized = []
seen = set()
breaking_count = 0

# =========================
# NORMALIZE EACH ITEM
# =========================

for item in raw:
    title = item.get("TITLE") or item.get("title")
    if not title:
        continue

    fid = fingerprint(title)
    if fid in seen:
        continue
    seen.add(fid)

    date_raw = item.get("DATE") or item.get("date") or iso(NOW)
    date = normalize_date(date_raw)

    age_hours = (NOW - datetime.fromisoformat(date.replace("Z","+00:00"))).total_seconds() / 3600

    is_breaking = bool(item.get("IS_BREAKING", False))

    # 🔴 AUTO DEMOTION
    if is_breaking and age_hours > BREAKING_TTL_HOURS:
        is_breaking = False

    # 🔴 HARD BREAKING CAP
    if is_breaking:
        if breaking_count >= MAX_BREAKING_ALLOWED:
            is_breaking = False
        else:
            breaking_count += 1

    category = normalize_category(
        item.get("CATEGORY") or item.get("category")
    )

    entry = {
        "TITLE": title.strip(),
        "SUMMARY": item.get("SUMMARY") or item.get("summary") or "",
        "CONTENT": item.get("CONTENT") or item.get("content") or "",
        "CATEGORY": category,
        "DATE": date,
        "SOURCE": item.get("SOURCE") or item.get("source") or "",

        # 🔐 REQUIRED SYSTEM FIELDS
        "COUNTRY": item.get("COUNTRY", DEFAULT_COUNTRY),
        "IS_BREAKING": is_breaking,
        "PUBLISH_GROUP": (
            "breaking" if is_breaking else item.get("PUBLISH_GROUP", "normal")
        ),

        # 🧠 DISCOVER / HEADLINE SYSTEM
        "HEADLINE_VARIANTS": item.get("HEADLINE_VARIANTS") or default_headlines(title),
        "HEADLINE_ACTIVE": int(item.get("HEADLINE_ACTIVE", 0)),
        "DISCOVER_SIGNAL": int(item.get("DISCOVER_SIGNAL", 0)),
        "VISIBILITY": item.get("VISIBILITY", "normal")
    }

    normalized.append(entry)

# =========================
# SAVE BACK (AUTHORITATIVE)
# =========================

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(normalized, f, indent=2)

print(f"✅ Normalized {len(normalized)} articles")
print(f"🔴 Active breaking items: {breaking_count}")
print("🛡 Schema locked. data.json is now system-managed.")

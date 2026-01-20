print("🧹 Starting PureStill data normalization…")

import json, os, hashlib
from datetime import datetime, timezone, timedelta

DATA_FILE = "data.json"
OUTPUT_FILE = "data.json"   # in-place normalization
SIGNALS_DIR = "signals"

os.makedirs(SIGNALS_DIR, exist_ok=True)

NOW = datetime.now(timezone.utc)

# ===================== SCHEMA DEFAULTS =====================
DEFAULT_ITEM = {
    "TITLE": "",
    "SUMMARY": "",
    "CONTENT": "",
    "CATEGORY": "General",
    "DATE": "",
    "SOURCE": "",
    "IS_BREAKING": False,
    "PUBLISH_GROUP": "normal",
    "COUNTRY": "GLOBAL",
    "VISIBILITY": "public",
    "WORD_COUNT": 0,
    "CANONICAL_READY": True
}

# ===================== LOAD DATA =====================
if not os.path.exists(DATA_FILE):
    raise Exception("❌ data.json not found")

with open(DATA_FILE, encoding="utf-8") as f:
    raw = json.load(f)

if not isinstance(raw, list):
    raise Exception("❌ data.json must be a list")

# ===================== HELPERS =====================
def iso_now():
    return NOW.isoformat()

def parse_date(d):
    try:
        return datetime.fromisoformat(str(d).replace("Z", "+00:00"))
    except Exception:
        return NOW

def hours_old(d):
    return (NOW - parse_date(d)).total_seconds() / 3600

def guess_country(title, source):
    s = f"{title} {source}".lower()
    if any(k in s for k in ["u.s.", "us ", "america", "federal", "wall street"]):
        return "US"
    if any(k in s for k in ["uk ", "britain", "london"]):
        return "UK"
    if any(k in s for k in ["canada", "toronto"]):
        return "CA"
    if any(k in s for k in ["india", "delhi", "mumbai"]):
        return "IN"
    return "GLOBAL"

def normalize_category(c):
    c = str(c).strip().title()
    allowed = {
        "Policy","Economy","Business","Technology","AI",
        "Sports","General"
    }
    return c if c in allowed else "General"

def word_count(text):
    return len(text.split()) if isinstance(text, str) else 0

def uid_for(item):
    key = f"{item.get('TITLE','')}{item.get('SOURCE','')}"
    return hashlib.md5(key.encode()).hexdigest()

# ===================== NORMALIZATION =====================
normalized = []
seen_ids = set()
demoted = 0
fixed = 0

for item in raw:
    if not isinstance(item, dict):
        continue

    n = DEFAULT_ITEM.copy()

    # --- map legacy keys ---
    n["TITLE"]   = item.get("TITLE") or item.get("title","").strip()
    n["SUMMARY"] = item.get("SUMMARY") or item.get("summary","").strip()
    n["CONTENT"] = item.get("CONTENT") or item.get("content","").strip()
    n["SOURCE"]  = item.get("SOURCE") or item.get("source","").strip()
    n["CATEGORY"]= normalize_category(item.get("CATEGORY") or item.get("category","General"))
    n["DATE"]    = item.get("DATE") or item.get("date") or iso_now()

    # --- breaking logic (STRICT) ---
    is_breaking = bool(item.get("IS_BREAKING") is True)
    age = hours_old(n["DATE"])

    if is_breaking and age > 2:
        is_breaking = False
        demoted += 1

    n["IS_BREAKING"] = is_breaking
    n["PUBLISH_GROUP"] = "breaking" if is_breaking else "normal"

    # --- country ---
    n["COUNTRY"] = item.get("COUNTRY") or guess_country(n["TITLE"], n["SOURCE"])

    # --- content checks ---
    wc = word_count(n["CONTENT"])
    n["WORD_COUNT"] = wc

    if wc > 0 and wc < 250:
        # weak content → hide from homepage
        n["VISIBILITY"] = "internal"

    # --- de-duplication ---
    uid = uid_for(n)
    if uid in seen_ids:
        continue
    seen_ids.add(uid)

    normalized.append(n)
    fixed += 1

# ===================== SAVE =====================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(normalized, f, indent=2, ensure_ascii=False)

# ===================== TRUST SIGNAL EMIT =====================
trust = {
    "normalized": True,
    "items_total": len(normalized),
    "breaking_demoted": demoted,
    "weak_content_hidden": len([i for i in normalized if i["VISIBILITY"]!="public"]),
    "last_run": iso_now()
}

with open(os.path.join(SIGNALS_DIR, "normalization.json"), "w") as f:
    json.dump(trust, f, indent=2)

print(f"✅ Normalized items: {fixed}")
print(f"⏱ Breaking auto-demoted: {demoted}")
print("🛡 Data schema locked. Safe for Discover.")

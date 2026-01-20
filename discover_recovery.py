import json
from datetime import datetime, timezone

# ================= CONFIG =================
DATA_FILE = "data.json"
NOW = datetime.now(timezone.utc)

# 🔧 Recovery rules (SAFE & CONSERVATIVE)
RECOVERY_MIN_DAYS = 3        # too early → skip
RECOVERY_MAX_DAYS = 10       # too old → skip
DROP_AFTER_DAYS = 5          # Discover cooling threshold
MAX_RECOVERIES = 3           # hard cap per run (anti-spam)

# ================= LOAD DATA =================
with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

if not isinstance(data, list):
    raise Exception("data.json must be a list")

recovered = 0

# ================= RECOVERY SCAN =================
for item in data:
    if recovered >= MAX_RECOVERIES:
        break

    # ❌ Never touch protected articles
    if item.get("HEADLINE_LOCKED") is True:
        continue
    if item.get("RECOVERY_FLAG") is True:
        continue

    # ⏱ Parse publish date safely
    try:
        published = datetime.fromisoformat(
            str(item.get("date", "")).replace("Z", "+00:00")
        )
    except Exception:
        continue

    age_days = (NOW - published).days

    # 🧠 Recovery eligibility window
    if not (RECOVERY_MIN_DAYS <= age_days <= RECOVERY_MAX_DAYS):
        continue

    # 📉 Detect Discover cooling
    discover_signal = item.get("DISCOVER_SIGNAL", 0)

    if age_days >= DROP_AFTER_DAYS and discover_signal == 0:
        item["RECOVERY_FLAG"] = True
        item["RECOVERY_AT"] = NOW.isoformat()

        recovered += 1

# ================= SAVE =================
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"🩺 Discover recovery flagged: {recovered}")

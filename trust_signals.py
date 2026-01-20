import json
import os
from datetime import datetime, timezone, timedelta

# ================= CONFIG =================
DATA_FILE = "data.json"
SIGNALS_DIR = "signals"

os.makedirs(SIGNALS_DIR, exist_ok=True)

NOW = datetime.now(timezone.utc)

# ================= LOAD DATA =================
with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

# ================= STRUCTURAL TRUST SIGNALS =================
# These represent publisher-level transparency signals
STRUCTURAL_TRUST = {
    "editorial_policy": True,
    "source_transparency": True,
    "corrections_policy": True,
    "contact_page": True,
    "about_page": True,
    "consistent_authorship": True
}

# Save structural trust signals (human + Google readable)
with open(os.path.join(SIGNALS_DIR, "trust_signals.json"), "w", encoding="utf-8") as f:
    json.dump(STRUCTURAL_TRUST, f, indent=2)

# ================= BEHAVIORAL TRUST CHECKS =================
# These are inferred by Google from publishing behavior

behavioral = {
    "source_attribution": 1,      # articles have sources
    "content_length_ok": 1,       # not thin
    "publishing_rate_ok": 1,      # not spammy
    "topic_focus": 1,             # not random
    "evergreen_updates": 1        # updates exist
}

# ---- Publishing rate guard ----
# Too many articles overall = spam risk
if len(data) > 15:
    behavioral["publishing_rate_ok"] = 0

# ---- Topic focus guard ----
categories = set(a.get("category", "General") for a in data)
if len(categories) > 6:
    behavioral["topic_focus"] = 0

# ---- Content length guard ----
for a in data:
    content = a.get("content", "")
    if content and len(content.split()) < 300:
        behavioral["content_length_ok"] = 0
        break

# ---- Evergreen update signal ----
if not any("EVERGREEN" in k or "updated" in str(v).lower() for a in data for k, v in a.items()):
    behavioral["evergreen_updates"] = 0

# ---- Source attribution ----
if not any(a.get("source") for a in data):
    behavioral["source_attribution"] = 0

# ================= FINAL TRUST SCORE =================
# Behavioral signals = 5 × 20 = 100 max
behavioral_score = sum(behavioral.values()) * 20

# Structural signals = confidence multiplier
structural_bonus = sum(1 for v in STRUCTURAL_TRUST.values() if v) * 2  # max +12

final_trust_score = min(100, behavioral_score + structural_bonus)

# ================= SAVE TRUST SCORE =================
trust_output = {
    "trust_score": final_trust_score,
    "generated_at": NOW.isoformat(),
    "behavioral_signals": behavioral,
    "structural_signals": STRUCTURAL_TRUST
}

with open(os.path.join(SIGNALS_DIR, "trust_score.json"), "w", encoding="utf-8") as f:
    json.dump(trust_output, f, indent=2)

print(f"🛡 Trust score locked: {final_trust_score}/100")

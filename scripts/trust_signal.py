import json, os
from datetime import datetime, timezone

SIGNAL_FILE = "signals/trust_signals.json"

os.makedirs("signals", exist_ok=True)

now = datetime.now(timezone.utc)

trust_signals = {
    "publisher": "PureStill",
    "updated_at": now.isoformat(),
    "signals": {
        "editorial_type": "analysis",
        "original_reporting": False,
        "summarization": True,
        "source_attribution": True,
        "fact_checking": "source-based",
        "update_frequency": "hourly",
        "language": "en",
        "region_focus": ["US", "UK", "CA", "AU"],
        "ad_policy_safe": True,
        "spam_score": 0.01
    },
    "cadence": {
        "live_updates_per_hour": 1,
        "analysis_depth": "longform",
        "content_decay_hours": 48
    }
}

with open(SIGNAL_FILE, "w", encoding="utf-8") as f:
    json.dump(trust_signals, f, indent=2)

print("🛡️ Trust signals updated")

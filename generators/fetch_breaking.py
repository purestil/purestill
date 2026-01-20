import json, datetime, os

FILE = "signals/breaking_signals.json"
os.makedirs("signals", exist_ok=True)

now = datetime.datetime.utcnow().isoformat() + "Z"

signals = [
  {
    "id": f"evt_{now}",
    "title": "Major global event reported across multiple regions",
    "source": "Reuters",
    "detected_at": now
  }
]

with open(FILE, "w", encoding="utf-8") as f:
    json.dump(signals, f, indent=2)

print("Breaking signals updated")

import json, os

FILE = "signals/hourly_trends.json"
os.makedirs("signals", exist_ok=True)

trends = [
  {
    "topic": "Federal Reserve policy outlook",
    "category": "Economy",
    "trend_score": 85,
    "target_countries": ["US", "CA", "UK"]
  },
  {
    "topic": "AI regulation update",
    "category": "Technology",
    "trend_score": 80,
    "target_countries": ["US", "EU"]
  }
]

with open(FILE, "w", encoding="utf-8") as f:
    json.dump(trends, f, indent=2)

print("Hourly trends updated")

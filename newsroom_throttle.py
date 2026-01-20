import json

with open("signals/site_health.json") as f:
    health = json.load(f)

QUALITY = health["site_quality_score"]

THROTTLE = False
MAX_ARTICLES = 10

if QUALITY < 80:
    THROTTLE = True
    MAX_ARTICLES = 4
elif QUALITY < 90:
    MAX_ARTICLES = 6

with open("signals/publish_limits.json", "w") as f:
    json.dump({
        "throttle": THROTTLE,
        "max_articles": MAX_ARTICLES
    }, f)

print("🚦 Throttle:", THROTTLE, "| Max articles:", MAX_ARTICLES)

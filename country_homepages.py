import json, os

DATA_FILE = "data.json"
OUT_DIR = "site"

COUNTRY_RPM = {
    "US": 100,
    "UK": 90,
    "CA": 85,
    "AU": 80
}

os.makedirs(OUT_DIR, exist_ok=True)

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

def score(article, country):
    base = article.get("final_score", 0)
    rpm = COUNTRY_RPM.get(country, 50)
    if country in article.get("TARGET_COUNTRIES", []):
        base += rpm * 0.5
    return base

for country in COUNTRY_RPM:
    country_articles = sorted(
        data,
        key=lambda a: score(a, country),
        reverse=True
    )[:15]

    html = "<h1>Top News for {}</h1>".format(country)

    for a in country_articles:
        html += f"""
        <div>
          <a href="/articles/{a['slug']}.html">{a['title']}</a>
        </div>
        """

    out = os.path.join(OUT_DIR, country.lower())
    os.makedirs(out, exist_ok=True)

    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(html)

print("🌍 Country homepages generated")

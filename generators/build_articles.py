import json, os

TEMPLATE = "site/articles/_article_template.html"
OUTPUT_DIR = "site/articles"
DATA = "signals/articles_data.json"   # your article content

with open(TEMPLATE, encoding="utf-8") as f:
    template = f.read()

with open(DATA, encoding="utf-8") as f:
    articles = json.load(f)

os.makedirs(OUTPUT_DIR, exist_ok=True)

for a in articles:
    html = template
    for k, v in a.items():
        html = html.replace(f"{{{{{k}}}}}", v)

    out = os.path.join(OUTPUT_DIR, f"{a['slug']}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

print("✅ Articles generated")

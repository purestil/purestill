print("Starting PureStill generator…")

import json, os, re
from datetime import datetime

# ================= CONFIG =================
BASE_URL = "https://purestill.pages.dev"
SITE_DIR = "site"
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")

os.makedirs(ARTICLES_DIR, exist_ok=True)

# ================= LOAD DATA =================
with open("data.json", encoding="utf-8") as f:
    raw_data = json.load(f)

if not isinstance(raw_data, list):
    raise Exception("data.json must be a list")

# ================= LOAD TEMPLATES =================
with open("article_template.html", encoding="utf-8") as f:
    ARTICLE_TEMPLATE = f.read()

with open("index_template.html", encoding="utf-8") as f:
    INDEX_TEMPLATE = f.read()

# ================= HELPERS =================
def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def safe(item, *keys, default=""):
    for k in keys:
        if k in item and item[k]:
            return str(item[k])
    return default

# ================= GENERATE ARTICLES =================
cards = []

for item in raw_data:
    title = safe(item, "TITLE", "title")
    if not title:
        continue  # skip broken entry safely

    summary = safe(item, "SUMMARY", "summary")
    content = safe(item, "CONTENT", "content")
    category = safe(item, "CATEGORY", "category", default="General")
    source = safe(item, "SOURCE", "source")
    date = safe(item, "DATE", "date", default=datetime.utcnow().isoformat())

    slug = slugify(title)
    canonical = f"{BASE_URL}/articles/{slug}.html"

    html = ARTICLE_TEMPLATE
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{SUMMARY}}", summary)
    html = html.replace("{{CONTENT}}", content)
    html = html.replace("{{CATEGORY}}", category)
    html = html.replace("{{SOURCE}}", source)
    html = html.replace("{{DATE}}", date)
    html = html.replace("{{CANONICAL_URL}}", canonical)
    html = html.replace("{{RELATED_LINKS}}", "")
    html = html.replace("{{AD_MID}}", "")
    html = html.replace("{{AD_BOTTOM}}", "")

    out_path = os.path.join(ARTICLES_DIR, f"{slug}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    cards.append(f"""
      <div class="card">
        <h3><a href="/articles/{slug}.html">{title}</a></h3>
        <p>{summary}</p>
        <div class="read-more">
          <a href="/articles/{slug}.html">Read analysis →</a>
        </div>
      </div>
    """)

print(f"Generated {len(cards)} articles")

# ================= GENERATE INDEX =================
if not cards:
    raise Exception("No articles generated")

index_html = INDEX_TEMPLATE
index_html = index_html.replace("{{FEATURED_ARTICLE}}", cards[0])
index_html = index_html.replace("{{RECENT_ARTICLES}}", "\n".join(cards))
index_html = index_html.replace("{{TOP_ARTICLES}}", "")
index_html = index_html.replace("{{OLDER_ARTICLES}}", "")

with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("Index generated")
print("PureStill build complete")

print("Starting PureStill generator...")

import json, os
from datetime import datetime
from collections import defaultdict

# ================== LOAD DATA ==================
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

# ================== DIRECTORIES ==================
SITE_DIR = "site"
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")
TOPICS_DIR = os.path.join(SITE_DIR, "topics")
PILLARS_DIR = os.path.join(SITE_DIR, "pillars")

os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs(TOPICS_DIR, exist_ok=True)
os.makedirs(PILLARS_DIR, exist_ok=True)

# ================== LOAD TEMPLATES ==================
with open("article_template.html", encoding="utf-8") as f:
    ARTICLE_TEMPLATE = f.read()

with open("index_template.html", encoding="utf-8") as f:
    INDEX_TEMPLATE = f.read()

# ================== CONSTANTS ==================
BASE_URL = "https://purestill.pages.dev"

PILLARS = {
    "Economy": "us-economy",
    "Technology": "technology-trends",
    "General": "us-economy"
}

# ================== HELPERS ==================
def excerpt(text, limit=220):
    words = text.split()
    return " ".join(words[:limit]) + ("…" if len(words) > limit else "")

def ensure_length(text, min_words=650):
    words = text.split()
    if len(words) >= min_words:
        return text
    filler = (
        " This analysis expands on broader economic context, historical patterns, "
        "policy implications, and market responses to provide a balanced and "
        "informational overview based on publicly available sources."
    )
    while len(words) < min_words:
        text += filler
        words = text.split()
    return text

def score(item):
    s = len(item.get("content", "").split()) // 200
    if item.get("category") in ["Economy", "Technology"]:
        s += 3
    return s

def build_related(current_index, items, limit=3):
    ranked = []
    for i, it in enumerate(items):
        if i != current_index:
            ranked.append((score(it), i, it))
    ranked.sort(reverse=True)
    html = ""
    for _, i, it in ranked[:limit]:
        html += f"<li><a href='/articles/article-{i+1}.html'>{it['title']}</a></li>\n"
    return html

def article_card(item, idx):
    return f"""
    <div class="card">
      <h3>
        <a href="/articles/article-{idx+1}.html">{item['title']}</a>
      </h3>
      <p class="meta">
        Published {item.get('date','')} · {item.get('category','General')}
      </p>
      <p>{excerpt(item.get('content',''))}</p>
      <a href="/articles/article-{idx+1}.html">Read more →</a>
    </div>
    """

# ================== ARTICLE GENERATION ==================
categories = defaultdict(list)

for i, item in enumerate(data):
    category = item.get("category", "General")
    slug = category.lower().replace(" ", "-")
    categories[category].append((i, item))

    canonical = f"{BASE_URL}/articles/article-{i+1}.html"
    date = item.get("date", datetime.utcnow().strftime("%Y-%m-%d"))

    content = ensure_length(item.get("content", item["title"]))

    page = ARTICLE_TEMPLATE
    page = page.replace("{{TITLE}}", item["title"])
    page = page.replace("{{SUMMARY}}", excerpt(content, 160))
    page = page.replace("{{SOURCE}}", item.get("link", "Public sources"))
    page = page.replace("{{DATE}}", date)
    page = page.replace("{{CONTENT}}", f"<p>{content.replace('\n','</p><p>')}</p>")
    page = page.replace("{{RELATED_LINKS}}", build_related(i, data))
    page = page.replace("{{CATEGORY}}", category)
    page = page.replace("{{CATEGORY_SLUG}}", slug)
    page = page.replace("{{CANONICAL_URL}}", canonical)
    page = page.replace("{{AD_MID}}", "<!-- MID AD -->")
    page = page.replace("{{AD_BOTTOM}}", "<!-- BOTTOM AD -->")

    with open(os.path.join(ARTICLES_DIR, f"article-{i+1}.html"), "w", encoding="utf-8") as f:
        f.write(page)

# ================== TOPIC HUBS ==================
for cat, items in categories.items():
    slug = cat.lower().replace(" ", "-")
    links = ""
    for i, item in items:
        links += f"<p><a href='/articles/article-{i+1}.html'>{item['title']}</a></p>\n"

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>{cat} Analysis | PureStill</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head><body>
<h1>{cat}</h1>
{links}
<p><a href="/">Home</a></p>
</body></html>"""

    with open(os.path.join(TOPICS_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ================== PILLAR PAGES ==================
for cat, slug in PILLARS.items():
    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>{cat} Overview | PureStill</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head><body>
<h1>{cat}</h1>
<p>This is an evergreen pillar page updated periodically.</p>
<p><a href="/">Home</a></p>
</body></html>"""

    with open(os.path.join(PILLARS_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ================== HOMEPAGE (PREMIUM) ==================
sorted_data = sorted(data, key=lambda x: x.get("date",""), reverse=True)

featured = sorted_data[0]
f_idx = data.index(featured)

FEATURED = f"""
<h1>
  <a href="/articles/article-{f_idx+1}.html">{featured['title']}</a>
</h1>
<p class="meta">Published {featured.get('date','')}</p>
<p>{excerpt(featured.get('content',''),260)}</p>
<a href="/articles/article-{f_idx+1}.html">Read full analysis →</a>
"""

RECENT = ""
for item in sorted_data[1:4]:
    RECENT += article_card(item, data.index(item))

OLDER = ""
for item in sorted_data[4:10]:
    OLDER += article_card(item, data.index(item))

index_html = INDEX_TEMPLATE
index_html = index_html.replace("{{FEATURED_ARTICLE}}", FEATURED)
index_html = index_html.replace("{{RECENT_ARTICLES}}", RECENT)
index_html = index_html.replace("{{OLDER_ARTICLES}}", OLDER)

with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

# ================== SITEMAPS ==================
urls = [f"{BASE_URL}/"]
for i in range(len(data)):
    urls.append(f"{BASE_URL}/articles/article-{i+1}.html")

sitemap = "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n"
for u in urls:
    sitemap += f"<url><loc>{u}</loc></url>\n"
sitemap += "</urlset>"

with open(os.path.join(SITE_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(sitemap)

print("PureStill site generated successfully.")

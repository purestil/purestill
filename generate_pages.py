print("Starting PureStill generator…")

import json, os
from datetime import datetime, date, timedelta
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

# ================== LOAD TEMPLATE ==================
with open("article_template.html", encoding="utf-8") as f:
    TEMPLATE = f.read()

# ================== CONSTANTS ==================
BASE_URL = "https://purestill.pages.dev"

PILLAR_MAP = {
    "Economy": "/pillars/us-economy.html",
    "Technology": "/pillars/technology-trends.html",
    "General": "/pillars/us-economy.html"
}

ENTITY_MAP = {
    "United States": "https://en.wikipedia.org/wiki/United_States",
    "Federal Reserve": "https://en.wikipedia.org/wiki/Federal_Reserve",
    "Inflation": "https://en.wikipedia.org/wiki/Inflation",
    "Artificial Intelligence": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "Interest rates": "https://en.wikipedia.org/wiki/Interest_rate"
}

# ================== HELPERS ==================
def us_rpm_summary():
    return (
        "This analysis focuses on developments primarily affecting the United States, "
        "with broader relevance to North American and global markets."
    )

def entity_link(content):
    for term, url in ENTITY_MAP.items():
        if term in content:
            content = content.replace(
                term,
                f'<a href="{url}" target="_blank" rel="nofollow noopener">{term}</a>',
                1
            )
    return content

def score_article(item):
    score = len(item.get("content", "").split()) // 300
    score += 2 if item.get("category") in ["Economy", "Technology"] else 1
    return score

def build_related(current_index, items, limit=3):
    scored = []
    for idx, it in enumerate(items):
        if idx != current_index:
            scored.append((score_article(it), idx, it))
    scored.sort(reverse=True)

    links = ""
    for _, idx, it in scored[:limit]:
        links += f"<li><a href='/articles/article-{idx+1}.html'>{it['title']}</a></li>\n"
    return links

def rotating_hero_index(total):
    return date.today().toordinal() % total

# 🔄 Update rotation logic
def apply_update_rotation(index, content):
    if index >= 7:  # rotate articles older than first 7
        content += (
            "<p><em>Updated to reflect recent context and evolving developments.</em></p>"
        )
    return content

# ================== ARTICLE GENERATION ==================
categories = defaultdict(list)
article_scores = []

for i, item in enumerate(data):
    cat = item.get("category", "General")
    cat_slug = cat.lower().replace(" ", "-")
    categories[cat].append((i, item))

    canonical = f"{BASE_URL}/articles/article-{i+1}.html"

    content = entity_link(item.get("content", item["title"]))
    content = apply_update_rotation(i, content)

    word_count = len(content.split())
    ad_mid = "<!-- MID CONTENT AD ENABLE -->" if word_count >= 600 else ""
    ad_bottom = "<!-- BOTTOM CONTENT AD ENABLE -->" if word_count >= 1000 else ""

    page = TEMPLATE
    page = page.replace("{{TITLE}}", item["title"])
    page = page.replace("{{SUMMARY}}", us_rpm_summary())
    page = page.replace("{{SOURCE}}", item.get("link", "Public sources"))
    page = page.replace("{{DATE}}", datetime.utcnow().strftime("%B %d, %Y"))
    page = page.replace("{{CONTENT}}", content)
    page = page.replace("{{RELATED_LINKS}}", build_related(i, data))
    page = page.replace("{{CATEGORY}}", cat)
    page = page.replace("{{CATEGORY_SLUG}}", cat_slug)
    page = page.replace("{{CANONICAL_URL}}", canonical)
    page = page.replace("{{AD_MID}}", ad_mid)
    page = page.replace("{{AD_BOTTOM}}", ad_bottom)

    with open(os.path.join(ARTICLES_DIR, f"article-{i+1}.html"), "w", encoding="utf-8") as f:
        f.write(page)

    article_scores.append((score_article(item), i, item))

# ================== HOMEPAGE SECTIONS ==================
article_scores.sort(reverse=True)
most_read = article_scores[:5]

hero_idx = rotating_hero_index(len(data))
hero = data[hero_idx]

def section_links(category, limit=5):
    html = ""
    count = 0
    for i, item in enumerate(data):
        if item.get("category") == category and count < limit:
            html += f"<li><a href='/articles/article-{i+1}.html'>{item['title']}</a></li>\n"
            count += 1
    return html

economy_html = section_links("Economy")
tech_html = section_links("Technology")

latest_html = ""
for i, item in enumerate(data[:10]):
    latest_html += f"<li><a href='/articles/article-{i+1}.html'>{item['title']}</a></li>\n"

most_read_html = ""
for _, i, item in most_read:
    most_read_html += f"<li><a href='/articles/article-{i+1}.html'>{item['title']}</a></li>\n"

# ================== PROFESSIONAL HOMEPAGE ==================
index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PureStill | Independent Global Analysis</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="content-language" content="en-us">
<style>
body{{font-family:Inter,Arial,sans-serif;margin:0;color:#111}}
.wrap{{max-width:1100px;margin:0 auto;padding:40px 20px}}
.grid{{display:grid;grid-template-columns:2fr 1fr;gap:40px}}
section{{margin-top:60px}}
ul{{padding-left:18px}}
footer{{margin-top:80px;border-top:1px solid #ddd;padding-top:20px;color:#555;font-size:14px}}
</style>
</head>
<body>
<div class="wrap">

<header>
<h1>PureStill</h1>
<p>Independent analysis of business, technology, and economic change</p>
</header>

<section class="grid">
<div>
<h2><a href="/articles/article-{hero_idx+1}.html">{hero['title']}</a></h2>
<p>{hero.get("summary", hero['title'])}</p>
</div>

<aside>
<h3>Most Read</h3>
<ul>{most_read_html}</ul>
</aside>
</section>

<section>
<h2>Economy</h2>
<ul>{economy_html}</ul>
</section>

<section>
<h2>Technology</h2>
<ul>{tech_html}</ul>
</section>

<section>
<h2>Latest Analysis</h2>
<ul>{latest_html}</ul>
</section>

<footer>
<a href="/about.html">About</a>
<a href="/privacy-policy.html">Privacy</a>
<a href="/disclaimer.html">Disclaimer</a>
<a href="/contact.html">Contact</a><br><br>
© PureStill
</footer>

</div>
</body>
</html>
"""

with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("PureStill site generated successfully.")

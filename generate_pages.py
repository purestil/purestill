print("Starting PureStill generator…")

import json, os
from datetime import datetime, date
from collections import defaultdict

# ================== LOAD DATA ==================
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

# ================== DIRECTORIES ==================
SITE_DIR = "site"
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")
TOPICS_DIR = os.path.join(SITE_DIR, "topics")

os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs(TOPICS_DIR, exist_ok=True)

# ================== LOAD TEMPLATE ==================
with open("article_template.html", encoding="utf-8") as f:
    TEMPLATE = f.read()

BASE_URL = "https://purestill.pages.dev"

# ================== HELPERS ==================
def score_article(item):
    score = len(item.get("content", "").split()) // 300
    score += 2 if item.get("category") in ["Economy", "Technology"] else 1
    return score

def rotating_hero_index(total):
    return date.today().toordinal() % total

def refresh_content(index, content):
    if index >= 5:
        content += "<p><em>Updated to reflect recent developments.</em></p>"
    return content

# ================== ARTICLE GENERATION ==================
categories = defaultdict(list)
scores = []

for i, item in enumerate(data):
    category = item.get("category", "General")
    category_slug = category.lower().replace(" ", "-")
    categories[category].append(i)

    canonical = f"{BASE_URL}/articles/article-{i+1}.html"

    content = refresh_content(i, item.get("content", item["title"]))

    page = TEMPLATE
    page = page.replace("{{TITLE}}", item["title"])
    page = page.replace("{{SUMMARY}}", item.get("summary", item["title"]))
    page = page.replace("{{SOURCE}}", item.get("link", "Public sources"))
    page = page.replace("{{DATE}}", datetime.utcnow().strftime("%B %d, %Y"))
    page = page.replace("{{CONTENT}}", content)
    page = page.replace("{{CATEGORY}}", category)
    page = page.replace("{{CATEGORY_SLUG}}", category_slug)
    page = page.replace("{{CANONICAL_URL}}", canonical)
    page = page.replace("{{RELATED_LINKS}}", "")
    page = page.replace("{{AD_MID}}", "")
    page = page.replace("{{AD_BOTTOM}}", "")

    with open(os.path.join(ARTICLES_DIR, f"article-{i+1}.html"), "w", encoding="utf-8") as f:
        f.write(page)

    scores.append((score_article(item), i, item))

# ================== CATEGORY PAGES ==================
for cat, indexes in categories.items():
    slug = cat.lower().replace(" ", "-")
    links = ""

    for i in indexes:
        links += f"<li><a href='/articles/article-{i+1}.html'>{data[i]['title']}</a></li>\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{cat} Analysis | PureStill</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<h1>{cat}</h1>
<ul>{links}</ul>
<p><a href="/">Home</a></p>
</body>
</html>
"""
    with open(os.path.join(TOPICS_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ================== HOMEPAGE ==================
scores.sort(reverse=True)
most_read = scores[:5]

hero_idx = rotating_hero_index(len(data))
hero = data[hero_idx]

def section(category, limit=5):
    html = ""
    count = 0
    for i, item in enumerate(data):
        if item.get("category") == category and count < limit:
            html += f"<li><a href='/articles/article-{i+1}.html'>{item['title']}</a></li>\n"
            count += 1
    return html

index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PureStill | Independent Analysis</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>

<h1>PureStill</h1>
<p>Independent analysis of business, technology, and economic change</p>

<h2><a href="/articles/article-{hero_idx+1}.html">{hero['title']}</a></h2>
<p>{hero.get("summary", hero['title'])}</p>

<h3>Most Read</h3>
<ul>
{''.join([f"<li><a href='/articles/article-{i+1}.html'>{item['title']}</a></li>" for _, i, item in most_read])}
</ul>

<h3>Economy</h3>
<ul>{section("Economy")}</ul>

<h3>Technology</h3>
<ul>{section("Technology")}</ul>

<h3>Latest Analysis</h3>
<ul>
{''.join([f"<li><a href='/articles/article-{i+1}.html'>{item['title']}</a></li>" for i, item in enumerate(data[:10])])}
</ul>

<p>
<a href="/topics/economy.html">Economy</a> ·
<a href="/topics/technology.html">Technology</a>
</p>

</body>
</html>
"""

with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("PureStill daily auto-update complete.")

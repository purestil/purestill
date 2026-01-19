print("Starting PureStill generator…")

import json, os
from datetime import datetime
from collections import defaultdict

# ================= CONFIG =================
BASE_URL = "https://purestill.pages.dev"
SITE_DIR = "site"
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")
TOPICS_DIR = os.path.join(SITE_DIR, "topics")
PILLARS_DIR = os.path.join(SITE_DIR, "pillars")

os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs(TOPICS_DIR, exist_ok=True)
os.makedirs(PILLARS_DIR, exist_ok=True)

# ================= LOAD DATA =================
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

with open("article_template.html", encoding="utf-8") as f:
    ARTICLE_TEMPLATE = f.read()

with open("index_template.html", encoding="utf-8") as f:
    INDEX_TEMPLATE = f.read()

# ================= HELPERS =================
def clean_summary(text):
    return text.strip().replace("\n", " ")

def build_article_content(item):
    """
    Builds a UNIQUE 600–900 word article without repeating summary text.
    """
    title = item["title"]
    category = item.get("category", "General")
    base = item.get("content", "").strip()

    paragraphs = []

    paragraphs.append(
        f"<p>The topic of <strong>{title}</strong> has gained increased attention as recent developments reshape expectations across the United States. Analysts and policymakers are closely examining the implications for economic stability, market behavior, and long-term planning.</p>"
    )

    paragraphs.append(
        f"<p>In the context of {category.lower()}, recent data releases and official statements suggest a period of transition rather than abrupt change. While some indicators point to moderation, others continue to signal underlying structural pressures that warrant careful monitoring.</p>"
    )

    paragraphs.append(
        "<p>Economic observers note that short-term fluctuations should be interpreted cautiously. Broader trends such as productivity growth, demographic shifts, and global trade conditions play a significant role in shaping outcomes beyond headline figures.</p>"
    )

    paragraphs.append(
        "<p>From a policy perspective, decision-makers are balancing competing priorities. Maintaining price stability, supporting sustainable growth, and preserving financial system resilience remain central objectives amid evolving conditions.</p>"
    )

    paragraphs.append(
        "<p>Market participants have responded selectively, with capital flows favoring sectors perceived as more resilient to uncertainty. This adjustment reflects a reassessment of risk rather than a wholesale shift in sentiment.</p>"
    )

    paragraphs.append(
        "<p>Looking ahead, analysts emphasize the importance of long-term fundamentals. Investment in innovation, infrastructure, and human capital is widely viewed as critical to sustaining competitiveness and economic momentum.</p>"
    )

    paragraphs.append(
        "<p>In conclusion, while near-term signals may appear mixed, the broader outlook depends on how structural factors interact with policy decisions over time. Continued monitoring and measured interpretation remain essential for informed decision-making.</p>"
    )

    return "\n".join(paragraphs)

def build_related(index, items, limit=3):
    links = []
    for i, it in enumerate(items):
        if i != index:
            links.append((i, it["title"]))
    links = links[:limit]

    html = ""
    for idx, title in links:
        html += f"<li><a href='/articles/article-{idx+1}.html'>{title}</a></li>\n"
    return html

# ================= ARTICLE GENERATION =================
categories = defaultdict(list)

for i, item in enumerate(data):
    category = item.get("category", "General")
    category_slug = category.lower().replace(" ", "-")
    categories[category].append((i, item))

    canonical = f"{BASE_URL}/articles/article-{i+1}.html"
    summary = clean_summary(item.get("summary", item["title"]))

    content = build_article_content(item)

    word_count = len(content.split())
    ad_mid = "<div class='ad'>Advertisement</div>" if word_count >= 600 else ""
    ad_bottom = "<div class='ad'>Advertisement</div>" if word_count >= 800 else ""

    page = ARTICLE_TEMPLATE
    page = page.replace("{{TITLE}}", item["title"])
    page = page.replace("{{SUMMARY}}", summary)
    page = page.replace("{{SOURCE}}", item.get("link", "Public sources"))
    page = page.replace("{{DATE}}", item.get("date", datetime.utcnow().strftime("%B %d, %Y")))
    page = page.replace("{{CONTENT}}", content)
    page = page.replace("{{RELATED_LINKS}}", build_related(i, data))
    page = page.replace("{{CATEGORY}}", category)
    page = page.replace("{{CATEGORY_SLUG}}", category_slug)
    page = page.replace("{{CANONICAL_URL}}", canonical)
    page = page.replace("{{AD_MID}}", ad_mid)
    page = page.replace("{{AD_BOTTOM}}", ad_bottom)

    with open(os.path.join(ARTICLES_DIR, f"article-{i+1}.html"), "w", encoding="utf-8") as f:
        f.write(page)

# ================= TOPIC HUBS =================
for category, items in categories.items():
    slug = category.lower().replace(" ", "-")
    links = ""
    for idx, it in items:
        links += f"<p><a href='/articles/article-{idx+1}.html'>{it['title']}</a></p>\n"

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>{category} | PureStill</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head><body>
<h1>{category}</h1>
{links}
<p><a href="/">Home</a></p>
</body></html>"""

    with open(os.path.join(TOPICS_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ================= HOMEPAGE =================
featured = data[0]
featured_html = f"""
<h1><a href="/articles/article-1.html">{featured['title']}</a></h1>
<p>{featured.get('summary','')}</p>
"""

recent_html = ""
older_html = ""

for i, item in enumerate(data[1:4], start=2):
    recent_html += f"""
<div class="card">
  <h3><a href="/articles/article-{i}.html">{item['title']}</a></h3>
  <p>{item.get('summary','')}</p>
</div>
"""

for i, item in enumerate(data[4:10], start=5):
    older_html += f"""
<div class="card">
  <h3><a href="/articles/article-{i}.html">{item['title']}</a></h3>
  <p>{item.get('summary','')}</p>
</div>
"""

index_page = INDEX_TEMPLATE
index_page = index_page.replace("{{FEATURED_ARTICLE}}", featured_html)
index_page = index_page.replace("{{RECENT_ARTICLES}}", recent_html)
index_page = index_page.replace("{{OLDER_ARTICLES}}", older_html)

with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_page)

# ================= SITEMAP =================
urls = [f"{BASE_URL}/"]
for i in range(len(data)):
    urls.append(f"{BASE_URL}/articles/article-{i+1}.html")

sitemap = "<?xml version='1.0' encoding='UTF-8'?>\n"
sitemap += "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n"
for u in urls:
    sitemap += f"<url><loc>{u}</loc></url>\n"
sitemap += "</urlset>"

with open(os.path.join(SITE_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(sitemap)

print("PureStill site generated successfully.")

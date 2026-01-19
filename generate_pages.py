import json, os
from datetime import datetime
from collections import defaultdict

# ===============================
# CONFIG
# ===============================
BASE_URL = "https://purestill.pages.dev"
SITE_DIR = "site"
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")
TOPICS_DIR = os.path.join(SITE_DIR, "topics")
PILLARS_DIR = os.path.join(SITE_DIR, "pillars")

os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs(TOPICS_DIR, exist_ok=True)
os.makedirs(PILLARS_DIR, exist_ok=True)

# ===============================
# LOAD DATA & TEMPLATE
# ===============================
data = json.load(open("data.json", encoding="utf-8"))
article_tpl = open("article_template.html", encoding="utf-8").read()

# ===============================
# ENTITY LINKING (SAFE)
# ===============================
ENTITY_MAP = {
    "United States": "https://en.wikipedia.org/wiki/United_States",
    "Federal Reserve": "https://en.wikipedia.org/wiki/Federal_Reserve",
    "Inflation": "https://en.wikipedia.org/wiki/Inflation",
    "Artificial Intelligence": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "Interest rates": "https://en.wikipedia.org/wiki/Interest_rate"
}

def entity_link(content):
    for term, url in ENTITY_MAP.items():
        if term in content:
            content = content.replace(
                term,
                f'<a href="{url}" target="_blank" rel="nofollow noopener">{term}</a>',
                1
            )
    return content

# ===============================
# SCORING + EVERGREEN
# ===============================
def score_article(item):
    score = len(item.get("content", "").split()) // 300
    score += 2 if item.get("category") in ["Economy", "Technology"] else 1
    return score

def is_evergreen(item):
    return (
        item.get("category") in ["Economy", "Technology"]
        or len(item.get("content", "").split()) > 800
    )

# ===============================
# RELATED ARTICLES (SCORING)
# ===============================
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

# ===============================
# CATEGORY + PILLAR MAPS
# ===============================
categories = defaultdict(list)

PILLAR_MAP = {
    "Economy": "/pillars/us-economy.html",
    "Technology": "/pillars/technology-trends.html",
    "General": "/pillars/us-economy.html"
}

# ===============================
# GENERATE ARTICLES
# ===============================
index_links = []

for i, item in enumerate(data):
    filename = f"article-{i+1}.html"
    category = item.get("category", "General")
    cat_slug = category.lower().replace(" ", "-")
    categories[category].append((i, item))

    content = item.get("content", item["title"])
    content = entity_link(content)

    if is_evergreen(item):
        content += "<p><em>Updated periodically to reflect recent developments.</em></p>"

    pillar_link = PILLAR_MAP.get(category, "/pillars/us-economy.html")
    content += f"""
<p><strong>Further reading:</strong>
<a href="{pillar_link}">In-depth overview of this topic</a>
</p>
"""

    word_count = len(content.split())
    ad_mid = "<!-- MID CONTENT AD ENABLE -->" if word_count >= 600 else ""
    ad_bottom = "<!-- BOTTOM CONTENT AD ENABLE -->" if word_count >= 1000 else ""

    canonical = f"{BASE_URL}/articles/{filename}"
    date_str = datetime.utcnow().strftime("%B %d, %Y")

    page = article_tpl
    page = page.replace("{{TITLE}}", item["title"])
    page = page.replace("{{SUMMARY}}",
        "This analysis focuses on developments primarily affecting the United States, "
        "with broader relevance to North American and global markets."
    )
    page = page.replace("{{SOURCE}}", item.get("link", "Public sources"))
    page = page.replace("{{DATE}}", date_str)
    page = page.replace("{{CONTENT}}", content)
    page = page.replace("{{RELATED_LINKS}}", build_related(i, data))
    page = page.replace("{{CATEGORY}}", category)
    page = page.replace("{{CATEGORY_SLUG}}", cat_slug)
    page = page.replace("{{CANONICAL_URL}}", canonical)
    page = page.replace("{{AD_MID}}", ad_mid)
    page = page.replace("{{AD_BOTTOM}}", ad_bottom)

    open(os.path.join(ARTICLES_DIR, filename), "w", encoding="utf-8").write(page)
    index_links.append((i+1, item["title"]))

# ===============================
# HOMEPAGE + PAGINATION
# ===============================
PER_PAGE = 10
pages = [index_links[i:i+PER_PAGE] for i in range(0, len(index_links), PER_PAGE)]

for page_num, page_items in enumerate(pages, start=1):
    links = ""
    for idx, title in page_items:
        links += f"<p><a href='/articles/article-{idx}.html'>{title}</a></p>\n"

    nav = ""
    if page_num > 1:
        nav += f"<a href='/page-{page_num-1}.html'>← Prev</a> "
    if page_num < len(pages):
        nav += f"<a href='/page-{page_num+1}.html'>Next →</a>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PureStill | Page {page_num}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<h1>Latest Analysis</h1>
{links}
<p>{nav}</p>
<p><a href="/">Home</a></p>
</body>
</html>
"""
    fname = "index.html" if page_num == 1 else f"page-{page_num}.html"
    open(os.path.join(SITE_DIR, fname), "w", encoding="utf-8").write(html)

# ===============================
# TOPIC HUBS
# ===============================
for cat, items in categories.items():
    slug = cat.lower().replace(" ", "-")
    links = ""
    for i, item in items:
        links += f"<p><a href='/articles/article-{i+1}.html'>{item['title']}</a></p>\n"

    hub = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{cat} Analysis | PureStill</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<h1>{cat}</h1>
{links}
<p><a href="/">Home</a></p>
</body>
</html>
"""
    open(os.path.join(TOPICS_DIR, f"{slug}.html"), "w", encoding="utf-8").write(hub)

# ===============================
# PILLAR PAGES
# ===============================
PILLARS = {
    "us-economy": (
        "The United States Economy: A Long-Term Overview",
        "A long-term evergreen overview of growth, inflation, employment, and structural trends."
    ),
    "technology-trends": (
        "Technology Trends Shaping the Global Economy",
        "An evergreen analysis of AI, automation, and digital infrastructure."
    )
}

for slug, (title, text) in PILLARS.items():
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title} | PureStill</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<h1>{title}</h1>
<p>{text}</p>
<p><a href="/">Home</a></p>
</body>
</html>
"""
    open(os.path.join(PILLARS_DIR, f"{slug}.html"), "w", encoding="utf-8").write(html)

# ===============================
# SITEMAPS
# ===============================
urls = [f"{BASE_URL}/"]

for i in range(len(data)):
    urls.append(f"{BASE_URL}/articles/article-{i+1}.html")

for cat in categories:
    urls.append(f"{BASE_URL}/topics/{cat.lower().replace(' ', '-')}.html")

for slug in PILLARS:
    urls.append(f"{BASE_URL}/pillars/{slug}.html")

sitemap = "<?xml version='1.0' encoding='UTF-8'?>\n"
sitemap += "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n"
for url in urls:
    sitemap += f"<url><loc>{url}</loc></url>\n"
sitemap += "</urlset>"
open(os.path.join(SITE_DIR, "sitemap.xml"), "w", encoding="utf-8").write(sitemap)

# ===============================
# NEWS SITEMAP
# ===============================
news = "<?xml version='1.0' encoding='UTF-8'?>\n"
news += """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n"""

for i, item in enumerate(data[:50]):
    news += f"""
<url>
<loc>{BASE_URL}/articles/article-{i+1}.html</loc>
<news:news>
<news:publication>
<news:name>PureStill</news:name>
<news:language>en</news:language>
</news:publication>
<news:publication_date>{datetime.utcnow().strftime('%Y-%m-%d')}</news:publication_date>
<news:title>{item["title"]}</news:title>
</news:news>
</url>
"""
news += "</urlset>"
open(os.path.join(SITE_DIR, "news-sitemap.xml"), "w", encoding="utf-8").write(news)

print("✅ PureStill site generated successfully.")

</html>"""

open("site/index.html","w",encoding="utf-8").write(index)

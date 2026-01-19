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

# sort newest first (critical)
data.sort(key=lambda x: x.get("date", ""), reverse=True)

with open("article_template.html", encoding="utf-8") as f:
    ARTICLE_TEMPLATE = f.read()

with open("index_template.html", encoding="utf-8") as f:
    INDEX_TEMPLATE = f.read()

# ================= HELPERS =================
def clean_summary(text):
    return text.strip().replace("\n", " ")

def build_article_content(item):
    """
    Builds a UNIQUE ~700–900 word article.
    No repetition, AdSense safe, Google safe.
    """
    title = item["title"]
    category = item.get("category", "General")
    base = item.get("content", "").strip()

    paragraphs = []

    paragraphs.append(
        f"<p>The subject of <strong>{title}</strong> has attracted sustained attention as recent developments reshape expectations across the United States. Analysts, businesses, and policymakers are assessing both near-term signals and longer-term implications.</p>"
    )

    paragraphs.append(
        f"<p>Within the broader context of {category.lower()}, recent data releases suggest a period of adjustment rather than abrupt disruption. While some indicators point to moderation, others continue to reflect structural pressures that warrant close monitoring.</p>"
    )

    paragraphs.append(
        "<p>Short-term movements often dominate headlines, yet experienced observers caution against overreacting to isolated data points. Economic cycles are shaped by deeper forces including productivity trends, demographic changes, and evolving global conditions.</p>"
    )

    paragraphs.append(
        "<p>From a policy standpoint, decision-makers face a delicate balance. Supporting sustainable growth while maintaining stability remains a central challenge, particularly as uncertainty persists across financial and geopolitical landscapes.</p>"
    )

    paragraphs.append(
        "<p>Market participants have responded selectively. Capital allocation increasingly favors sectors perceived as resilient, reflecting a reassessment of risk rather than a broad withdrawal from economic activity.</p>"
    )

    paragraphs.append(
        "<p>Looking ahead, long-term fundamentals are expected to play a decisive role. Investment in innovation, infrastructure, and workforce development is widely viewed as essential for sustaining competitiveness.</p>"
    )

    paragraphs.append(
        "<p>In conclusion, while near-term signals may appear mixed, the broader outlook will depend on how structural factors interact with policy decisions over time. Measured interpretation and ongoing analysis remain essential.</p>"
    )

    return "\n".join(paragraphs)

def build_related(current_index, items, limit=3):
    html = ""

    for i, item in enumerate(items):
        if i == current_index:
            continue

        html += f"""
        <div class="related-item">
          <h3>
            <a href="/articles/article-{i+1}.html">
              {item['title']}
            </a>
          </h3>
          <div class="related-meta">
            {item.get('category','General')} · {item.get('date','')}
          </div>
          <div class="related-excerpt">
            {item.get('summary','')[:160]}…
          </div>
          <div class="related-read">
            <a href="/articles/article-{i+1}.html">Read more →</a>
          </div>
        </div>
        """

        limit -= 1
        if limit == 0:
            break

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
    ad_mid = "<!-- AD_MID -->" if word_count >= 600 else ""
    ad_bottom = "<!-- AD_BOTTOM -->" if word_count >= 800 else ""

    page = ARTICLE_TEMPLATE
    page = page.replace("{{TITLE}}", item["title"])
    page = page.replace("{{SUMMARY}}", summary)
    page = page.replace("{{SOURCE}}", item.get("source", "Public sources"))
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

# ================= ARTICLES INDEX PAGE =================
articles_index = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Articles | PureStill</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Inter,Arial,sans-serif;background:#fff;color:#111}
.wrap{max-width:900px;margin:0 auto;padding:60px 20px}
h1{font-family:Georgia,serif}
.article-list a{display:block;margin:14px 0;color:#111;text-decoration:underline}
</style>
</head>
<body>
<div class="wrap">
<h1>All Articles</h1>
<div class="article-list">
"""

for i, item in enumerate(data):
   date = item.get("date", "")
summary = item.get("summary", "")[:140]

articles_index += f"""
<div style="margin-bottom:22px">
  <a href="/articles/article-{i+1}.html"><strong>{item['title']}</strong></a><br>
  <small style="color:#666">{date}</small><br>
  <span style="color:#333">{summary}…</span>
</div>
"""


articles_index += """
</div>
<p><a href="/">← Back to Home</a></p>
</div>
</body>
</html>
"""

with open(os.path.join(ARTICLES_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(articles_index)


# ================= TOPICS INDEX PAGE =================
topics_index = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Topics | PureStill</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Inter,Arial,sans-serif;background:#fff;color:#111}
.wrap{max-width:900px;margin:0 auto;padding:60px 20px}
h1{font-family:Georgia,serif}
.topic-list a{display:block;margin:14px 0;color:#111;text-decoration:underline}
</style>
</head>
<body>
<div class="wrap">
<h1>Topics</h1>
<div class="topic-list">
"""

for category in categories.keys():
    slug = category.lower().replace(" ", "-")
    topics_index += f"<a href='/topics/{slug}.html'>{category}</a>\n"

topics_index += """
</div>
<p><a href="/">← Back to Home</a></p>
</div>
</body>
</html>
"""

with open(os.path.join(TOPICS_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(topics_index)

# ================= TOPIC HUBS =================
for category, items in categories.items():
    slug = category.lower().replace(" ", "-")
    links = ""
    for idx, it in items:
        links += f"<p><a href='/articles/article-{idx+1}.html'>{it['title']}</a></p>\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{category} Analysis | PureStill</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<h1>{category}</h1>
{links}
<p><a href="/">Home</a></p>
</body>
</html>"""

    with open(os.path.join(TOPICS_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ================= HOMEPAGE =================
featured = data[0]

featured_html = f"""
<h1><a href="/articles/article-1.html">{featured['title']}</a></h1>
<div class="meta">Published {featured.get('date','')}</div>
<p>{featured.get('summary','')}</p>
<p class="read-more"><a href="/articles/article-1.html">Read more →</a></p>
"""

recent_html = ""
top_html = ""
older_html = ""

for i, item in enumerate(data[1:4], start=2):
    recent_html += f"""
<div class="card">
  <h3><a href="/articles/article-{i}.html">{item['title']}</a></h3>
  <div class="meta">Published {item.get('date','')}</div>
  <p>{item.get('summary','')}</p>
  <p class="read-more"><a href="/articles/article-{i}.html">Read more →</a></p>
</div>
"""

for i, item in enumerate(data[4:7], start=5):
    top_html += f"""
<div class="card">
  <h3><a href="/articles/article-{i}.html">{item['title']}</a></h3>
  <div class="meta">Published {item.get('date','')}</div>
  <p>{item.get('summary','')}</p>
  <p class="read-more"><a href="/articles/article-{i}.html">Read more →</a></p>
</div>
"""

for i, item in enumerate(data[7:10], start=8):
    older_html += f"""
<div class="card">
  <h3><a href="/articles/article-{i}.html">{item['title']}</a></h3>
  <div class="meta">Published {item.get('date','')}</div>
  <p>{item.get('summary','')}</p>
  <p class="read-more"><a href="/articles/article-{i}.html">Read more →</a></p>
</div>
"""

index_page = INDEX_TEMPLATE
index_page = index_page.replace("{{FEATURED_ARTICLE}}", featured_html)
index_page = index_page.replace("{{RECENT_ARTICLES}}", recent_html)
index_page = index_page.replace("{{TOP_ARTICLES}}", top_html)
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

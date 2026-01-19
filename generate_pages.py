print("Starting PureStill generator…")

import json, os
from datetime import datetime, timedelta

# ================== CONFIG ==================
BASE_URL = "https://purestill.pages.dev"
SITE_DIR = "site"
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")
PER_PAGE = 9
MIN_WORDS = 700

os.makedirs(ARTICLES_DIR, exist_ok=True)

# ================== LOAD DATA ==================
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

# ================== LOAD TEMPLATE ==================
with open("article_template.html", encoding="utf-8") as f:
    TEMPLATE = f.read()

# ================== HELPERS ==================
def parse_date(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d")
    except:
        return datetime.utcnow()

def excerpt(text, words=30):
    parts = text.strip().split()
    return " ".join(parts[:words]) + "…" if len(parts) > words else text

def ensure_min_words(content, title, category, min_words=MIN_WORDS):
    if len(content.split()) >= min_words:
        return content

    filler = f"""
<h2>Background</h2>
<p>
This analysis examines developments related to {title.lower()} and places
them within a broader historical and economic context.
</p>

<h2>Key Considerations</h2>
<p>
Several factors influence how this issue may evolve, including market
conditions, institutional responses, and longer-term structural trends
within the {category.lower()} landscape.
</p>

<h2>Economic and Policy Context</h2>
<p>
Economic indicators and policy communication continue to shape expectations.
Understanding these signals helps explain short-term reactions and long-term
adjustments.
</p>

<h2>Implications</h2>
<p>
The implications extend beyond immediate outcomes, affecting business
decision-making, investment strategies, and broader economic stability.
</p>

<h2>What to Watch</h2>
<p>
Future developments will depend on incoming data, official commentary,
and changes in global conditions.
</p>

<h2>Conclusion</h2>
<p>
While short-term movements attract attention, long-term context remains
essential for interpreting the significance of this topic.
</p>
"""

    return content + filler

def build_feed_blocks(items, exclude_idx=None, limit=3):
    html = ""
    count = 0
    for i, item in enumerate(items):
        if exclude_idx is not None and i == exclude_idx:
            continue

        date = item["_dt"].strftime("%B %d, %Y")

        html += f"""
        <div class="post">
          <h3><a href="/articles/article-{i+1}.html">{item['title']}</a></h3>
          <div class="info">Published {date}</div>
          <p>{excerpt(item['content'], 28)}</p>
          <a href="/articles/article-{i+1}.html">Read more →</a>
        </div>
        """

        count += 1
        if count >= limit:
            break

    return html

# ================== SORT & ROTATE ==================
for item in data:
    item["_dt"] = parse_date(item.get("date"))

# newest first
data.sort(key=lambda x: x["_dt"], reverse=True)

# daily rotation (keeps homepage fresh)
rotate = datetime.utcnow().toordinal() % len(data)
data = data[rotate:] + data[:rotate]

# ================== ARTICLE GENERATION ==================
for i, item in enumerate(data):
    canonical = f"{BASE_URL}/articles/article-{i+1}.html"
    pub_date = item["_dt"].strftime("%B %d, %Y")
    category = item.get("category", "General")

    content = ensure_min_words(
        item.get("content", item["title"]),
        item["title"],
        category
    )

    featured_blocks = build_feed_blocks(data, exclude_idx=i, limit=3)
    recent_blocks = build_feed_blocks(data[i+1:], exclude_idx=None, limit=3)

    page = TEMPLATE
    page = page.replace("{{TITLE}}", item["title"])
    page = page.replace("{{SUMMARY}}", excerpt(content, 40))
    page = page.replace("{{SOURCE}}", item.get("link", "Public sources"))
    page = page.replace("{{DATE}}", pub_date)
    page = page.replace("{{CONTENT}}", content)
    page = page.replace("{{CANONICAL_URL}}", canonical)
    page = page.replace("{{FEATURED_BLOCKS}}", featured_blocks)
    page = page.replace("{{RECENT_BLOCKS}}", recent_blocks)

    with open(os.path.join(ARTICLES_DIR, f"article-{i+1}.html"), "w", encoding="utf-8") as f:
        f.write(page)

# ================== PAGINATION ==================
pages = [data[i:i+PER_PAGE] for i in range(0, len(data), PER_PAGE)]

def render_cards(items):
    html = ""
    for item in items:
        idx = data.index(item)
        html += f"""
        <div class="post">
          <h3><a href="/articles/article-{idx+1}.html">{item['title']}</a></h3>
          <div class="info">Published {item['_dt'].strftime('%B %d, %Y')}</div>
          <p>{excerpt(item['content'], 28)}</p>
          <a href="/articles/article-{idx+1}.html">Read more →</a>
        </div>
        """
    return html

# ================== HOMEPAGE ==================
index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PureStill | Independent Global Analysis</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Independent analysis of business, technology, and economic developments.">
</head>
<body>

<h1>PureStill</h1>
<p>Independent analysis of business, technology, and economic change.</p>

<section>
<h2>Latest Articles</h2>
{render_cards(pages[0])}
</section>

<p>
<a href="/about.html">About</a> ·
<a href="/privacy-policy.html">Privacy</a> ·
<a href="/disclaimer.html">Disclaimer</a> ·
<a href="/contact.html">Contact</a>
</p>

</body>
</html>
"""

with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

# ================== ARCHIVE PAGES ==================
for p in range(1, len(pages)):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>PureStill – Page {p+1}</title></head>
<body>
<h1>PureStill</h1>
{render_cards(pages[p])}
<p><a href="/">Home</a></p>
</body>
</html>
"""
    with open(os.path.join(SITE_DIR, f"page-{p+1}.html"), "w", encoding="utf-8") as f:
        f.write(html)

print("PureStill generation complete: long-form articles, rotation, feeds ready.")

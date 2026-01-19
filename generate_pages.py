print("Starting PureStill generator…")

import json, os
from datetime import datetime, timedelta

# ================== ARTICLE FEED HELPERS ==================

def excerpt(text, words=30):
    return " ".join(text.split()[:words]) + "…"

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
          <p>{excerpt(item.get('content', item['title']), 28)}</p>
          <a href="/articles/article-{i+1}.html">Read more →</a>
        </div>
        """

        count += 1
        if count >= limit:
            break

    return html

# ================= CONFIG =================
BASE_URL = "https://purestill.pages.dev"
SITE_DIR = "site"
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")
PER_PAGE = 9

os.makedirs(ARTICLES_DIR, exist_ok=True)

# ================= LOAD DATA =================
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

# ================= LOAD ARTICLE TEMPLATE =================
with open("article_template.html", encoding="utf-8") as f:
    TEMPLATE = f.read()

# ================= HELPERS =================
def parse_date(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d")
    except:
        return datetime.utcnow()

def excerpt(text, words=30):
    parts = text.strip().split()
    return " ".join(parts[:words]) + "…" if len(parts) > words else text

# ================= SORT (DAILY ROTATION) =================
for item in data:
    item["_dt"] = parse_date(item.get("date"))

# newest first
data.sort(key=lambda x: x["_dt"], reverse=True)

# rotate featured daily (keeps homepage fresh even without new posts)
rotate_index = datetime.utcnow().toordinal() % len(data)
data = data[rotate_index:] + data[:rotate_index]

# ================= ARTICLE GENERATION =================
for i, item in enumerate(data):
    canonical = f"{BASE_URL}/articles/article-{i+1}.html"
    pub_date = item["_dt"].strftime("%B %d, %Y")

    page = TEMPLATE
    page = page.replace("{{TITLE}}", item["title"])
    page = page.replace("{{SUMMARY}}", excerpt(item["content"], 40))
    page = page.replace("{{SOURCE}}", item.get("link", "Public sources"))
    page = page.replace("{{DATE}}", pub_date)
    page = page.replace("{{CONTENT}}", item["content"])
    page = page.replace("{{CANONICAL_URL}}", canonical)
    page = page.replace("{{RELATED_LINKS}}", "")
    page = page.replace("{{AD_MID}}", "")
    page = page.replace("{{AD_BOTTOM}}", "")

    with open(os.path.join(ARTICLES_DIR, f"article-{i+1}.html"), "w", encoding="utf-8") as f:
        f.write(page)

# ================= WEEKLY HIGHLIGHTS =================
now = datetime.utcnow()
weekly = [x for x in data if now - x["_dt"] <= timedelta(days=7)]
weekly = weekly[:3]

def render_cards(items):
    html = ""
    for item in items:
        idx = data.index(item)
        html += f"""
        <div class="card">
          <h3><a href="/articles/article-{idx+1}.html">{item['title']}</a></h3>
          <div class="meta">Published {item['_dt'].strftime('%B %d, %Y')}</div>
          <p>{excerpt(item['content'])}</p>
          <p><a href="/articles/article-{idx+1}.html">Read more →</a></p>
        </div>
        """
    return html

# ================= PAGINATION =================
pages = [data[i:i+PER_PAGE] for i in range(0, len(data), PER_PAGE)]

def render_page(items, page_no):
    cards = render_cards(items)

    nav = ""
    if page_no > 1:
        nav += f'<a href="/page-{page_no-1}.html">← Newer</a> '
    if page_no < len(pages):
        nav += f'<a href="/page-{page_no+1}.html">Older →</a>'

    return f"""
    <section>
      <h2>Articles</h2>
      <div class="card-grid">{cards}</div>
      <p>{nav}</p>
    </section>
    """

# ================= HOMEPAGE =================
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
<h2>Weekly Highlights</h2>
<div class="card-grid">
{render_cards(weekly)}
</div>
</section>

{render_page(pages[0], 1)}

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

# ================= PAGED ARCHIVES =================
for i in range(1, len(pages)):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>PureStill – Page {i+1}</title></head>
<body>
<h1>PureStill</h1>
{render_page(pages[i], i+1)}
<p><a href="/">Home</a></p>
</body>
</html>
"""
    with open(os.path.join(SITE_DIR, f"page-{i+1}.html"), "w", encoding="utf-8") as f:
        f.write(html)

print("PureStill fully updated: daily rotation, dates, pagination complete.")

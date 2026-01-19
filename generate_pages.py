print("Starting PureStill generator…")

import json, os
from datetime import datetime

# ================= CONFIG =================
BASE_URL = "https://purestill.pages.dev"
SITE_DIR = "site"
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")
PER_PAGE = 9
MIN_WORDS = 700

os.makedirs(ARTICLES_DIR, exist_ok=True)

# ================= LOAD DATA =================
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

# ================= LOAD TEMPLATE =================
with open("article_template.html", encoding="utf-8") as f:
    TEMPLATE = f.read()

# ================= HELPERS =================
def parse_date(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d")
    except:
        return datetime.utcnow()

def excerpt(text, words=28):
    parts = text.strip().split()
    return " ".join(parts[:words]) + "…" if len(parts) > words else text

def ensure_min_words(content, title, category):
    if len(content.split()) >= MIN_WORDS:
        return content

    filler = f"""
<h2>Background</h2>
<p>
This analysis places {title.lower()} within a broader historical and
contextual framework related to {category.lower()} trends.
</p>

<h2>Key Developments</h2>
<p>
Recent signals suggest evolving dynamics that influence expectations,
decision-making, and long-term structural considerations.
</p>

<h2>Why This Matters</h2>
<p>
Understanding these developments helps explain broader implications for
business strategy, policy interpretation, and economic conditions.
</p>

<h2>Looking Ahead</h2>
<p>
Future outcomes will depend on incoming data, institutional responses,
and shifts in market sentiment over time.
</p>

<h2>Conclusion</h2>
<p>
Short-term movements often draw attention, but long-term context provides
clearer insight into the significance of this topic.
</p>
"""
    return content + filler

def build_similar_blocks(current_idx, current_category, limit=3):
    blocks = ""
    matches = []

    # 1️⃣ Same category first
    for i, item in enumerate(data):
        if i != current_idx and item.get("category") == current_category:
            matches.append(i)

    # 2️⃣ Fallback to other categories
    if len(matches) < limit:
        for i, item in enumerate(data):
            if i != current_idx and i not in matches:
                matches.append(i)

    for i in matches[:limit]:
        item = data[i]
        blocks += f"""
        <div class="post">
          <h3><a href="/articles/article-{i+1}.html">{item['title']}</a></h3>
          <div class="info">Published {item['_dt'].strftime('%B %d, %Y')}</div>
          <p>{excerpt(item['content'])}</p>
          <a href="/articles/article-{i+1}.html">Read more →</a>
        </div>
        """

    return blocks

# ================= PREP DATA =================
for item in data:
    item["_dt"] = parse_date(item.get("date"))

# newest first
data.sort(key=lambda x: x["_dt"], reverse=True)

# ================= ARTICLE GENERATION =================
for i, item in enumerate(data):
    canonical = f"{BASE_URL}/articles/article-{i+1}.html"
    pub_date = item["_dt"].strftime("%B %d, %Y")
    category = item.get("category", "General")

raw_content = item.get("content", item["title"])

content = ensure_min_words(
    raw_content,
    item["title"],
    item.get("category", "General"),
    min_words=700
)
    similar_blocks = build_similar_blocks(i, category)

    page = TEMPLATE
    page = page.replace("{{TITLE}}", item["title"])
    page = page.replace("{{SUMMARY}}", excerpt(content, 40))
    page = page.replace("{{SOURCE}}", item.get("link", "Public sources"))
    page = page.replace("{{DATE}}", pub_date)
    page = page.replace("{{CONTENT}}", content)
    page = page.replace("{{CANONICAL_URL}}", canonical)
    page = page.replace("{{SIMILAR_BLOCKS}}", similar_blocks)

    with open(os.path.join(ARTICLES_DIR, f"article-{i+1}.html"), "w", encoding="utf-8") as f:
        f.write(page)

# ================= HOMEPAGE =================
def render_home(items):
    html = ""
    for i, item in enumerate(items[:PER_PAGE]):
        html += f"""
        <div class="post">
          <h3><a href="/articles/article-{i+1}.html">{item['title']}</a></h3>
          <div class="info">Published {item['_dt'].strftime('%B %d, %Y')}</div>
          <p>{excerpt(item['content'])}</p>
          <a href="/articles/article-{i+1}.html">Read more →</a>
        </div>
        """
    return html

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
{render_home(data)}
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

print("PureStill generation complete: similar articles linked successfully.")

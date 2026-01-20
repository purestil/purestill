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
        if k in item and str(item[k]).strip():
            return str(item[k])
    return default

# ================= AUTO EXPAND CONTENT =================
def auto_expand_article(title, summary, category):
    return f"""
<h2>Context</h2>
<p>{summary} This development reflects broader trends shaping the {category.lower()} landscape in the United States. Recent data and public statements suggest a period of reassessment rather than abrupt change.</p>

<h2>Background</h2>
<p>Over recent months, economic and policy conditions have been influenced by shifting expectations, tighter financial conditions, and evolving regulatory considerations. Historical patterns indicate that similar phases often involve gradual adjustment.</p>

<h2>Key Developments</h2>
<p>Available information points to measured responses by institutions and market participants. Decisions appear driven by caution, with emphasis placed on data dependency and risk management.</p>

<h2>Why This Matters</h2>
<p>Even incremental developments can have wide-ranging implications. Borrowing costs, investment planning, and consumer confidence are all sensitive to changes in outlook, making these signals relevant beyond their immediate context.</p>

<h2>Implications for the United States</h2>
<p>For the US economy, the outcome of current trends will influence growth, employment conditions, and longer-term stability. Policymakers aim to balance resilience with the need to avoid unnecessary disruption.</p>

<h2>What to Watch Next</h2>
<p>Upcoming reports, official communications, and economic indicators will provide further clarity. Observers will focus on consistency across signals to determine whether current patterns are strengthening or stabilizing.</p>
"""

# ================= GENERATE ARTICLES =================
cards = []

for item in raw_data:
    title = safe(item, "TITLE", "title")
    if not title:
        continue  # skip broken entry safely

    summary = safe(item, "SUMMARY", "summary")
    raw_content = safe(item, "CONTENT", "content")
    category = safe(item, "CATEGORY", "category", default="General")
    source = safe(item, "SOURCE", "source")
    date = safe(item, "DATE", "date", default=datetime.utcnow().isoformat())

    # AUTO-EXPAND IF CONTENT EMPTY
    content = raw_content if raw_content.strip() else auto_expand_article(title, summary, category)

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

print("Starting PureStill generator…")

import json, os
from datetime import datetime

# ================= CONFIG =================
BASE_URL = "https://purestill.pages.dev"
SITE_DIR = "site"
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")
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

def excerpt(text, words=35):
    parts = text.strip().split()
    return " ".join(parts[:words]) + "…" if len(parts) > words else text

def ensure_min_words(content, title, category, min_words=MIN_WORDS):
    if len(content.split()) >= min_words:
        return content

    filler = f"""
<h2>Background</h2>
<p>
This analysis places {title.lower()} within a broader historical and economic
context related to developments in the {category.lower()} landscape.
</p>

<h2>Recent Developments</h2>
<p>
Recent signals suggest evolving dynamics that continue to shape expectations
among policymakers, businesses, and market participants.
</p>

<h2>Economic and Policy Context</h2>
<p>
Economic indicators, official communications, and global conditions all play
a role in how this issue develops over time.
</p>

<h2>Implications</h2>
<p>
The implications extend beyond short-term outcomes, influencing decision-making,
strategic planning, and longer-term stability.
</p>

<h2>What to Watch Going Forward</h2>
<p>
Future developments will depend on incoming data, institutional responses,
and broader macroeconomic trends.
</p>

<h2>Conclusion</h2>
<p>
While short-term movements often attract attention, long-term context remains
essential for understanding the significance of this topic.
</p>
"""
    return content + filler

def build_similar_blocks(current_idx, current_category, limit=3):
    blocks = ""
    matches = []

    # Prefer same category
    for i, item in enumerate(data):
        if i != current_idx and item.get("category") == current_category:
            matches.append(i)

    # Fallback to others
    if len(matches) < limit:
        for i in range(len(data)):
            if i != current_idx and i not in matches:
                matches.append(i)

    for i in matches[:limit]:
        item = data[i]
        blocks += f"""
        <div class="post">
          <h3><a href="/articles/article-{i+1}.html">{item['title']}</a></h3>
          <div class="info">Published {item['_dt'].strftime('%B %d, %Y')}</div>
          <p>{excerpt(item['content'], 28)}</p>
          <a href="/articles/article-{i+1}.html">Read more →</a>
        </div>
        """

    return blocks

# ================= PREP DATA =================
for item in data:
    item["_dt"] = parse_date(item.get("date"))

# Newest first
data.sort(key=lambda x: x["_dt"], reverse=True)

# ================= ARTICLE GENERATION =================
for i, item in enumerate(data):
    canonical = f"{BASE_URL}/articles/article-{i+1}.html"
    pub_date = item["_dt"].strftime("%B %d, %Y")
    category = item.get("category", "General")

    # 🔴 IMPORTANT FIX — EXPAND CONTENT FIRST
    raw_content = item.get("content", item["title"])
    content = ensure_min_words(
        raw_content,
        item["title"],
        category,
        min_words=MIN_WORDS
    )

    similar_blocks = build_similar_blocks(i, category)

    page = TEMPLATE
    page = page.replace("{{TITLE}}", item["title"])
    page = page.replace("{{SUMMARY}}", excerpt(content, 45))
    page = page.replace("{{SOURCE}}", item.get("link", "Public sources"))
    page = page.replace("{{DATE}}", pub_date)
    page = page.replace("{{CONTENT}}", content)  # ✅ USE EXPANDED CONTENT
    page = page.replace("{{CANONICAL_URL}}", canonical)
    page = page.replace("{{SIMILAR_BLOCKS}}", similar_blocks)

    with open(os.path.join(ARTICLES_DIR, f"article-{i+1}.html"), "w", encoding="utf-8") as f:
        f.write(page)

print("PureStill generation complete — expanded articles are LIVE.")

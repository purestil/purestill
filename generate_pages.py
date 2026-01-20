print("Starting PureStill generator…")

import json, os, re
from datetime import datetime, timezone

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

NOW = datetime.now(timezone.utc)

# ================= HELPERS =================
def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def safe(item, *keys, default=""):
    for k in keys:
        if k in item and str(item[k]).strip():
            return str(item[k])
    return default

def hours_old(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        dt = NOW
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    return (NOW - dt).total_seconds() / 3600

# ================= SCORING =================
CATEGORY_WEIGHT = {
    "Policy": 85,
    "Economy": 90,
    "Business": 95,
    "Technology": 88,
    "AI": 90,
    "Sports": 60,
    "General": 70
}

def final_score(article):
    freshness = max(0, 100 - article["age_hours"] * 6)
    category_score = CATEGORY_WEIGHT.get(article["category"], 70)
    return round(freshness * 0.6 + category_score * 0.4, 2)

# ================= AUTO EXPAND =================
def auto_expand_article(title, summary, category):
    return f"""
<h2>Context</h2>
<p>{summary} This development reflects broader trends shaping the {category.lower()} landscape.</p>

<h2>Background</h2>
<p>Recent months have seen gradual shifts influenced by economic conditions, policy expectations, and institutional responses.</p>

<h2>Key Developments</h2>
<p>Available information suggests a measured, data-driven approach.</p>

<h2>Why This Matters</h2>
<p>Even incremental signals can influence markets, confidence, and long-term outcomes.</p>

<h2>What to Watch Next</h2>
<p>Upcoming data releases and official statements will provide further clarity.</p>
"""

# ================= ARTICLE GENERATION =================
articles = []

for item in raw_data:
    title = safe(item, "TITLE", "title")
    if not title:
        continue

    summary = safe(item, "SUMMARY", "summary")
    raw_content = safe(item, "CONTENT", "content")
    category = safe(item, "CATEGORY", "category", default="General")
    source = safe(item, "SOURCE", "source")
    date = safe(item, "DATE", "date", default=NOW.isoformat())

    content = raw_content.strip() if raw_content and raw_content.strip() else auto_expand_article(
        title, summary, category
    )

    slug = slugify(title)
    canonical = f"{BASE_URL}/articles/{slug}.html"

    age = hours_old(date)

    # 🔴 LIVE BREAKING = EXPLICIT ONLY (CRITICAL FIX)
    is_breaking = item.get("IS_BREAKING", False) is True

    article = {
        "title": title,
        "summary": summary,
        "category": category,
        "date": date,
        "slug": slug,
        "age_hours": age,
        "is_breaking": is_breaking
    }

    article["final_score"] = final_score(article)

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

    with open(os.path.join(ARTICLES_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)

    articles.append(article)

print(f"Generated {len(articles)} articles")

# ================= CARD RENDERERS =================
def render_card(a):
    return f"""
    <div class="card">
      <h3><a href="/articles/{a['slug']}.html">{a['title']}</a></h3>
      <p>{a['summary']}</p>
      <div class="read-more">
        <a href="/articles/{a['slug']}.html">Read analysis →</a>
      </div>
    </div>
    """

def render_live(a):
    minutes = int(a["age_hours"] * 60)
    label = f"{minutes}m ago" if minutes < 60 else f"{int(a['age_hours'])}h ago"
    return f"""
    <div class="live-item">
      <span class="live-badge">LIVE</span>
      <a href="/articles/{a['slug']}.html">{a['title']}</a>
      <small class="live-age">{label}</small>
    </div>
    """

# ================= HOMEPAGE BUILD =================
used = set()

# 🔴 LIVE BREAKING (ONLY EXPLICIT LIVE)
live = [a for a in articles if a["is_breaking"]]
live.sort(key=lambda x: x["age_hours"])

if live:
    live_html = "".join(render_live(a) for a in live[:20])
else:
    live_html = """
    <div class="live-empty">
      No breaking developments at this moment.
    </div>
    """

used.update(a["slug"] for a in live)

# 🔵 TRENDING NOW
remaining = [a for a in articles if a["slug"] not in used]
trending = sorted(remaining, key=lambda x: x["final_score"], reverse=True)[:6]
used.update(a["slug"] for a in trending)

# 🟢 TOP STORIES
remaining = [a for a in remaining if a["slug"] not in used]
top = sorted(remaining, key=lambda x: x["final_score"], reverse=True)[:6]
used.update(a["slug"] for a in top)

# 🟣 RECENT
remaining = [a for a in remaining if a["slug"] not in used]
recent = sorted(remaining, key=lambda x: x["date"], reverse=True)[:6]
used.update(a["slug"] for a in recent)

# ⚪ OLDER
older = [a for a in articles if a["slug"] not in used][:6]

# ⭐ FEATURED (NON-BREAKING ONLY)
featured_candidates = [a for a in articles if not a["is_breaking"]]
featured = max(featured_candidates, key=lambda x: x["final_score"]) if featured_candidates else None

# ================= RENDER INDEX =================
index_html = INDEX_TEMPLATE
index_html = index_html.replace("{{LIVE_BREAKING}}", live_html)
index_html = index_html.replace("{{TRENDING_ARTICLES}}", "".join(render_card(a) for a in trending))
index_html = index_html.replace("{{TOP_ARTICLES}}", "".join(render_card(a) for a in top))
index_html = index_html.replace(
    "{{FEATURED_ARTICLE}}",
    render_card(featured) if featured else ""
)
index_html = index_html.replace("{{RECENT_ARTICLES}}", "".join(render_card(a) for a in recent))
index_html = index_html.replace("{{OLDER_ARTICLES}}", "".join(render_card(a) for a in older))

with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("Index generated")
print("PureStill build complete ✅")

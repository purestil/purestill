print("Starting PureStill generator…")

import json, os, re
from datetime import datetime, timezone, timedelta

# ================= CONFIG =================
BASE_URL = "https://purestill.pages.dev"
SITE_DIR = "site"
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")
SIGNALS_DIR = "signals"

# 🔴 LIVE rules
LIVE_DEMOTION_HOURS = 2      # auto-demote LIVE after 2h
LIVE_MAX_DISPLAY = 20

# 🌍 Country RPM priority
COUNTRY_RPM = {
    "US": 100,
    "UK": 95,
    "CA": 90,
    "AU": 85,
    "GLOBAL": 70
}

os.makedirs(ARTICLES_DIR, exist_ok=True)

# ================= LOAD DATA =================
with open("data.json", encoding="utf-8") as f:
    raw_data = json.load(f)

if not isinstance(raw_data, list):
    raise Exception("data.json must be a list")

# ================= LOAD LIVE FEED =================
live_feed = []
live_file = os.path.join(SIGNALS_DIR, "live_feed.json")
if os.path.exists(live_file):
    with open(live_file, encoding="utf-8") as f:
        live_feed = json.load(f)

# ================= LOAD TRUST / CTR SIGNALS =================
trust_score = 100
trust_path = os.path.join(SIGNALS_DIR, "trust_score.json")
if os.path.exists(trust_path):
    with open(trust_path) as f:
        trust_score = json.load(f).get("trust_score", 100)

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
        return 999
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    return (NOW - dt).total_seconds() / 3600

# ================= SCORING =================
CATEGORY_WEIGHT = {
    "Business": 95,
    "Economy": 90,
    "Technology": 88,
    "AI": 90,
    "Policy": 85,
    "Politics": 80,
    "Sports": 60,
    "General": 70
}

def final_score(article):
    freshness = max(0, 100 - article["age_hours"] * 6)
    category_score = CATEGORY_WEIGHT.get(article["category"], 70)
    rpm = COUNTRY_RPM.get(article["country"], 70)
    trust_boost = trust_score / 10
    return round(
        freshness * 0.35 +
        category_score * 0.30 +
        rpm * 0.25 +
        trust_boost,
        2
    )

# ================= AUTO CONTENT =================
def auto_expand_article(title, summary, category):
    return f"""
<h2>Context</h2>
<p>{summary}</p>

<h2>Background</h2>
<p>Recent developments in the {category.lower()} space indicate a broader structural trend.</p>

<h2>Why It Matters</h2>
<p>The outcome has implications for markets, institutions, and public confidence.</p>

<h2>What Happens Next</h2>
<p>Further updates and official responses are expected in the coming days.</p>
"""

# ================= ARTICLE BUILD =================
articles = []

for item in raw_data:
    title = safe(item, "TITLE", "title")
    if not title:
        continue

    summary = safe(item, "SUMMARY", "summary")
    content_raw = safe(item, "CONTENT", "content")
    category = safe(item, "CATEGORY", "category", default="General")
    source = safe(item, "SOURCE", "source")
    date = safe(item, "DATE", "date", default=NOW.isoformat())
    country = safe(item, "COUNTRY", default="GLOBAL")

    age = hours_old(date)

    # 🔴 LIVE demotion logic
    is_live = item.get("IS_BREAKING", False) is True and age <= LIVE_DEMOTION_HOURS

    content = content_raw.strip() if content_raw else auto_expand_article(
        title, summary, category
    )

    slug = slugify(title)
    canonical = f"{BASE_URL}/articles/{slug}.html"

    article = {
        "title": title,
        "summary": summary,
        "category": category,
        "date": date,
        "slug": slug,
        "age_hours": age,
        "is_live": is_live,
        "country": country
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

# ================= RENDER HELPERS =================
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

def render_live(item):
    mins = int(item["age_hours"] * 60)
    label = f"{mins}m ago" if mins < 60 else f"{int(item['age_hours'])}h ago"
    return f"""
    <div class="live-item">
      <span class="live-badge">LIVE</span>
      <a href="/articles/{item['slug']}.html">{item['title']}</a>
      <small class="live-age">{label}</small>
    </div>
    """

# ================= HOMEPAGE LOGIC =================
used = set()

# 🔴 LIVE BREAKING (EXPLICIT + AUTO-DEMOTED)
live_articles = [a for a in articles if a["is_live"]]
live_articles.sort(key=lambda x: x["age_hours"])

live_html = "".join(render_live(a) for a in live_articles[:LIVE_MAX_DISPLAY]) \
    if live_articles else "<div class='live-empty'>No breaking developments.</div>"

used.update(a["slug"] for a in live_articles)

# 🔵 TRENDING NOW
remaining = [a for a in articles if a["slug"] not in used]
trending = sorted(remaining, key=lambda x: x["final_score"], reverse=True)[:6]
used.update(a["slug"] for a in trending)

# 🟢 TOP STORIES (RPM weighted)
remaining = [a for a in remaining if a["slug"] not in used]
top = sorted(remaining, key=lambda x: x["final_score"], reverse=True)[:6]
used.update(a["slug"] for a in top)

# 🟣 RECENT
remaining = [a for a in remaining if a["slug"] not in used]
recent = sorted(remaining, key=lambda x: x["date"], reverse=True)[:6]
used.update(a["slug"] for a in recent)

# ⚪ OLDER
older = [a for a in articles if a["slug"] not in used][:6]

# ⭐ FEATURED (non-live only)
featured_candidates = [a for a in articles if not a["is_live"]]
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

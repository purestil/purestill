print("Starting PureStill generator…")

import json, os, re
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

# ✅ FIX: normalize keys + sort newest first
for item in data:
    item["DATE"] = item.get("DATE") or item.get("date") or datetime.utcnow().isoformat()
    item["TITLE"] = item.get("TITLE") or item.get("title", "")
    item["SUMMARY"] = item.get("SUMMARY") or item.get("summary", "")
    item["CONTENT"] = item.get("CONTENT") or item.get("content", "")
    item["CATEGORY"] = item.get("CATEGORY") or item.get("category", "General")
    item["SOURCE"] = item.get("SOURCE") or item.get("source", "")
    item["RELATED_LINKS"] = item.get("RELATED_LINKS", "")

data.sort(key=lambda x: x["DATE"], reverse=True)

# ================= LOAD TEMPLATES =================
with open("article_template.html", encoding="utf-8") as f:
    ARTICLE_TEMPLATE = f.read()

with open("index_template.html", encoding="utf-8") as f:
    INDEX_TEMPLATE = f.read()

# ================= HELPERS =================
def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def replace_placeholders(template, mapping):
    html = template
    for key, value in mapping.items():
        html = html.replace("{{" + key + "}}", value)
    return html

# ================= GENERATE ARTICLES =================
index_cards = []
topics = defaultdict(list)

for item in data:
    slug = slugify(item["TITLE"])
    article_path = os.path.join(ARTICLES_DIR, f"{slug}.html")
    canonical = f"{BASE_URL}/articles/{slug}.html"

    mapping = {
        "TITLE": item["TITLE"],
        "SUMMARY": item["SUMMARY"],
        "CONTENT": item["CONTENT"],
        "CATEGORY": item["CATEGORY"],
        "SOURCE": item["SOURCE"],
        "DATE": item["DATE"],
        "CANONICAL_URL": canonical,
        "RELATED_LINKS": item["RELATED_LINKS"],
        "AD_MID": "",
        "AD_BOTTOM": ""
    }

    html = replace_placeholders(ARTICLE_TEMPLATE, mapping)

    with open(article_path, "w", encoding="utf-8") as f:
        f.write(html)

    # index card
    index_cards.append(f"""
      <div class="card">
        <h3><a href="/articles/{slug}.html">{item["TITLE"]}</a></h3>
        <p>{item["SUMMARY"]}</p>
        <div class="read-more"><a href="/articles/{slug}.html">Read analysis →</a></div>
      </div>
    """)

    topics[item["CATEGORY"].lower()].append(index_cards[-1])

print(f"✅ Generated {len(data)} articles")

# ================= GENERATE INDEX =================
index_html = INDEX_TEMPLATE.replace("{{FEATURED_ARTICLE}}", index_cards[0])
index_html = index_html.replace("{{RECENT_ARTICLES}}", "\n".join(index_cards[:6]))
index_html = index_html.replace("{{TOP_ARTICLES}}", "\n".join(index_cards[6:12]))
index_html = index_html.replace("{{OLDER_ARTICLES}}", "\n".join(index_cards[12:]))

with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("✅ Index page generated")

# ================= GENERATE TOPIC PAGES =================
for topic, cards in topics.items():
    topic_html = INDEX_TEMPLATE
    topic_html = topic_html.replace("{{FEATURED_ARTICLE}}", cards[0])
    topic_html = topic_html.replace("{{RECENT_ARTICLES}}", "\n".join(cards))
    topic_html = topic_html.replace("{{TOP_ARTICLES}}", "")
    topic_html = topic_html.replace("{{OLDER_ARTICLES}}", "")

    with open(os.path.join(TOPICS_DIR, f"{topic}.html"), "w", encoding="utf-8") as f:
        f.write(topic_html)

print("✅ Topic pages generated")
print("🎉 PureStill build complete")

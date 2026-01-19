import json, os
from datetime import datetime

BASE_URL = "https://purestill.pages.dev"
SITE_DIR = "site"
ART_DIR = os.path.join(SITE_DIR, "articles")

os.makedirs(ART_DIR, exist_ok=True)

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

data.sort(key=lambda x: x["date"], reverse=True)

# ---------- ARTICLE PAGES ----------
with open("article_template.html", encoding="utf-8") as f:
    ARTICLE_TPL = f.read()

for i, item in enumerate(data):
    html = ARTICLE_TPL
    html = html.replace("{{TITLE}}", item["title"])
    html = html.replace("{{SUMMARY}}", item["summary"])
    html = html.replace("{{CONTENT}}", item["content"])
    html = html.replace("{{DATE}}", item["date"])
    html = html.replace("{{SOURCE}}", item["source"])
    html = html.replace("{{CANONICAL_URL}}", f"{BASE_URL}/articles/article-{i+1}.html")

    # related links
    related = ""
    for j, r in enumerate(data):
        if j != i:
            related += f"<li><a href='/articles/article-{j+1}.html'>{r['title']}</a></li>"
    html = html.replace("{{RELATED_LINKS}}", related)

    with open(f"{ART_DIR}/article-{i+1}.html", "w", encoding="utf-8") as f:
        f.write(html)

# ---------- HOMEPAGE ----------
with open("index_template.html", encoding="utf-8") as f:
    INDEX_TPL = f.read()

def card(item, idx):
    return f"""
    <div class="card">
      <h3><a href="/articles/article-{idx}.html">{item['title']}</a></h3>
      <div class="meta">Published {item['date']}</div>
      <p>{item['summary']}</p>
      <p class="read-more"><a href="/articles/article-{idx}.html">Read more →</a></p>
    </div>
    """

featured = f"""
<h1><a href="/articles/article-1.html">{data[0]['title']}</a></h1>
<div class="meta">Published {data[0]['date']}</div>
<p>{data[0]['summary']}</p>
<p class="read-more"><a href="/articles/article-1.html">Read more →</a></p>
"""

recent = "".join(card(data[i], i+1) for i in range(1, min(4, len(data))))
top = "".join(card(data[i], i+1) for i in range(4, min(7, len(data))))
older = "".join(card(data[i], i+1) for i in range(7, min(10, len(data))))

INDEX_TPL = INDEX_TPL.replace("{{FEATURED_ARTICLE}}", featured)
INDEX_TPL = INDEX_TPL.replace("{{RECENT_ARTICLES}}", recent)
INDEX_TPL = INDEX_TPL.replace("{{TOP_ARTICLES}}", top)
INDEX_TPL = INDEX_TPL.replace("{{OLDER_ARTICLES}}", older)

with open(f"{SITE_DIR}/index.html", "w", encoding="utf-8") as f:
    f.write(INDEX_TPL)

print("PureStill site generated successfully.")

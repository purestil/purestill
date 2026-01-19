print("Starting PureStill generator…")

import json, os
from datetime import datetime

# ================= CONFIG =================
BASE_URL = "https://purestill.pages.dev"
SITE_DIR = "site"
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")

os.makedirs(ARTICLES_DIR, exist_ok=True)

# ================= LOAD DATA =================
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

# ================= LOAD TEMPLATE =================
with open("article_template.html", encoding="utf-8") as f:
    TEMPLATE = f.read()

# ================= CONTENT EXPANSION (CRITICAL) =================
def ensure_min_words(text, title, min_words=700):
    filler = [
        f"<h2>Background</h2><p>{title} has developed within a broader economic and policy context in the United States.</p>",
        "<h2>Recent Developments</h2><p>Recent signals suggest gradual adjustments rather than abrupt changes, with markets responding cautiously.</p>",
        "<h2>Economic Context</h2><p>Inflation trends, interest rate expectations, and labor market data provide essential context.</p>",
        "<h2>Implications</h2><p>This development may influence business decisions, investment strategies, and regulatory considerations.</p>",
        "<h2>What to Watch</h2><p>Upcoming data releases and policy communications will help clarify future direction.</p>",
        "<h2>Conclusion</h2><p>A long-term perspective remains essential when interpreting economic and market signals.</p>",
    ]

    expanded = f"<p>{text}</p>"
    i = 0
    while len(expanded.split()) < min_words:
        expanded += filler[i % len(filler)]
        i += 1

    return expanded

# ================= RELATED ARTICLES =================
def build_related_blocks(current_index, items, limit=3):
    blocks = ""
    count = 0

    for i, it in enumerate(items):
        if i == current_index:
            continue

        blocks += f"""
        <div class="related-item">
          <h3><a href="/articles/article-{i+1}.html">{it['title']}</a></h3>
          <p>{it.get('content','')[:140]}…</p>
        </div>
        """

        count += 1
        if count >= limit:
            break

    return blocks

# ================= GENERATE ARTICLES =================
for i, item in enumerate(data):
    title = item.get("title", "Untitled")
    raw_content = item.get("content", title)

    # 🔥 FORCE EXPANSION
    content = ensure_min_words(raw_content, title)

    related_blocks = build_related_blocks(i, data)

    html = TEMPLATE
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{SUMMARY}}", raw_content[:160])
    html = html.replace("{{SOURCE}}", item.get("link", "Public sources"))
    html = html.replace("{{DATE}}", datetime.utcnow().strftime("%B %d, %Y"))
    html = html.replace("{{CONTENT}}", content)
    html = html.replace("{{RELATED_BLOCKS}}", related_blocks)
    html = html.replace(
        "{{CANONICAL_URL}}",
        f"{BASE_URL}/articles/article-{i+1}.html"
    )

    with open(os.path.join(ARTICLES_DIR, f"article-{i+1}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ================= HOMEPAGE =================
index_items = ""
for i, item in enumerate(data[:10]):
    index_items += f"<p><a href='/articles/article-{i+1}.html'>{item['title']}</a></p>\n"

index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PureStill | Independent Global Analysis</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<h1>PureStill</h1>
<p>Independent analysis of business, technology, and economic change.</p>
{index_items}
</body>
</html>
"""

with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("PureStill site generated successfully — expanded articles + related links live.")

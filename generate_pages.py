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

# ================= CONTENT EXPANDER (CRITICAL) =================
def ensure_min_words(text, title, min_words=700):
    words = text.split()

    filler_sections = [
        f"<h2>Background</h2><p>{title} has been developing over time as part of broader economic and policy trends in the United States. Analysts and institutions continue to monitor these shifts closely.</p>",
        "<h2>Key Developments</h2><p>Recent data, statements, and indicators suggest gradual adjustments rather than abrupt changes. Market participants are responding cautiously.</p>",
        "<h2>Economic Context</h2><p>Macroeconomic conditions, including inflation trends, interest rate expectations, and labor market signals, provide essential context for this development.</p>",
        "<h2>Implications</h2><p>This may influence investment decisions, regulatory considerations, and strategic planning across multiple sectors.</p>",
        "<h2>What to Watch</h2><p>Upcoming releases, policy meetings, and economic indicators will help clarify the direction of future developments.</p>",
        "<h2>Conclusion</h2><p>Overall, this situation highlights the importance of measured analysis and long-term perspective when assessing economic and market signals.</p>",
    ]

    expanded = f"<p>{text}</p>"

    i = 0
    while len(expanded.split()) < min_words:
        expanded += filler_sections[i % len(filler_sections)]
        i += 1

    return expanded

# ================= GENERATE ARTICLES =================
for i, item in enumerate(data):
    title = item.get("title", "Untitled")
    raw_content = item.get("content", title)

    # 🔥 FORCE EXPANSION HERE
    content = ensure_min_words(raw_content, title)

    html = TEMPLATE
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{SUMMARY}}", raw_content[:160])
    html = html.replace("{{SOURCE}}", item.get("link", "Public sources"))
    html = html.replace("{{DATE}}", datetime.utcnow().strftime("%B %d, %Y"))
    html = html.replace("{{CONTENT}}", content)
    html = html.replace("{{CANONICAL_URL}}", f"{BASE_URL}/articles/article-{i+1}.html")
    html = html.replace("{{SIMILAR_BLOCKS}}", "")

    with open(os.path.join(ARTICLES_DIR, f"article-{i+1}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ================= HOMEPAGE =================
index_links = ""
for i, item in enumerate(data[:10]):
    index_links += f"<p><a href='/articles/article-{i+1}.html'>{item['title']}</a></p>\n"

index_html = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>PureStill</title>
</head><body>
<h1>PureStill</h1>
{index_links}
</body></html>
"""

with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("PureStill site generated successfully.")

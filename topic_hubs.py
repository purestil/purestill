import json, os
from collections import defaultdict

DATA_FILE = "data.json"
OUT_DIR = "site/topics"

os.makedirs(OUT_DIR, exist_ok=True)

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

topics = defaultdict(list)

for item in data:
    cat = item.get("category", "General")
    topics[cat].append(item)

for topic, items in topics.items():
    # sort by quality
    items = sorted(
        items,
        key=lambda x: x.get("final_score", 0),
        reverse=True
    )[:20]

    slug = topic.lower().replace(" ", "-")
    html = f"""
    <html>
    <head>
      <title>{topic} Analysis | PureStill</title>
      <meta name="description" content="Independent analysis of {topic.lower()} developments">
      <link rel="canonical" href="https://purestill.pages.dev/topics/{slug}.html">
    </head>
    <body>
      <h1>{topic} Analysis</h1>
    """

    for a in items:
        html += f"""
        <div style="margin-bottom:24px">
          <h3>
            <a href="/articles/{a['slug']}.html">{a['title']}</a>
          </h3>
          <p>{a['summary']}</p>
        </div>
        """

    html += "</body></html>"

    with open(os.path.join(OUT_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)

print("Topic hubs generated")

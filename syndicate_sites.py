import json
import os

DATA_FILE = "data.json"
OUT_DIR = "syndication"

SITES = {
    "economy": ["Economy", "Policy"],
    "tech": ["Technology", "AI"]
}

os.makedirs(OUT_DIR, exist_ok=True)

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

for site, cats in SITES.items():
    html = f"<h1>{site.title()} Analysis</h1>"

    for a in data:
        if a.get("category") in cats:
            html += f"""
            <div>
              <h3>{a['title']}</h3>
              <p>{a['summary']}</p>
              <a href="https://purestill.pages.dev/articles/{a['slug']}.html" rel="canonical">
                Read full analysis
              </a>
            </div>
            """

    with open(os.path.join(OUT_DIR, f"{site}.html"), "w") as f:
        f.write(html)

print("🕸️ Syndication mesh generated")

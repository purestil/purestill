import json

TARGET_SITES = [
    "https://purestillglobal.pages.dev",
    "https://purestilltech.pages.dev"
]

with open("data.json") as f:
    data = json.load(f)

payload = []

for a in data[:10]:
    payload.append({
        "title": a["title"],
        "summary": a["summary"],
        "canonical": f"https://purestill.pages.dev/articles/{a['slug']}.html"
    })

with open("signals/syndication_payload.json","w") as f:
    json.dump(payload, f, indent=2)

print("🌐 Syndication payload generated")

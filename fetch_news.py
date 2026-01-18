import feedparser, json

feeds = open("feeds.txt").read().splitlines()
articles = []

for url in feeds:
    feed = feedparser.parse(url)
    for entry in feed.entries[:8]:
        articles.append({
            "title": entry.title,
            "link": entry.link
        })

with open("data.json","w") as f:
    json.dump(articles,f,indent=2)

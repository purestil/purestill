import json
from datetime import datetime
import xml.etree.ElementTree as ET

BASE_URL = "https://purestill.pages.dev"

with open("data.json") as f:
    data = json.load(f)

news = [a for a in data if a.get("is_breaking") or a.get("category") in ["Business","Technology","Policy"]]

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss,"channel")

ET.SubElement(channel,"title").text = "PureStill News"
ET.SubElement(channel,"link").text = BASE_URL
ET.SubElement(channel,"description").text = "Independent global news and analysis"

for a in news[:100]:
    item = ET.SubElement(channel,"item")
    ET.SubElement(item,"title").text = a["title"]
    ET.SubElement(item,"link").text = f"{BASE_URL}/articles/{a['slug']}.html"
    ET.SubElement(item,"pubDate").text = a["date"]
    ET.SubElement(item,"guid").text = a["slug"]

tree = ET.ElementTree(rss)
tree.write("site/google-news.xml", encoding="utf-8", xml_declaration=True)

print("📰 Google News feed generated")

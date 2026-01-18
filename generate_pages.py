import json, os

data = json.load(open("data.json"))
os.makedirs("site", exist_ok=True)

article_tpl = open("article_template.html").read()
links = ""

for i, item in enumerate(data):
    filename = f"article-{i+1}.html"
    page = article_tpl.replace("{{TITLE}}", item["title"])
    page = page.replace("{{SUMMARY}}",
        "This article provides an independent summary and contextual analysis of recent developments affecting business, technology, and economic conditions in the United States.")
    page = page.replace("{{SOURCE}}", item["link"])
    open("site/"+filename,"w",encoding="utf-8").write(page)
    links += f"<p><a href='{filename}'>{item['title']}</a></p>\n"

index = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>PureStill | Independent Market Analysis</title>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<style>
body{{font-family:Inter,Arial,sans-serif;line-height:1.7;color:#111}}
.wrap{{max-width:720px;margin:0 auto;padding:80px 20px}}
h1,h2{{font-family:Georgia,serif}}
a{{color:#111;text-decoration:underline}}
footer{{margin-top:80px;color:#555;font-size:14px}}
</style>
</head>
<body>
<div class='wrap'>
<h1>Independent analysis of business, technology, and economic change</h1>
<p>PureStill provides calm summaries and context based on publicly available information, focusing on developments shaping the United States.</p>
<h2>Latest Analysis</h2>
{links}
<footer>
<a href='about.html'>About</a> ·
<a href='privacy-policy.html'>Privacy</a> ·
<a href='disclaimer.html'>Disclaimer</a> ·
<a href='contact.html'>Contact</a><br><br>
© PureStill
</footer>
</div>
</body>
</html>"""

open("site/index.html","w",encoding="utf-8").write(index)

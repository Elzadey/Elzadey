import os, json, urllib.request
from collections import Counter

USER = "Elzadey"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
BG, BORDER, ACCENT, TEXT = "#14110f", "#3a2e27", "#d9774a", "#f4ece4"
def get(url):
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as r:
        return json.load(r)

user = get(f"https://api.github.com/users/{USER}")
repos, page = [], 1
while True:
    batch = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner")
    if not batch:
        break
    repos += batch
    page += 1
repos = [r for r in repos if not r["fork"]]

stars = sum(r["stargazers_count"] for r in repos)
langs = Counter(r["language"] for r in repos if r["language"])
total = sum(langs.values()) or 1

STYLE = f"""<style>
text{{font-family:'Segoe UI',Ubuntu,sans-serif}}
.t{{fill:{ACCENT};font-size:18px;font-weight:700}}
.l{{fill:{TEXT};font-size:14px}}
.v{{fill:{ACCENT};font-size:14px;font-weight:700}}
.fade{{opacity:0;animation:f .6s ease forwards}}
@keyframes f{{to{{opacity:1}}}}
.bar{{transform-origin:left;animation:g 1s ease forwards;transform:scaleX(0)}}
@keyframes g{{to{{transform:scaleX(1)}}}}
</style>"""

def card(title, body, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="{h}" viewBox="0 0 400 {h}">{STYLE}'
            f'<rect x="1" y="1" width="398" height="{h-2}" rx="10" fill="{BG}" stroke="{BORDER}"/>'
            f'<text x="25" y="35" class="t">{title}</text>{body}</svg>')

rows = [("Public Repos", user["public_repos"]), ("Total Stars", stars),
        ("Followers", user["followers"]), ("Following", user["following"])]
body = "".join(
    f'<g class="fade" style="animation-delay:{i*0.15}s">'
    f'<text x="25" y="{70+i*28}" class="l">{k}</text>'
    f'<text x="375" y="{70+i*28}" class="v" text-anchor="end">{v}</text></g>'
    for i, (k, v) in enumerate(rows))
os.makedirs("assets", exist_ok=True)
open("assets/stats.svg", "w", encoding="utf-8").write(card("GitHub Stats", body, 190))

top = langs.most_common(5)
body = ""
for i, (name, n) in enumerate(top):
    pct = n * 100 / total
    y = 62 + i * 30
    body += (f'<text x="25" y="{y}" class="l">{name}</text>'
             f'<text x="375" y="{y}" class="v" text-anchor="end">{pct:.0f}%</text>'
             f'<rect x="25" y="{y+6}" width="350" height="6" rx="3" fill="{BORDER}"/>'
             f'<rect class="bar" x="25" y="{y+6}" width="{350*pct/100:.0f}" height="6" rx="3" '
             f'fill="{ACCENT}" style="animation-delay:{i*0.15}s"/>')
open("assets/langs.svg", "w", encoding="utf-8").write(card("Top Languages", body, 62 + len(top) * 30 + 20))

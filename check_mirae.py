import re

with open("mirae_page.html", encoding="utf-8") as f:
    html = f.read()

pattern = re.compile(
    r'\\"nav_value\\":([0-9.]+).*?\\"nse_symbol\\":\\"([^\\"]+)\\"',
    re.S,
)

rows = pattern.findall(html)

print("Records:", len(rows))

for nav, symbol in rows:
    print(f"{symbol}: {nav}")
#!/usr/bin/env python3
"""Bring an existing html-worker page directory up to the skill's current mechanics.

A page is a copy of page-template.html plus content inside <main>, and sits beside
copies of server.py and export-md.py. Changes to the skill do not reach those copies.
This syncs everything that is mechanics, and nothing that is content:

  index.html   <style>, font <link>, theme script, #pop markup, the right column, the page <script>
  server.py    replaced
  export-md.py replaced

<main>, data-anchor/data-radio/data-check blocks and state.json are untouched. Restart
the server after syncing (server.py is loaded once at start); the page itself needs
only a browser refresh.

    python3 sync.py path/to/page-dir [more-dirs ...]
"""
import re, shutil, sys
from pathlib import Path

SKILL = Path(__file__).parent
TEMPLATE = (SKILL / "page-template.html").read_text()

PARTS = {  # name: regex over the page; each must match exactly once in the template
    "font":   r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>\n',
    "style":  r"<style>.*?</style>\n",
    "theme":  r'<script id="theme">.*?</script>\n',
    "pop":    r'<div id="pop">.*?</div>\n</div>\n',
    "aside":  r'<aside class="right">.*?</aside>\n(?:<div id="wideview"></div>\n)?(?:<button id="cpfab">.*?</button>\n)?',   # the right column (conversation panel)
    "script": r"<script>\n(?!\(\(\)=>).*?</script>\n",     # the page script, not the theme one
}
FRESH = {}
for name, rx in PARTS.items():
    found = re.findall(rx, TEMPLATE, re.S)
    if name != "font" and len(found) != 1:
        sys.exit(f"template: expected one {name} block, found {len(found)}")
    FRESH[name] = found[0] if found else ""

for arg in sys.argv[1:]:
    d = Path(arg)
    page = d / "index.html"
    if not page.exists():
        sys.exit(f"{d}: no index.html")
    s = page.read_text()
    for name, rx in PARTS.items():
        if name == "font":
            s = re.sub(rx, "", s)                      # dropped, re-added with style
            continue
        if not re.search(rx, s, re.S) and name != "theme":
            sys.exit(f"{page}: no {name} block found; not a template page?")
        s = re.sub(rx, "", s, count=1, flags=re.S)
    s = s.replace("</head>", FRESH["font"] + FRESH["style"] + FRESH["theme"] + "</head>", 1)
    s = s.replace('<div id="toast"></div>', FRESH["pop"] + '<div id="toast"></div>', 1)
    s = s.replace("</main>\n", "</main>\n\n" + FRESH["aside"], 1)
    s = s.replace("</body>", FRESH["script"] + "</body>", 1)
    page.write_text(s)
    for f in ("server.py", "export-md.py"):
        shutil.copy(SKILL / f, d / f)
    print(f"synced {d} — refresh the page, restart the server")

#!/usr/bin/env python3
"""Check a generated design/BRIEF.md before it is handed over.

    python3 check_brief.py <app>/design/BRIEF.md

Fails (exit 1) on:
  - any {{placeholder}} left in the file
  - a §4 table row with an empty state cell (Empty / Loading / Error / Success)
  - a file named in §6 that does not exist under design/references/
  - more than 200 lines (the brief is repeating the PRD instead of pointing at it)
  - a required section heading missing
Prints every problem, not just the first, so one run fixes them all.
"""
import os
import re
import sys

MAX_LINES = 200
REQUIRED = [
    "## 0. How this brief is used",
    "## 1. What this is, and for whom",
    "## 2. Platform and device",
    "## 3. Navigation model",
    "## 4. Screen inventory, with every state",
    "## 5. Copy",
    "## 6. Data: real vs placeholder",
    "## 7. Visual direction",
    "## 8. Tokens",
    "## 9. Accessibility",
    "## 10. What is fixed, what is open",
    "## 11. What we need back",
]


def section(text, start, end):
    """Text between the heading that starts with `start` and the next one starting with `end`."""
    i = text.find(start)
    if i < 0:
        return ""
    j = text.find(end, i + 1) if end else -1
    return text[i:j] if j > 0 else text[i:]


def main(path):
    problems = []
    text = open(path).read()
    lines = text.splitlines()
    design_dir = os.path.dirname(os.path.abspath(path))
    refs = os.path.join(design_dir, "references")

    if len(lines) > MAX_LINES:
        problems.append(f"{len(lines)} lines — over {MAX_LINES}. Point at the PRD, don't repeat it.")

    for h in REQUIRED:
        if h not in text:
            problems.append(f"missing section: {h}")

    for m in re.finditer(r"\{\{[^}]*\}\}", text):
        line = text.count("\n", 0, m.start()) + 1
        problems.append(f"line {line}: placeholder left: {m.group(0)}")

    for m in re.finditer(r"<!--.*?-->", text, re.S):
        line = text.count("\n", 0, m.start()) + 1
        problems.append(f"line {line}: template comment left in the brief")

    # §4 rows: | # | Screen | What's on it | Serves | Empty | Loading | Error | Success |
    s4 = section(text, "## 4.", "## 5.")
    rows = [l for l in s4.splitlines() if l.startswith("|") and not l.startswith("|--") and not l.startswith("|---")]
    rows = [r for r in rows if not r.lower().startswith("| #")]
    if not rows:
        problems.append("§4 has no screen rows")
    for r in rows:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        if len(cells) < 8:
            problems.append(f"§4 row has {len(cells)} cells, needs 8: {r[:60]}")
            continue
        for name, val in zip(("Empty", "Loading", "Error", "Success"), cells[4:8]):
            if not val:
                problems.append(f"§4 '{cells[1]}': {name} cell is blank — write the copy, a §5 pointer, or '—'")

    # §6 files must exist in references/
    s6 = section(text, "## 6.", "## 7.")
    named = re.findall(r"`([^`\n]+\.(?:jpe?g|png|heic|webp|mp4|mov|pdf|json|csv))`", s6, re.I)
    for f in named:
        base = os.path.basename(f)
        if not os.path.exists(os.path.join(refs, base)) and not os.path.exists(os.path.join(design_dir, f)):
            problems.append(f"§6 names `{f}` but it is not in {refs}/")
    if not named and "real" in s6.lower():
        problems.append("§6 names no real files — if none exist, say so explicitly in the section")

    if problems:
        print(f"BRIEF CHECK — {len(problems)} problem(s) in {path}")
        for p in problems:
            print(" -", p)
        return 1
    print(f"BRIEF CHECK — ok: {len(lines)} lines, {len(rows)} screens, {len(named)} reference files")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))

#!/usr/bin/env python3
"""Every "…" — [link] quote in the file must exist verbatim in reviews/*.json. Usage: verify_quotes.py <file.md>"""
import glob, json, re, sys
norm = lambda t: t.replace("’", "'").replace("“", '"').replace("”", '"')
texts = []
for f in glob.glob("reviews/*.json"):
    for d in json.load(open(f)).values():
        texts += [r["text"] for r in d["reviews"]]
corpus = norm(" ".join(texts)); loose = re.sub(r"\s+", " ", corpus)
s = norm(open(sys.argv[1]).read())
pat = re.compile(r'[>\-]\s*"(.{20,}?)"\s*—\s*\[')
n = bad = ws = 0
for m in pat.finditer(s):
    n += 1; qt = m.group(1)
    if qt in corpus: continue
    if re.sub(r"\s+", " ", qt) in loose: ws += 1; print("WHITESPACE ONLY:", qt[:80]); continue
    bad += 1; print("NOT FOUND:", qt[:80])
print(f"{n} quotes · {bad} not found · {ws} whitespace-only")
sys.exit(1 if bad else 0)

import re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; missing=[]
for p in list(ROOT.glob("*.md"))+list((ROOT/"docs").glob("*.md"))+list((ROOT/"results").glob("**/*.md")):
    text=p.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)",text):
        if "://" in target or target.startswith("#"): continue
        q=(p.parent/target.split("#",1)[0]).resolve()
        if not q.exists(): missing.append((p.relative_to(ROOT),target))
if missing:
    for p,t in missing: print("MISSING",p,t)
    sys.exit(2)
print("documentation links and local paths pass")

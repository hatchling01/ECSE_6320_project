from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[2]
bad=[]
for p in (ROOT/"data"/"raw").glob("**/*.json"):
 try:r=json.loads(p.read_text()); assert r.get("status")=="VALID"; assert r.get("affinity_ok",True); assert r.get("validation_ok",True)
 except Exception as e:bad.append((p,e))
if bad:
 for p,e in bad: print("INVALID",p,e)
 sys.exit(2)
print("all retained JSON records parse and required validity flags pass")

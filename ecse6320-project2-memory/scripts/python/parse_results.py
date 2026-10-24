from __future__ import annotations
import json, math, statistics
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
rows=[]
for p in sorted((ROOT/"data"/"raw").glob("phase*/*.json")):
    r=json.loads(p.read_text(encoding="utf-8")); r["source_file"]=str(p.relative_to(ROOT)); r["phase"]=p.parent.name; rows.append(r)
df=pd.DataFrame(rows)
out=ROOT/"data"/"parsed"; out.mkdir(parents=True,exist_ok=True)
df.to_csv(out/"all_production_runs.csv",index=False)
metrics=[m for m in ("ns_per_load","useful_gib_per_s","ns_per_operation","probe_ns_per_load","worker_gib_per_s","l_inferred") if m in df]
keys=[k for k in ("phase","mode","working_set_bytes","spacing_bytes","stride_bytes","pattern","requested_read_pct","workers") if k in df]
records=[]
if not df.empty:
 for group,part in df.groupby(keys,dropna=False):
  keyvals=group if isinstance(group,tuple) else (group,)
  base=dict(zip(keys,keyvals)); base["n"]=len(part)
  for m in metrics:
   vals=[float(x) for x in part[m].dropna()]
   if not vals: continue
   mean=statistics.fmean(vals); sd=statistics.stdev(vals) if len(vals)>1 else 0
   base.update({f"{m}_median":statistics.median(vals),f"{m}_mean":mean,f"{m}_std":sd,f"{m}_cv":sd/mean if mean else math.nan,f"{m}_min":min(vals),f"{m}_max":max(vals)})
  records.append(base)
pd.DataFrame(records).to_csv(out/"summary.csv",index=False)
print(f"parsed {len(df)} production runs into {out}")

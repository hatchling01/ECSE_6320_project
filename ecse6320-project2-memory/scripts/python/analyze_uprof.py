import csv
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]; rows=[]
for p in sorted((ROOT/"profiler"/"reports").glob("*.csv")):
    lines=p.read_text(encoding="utf-8-sig").splitlines()
    for i,line in enumerate(lines):
        if line.startswith('PROCESS,"CYCLES_NOT_IN_HALT"'):
            head=next(csv.reader([line])); vals=next(csv.reader([lines[i+1]])); row=dict(zip(head,vals)); row["case"]=p.stem;rows.append(row);break
df=pd.DataFrame(rows)
numeric=[c for c in df.columns if c not in ("PROCESS","case")]
for c in numeric: df[c]=pd.to_numeric(df[c],errors="coerce")
df.to_csv(ROOT/"data"/"parsed"/"uprof_process_summary.csv",index=False)
core=df[df.case.isin(["l1","l2","llc","dram"])].set_index("case").reindex(["l1","l2","llc","dram"])
core[["IPC","L2_CACHE_ACCESSES_FROM_DC_MISSES (PTI)"]].plot.bar(subplots=True,legend=False,figsize=(7,6));plt.tight_layout();plt.savefig(ROOT/"results"/"plots"/"phase4_uprof_correlation.png",dpi=160);plt.close()
print(df[["case","IPC","CPI","L1_DC_ACCESSES_ALL","L2_CACHE_ACCESS_FROM_L1_DC_MISS","L1_DTLB_MISSES","L2_CACHE_ACCESSES_FROM_DC_MISSES (PTI)"]].to_string(index=False))

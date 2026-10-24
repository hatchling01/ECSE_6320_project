from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]; data=pd.read_csv(ROOT/"data"/"parsed"/"all_production_runs.csv"); out=ROOT/"results"/"plots"; out.mkdir(parents=True,exist_ok=True)
def save(name,xlabel,ylabel): plt.xlabel(xlabel);plt.ylabel(ylabel);plt.grid(True,alpha=.3);plt.tight_layout();plt.savefig(out/name,dpi=160);plt.close()
if "phase1" in set(data.phase):
 d=data[data.phase=="phase1"]; g=d.groupby("working_set_bytes").ns_per_load.agg(["median","std"]); plt.errorbar(g.index/1024,g["median"],yerr=g["std"],marker="o");plt.xscale("log");save("phase1_hierarchy_latency.png","Working set (KiB)","ns/dependent load")
if "phase2" in set(data.phase):
 d=data[(data.phase=="phase2")&(data["mode"]=="stream")];g=d.groupby(["pattern","requested_read_pct","stride_bytes"]).useful_gib_per_s.median()
 for (pat,rp),v in g.groupby(level=[0,1]): plt.plot(v.index.get_level_values(2),v.values,marker="o",label=f"{pat} {int(rp)}% read")
 plt.legend(fontsize=7);plt.xscale("log",base=2);save("phase2_stride_bandwidth.png","Stride (B)","Useful GiB/s")
 g=d.groupby(["pattern","requested_read_pct","stride_bytes"]).ns_per_operation.median()
 for (pat,rp),v in g.groupby(level=[0,1]): plt.plot(v.index.get_level_values(2),v.values,marker="o",label=f"{pat} {int(rp)}% read")
 plt.legend(fontsize=7);plt.xscale("log",base=2);save("phase2_stride_ns_per_operation.png","Stride (B)","ns/useful operation")
 d=data[(data.phase=="phase2")&(data["mode"]=="mix")];g=d.groupby(["pattern","requested_read_pct"]).useful_gib_per_s.median()
 for pat,v in g.groupby(level=0): plt.plot(v.index.get_level_values(1),v.values,marker="o",label=pat)
 plt.legend();save("phase2_mix_bandwidth.png","Read percentage","Useful GiB/s")
if "phase3" in set(data.phase):
 d=data[data.phase=="phase3"];g=d.groupby("workers")[["worker_gib_per_s","probe_ns_per_load","l_inferred"]].median()
 plt.plot(g.index,g.worker_gib_per_s,marker="o");save("phase3_workers_bandwidth.png","Background workers","Useful GiB/s")
 plt.plot(g.index,g.probe_ns_per_load,marker="o");save("phase3_workers_probe_latency.png","Background workers","Probe ns/load")
 plt.plot(g.probe_ns_per_load,g.worker_gib_per_s,marker="o");
 for w,x,y in zip(g.index,g.probe_ns_per_load,g.worker_gib_per_s):plt.annotate(str(w),(x,y))
 save("phase3_throughput_latency.png","Probe ns/load","Useful GiB/s")
 plt.plot(g.index,g.l_inferred,marker="o");save("phase3_littles_law.png","Background workers","L inferred (operations)")
if "phase4" in set(data.phase):
 d=data[(data.phase=="phase4")&(data["mode"]=="latency")];g=d.groupby("working_set_bytes").ns_per_load.median();plt.plot(g.index/1024,g.values,marker="o");plt.xscale("log",base=2);save("phase4_working_set_latency.png","Working set (KiB)","ns/dependent load")
 d=data[(data.phase=="phase4")&(data["mode"]=="tlb")];g=d.groupby("working_set_bytes").ns_per_load.median();plt.plot(g.index/4096,g.values,marker="o");plt.xscale("log",base=2);save("phase4_tlb_latency.png","4 KiB pages","ns/page access")
if "phase5" in set(data.phase):
 d=data[data.phase=="phase5"];g=d.groupby("working_set_bytes").useful_gib_per_s.agg(["median","std"]);plt.bar(["16 MiB reuse","1 GiB DRAM-sensitive"],g["median"],yerr=g["std"]);save("phase5_cache_reuse_pitfall.png","Case","Useful GiB/s")
print(f"plots regenerated in {out}")

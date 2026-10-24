"""Collect four bounded process-level uProf profiles; never overwrites sessions."""
import argparse, json, os, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
UPROF=Path(r"C:\Program Files\AMD\AMDuProf\bin\AMDuProfCLI.exe")
EXE=ROOT/"build-clang-gnu"/"memory_bench.exe"
EVENTS=("CYCLES_NOT_IN_HALT","RETIRED_INST","L1_DC_ACCESSES_ALL","L2_CACHE_ACCESS_FROM_L1_DC_MISS","L1_DTLB_MISSES")
ap=argparse.ArgumentParser();ap.add_argument("set",choices=("representative","tlb"),nargs="?",default="representative");ns=ap.parse_args()
CASES=(("l1","latency",16384,0),("l2","latency",524288,0),("llc","latency",16777216,0),("dram","latency",536870912,0)) if ns.set=="representative" else (("tlb_low","tlb",64,500000000),("tlb_high","tlb",16384,100000000))
env=os.environ.copy();env["PATH"]=r"C:\msys64\ucrt64\bin;"+env.get("PATH","")
for name,mode,size,operations in CASES:
    out=ROOT/"profiler"/"raw"/name
    report=ROOT/"profiler"/"reports"/f"{name}.csv"
    log=ROOT/"profiler"/"reports"/f"{name}_console.txt"
    manifest=ROOT/"profiler"/"reports"/f"{name}_manifest.json"
    if out.exists() or report.exists() or manifest.exists(): raise FileExistsError(f"refusing to overwrite profile {name}")
    args=[str(UPROF),"profile"]
    for event in EVENTS: args += ["--event",f"event={event},interval=250000"]
    bench_args=[mode,"--operations",str(operations),"--cpu","0","--seed","43206320","--classification","uprof_supporting"]
    bench_args += ["--bytes",str(size),"--target-ms","2000"] if mode=="latency" else ["--pages",str(size)]
    args += ["--affinity","0","--output-dir",str(out),"--show-event-count","--stdout","--report-output",str(report),"--working-dir",str(ROOT),str(EXE),*bench_args]
    p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True,env=env,check=False)
    log.write_text(p.stdout+"\nSTDERR\n"+p.stderr,encoding="utf-8")
    manifest.write_text(json.dumps({"case":name,"working_set_bytes":size,"events":EVENTS,"sampling_interval":250000,"command":args,"returncode":p.returncode,"process_level":True},indent=2)+"\n",encoding="utf-8")
    if p.returncode or not report.exists(): raise RuntimeError(f"uProf case failed; retained {manifest}")
print(f"uProf profile set completed: {ns.set}")

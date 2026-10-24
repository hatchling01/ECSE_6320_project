"""Safety-gated, append-only experiment orchestration. No PowerShell scripts required."""
from __future__ import annotations
import argparse, ctypes, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXE = ROOT / "build-clang-gnu" / "memory_bench.exe"
GIT = Path(r"C:\Program Files\Git\cmd\git.exe")
GIB = 1024**3

class Mem(ctypes.Structure):
    _fields_=[("length",ctypes.c_ulong),("load",ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in ("total_phys","avail_phys","total_page","avail_page","total_virtual","avail_virtual","avail_extended")]

def available() -> int:
    m=Mem(); m.length=ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)): raise OSError("GlobalMemoryStatusEx failed")
    return m.avail_phys

def revision() -> str:
    p=subprocess.run([GIT,"-c",f"safe.directory={ROOT.as_posix()}","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True,check=False)
    return p.stdout.strip() if p.returncode==0 else "uncommitted"

def run(phase:str,name:str,args:list[str], allocation:int=0, classification:str="production") -> dict:
    if allocation>8*GIB: raise RuntimeError("8 GiB process allocation cap")
    if allocation>GIB and available()<16*GIB: raise RuntimeError("RAM GATE: <16 GiB available before >1 GiB allocation")
    outdir=ROOT/"data"/"raw"/phase; outdir.mkdir(parents=True,exist_ok=True)
    path=outdir/f"{name}.json"
    if path.exists(): raise FileExistsError(f"refusing to overwrite {path}")
    env=os.environ.copy(); env["PATH"]=r"C:\msys64\ucrt64\bin;"+env.get("PATH","")
    cmd=[str(EXE),*args,"--git-commit",revision(),"--classification",classification]
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,env=env,check=False)
    try: rec=json.loads((p.stdout or p.stderr).strip().splitlines()[-1])
    except Exception: rec={"status":"INVALID","error":"non-JSON output","stdout":p.stdout,"stderr":p.stderr}
    rec["command"]=cmd; rec["returncode"]=p.returncode; rec["orchestrator_available_before"]=available()
    path.write_text(json.dumps(rec,indent=2)+"\n",encoding="utf-8")
    if p.returncode or rec.get("status")!="VALID": raise RuntimeError(f"invalid run retained at {path}: {rec}")
    return rec

def p0():
    cases=[
      ("latency_small",["latency","--bytes","65536","--operations","1000000","--repetition","1"],65536),
      ("stream_read",["stream","--bytes","1048576","--operations","200000","--pattern","sequential","--read-pct","100","--repetition","1"],1048576),
      ("stream_write",["stream","--bytes","1048576","--operations","200000","--pattern","sequential","--read-pct","0","--repetition","1"],1048576),
      ("mix",["mix","--bytes","1048576","--operations","200000","--pattern","random","--read-pct","70","--repetition","1"],1048576),
      ("loaded_two",["loaded-latency","--workers","1","--probe-bytes","16777216","--worker-bytes","16777216","--warmup-ms","100","--duration-ms","300","--repetition","1"],33554432),
      ("tlb_small",["tlb","--pages","64","--operations","1000000","--repetition","1"],262144),
    ]
    for n,a,b in cases: run("smoke",n,a,b,"smoke_not_for_performance_analysis")

def p1():
    labels=[("L1",16384),("L2",524288),("LLC",16777216),("DRAM",536870912)]
    for label,b in labels:
      for rep in range(1,6): run("phase1",f"{label}_{rep}",["latency","--bytes",str(b),"--operations","0","--target-ms","250","--seed",str(43206320+rep),"--repetition",str(rep)],b)

def p2():
    b=GIB; ops=8_388_608
    for stride in (64,256,1024):
      for pattern in ("sequential","random"):
       for rp in (100,0):
        for rep in range(1,4): run("phase2",f"matrix_s{stride}_{pattern}_r{rp}_{rep}",["stream","--bytes",str(b),"--stride",str(stride),"--operations",str(ops),"--pattern",pattern,"--read-pct",str(rp),"--seed","43206320","--repetition",str(rep)],b)
    for pattern in ("sequential","random"):
      for rp in (100,70,50,0):
       for rep in range(1,4): run("phase2",f"mix_{pattern}_r{rp}_{rep}",["mix","--bytes",str(b),"--stride","64","--operations",str(ops),"--pattern",pattern,"--read-pct",str(rp),"--seed","43206320","--repetition",str(rep)],b)

def p3():
    for w in (0,1,2,4,8,12,15):
      alloc=512*1024**2+w*128*1024**2
      for rep in range(1,4): run("phase3",f"workers_{w}_{rep}",["loaded-latency","--workers",str(w),"--probe-bytes",str(512*1024**2),"--worker-bytes",str(128*1024**2),"--warmup-ms","1000","--duration-ms","5000","--seed",str(43206320+rep),"--repetition",str(rep)],alloc)

def p4():
    sizes=(16384,32768,49152,65536,131072,262144,524288,1048576,2097152,4194304,8388608,16777216,33554432,67108864,134217728,268435456,536870912,1073741824)
    for b in sizes:
      for rep in range(1,4): run("phase4",f"latency_{b}_{rep}",["latency","--bytes",str(b),"--operations","0","--target-ms","200","--seed",str(43206320+rep),"--repetition",str(rep)],b)
    for b in (32768,524288,16777216,134217728,1073741824):
      for rep in range(1,4): run("phase4",f"stream_{b}_{rep}",["stream","--bytes",str(b),"--stride","64","--operations","4194304","--pattern","sequential","--read-pct","100","--repetition",str(rep)],b)
    for pages in (16,64,256,1024,4096,16384):
      for rep in range(1,4): run("phase4",f"tlb_{pages}_{rep}",["tlb","--pages",str(pages),"--operations","0","--seed",str(43206320+rep),"--repetition",str(rep)],pages*4096)

def p5():
    total_ops=16_777_216
    for b,label in ((16*1024**2,"cache_reuse"),(GIB,"dram_sensitive")):
      for rep in range(1,4): run("phase5",f"{label}_{rep}",["stream","--bytes",str(b),"--stride","64","--operations",str(total_ops),"--pattern","sequential","--read-pct","100","--repetition",str(rep)],b)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("phase",choices=["smoke","phase1","phase2","phase3","phase4","phase5"]); ns=ap.parse_args()
    if not EXE.is_file(): raise SystemExit(f"missing {EXE}")
    {"smoke":p0,"phase1":p1,"phase2":p2,"phase3":p3,"phase4":p4,"phase5":p5}[ns.phase]()
if __name__=="__main__": main()

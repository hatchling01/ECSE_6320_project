# Reproduction Guide

## Environment and target

- Windows 11; FIO 3.43 at `C:\Program Files\fio\fio.exe`.
- Existing Python: `C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe`.
- Required imports: numpy 2.3.5, pandas 2.3.3, matplotlib 3.10.6.
- FIO always runs with cwd `benchmark_data` and basename `fio_production.bin`.
- Production range: 8 GiB; primary engine `windowsaio`; primary `direct=1`.

Do not call FIO directly. Use the hardened Python runners, which enforce target, free-space, and logical-write-budget gates. The scripts under `scripts/powershell` are reference-only; do not change PowerShell execution policy.

## Safety-only validation

```powershell
& 'C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe' scripts/python/test_safe_target.py
```

## Phase runners

The production runners are `run_phase2.py`, `run_phase3.py`, `run_phase4.py`, staged `run_phase5.py`, staged `run_phase6.py`, and `run_phase7.py`. Their source records every runtime, I/O bound, block size, QD, job count, mix, range, and repetition. Existing raw JSON is immutable; do not rerun into or overwrite it.

## Regenerate derived artifacts only

```powershell
& 'C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe' scripts/python/analyze_phase2.py
& 'C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe' scripts/python/analyze_phase3.py
& 'C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe' scripts/python/analyze_phase4.py
& 'C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe' scripts/python/analyze_phase5.py
& 'C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe' scripts/python/analyze_phase6.py
& 'C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe' scripts/python/analyze_phase7.py
& 'C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe' scripts/python/build_final_report.py
```

Canonical evidence is the FIO JSON in `data/raw` paired with validation metadata in `data/metadata`. Parsed CSV, Markdown, and PNG outputs are derived and regenerable.

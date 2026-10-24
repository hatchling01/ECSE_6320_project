# Mac source inventory

The read-only source was `C:/Users/CHOUDN3/Downloads/navnil-cache-memory-project/navnil-cache-memory-project`. It was not a Git repository. Before integration it contained 6,492 files totaling 672,289,713 bytes.

| Area | Evidence |
|---|---|
| Native source | `src/bench.c`, plus `validation/memory_probe.c` |
| Orchestration and analysis | `scripts/run.py`, `counters.py`, `analyze.py`, `check.py` |
| Build | `Makefile`; Apple Clang with C11 and pthreads |
| Dependencies | `requirements.txt`; recorded `software-versions.json` |
| Raw data | `data/raw/20261023-150209/measurements.csv`, JSONL, plan, logs, environment, counter exports |
| Processed data | `data/processed/summary.csv`, `counter_summary.csv`, `analysis.json` |
| Figures | Seven PNG and seven PDF plots |
| Report | `report/REPORT.md` |
| Validation | Feasibility source, scripts, logs, trial output, and summary |
| Reproduction | Root README and Make targets |

The monorepo copy contains all 139 files outside Instruments `.trace` directory trees (11,706,915 bytes before adding comparison artifacts). It excludes 6,353 trace-internal files totaling 660,582,798 bytes. Those bundles are large, profiler-generated, platform-specific, and may expose device identifiers, process names, or local paths. Their derived XML summaries, recording logs, status files, measurements, and validation summaries are retained. No scientific value was silently rewritten.

The pre-copy metadata manifest (sorted relative path, byte length, and UTC modification ticks) had SHA-256 `32775d50aa878adfac76a76d812eb88ad9d1d6c48a55fd83e523e92e91fd33fc`. This is an integrity guard for the non-Git source and is checked again after integration.

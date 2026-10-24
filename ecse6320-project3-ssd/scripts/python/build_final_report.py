"""Build the final Phase 8 Markdown reports from canonical parsed results."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from safe_target import repository_root


def row(df: pd.DataFrame, **conditions: object) -> pd.Series:
    selected = df
    for key, value in conditions.items():
        selected = selected[selected[key] == value]
    if len(selected) != 1:
        raise RuntimeError(f"Expected one row for {conditions}, found {len(selected)}")
    return selected.iloc[0]


def write(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def main() -> int:
    repo = repository_root()
    parsed = repo / "data" / "parsed"
    qd1 = pd.read_csv(parsed / "phase2_qd1_summary.csv")
    block = pd.read_csv(parsed / "phase3_block_pattern_summary.csv")
    mix = pd.read_csv(parsed / "phase4_mix_summary.csv")
    queue = pd.read_csv(parsed / "phase5_queue_summary.csv")
    tail = pd.read_csv(parsed / "phase6_tail_summary.csv")
    working = pd.read_csv(parsed / "phase6_working_set_summary.csv")
    phase6_runs = pd.read_csv(parsed / "phase6_runs.csv")
    pitfall = pd.read_csv(parsed / "phase7_pitfall_summary.csv")

    rr = row(qd1, configuration="randread_4k_qd1")
    rw = row(qd1, configuration="randwrite_4k_qd1")
    sr = row(qd1, configuration="seqread_128k_qd1")
    sw = row(qd1, configuration="seqwrite_128k_qd1")
    knee = row(queue, workload="4K random read", iodepth=16)
    qd32 = row(queue, workload="4K random read", iodepth=32)
    max4k = queue[queue.workload.str.startswith("4K")].loc[queue[queue.workload.str.startswith("4K")].total_iops_median.idxmax()]
    maxseq = queue[queue.workload == "128K sequential read"].loc[queue[queue.workload == "128K sequential read"].total_bw_bytes_s_median.idxmax()]
    max_block_iops = block.loc[block.total_iops_median.idxmax()]
    max_block_bw = block.loc[block.total_bw_bytes_s_median.idxmax()]
    tr8 = row(tail, workload="4K random read", iodepth=8, direction="read")
    tr16 = row(tail, workload="4K random read", iodepth=16, direction="read")
    ws_small = row(working, range_gib=0.25)
    ws_large = row(working, range_gib=8.0)
    device = phase6_runs[phase6_runs.configuration.str.startswith("device_state")].iloc[0]
    direct = row(pitfall, configuration="pitfall_direct")
    buffered1 = row(pitfall, configuration="pitfall_buffered_first")
    buffered2 = row(pitfall, configuration="pitfall_buffered_second")

    qd1_rows = "\n".join(
        f"| {r.configuration} | {r.total_iops_median:,.0f} | {r.total_bw_bytes_s_median/1024**2:,.1f} | {r.weighted_mean_clat_ns_median/1e3:,.1f} | {r.primary_p99_0_ns_median/1e3:,.1f} |"
        for _, r in qd1.iterrows()
    )
    mix_rows = "\n".join(
        f"| {int(r.read_pct)}/{int(r.write_pct)} | {r.total_iops_median:,.0f} | {r.total_bw_bytes_s_median/1024**2:,.1f} | {r.weighted_mean_clat_ns_median/1e3:,.1f} |"
        for _, r in mix.sort_values("read_pct", ascending=False).iterrows()
    )

    readme = f"""
# SSD Performance Profiling on KIOXIA KXG80ZNV1T02

## 1. Objective

This project profiles host-visible SSD performance across access pattern, block size, read/write mix, queue depth, tail latency, active range, device state, and one deliberately misleading buffered-I/O setup. Every measurement uses one disposable regular file; no raw disk, partition, or volume was targeted.

## 2. Safety strategy

The Python runner canonicalizes the target before every FIO invocation, permits only `benchmark_data/fio_production.bin`, sets the working directory to `benchmark_data`, passes only the basename to `--filename`, and verifies the reconstructed filename from actual FIO JSON afterward. It also enforces a 100 GiB free-space floor, an 80 GiB logical-write budget, immutable raw outputs, and `direct=0` only for Phase 7. The production file is ignored by Git.

## 3. Pre-experiment hypotheses

The twelve unchanged hypotheses are in [docs/hypotheses.md](docs/hypotheses.md); their measured outcomes are in [docs/hypothesis_outcomes.md](docs/hypothesis_outcomes.md).

## 4. Hardware/software environment

The system SSD is a KIOXIA KXG80ZNV1T02 REV2 (APGA4102), NVMe, 953.87 GiB usable, on Windows 11 Enterprise. Measurements used official FIO 3.43 at `C:\\Program Files\\fio\\fio.exe`, `windowsaio`, and the existing Anaconda Python 3.13.9 stack. See [docs/environment.md](docs/environment.md).

## 5. Experimental methodology

Primary runs use `direct=1`, one 8 GiB initialized regular file, FIO JSON, explicit percentile collection, and three independent repetitions per ordinary configuration. Read jobs use bounded time windows; write-capable jobs use bounded logical I/O. Canonical raw JSON lives under `data/raw`; regenerated run/summary CSVs live under `data/parsed`. The Phase 0/1 smoke artifacts are excluded from performance analysis.

## 6. QD=1 baselines

| Workload | Median IOPS | Median MiB/s | Mean clat us | p99 us |
|---|---:|---:|---:|---:|
{qd1_rows}

The identity `IOPS x block size ~= throughput` passed within 0.2% for every baseline run. See [QD1 table](results/tables/qd1_baseline.md) and [analysis](docs/phase2_qd1_analysis.md).

![QD1 latency](results/plots/phase2_qd1_latency.png)

## 7. Block-size effects

At fixed QD1, small blocks emphasized IOPS while larger transfers raised bandwidth and completion latency. The highest matrix median was {max_block_iops.total_iops_median:,.0f} IOPS for {max_block_iops.pattern} {max_block_iops.direction} at {max_block_iops.bs}; the highest matrix throughput was {max_block_bw.total_bw_bytes_s_median/1024**2:,.1f} MiB/s for {max_block_bw.pattern} {max_block_bw.direction} at {max_block_bw.bs}. These are QD1 results, not device maxima.

![Block-size throughput](results/plots/phase3_throughput_vs_block_size.png)

## 8. Random vs sequential access

The full 24-configuration Phase 3 matrix separates random/sequential and read/write behavior across 4, 16, 32, 64, 128, and 256 KiB. Sequential large-block access reached much higher bandwidth than 4 KiB random access, supporting the pre-experiment pattern hypothesis within this host stack.

## 9. Read vs write behavior

Read and write endpoints differed substantially. At QD1, 4 KiB random write measured {rw.total_iops_median:,.0f} IOPS versus {rr.total_iops_median:,.0f} for random read; 128 KiB sequential write measured {sw.total_bw_bytes_s_median/1024**2:,.1f} MiB/s versus {sr.total_bw_bytes_s_median/1024**2:,.1f} for read. These are observed results, not evidence of a specific controller or NAND mechanism.

## 10. Read/write mixes

| Read/write | Median IOPS | Median MiB/s | Weighted mean clat us |
|---|---:|---:|---:|
{mix_rows}

The mixed points were not a simple linear interpolation of pure endpoints, and direction-specific tail distributions differed. See [Phase 4 analysis](docs/phase4_mix_analysis.md).

## 11. Queue-depth scaling

4 KiB random-read IOPS rose from {row(queue, workload='4K random read', iodepth=1).total_iops_median:,.0f} at QD1 to {knee.total_iops_median:,.0f} at QD16 and peaked at {max4k.total_iops_median:,.0f} at QD{int(max4k.iodepth)}. QD64 was lower and much slower in latency, so QD128/256 were not scientifically justified.

![QD scaling](results/plots/phase5_iops_vs_qd.png)

## 12. Throughput-latency knee

The predeclared numerical rule selects the earliest QD whose next doubling adds less than 10% median IOPS while raising mean completion latency by at least 20%. It identifies QD16: QD16 to QD32 added {knee.next_iops_gain_pct:.1f}% IOPS while latency rose {knee.next_latency_gain_pct:.1f}%.

![Knee](results/plots/phase5_throughput_latency_knee.png)

## 13. Little's Law

At QD16, `L_inferred = IOPS x mean_clat` was {knee.l_inferred_median:.2f}, versus configured `iodepth=16`; at QD32 it was {qd32.l_inferred_median:.2f}. The trend is queueing-consistent, but configured submission depth and inferred average occupancy are not identical because of host scheduling, batching, and latency accounting boundaries.

## 14. Tail latency

For 4 KiB random read at QD8, p50/p95/p99/p99.9 were {tr8.p50_0_ns_median/1e3:.1f}/{tr8.p95_0_ns_median/1e3:.1f}/{tr8.p99_0_ns_median/1e3:.1f}/{tr8.p99_9_ns_median/1e3:.1f} us. At the QD16 knee they were {tr16.p50_0_ns_median/1e3:.1f}/{tr16.p95_0_ns_median/1e3:.1f}/{tr16.p99_0_ns_median/1e3:.1f}/{tr16.p99_9_ns_median/1e3:.1f} us. Millions of completed read I/Os make p99.9 interpretable with thousands of tail observations.

![Tail percentiles](results/plots/phase6_tail_percentiles.png)

## 15. Working-set / LBA-range

At fixed 4 KiB random read QD16, the 256 MiB range produced {ws_small.total_iops_median:,.0f} median IOPS and the 8 GiB range {ws_large.total_iops_median:,.0f}; p99 was {ws_small.read_p99_0_median/1e3:.1f} versus {ws_large.read_p99_0_median/1e3:.1f} us. The small difference is host-visible and does not identify a physical NAND boundary.

## 16. Burst vs sustained/device-state behavior

One safe 8 GiB direct sequential-write pass at 1 MiB/QD8 completed at {device.total_bw_bytes_s/1024**2:,.1f} MiB/s in {device.write_runtime_ms/1000:.2f} s. The 1-second logger produced only one interval, so early/middle/late behavior is unresolved. No clear burst-to-steady-state transition was observed within the safe 8 GiB test window, and temperature telemetry was unavailable.

## 17. Benchmark pitfalls

The immediate second buffered pass reached {buffered2.total_bw_bytes_s_median/1024**2:,.1f} MiB/s, versus {buffered1.total_bw_bytes_s_median/1024**2:,.1f} MiB/s for the first buffered pass and {direct.total_bw_bytes_s_median/1024**2:,.1f} MiB/s for direct I/O. This demonstrates host page-cache contamination. Other pitfalls include Windows FIO colon parsing for absolute paths, QD/occupancy confusion, short bursts, sparse tail samples, device-state uncertainty, and noise.

![Buffered pitfall](results/plots/phase7_buffered_vs_direct.png)

## 18. Anomalies

The Phase 0 absolute-path smoke attempt exposed FIO's Windows colon parsing and created an unintended regular file named `C`; it was safely audited, explicitly authorized for deletion, and its invalid artifacts remain excluded. Phase 4 analysis initially rejected empty inactive-direction percentile fields; the parser was corrected to preserve them as missing, and no FIO run was repeated. The device-state log contained only one interval due to the short completion time.

## 19. Limitations

This is a regular-file study on the boot/system SSD through the Windows storage stack, not raw-device testing. No device-internal temperature, wear, NAND, garbage-collection, or SLC telemetry was available. Logical FIO writes are not physical NAND writes. Direct I/O reduces page-cache effects but does not expose all internal caching. Short safe state testing may not reach steady state, and extreme percentiles remain sample-count dependent.

## 20. Reproducibility

See [docs/reproduction.md](docs/reproduction.md), [final requirement audit](docs/final_requirement_audit.md), [final figures](results/plots/FINAL_FIGURES.md), and [final tables](results/tables/FINAL_TABLES.md). Python is the supported executable workflow because `.ps1` execution is restricted; no PowerShell policy change is required.

## 21. Conclusions

The tested stack transitions from QD-limited scaling to a QD16 knee, reaches {max4k.total_iops_median:,.0f} median 4 KiB IOPS and {maxseq.total_bw_bytes_s_median/1024**2:,.1f} MiB/s median 128 KiB sequential-read throughput within the measured matrix, and shows sharply rising tails with concurrency. Block size, access pattern, direction, and mix all materially affect results. Buffered repeat reads can overstate apparent storage throughput by an order of magnitude.

## 22. AI-use statement

Codex assisted with safety scripting, experiment orchestration, parsing, plotting, statistics, repository organization, and analysis drafting. Claims are grounded in retained FIO JSON, repeated measurements, target validation, and regenerable summaries; AI did not independently verify internal SSD behavior. See [docs/ai_use.md](docs/ai_use.md).
"""
    write(repo / "README.md", readme)

    outcomes = f"""
# Final Hypothesis Outcomes

The original wording remains unchanged in `docs/hypotheses.md`.

| # | Outcome | Evidence |
|---:|---|---|
| 1 | Supported | QD1 exposed 56.9 us mean clat for 4 KiB random read while throughput was 61.6 MiB/s. |
| 2 | Supported | 4 KiB random-read IOPS increased from {row(queue, workload='4K random read', iodepth=1).total_iops_median:,.0f} at QD1 to {knee.total_iops_median:,.0f} at QD16. |
| 3 | Supported | QD16-to-QD32 gained only {knee.next_iops_gain_pct:.1f}% IOPS while latency rose {knee.next_latency_gain_pct:.1f}%. |
| 4 | Supported | Larger blocks traded IOPS for bandwidth; 256 KiB sequential write reached {max_block_bw.total_bw_bytes_s_median/1024**2:,.1f} MiB/s at QD1. |
| 5 | Supported | Sequential large-block bandwidth substantially exceeded small-block random bandwidth. |
| 6 | Supported | Read/write endpoints differed across QD1, mix, and concurrency results; no internal cause is asserted. |
| 7 | Supported | 100/0, 70/30, 50/50, and 0/100 produced distinct IOPS and direction-specific latency distributions. |
| 8 | Supported | Read p50 rose from {tr8.p50_0_ns_median/1e3:.1f} to {tr16.p50_0_ns_median/1e3:.1f} us from QD8 to QD16, while p99.9 rose from {tr8.p99_9_ns_median/1e3:.1f} to {tr16.p99_9_ns_median/1e3:.1f} us. |
| 9 | Not resolved | The safe 8 GiB pass completed in {device.write_runtime_ms/1000:.2f} s and yielded one 1-second log interval. |
| 10 | Supported | The immediate buffered second pass reached {buffered2.total_bw_bytes_s_median/1024**2:,.1f} MiB/s, far above direct I/O. |
| 11 | Partially supported | Range affected results slightly ({ws_small.total_iops_median:,.0f} versus {ws_large.total_iops_median:,.0f} IOPS), but the effect was small. |
| 12 | Supported | Inferred L tracked QD but differed from configured depth, including {knee.l_inferred_median:.2f} at configured QD16. |
"""
    write(repo / "docs" / "hypothesis_outcomes.md", outcomes)

    audit_items = [
        ("Safe regular-file setup", "COMPLETE", "`scripts/python/fio_runner.py`, `docs/safety.md`"),
        ("Direct I/O primary data", "COMPLETE", "Metadata in `data/metadata/phase2` through `phase6`"),
        ("QD1 4 KiB random read/write", "COMPLETE", "`data/parsed/phase2_qd1_summary.csv`"),
        ("QD1 128 KiB sequential read/write", "COMPLETE", "`results/tables/qd1_baseline.md`"),
        ("p95/p99 baseline latency", "COMPLETE", "`results/tables/qd1_baseline.md`"),
        ("Required block sizes and sequential/random patterns", "COMPLETE", "`data/parsed/phase3_block_pattern_summary.csv`"),
        ("100/0, 70/30, 50/50, 0/100 mixes", "COMPLETE", "`data/parsed/phase4_mix_summary.csv`"),
        ("Queue-depth scaling and throughput-latency curve", "COMPLETE", "`docs/phase5_queue_analysis.md`"),
        ("Numerical knee", "COMPLETE", "QD16 criterion in `docs/phase5_queue_analysis.md`"),
        ("Little's Law", "COMPLETE", "`results/plots/phase5_little_law.png`"),
        ("p50/p95/p99/p99.9 tail analysis", "COMPLETE", "`results/tables/phase6_tail_latency.md`"),
        ("Working-set/LBA range", "COMPLETE", "`data/parsed/phase6_working_set_summary.csv`"),
        ("Device-state discussion", "COMPLETE", "Safe 8 GiB pass and bounded interpretation in `docs/phase6_tail_state_analysis.md`"),
        ("Device-state time-series resolution", "LIMITATION", "Only one 1-second log interval; temporal transition unresolved"),
        ("Misleading buffered benchmark", "COMPLETE", "`docs/phase7_pitfall_analysis.md`"),
        ("Raw and parsed data", "COMPLETE", "`data/raw`, `data/parsed`"),
        ("Configs/scripts/plots", "COMPLETE", "`scripts/python`, `results/plots`"),
        ("Environment", "COMPLETE", "`docs/environment.md`"),
        ("Repetitions/statistics", "COMPLETE", "Three reps and median/mean/std/CV in summary CSVs"),
        ("AI-use note", "COMPLETE", "`docs/ai_use.md`"),
        ("Anomalies/limitations", "COMPLETE", "README sections 18-19 and `docs/anomalies.md`"),
    ]
    audit_rows = "\n".join(f"| {name} | {status} | {evidence} |" for name, status, evidence in audit_items)
    write(repo / "docs" / "final_requirement_audit.md", f"""
# Final Requirement Audit

| Requirement | Status | Repository evidence |
|---|---|---|
{audit_rows}

The LIMITATION is a measurement-window constraint, not a missing safety control or omitted required discussion. No unsupported burst/cache/thermal causal claim is made.
""")

    write(repo / "docs" / "reproduction.md", r"""
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
""")

    figures = [
        ("QD1 latency", "phase2_qd1_latency.png"),
        ("Block-size IOPS", "phase3_iops_vs_block_size.png"),
        ("Block-size throughput", "phase3_throughput_vs_block_size.png"),
        ("Block-size latency", "phase3_latency_vs_block_size.png"),
        ("Read/write mix IOPS", "phase4_mix_iops.png"),
        ("Queue-depth scaling", "phase5_iops_vs_qd.png"),
        ("Throughput-latency knee", "phase5_throughput_latency_knee.png"),
        ("Little's-Law occupancy", "phase5_little_law.png"),
        ("Tail percentiles", "phase6_tail_percentiles.png"),
        ("Working-set effect", "phase6_working_set.png"),
        ("Buffered-vs-direct pitfall", "phase7_buffered_vs_direct.png"),
    ]
    figure_lines = "\n".join(f"{i}. [{label}]({filename})" for i, (label, filename) in enumerate(figures, 1))
    write(repo / "results" / "plots" / "FINAL_FIGURES.md", f"# Final Figure Set\n\n{figure_lines}\n\nThe single-sample device-state plot remains available as `phase6_device_state_bandwidth.png` but is excluded from the strongest figure set because it cannot establish a time trend.")

    final_tables = f"""
# Final Table Set

## Environment

| Item | Value |
|---|---|
| SSD | KIOXIA KXG80ZNV1T02 REV2, firmware APGA4102 |
| Interface / filesystem | NVMe / NTFS |
| OS | Windows 11 Enterprise build 26200 |
| FIO | 3.43, windowsaio |
| Python | Anaconda Python 3.13.9 |
| Target | One 8 GiB regular file, basename-only FIO target |

## QD1 baseline

| Workload | Median IOPS | Median MiB/s | Mean clat us | p99 us |
|---|---:|---:|---:|---:|
{qd1_rows}

## Block-size/pattern headlines

| Metric | Configuration | Result |
|---|---|---:|
| Highest QD1 IOPS | {max_block_iops.pattern} {max_block_iops.direction}, {max_block_iops.bs} | {max_block_iops.total_iops_median:,.0f} IOPS |
| Highest QD1 throughput | {max_block_bw.pattern} {max_block_bw.direction}, {max_block_bw.bs} | {max_block_bw.total_bw_bytes_s_median/1024**2:,.1f} MiB/s |

## Read/write mix

| Read/write | Median IOPS | Median MiB/s | Weighted mean clat us |
|---|---:|---:|---:|
{mix_rows}

## Queue-depth and knee

| Item | Result |
|---|---:|
| Knee | QD16 |
| QD16 4 KiB random-read IOPS | {knee.total_iops_median:,.0f} |
| QD16 mean clat | {knee.weighted_mean_clat_ns_median/1e3:,.1f} us |
| QD16 inferred L | {knee.l_inferred_median:.2f} |
| Maximum observed 4 KiB IOPS | {max4k.total_iops_median:,.0f} at QD{int(max4k.iodepth)} |
| Maximum observed 128 KiB sequential read | {maxseq.total_bw_bytes_s_median/1024**2:,.1f} MiB/s at QD{int(maxseq.iodepth)} |

## Tail latency

| QD | p50 us | p95 us | p99 us | p99.9 us | Median completed reads |
|---:|---:|---:|---:|---:|---:|
| 8 | {tr8.p50_0_ns_median/1e3:.1f} | {tr8.p95_0_ns_median/1e3:.1f} | {tr8.p99_0_ns_median/1e3:.1f} | {tr8.p99_9_ns_median/1e3:.1f} | {tr8.completed_ios_median:,.0f} |
| 16 | {tr16.p50_0_ns_median/1e3:.1f} | {tr16.p95_0_ns_median/1e3:.1f} | {tr16.p99_0_ns_median/1e3:.1f} | {tr16.p99_9_ns_median/1e3:.1f} | {tr16.completed_ios_median:,.0f} |

## Working set

| Active range | Median IOPS | p99 us |
|---:|---:|---:|
| 256 MiB | {ws_small.total_iops_median:,.0f} | {ws_small.read_p99_0_median/1e3:.1f} |
| 8 GiB | {ws_large.total_iops_median:,.0f} | {ws_large.read_p99_0_median/1e3:.1f} |

## Device state

| Pass | Size | Median/aggregate throughput | Time-series evidence |
|---|---:|---:|---|
| Sequential write, 1 MiB, QD8 | 8 GiB | {device.total_bw_bytes_s/1024**2:,.1f} MiB/s | One 1-second interval; transition unresolved |

## Buffered pitfall

| Setup | Median MiB/s | Mean clat us |
|---|---:|---:|
| Direct | {direct.total_bw_bytes_s_median/1024**2:,.1f} | {direct.weighted_mean_clat_ns_median/1e3:,.1f} |
| Buffered first | {buffered1.total_bw_bytes_s_median/1024**2:,.1f} | {buffered1.weighted_mean_clat_ns_median/1e3:,.1f} |
| Buffered immediate second | {buffered2.total_bw_bytes_s_median/1024**2:,.1f} | {buffered2.weighted_mean_clat_ns_median/1e3:,.1f} |

## Hypotheses and limitations

See [hypothesis outcomes](../../docs/hypothesis_outcomes.md) and the final report's [limitations](../../README.md#19-limitations). Detailed canonical summaries remain in `data/parsed`.
"""
    write(repo / "results" / "tables" / "FINAL_TABLES.md", final_tables)

    write(repo / "docs" / "ai_use.md", """
# AI-Use Disclosure

Codex assisted with repository organization, safety scripting, FIO configuration, experiment orchestration, parsing, plotting, statistical summaries, documentation, and analysis drafting.

Claims in this repository are grounded in actual retained FIO JSON, pre- and post-run target validation, repeated measurements, parser checks, and explicit methodology. Derived CSVs, figures, and reports are regenerable from canonical raw data. Codex did not independently verify or infer internal SSD behavior such as NAND placement, write amplification, garbage collection, SLC-cache boundaries, or thermal throttling.

The student remains responsible for reviewing the commands, evidence, interpretations, limitations, and final submission.
""")
    print("Final README, audit, hypothesis outcomes, reproduction guide, and indexes generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Analyze Phase 6 tail latency, working set, and device-state evidence."""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from collect_results import collect_phase
from safe_target import repository_root


PERCENTILES = ("p50_0", "p95_0", "p99_0", "p99_9")


def main() -> int:
    repo = repository_root()
    runs = pd.DataFrame(collect_phase("phase6"))
    if len(runs) != 22 or runs.configuration.nunique() != 8:
        raise RuntimeError("Phase 6 gate requires 22 valid runs across 8 configurations")
    runs.to_csv(repo / "data" / "parsed" / "phase6_runs.csv", index=False)

    tail = runs[runs.configuration.str.startswith("tail_")].copy()
    tail["workload"] = np.where(tail.rw.eq("randread"), "4K random read", "4K random 70/30")
    tail_records = []
    for (workload, qd), group in tail.groupby(["workload", "iodepth"]):
        directions = ("read",) if workload == "4K random read" else ("read", "write")
        for direction in directions:
            row = {"workload": workload, "iodepth": int(qd), "direction": direction, "repetitions": len(group)}
            for pct in PERCENTILES:
                row[f"{pct}_ns_median"] = pd.to_numeric(group[f"{direction}_{pct}"], errors="coerce").median()
            row["completed_ios_median"] = pd.to_numeric(group[f"{direction}_total_ios"]).median()
            row["iops_median"] = pd.to_numeric(group[f"{direction}_iops"]).median()
            tail_records.append(row)
    tail_summary = pd.DataFrame(tail_records).sort_values(["workload", "iodepth", "direction"])
    tail_summary.to_csv(repo / "data" / "parsed" / "phase6_tail_summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 5))
    labels, x = [], np.arange(len(tail_summary))
    for pct, marker in zip(PERCENTILES, ("o", "s", "^", "D")):
        ax.plot(x, tail_summary[f"{pct}_ns_median"] / 1e3, marker=marker, label=pct.replace("_", "."))
    for row in tail_summary.itertuples():
        labels.append(f"{row.workload.replace('4K random ', '')}\nQD{row.iodepth} {row.direction}")
    ax.set_xticks(x, labels, rotation=25, ha="right")
    ax.set_yscale("log")
    ax.set_ylabel("Completion latency (us)")
    ax.set_title("Tail-latency percentiles at mid-QD and knee")
    ax.grid(alpha=.25, which="both"); ax.legend(); fig.tight_layout()
    fig.savefig(repo / "results" / "plots" / "phase6_tail_percentiles.png", dpi=180); plt.close(fig)

    working = runs[runs.configuration.str.startswith("working_set")].copy()
    work_records = []
    for size, group in working.groupby("size_bytes"):
        row = {"range_bytes": int(size), "range_gib": int(size) / 1024**3, "repetitions": len(group)}
        for metric in ("total_iops", "weighted_mean_clat_ns", "read_p99_0"):
            values = pd.to_numeric(group[metric], errors="coerce")
            row[f"{metric}_median"] = values.median()
            row[f"{metric}_cv_pct"] = values.std(ddof=1) / values.mean() * 100
        work_records.append(row)
    working_summary = pd.DataFrame(work_records).sort_values("range_bytes")
    working_summary.to_csv(repo / "data" / "parsed" / "phase6_working_set_summary.csv", index=False)
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(working_summary.range_gib, working_summary.total_iops_median, "o-", color="tab:blue", label="IOPS")
    ax1.set(xscale="log", xlabel="Active range (GiB)", ylabel="Median IOPS", title="4 KiB random-read working-set effect at QD16")
    ax2 = ax1.twinx(); ax2.plot(working_summary.range_gib, working_summary.read_p99_0_median / 1e3, "s--", color="tab:red", label="p99")
    ax2.set_ylabel("Median p99 completion latency (us)")
    ax1.grid(alpha=.25); fig.tight_layout()
    fig.savefig(repo / "results" / "plots" / "phase6_working_set.png", dpi=180); plt.close(fig)

    device = runs[runs.configuration.str.startswith("device_state")].iloc[0]
    metadata_path = next((repo / "data" / "metadata" / "phase6").glob("*device_state*.json"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    bw_path = repo / metadata["bandwidth_logs"][0]
    bw = pd.read_csv(bw_path, header=None, names=["time_ms", "bw_kib_s", "direction", "bs", "offset"])
    bw["bw_mib_s"] = bw.bw_kib_s / 1024
    bw.to_csv(repo / "data" / "parsed" / "phase6_device_state_bandwidth.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(bw.time_ms / 1000, bw.bw_mib_s, "o-")
    ax.set(xlabel="Elapsed time (s)", ylabel="Logged bandwidth (MiB/s)", title="8 GiB sequential-write observation (1 s logging)")
    if len(bw) < 3:
        ax.text(.5, .15, "Only one averaged interval: early/middle/late comparison unresolved", transform=ax.transAxes, ha="center")
    ax.grid(alpha=.25); fig.tight_layout()
    fig.savefig(repo / "results" / "plots" / "phase6_device_state_bandwidth.png", dpi=180); plt.close(fig)

    table = ["# Phase 6 Tail Latency", "", "| Workload | QD | Direction | p50 us | p95 us | p99 us | p99.9 us | Median I/Os |", "|---|---:|---|---:|---:|---:|---:|---:|"]
    for row in tail_summary.itertuples():
        table.append(f"| {row.workload} | {row.iodepth} | {row.direction} | {row.p50_0_ns_median/1e3:.1f} | {row.p95_0_ns_median/1e3:.1f} | {row.p99_0_ns_median/1e3:.1f} | {row.p99_9_ns_median/1e3:.1f} | {row.completed_ios_median:,.0f} |")
    (repo / "results" / "tables" / "phase6_tail_latency.md").write_text("\n".join(table) + "\n", encoding="utf-8")

    read8 = tail_summary[(tail_summary.workload == "4K random read") & (tail_summary.iodepth == 8)].iloc[0]
    read16 = tail_summary[(tail_summary.workload == "4K random read") & (tail_summary.iodepth == 16)].iloc[0]
    small = working_summary.iloc[0]; large = working_summary.iloc[-1]
    transition = "No clear burst-to-steady-state transition was observed within the safe 8 GiB test window."
    doc = f"""# Phase 6: Tail Latency, Working Set, and Device State

## Tail latency

QD8 represents mid-concurrency and QD16 is the Phase 5 knee. For 4 KiB random read, median p50/p95/p99/p99.9 at QD8 were {read8.p50_0_ns_median/1e3:.1f}/{read8.p95_0_ns_median/1e3:.1f}/{read8.p99_0_ns_median/1e3:.1f}/{read8.p99_9_ns_median/1e3:.1f} us; at QD16 they were {read16.p50_0_ns_median/1e3:.1f}/{read16.p95_0_ns_median/1e3:.1f}/{read16.p99_0_ns_median/1e3:.1f}/{read16.p99_9_ns_median/1e3:.1f} us. Each read run completed well over one million I/Os, so p99.9 represents thousands of tail observations. The bounded mixed runs completed about 262 thousand total I/Os each, still providing hundreds of observations in each direction near the 0.1% tail.

## Working set

At fixed 4 KiB random read and QD16, the 256 MiB and 8 GiB active ranges produced {small.total_iops_median:,.0f} and {large.total_iops_median:,.0f} median IOPS, respectively. These are host-visible range effects only; an active byte range does not identify physical NAND placement or an internal cache boundary.

## Device-state observation

One bounded direct sequential-write pass covered exactly 8 GiB with 1 MiB blocks at QD8. It completed at {device.total_bw_bytes_s/1024**2:,.1f} MiB/s. FIO's 1-second logger emitted only {len(bw)} averaged interval because the pass completed in roughly {float(device.write_runtime_ms)/1000:.2f} s. Consequently, an early/middle/late comparison is unresolved rather than evidence of stability. {transition} Temperature telemetry was unavailable, so thermal causality cannot be evaluated.
"""
    (repo / "docs" / "phase6_tail_state_analysis.md").write_text(doc, encoding="utf-8")
    print(f"Phase 6: {len(runs)} runs; device log samples={len(bw)}; cumulative device write={device.logical_bytes_written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

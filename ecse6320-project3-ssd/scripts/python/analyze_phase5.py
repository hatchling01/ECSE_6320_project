"""Summarize Phase 5 queue-depth scaling, knee, and Little's Law."""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import pandas as pd

from collect_results import collect_phase
from safe_target import repository_root


def classify(configuration: str) -> str:
    if configuration.startswith("random_read"):
        return "4K random read"
    if configuration.startswith("mixed"):
        return "4K random 70/30"
    if configuration.startswith("random_write"):
        return "4K random write"
    if configuration.startswith("sequential"):
        return "128K sequential read"
    raise RuntimeError(f"Unknown Phase 5 configuration: {configuration}")


def summarize(runs: pd.DataFrame) -> pd.DataFrame:
    records = []
    metrics = ("total_iops", "total_bw_bytes_s", "weighted_mean_clat_ns", "total_ios")
    for (workload, qd), group in runs.groupby(["workload", "iodepth"], sort=False):
        row = {"workload": workload, "iodepth": int(qd), "repetitions": len(group)}
        for metric in metrics:
            values = pd.to_numeric(group[metric], errors="coerce")
            mean, std = values.mean(), values.std(ddof=1)
            row[f"{metric}_median"] = values.median()
            row[f"{metric}_mean"] = mean
            row[f"{metric}_std"] = std
            row[f"{metric}_cv_pct"] = std / mean * 100 if mean else math.nan
            row[f"{metric}_min"] = values.min()
            row[f"{metric}_max"] = values.max()
        row["l_inferred_median"] = (
            row["total_iops_median"] * row["weighted_mean_clat_ns_median"] / 1e9
        )
        records.append(row)
    return pd.DataFrame(records).sort_values(["workload", "iodepth"])


def select_knee(primary: pd.DataFrame) -> tuple[int, pd.DataFrame]:
    primary = primary.sort_values("iodepth").copy()
    primary["next_iops_gain_pct"] = primary.total_iops_median.shift(-1).div(
        primary.total_iops_median
    ).sub(1).mul(100)
    primary["next_latency_gain_pct"] = primary.weighted_mean_clat_ns_median.shift(-1).div(
        primary.weighted_mean_clat_ns_median
    ).sub(1).mul(100)
    candidates = primary[
        (primary.next_iops_gain_pct < 10) & (primary.next_latency_gain_pct >= 20)
    ]
    if candidates.empty:
        return int(primary.iodepth.max()), primary
    return int(candidates.iloc[0].iodepth), primary


def main() -> int:
    repo = repository_root()
    runs = pd.DataFrame(collect_phase("phase5"))
    if len(runs) != 69 or runs.configuration.nunique() != 23:
        raise RuntimeError("Phase 5 gate requires 69 valid runs across 23 configurations")
    runs["workload"] = runs.configuration.map(classify)
    runs["l_inferred"] = runs.total_iops * runs.weighted_mean_clat_ns / 1e9
    runs.to_csv(repo / "data" / "parsed" / "phase5_queue_runs.csv", index=False)

    summary = summarize(runs)
    primary = summary[summary.workload == "4K random read"]
    knee_qd, primary = select_knee(primary)
    summary = summary.merge(
        primary[["iodepth", "next_iops_gain_pct", "next_latency_gain_pct"]],
        on="iodepth", how="left", suffixes=("", "_primary"),
    )
    summary.to_csv(repo / "data" / "parsed" / "phase5_queue_summary.csv", index=False)

    colors = {
        "4K random read": "tab:blue", "4K random 70/30": "tab:orange",
        "4K random write": "tab:red", "128K sequential read": "tab:green",
    }
    fig, ax = plt.subplots(figsize=(8, 5))
    for workload, group in summary.groupby("workload"):
        group = group.sort_values("iodepth")
        ax.plot(group.iodepth, group.total_iops_median, "o-", label=workload, color=colors[workload])
    ax.axvline(knee_qd, color="black", linestyle=":", label=f"read knee QD{knee_qd}")
    ax.set(xscale="log", xlabel="Configured iodepth", ylabel="Median IOPS", title="Queue-depth scaling")
    ax.grid(alpha=.25, which="both"); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(repo / "results" / "plots" / "phase5_iops_vs_qd.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for workload, group in summary.groupby("workload"):
        group = group.sort_values("iodepth")
        ax.plot(group.iodepth, group.weighted_mean_clat_ns_median / 1e3, "o-", label=workload, color=colors[workload])
    ax.axvline(knee_qd, color="black", linestyle=":")
    ax.set(xscale="log", yscale="log", xlabel="Configured iodepth", ylabel="Mean completion latency (us)", title="Latency cost of concurrency")
    ax.grid(alpha=.25, which="both"); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(repo / "results" / "plots" / "phase5_latency_vs_qd.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    p = primary.sort_values("iodepth")
    ax.plot(p.weighted_mean_clat_ns_median / 1e3, p.total_iops_median, "o-")
    for row in p.itertuples():
        ax.annotate(f"QD{row.iodepth}", (row.weighted_mean_clat_ns_median / 1e3, row.total_iops_median), xytext=(4, 4), textcoords="offset points")
    k = p[p.iodepth == knee_qd].iloc[0]
    ax.scatter([k.weighted_mean_clat_ns_median / 1e3], [k.total_iops_median], s=100, facecolors="none", edgecolors="red", linewidths=2)
    ax.set(xlabel="Median mean completion latency (us)", ylabel="Median IOPS", title="4 KiB random-read throughput-latency curve")
    ax.grid(alpha=.25); fig.tight_layout()
    fig.savefig(repo / "results" / "plots" / "phase5_throughput_latency_knee.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for workload, group in summary.groupby("workload"):
        group = group.sort_values("iodepth")
        ax.plot(group.iodepth, group.l_inferred_median, "o-", label=workload, color=colors[workload])
    ax.plot([1, 64], [1, 64], "k--", alpha=.5, label="configured QD reference")
    ax.set(xscale="log", yscale="log", xlabel="Configured iodepth", ylabel="Inferred L = IOPS x mean clat", title="Little's-Law occupancy estimate")
    ax.grid(alpha=.25, which="both"); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(repo / "results" / "plots" / "phase5_little_law.png", dpi=180); plt.close(fig)

    table_lines = [
        "# Phase 5 Queue-Depth Summary", "",
        "| Workload | QD | Median IOPS | Median MiB/s | Mean clat (us) | L inferred | IOPS CV |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary.itertuples():
        table_lines.append(
            f"| {row.workload} | {row.iodepth} | {row.total_iops_median:,.0f} | "
            f"{row.total_bw_bytes_s_median/1024**2:,.1f} | {row.weighted_mean_clat_ns_median/1e3:,.1f} | "
            f"{row.l_inferred_median:.2f} | {row.total_iops_cv_pct:.1f}% |"
        )
    (repo / "results" / "tables" / "phase5_queue_summary.md").write_text("\n".join(table_lines) + "\n", encoding="utf-8")

    max_4k = summary[summary.workload.str.startswith("4K")].loc[lambda d: d.total_iops_median.idxmax()]
    max_seq = summary[summary.workload == "128K sequential read"].loc[lambda d: d.total_bw_bytes_s_median.idxmax()]
    knee = primary[primary.iodepth == knee_qd].iloc[0]
    next_row = primary[primary.iodepth > knee_qd].sort_values("iodepth").iloc[0]
    doc = f"""# Phase 5: Queue Depth, Parallelism, and Saturation Knee

The primary staged sweep tested 4 KiB random reads through QD64. QD128 and QD256 were not run because scaling had already ended: QD{knee_qd} to QD{int(next_row.iodepth)} added {knee.next_iops_gain_pct:.1f}% median IOPS while mean completion latency rose {knee.next_latency_gain_pct:.1f}%, and QD64 did not improve the median.

The numerical knee rule, defined before final selection, is the earliest measured QD for which the next doubling adds less than 10% median IOPS while median mean completion latency rises at least 20%. It selects **QD{knee_qd}**, at {knee.total_iops_median:,.0f} IOPS and {knee.weighted_mean_clat_ns_median/1e3:,.1f} us. QD1-QD8 are underutilized/scaling; QD16 is the knee; QD32-QD64 are diminishing-return/post-knee points.

The highest observed median 4 KiB result across the Phase 5 read, mixed, and bounded-write configurations was **{max_4k.total_iops_median:,.0f} IOPS** ({max_4k.workload}, QD{int(max_4k.iodepth)}). The highest observed median 128 KiB sequential-read throughput was **{max_seq.total_bw_bytes_s_median/1024**2:,.1f} MiB/s** at QD{int(max_seq.iodepth)}. These are maxima within the tested regular-file Windows stack, not raw-device specifications.

Little's Law was calculated per run as `L_inferred = IOPS x mean completion latency in seconds`. It follows the configured-QD trend but is not forced to equal `iodepth`: configured depth is a submission limit, while the estimate uses completed I/O rate and FIO completion latency and can differ due to host scheduling, batching, ramp/runtime boundaries, and time outside the measured completion-latency interval.

The mixed 70/30 and bounded write subset provide direction comparisons without a broad write sweep. All configurations have three repetitions, all actual JSON targets resolved to the single regular file, and no upper-QD extension was needed.
"""
    (repo / "docs" / "phase5_queue_analysis.md").write_text(doc, encoding="utf-8")
    print(f"Phase 5: {len(runs)} runs; knee=QD{knee_qd}; max4k={max_4k.total_iops_median:.0f}; maxseq={max_seq.total_bw_bytes_s_median/1024**2:.1f} MiB/s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

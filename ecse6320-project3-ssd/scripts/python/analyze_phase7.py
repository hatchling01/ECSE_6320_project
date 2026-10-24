"""Analyze the Phase 7 buffered-I/O benchmark pitfall."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from collect_results import collect_phase
from safe_target import repository_root


ORDER = ("pitfall_direct", "pitfall_buffered_first", "pitfall_buffered_second")
LABELS = {
    "pitfall_direct": "Direct I/O",
    "pitfall_buffered_first": "Buffered first",
    "pitfall_buffered_second": "Buffered immediate second",
}


def main() -> int:
    repo = repository_root()
    runs = pd.DataFrame(collect_phase("phase7"))
    if len(runs) != 9 or set(runs.configuration) != set(ORDER):
        raise RuntimeError("Phase 7 gate requires nine valid runs across A/B/C")
    runs.to_csv(repo / "data" / "parsed" / "phase7_pitfall_runs.csv", index=False)
    records = []
    for configuration in ORDER:
        group = runs[runs.configuration == configuration]
        row = {"configuration": configuration, "label": LABELS[configuration], "direct": int(group.direct.iloc[0]), "repetitions": len(group)}
        for metric in ("total_iops", "total_bw_bytes_s", "weighted_mean_clat_ns", "read_p99_0"):
            values = pd.to_numeric(group[metric])
            row[f"{metric}_median"] = values.median()
            row[f"{metric}_mean"] = values.mean()
            row[f"{metric}_std"] = values.std(ddof=1)
            row[f"{metric}_cv_pct"] = values.std(ddof=1) / values.mean() * 100
        records.append(row)
    summary = pd.DataFrame(records)
    summary.to_csv(repo / "data" / "parsed" / "phase7_pitfall_summary.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    axes[0].bar(summary.label, summary.total_bw_bytes_s_median / 1024**2, color=("tab:blue", "tab:orange", "tab:red"))
    axes[0].set_ylabel("Median throughput (MiB/s)"); axes[0].set_title("Same 512 MiB sequential-read range")
    axes[1].bar(summary.label, summary.weighted_mean_clat_ns_median / 1e3, color=("tab:blue", "tab:orange", "tab:red"))
    axes[1].set_ylabel("Mean completion latency (us)"); axes[1].set_title("Host-visible latency")
    for ax in axes:
        ax.tick_params(axis="x", rotation=20); ax.grid(axis="y", alpha=.25)
    fig.tight_layout(); fig.savefig(repo / "results" / "plots" / "phase7_buffered_vs_direct.png", dpi=180); plt.close(fig)

    table = ["# Phase 7 Direct vs Buffered Reads", "", "| Setup | direct | Median MiB/s | Mean clat us | p99 us | Throughput CV |", "|---|---:|---:|---:|---:|---:|"]
    for row in summary.itertuples():
        table.append(f"| {row.label} | {row.direct} | {row.total_bw_bytes_s_median/1024**2:,.1f} | {row.weighted_mean_clat_ns_median/1e3:,.1f} | {row.read_p99_0_median/1e3:,.1f} | {row.total_bw_bytes_s_cv_pct:.1f}% |")
    (repo / "results" / "tables" / "phase7_pitfall.md").write_text("\n".join(table) + "\n", encoding="utf-8")

    direct = summary.iloc[0]; first = summary.iloc[1]; second = summary.iloc[2]
    second_gain = (second.total_bw_bytes_s_median / first.total_bw_bytes_s_median - 1) * 100
    doc = f"""# Phase 7: Misleading Benchmark Setup

The experiment held the target, 512 MiB active range, sequential access, 128 KiB block size, QD1, one job, and three-repetition policy fixed. Only cache bypass changed: A used `direct=1`; B and C used `direct=0`, with C immediately following B in every repetition. No cache flush, elevated privilege, or system setting change was used.

Median throughput was {direct.total_bw_bytes_s_median/1024**2:,.1f} MiB/s direct, {first.total_bw_bytes_s_median/1024**2:,.1f} MiB/s on the first buffered pass, and {second.total_bw_bytes_s_median/1024**2:,.1f} MiB/s on the immediate second buffered pass. The second buffered pass differed from the first by {second_gain:+.1f}%. These results are host-stack observations: buffered reads may include filesystem/page-cache behavior, read-ahead, and memory copies, so they cannot be interpreted as an isolated SSD measurement even if the second-pass speedup is modest. This is why all primary project results use `direct=1`.

Additional reproducibility pitfalls encountered or controlled in this project include Windows FIO's colon parsing of absolute drive-qualified filenames, configured QD versus inferred occupancy, misleadingly short burst tests, inadequate tail sample counts, uncertain device state, and ordinary run-to-run noise. The failed Phase 0 filename attempt remains preserved and excluded from performance analysis.
"""
    (repo / "docs" / "phase7_pitfall_analysis.md").write_text(doc, encoding="utf-8")
    print(summary[["label", "total_bw_bytes_s_median", "weighted_mean_clat_ns_median", "total_bw_bytes_s_cv_pct"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

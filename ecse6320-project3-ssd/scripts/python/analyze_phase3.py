"""Summarize and visualize Phase 3 block-size/pattern results."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from collect_results import collect_phase
from safe_target import repository_root


BS_ORDER = ["4k", "16k", "32k", "64k", "128k", "256k"]
BS_BYTES = {value: int(value[:-1]) * 1024 for value in BS_ORDER}


def main() -> int:
    repo = repository_root()
    runs = pd.DataFrame(collect_phase("phase3"))
    if len(runs) != 72 or runs["configuration"].nunique() != 24:
        raise RuntimeError("Phase 3 gate requires 72 runs across 24 configurations")
    runs["pattern"] = runs["configuration"].str.extract(r"^(sequential|random)")
    runs["direction"] = runs["configuration"].str.extract(r"_(read|write)_")
    runs["bs_bytes"] = runs["bs"].map(BS_BYTES)
    runs["primary_mean_clat_ns"] = runs["weighted_mean_clat_ns"]
    runs.to_csv(repo / "data" / "parsed" / "phase3_block_pattern_runs.csv", index=False)

    metrics = ["total_iops", "total_bw_bytes_s", "primary_mean_clat_ns", "total_ios"]
    records = []
    for keys, group in runs.groupby(["pattern", "direction", "bs", "bs_bytes"], sort=False):
        record = dict(zip(["pattern", "direction", "bs", "bs_bytes"], keys))
        for metric in metrics:
            values = group[metric].astype(float)
            record[f"{metric}_median"] = values.median()
            record[f"{metric}_mean"] = values.mean()
            record[f"{metric}_std"] = values.std(ddof=1)
            record[f"{metric}_cv_pct"] = values.std(ddof=1) / values.mean() * 100 if values.mean() else 0
            record[f"{metric}_min"] = values.min()
            record[f"{metric}_max"] = values.max()
        records.append(record)
    summary = pd.DataFrame(records).sort_values(["direction", "pattern", "bs_bytes"])
    summary.to_csv(repo / "data" / "parsed" / "phase3_block_pattern_summary.csv", index=False)

    plot_specs = [
        ("total_iops_median", "IOPS", "phase3_iops_vs_block_size.png", True),
        ("total_bw_bytes_s_median", "Throughput (MiB/s)", "phase3_throughput_vs_block_size.png", False),
        ("primary_mean_clat_ns_median", "Mean completion latency (µs)", "phase3_latency_vs_block_size.png", True),
    ]
    for metric, ylabel, filename, log_y in plot_specs:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharex=True)
        for ax, direction in zip(axes, ("read", "write")):
            for pattern, marker in (("sequential", "o"), ("random", "s")):
                subset = summary[(summary.direction == direction) & (summary.pattern == pattern)].sort_values("bs_bytes")
                values = subset[metric].astype(float)
                if metric == "total_bw_bytes_s_median":
                    values = values / 1024**2
                elif metric == "primary_mean_clat_ns_median":
                    values = values / 1e3
                ax.plot(subset.bs_bytes / 1024, values, marker=marker, label=pattern)
            ax.set_xscale("log", base=2)
            if log_y:
                ax.set_yscale("log")
            ax.set_title(direction.capitalize())
            ax.set_xlabel("Block size (KiB)")
            ax.set_ylabel(ylabel)
            ax.grid(True, which="both", alpha=0.25)
            ax.legend()
        fig.suptitle(f"QD=1 {ylabel.lower()} versus block size")
        fig.tight_layout()
        fig.savefig(repo / "results" / "plots" / filename, dpi=180)
        plt.close(fig)

    max_iops = summary.loc[summary.total_iops_median.idxmax()]
    max_bw = summary.loc[summary.total_bw_bytes_s_median.idxmax()]
    worst_cv = summary.total_iops_cv_pct.max()
    analysis = f"""# Phase 3: Block Size and Access Pattern

The complete required matrix contains 24 configurations (six block sizes × two patterns × two directions), each with three validated QD=1 repetitions. Reads used 2 s ramp plus 8 s measured time; writes were bounded to 256 MiB per repetition.

The highest median IOPS in this QD=1 sweep was {max_iops.total_iops_median:,.0f} for {max_iops.pattern} {max_iops.direction} at {max_iops.bs}. The highest median throughput was {max_bw.total_bw_bytes_s_median/1024**2:,.1f} MiB/s for {max_bw.pattern} {max_bw.direction} at {max_bw.bs}. These are QD=1 observations, not claims of device or interface maxima.

Across the matrix, small blocks emphasize IOPS and larger blocks convert fewer operations into higher bandwidth. Completion latency generally increases with transfer size. Sequential/random and read/write differences are treated as host-visible measurements; no internal NAND/controller cause is asserted.

The maximum IOPS coefficient of variation was {worst_cv:.1f}%. All original runs are retained. Extreme percentiles are not used as a primary Phase 3 conclusion because bounded large-block writes can provide relatively few p99.9 tail observations.
"""
    (repo / "docs" / "phase3_block_pattern_analysis.md").write_text(analysis, encoding="utf-8")
    print(f"Phase 3: {len(runs)} runs, {len(summary)} summaries, max CV={worst_cv:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


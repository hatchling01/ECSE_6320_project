"""Analyze Phase 4 read/write mix results."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from collect_results import collect_phase
from safe_target import repository_root


def main() -> int:
    repo = repository_root()
    runs = pd.DataFrame(collect_phase("phase4"))
    if len(runs) != 12 or runs.configuration.nunique() != 4:
        raise RuntimeError("Phase 4 gate requires 12 runs and all four mixes")
    runs["read_pct"] = runs["rwmixread"].astype(int)
    runs.to_csv(repo / "data" / "parsed" / "phase4_mix_runs.csv", index=False)

    metrics = [
        "total_iops", "read_iops", "write_iops", "total_bw_bytes_s",
        "read_bw_bytes_s", "write_bw_bytes_s", "weighted_mean_clat_ns",
        "read_p50_0", "read_p95_0", "read_p99_0", "read_p99_9",
        "write_p50_0", "write_p95_0", "write_p99_0", "write_p99_9", "total_ios",
    ]
    records = []
    for read_pct, group in runs.groupby("read_pct"):
        record = {"read_pct": read_pct, "write_pct": 100 - read_pct}
        for metric in metrics:
            # FIO leaves the inactive direction's percentile cells blank for
            # pure-read and pure-write jobs.  Preserve those as missing data;
            # they are not zero-latency observations.
            values = pd.to_numeric(group[metric], errors="coerce")
            mean = values.mean()
            std = values.std(ddof=1)
            record[f"{metric}_median"] = values.median()
            record[f"{metric}_mean"] = mean
            record[f"{metric}_std"] = std
            record[f"{metric}_cv_pct"] = std / mean * 100 if pd.notna(mean) and mean != 0 else np.nan
        records.append(record)
    summary = pd.DataFrame(records).sort_values("read_pct")
    summary.to_csv(repo / "data" / "parsed" / "phase4_mix_summary.csv", index=False)

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(summary.read_pct, summary.total_iops_median, "o-", label="Total IOPS")
    ax1.plot(summary.read_pct, summary.read_iops_median, "s--", label="Read IOPS")
    ax1.plot(summary.read_pct, summary.write_iops_median, "^--", label="Write IOPS")
    ax1.set_xlabel("Read percentage")
    ax1.set_ylabel("IOPS")
    ax1.set_title("4 KiB random QD8 performance versus read mix")
    ax1.grid(alpha=0.25)
    ax1.legend()
    fig.tight_layout()
    fig.savefig(repo / "results" / "plots" / "phase4_mix_iops.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(summary.read_pct, summary.weighted_mean_clat_ns_median / 1e3, "o-", label="Weighted mean")
    ax.plot(summary.read_pct, summary.read_p99_0_median.replace(0, np.nan) / 1e3, "s--", label="Read p99")
    ax.plot(summary.read_pct, summary.write_p99_0_median.replace(0, np.nan) / 1e3, "^--", label="Write p99")
    ax.set_xlabel("Read percentage")
    ax.set_ylabel("Completion latency (µs)")
    ax.set_yscale("log")
    ax.set_title("4 KiB random QD8 latency versus read mix")
    ax.grid(alpha=0.25, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(repo / "results" / "plots" / "phase4_mix_latency.png", dpi=180)
    plt.close(fig)

    lines = [
        "# Phase 4: Read/Write Mix Sweep",
        "",
        "The fixed workload is 4 KiB random I/O at `iodepth=8`, one job, `windowsaio`, and `direct=1`. This choice represents a common small-block workload while introducing enough concurrency for mixed-I/O interaction without conflating the result with the later saturation sweep.",
        "",
        "| Read/write mix | Median total IOPS | Median MiB/s | Weighted mean clat (µs) | IOPS CV |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in summary.sort_values("read_pct", ascending=False).itertuples():
        lines.append(
            f"| {row.read_pct}/{row.write_pct} | {row.total_iops_median:,.0f} | "
            f"{row.total_bw_bytes_s_median/1024**2:,.1f} | {row.weighted_mean_clat_ns_median/1e3:,.1f} | "
            f"{row.total_iops_cv_pct:.1f}% |"
        )
    lines.extend(
        [
            "",
            "Mixed workloads show host-visible read/write asymmetry and latency interaction rather than a linear interpolation of pure endpoints. Read and write percentile series are kept separate because FIO reports direction-specific latency distributions; the weighted mean combines directions by completed I/O count.",
            "",
            "All three repetitions per mix are preserved. p99.9 is retained in parsed data, with interpretation conditioned on each direction's completion count.",
        ]
    )
    (repo / "docs" / "phase4_mix_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(summary[["read_pct", "total_iops_median", "weighted_mean_clat_ns_median", "total_iops_cv_pct"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


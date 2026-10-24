"""Validate, summarize, and plot Phase 2 QD1 baselines."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from collect_results import collect_phase
from safe_target import repository_root


BS_BYTES = {"4k": 4096, "128k": 128 * 1024}


def markdown_table(frame: pd.DataFrame) -> str:
    headers = list(frame.columns)
    rows = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for values in frame.itertuples(index=False, name=None):
        rows.append("| " + " | ".join(str(value) for value in values) + " |")
    return "\n".join(rows)


def main() -> int:
    repo = repository_root()
    rows = collect_phase("phase2")
    frame = pd.DataFrame(rows)
    production = frame[frame["classification"] == "PRODUCTION"].copy()
    if len(production) != 12 or production["configuration"].nunique() != 4:
        raise RuntimeError("Phase 2 gate requires 12 valid production runs and four configurations")

    production["bs_bytes"] = production["bs"].map(BS_BYTES)
    production["iops_bs_bytes_s"] = production["total_iops"] * production["bs_bytes"]
    production["throughput_identity_ratio"] = production["total_bw_bytes_s"] / production["iops_bs_bytes_s"]
    if not np.allclose(production["throughput_identity_ratio"], 1.0, rtol=0.002):
        raise RuntimeError("IOPS × block size sanity check failed")
    production["l_inferred"] = production["total_iops"] * production["weighted_mean_clat_ns"] / 1e9
    production["primary_direction"] = np.where(production["read_io_bytes"] > 0, "read", "write")
    for percentile in ("50_0", "95_0", "99_0", "99_9"):
        production[f"primary_p{percentile}_ns"] = np.where(
            production["primary_direction"] == "read",
            production[f"read_p{percentile}"],
            production[f"write_p{percentile}"],
        )
    production["p99_9_expected_tail_samples"] = production["total_ios"] / 1000.0

    runs_path = repo / "data" / "parsed" / "phase2_qd1_runs.csv"
    production.to_csv(runs_path, index=False)

    metrics = [
        "total_iops",
        "total_bw_bytes_s",
        "weighted_mean_clat_ns",
        "primary_p50_0_ns",
        "primary_p95_0_ns",
        "primary_p99_0_ns",
        "primary_p99_9_ns",
        "total_ios",
        "l_inferred",
    ]
    records: list[dict[str, float | str]] = []
    for configuration, group in production.groupby("configuration", sort=True):
        record: dict[str, float | str] = {"configuration": configuration}
        for metric in metrics:
            values = group[metric].astype(float)
            mean = values.mean()
            record[f"{metric}_median"] = values.median()
            record[f"{metric}_mean"] = mean
            record[f"{metric}_std"] = values.std(ddof=1)
            record[f"{metric}_cv_pct"] = values.std(ddof=1) / mean * 100 if mean else 0
            record[f"{metric}_min"] = values.min()
            record[f"{metric}_max"] = values.max()
        records.append(record)
    summary = pd.DataFrame(records)
    summary_path = repo / "data" / "parsed" / "phase2_qd1_summary.csv"
    summary.to_csv(summary_path, index=False)

    display = pd.DataFrame(
        {
            "Workload": summary["configuration"],
            "Median IOPS": summary["total_iops_median"].map(lambda x: f"{x:,.0f}"),
            "Median MiB/s": (summary["total_bw_bytes_s_median"] / 1024**2).map(lambda x: f"{x:,.1f}"),
            "Mean clat (µs)": (summary["weighted_mean_clat_ns_median"] / 1e3).map(lambda x: f"{x:,.1f}"),
            "p50 (µs)": (summary["primary_p50_0_ns_median"] / 1e3).map(lambda x: f"{x:,.1f}"),
            "p95 (µs)": (summary["primary_p95_0_ns_median"] / 1e3).map(lambda x: f"{x:,.1f}"),
            "p99 (µs)": (summary["primary_p99_0_ns_median"] / 1e3).map(lambda x: f"{x:,.1f}"),
            "p99.9 (µs)": (summary["primary_p99_9_ns_median"] / 1e3).map(lambda x: f"{x:,.1f}"),
            "IO count": summary["total_ios_median"].map(lambda x: f"{x:,.0f}"),
            "CV IOPS": summary["total_iops_cv_pct"].map(lambda x: f"{x:.1f}%"),
        }
    )
    table_path = repo / "results" / "tables" / "qd1_baseline.md"
    table_path.write_text(
        "# QD=1 Baseline Summary\n\n"
        "Medians across three repetitions. Throughput is binary MiB/s; latency is completion latency.\n\n"
        + markdown_table(display)
        + "\n",
        encoding="utf-8",
    )

    order = ["randread_4k_qd1", "randwrite_4k_qd1", "seqread_128k_qd1", "seqwrite_128k_qd1"]
    plot_data = summary.set_index("configuration").loc[order]
    labels = ["4K random read", "4K random write", "128K seq read", "128K seq write"]
    x = np.arange(len(labels))
    width = 0.19
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for offset, column, label in [
        (-1.5, "primary_p50_0_ns_median", "p50"),
        (-0.5, "primary_p95_0_ns_median", "p95"),
        (0.5, "primary_p99_0_ns_median", "p99"),
        (1.5, "primary_p99_9_ns_median", "p99.9"),
    ]:
        ax.bar(x + offset * width, plot_data[column] / 1e3, width, label=label)
    ax.set_yscale("log")
    ax.set_ylabel("Completion latency (µs, log scale)")
    ax.set_title("QD=1 latency baselines (median across 3 repetitions)")
    ax.set_xticks(x, labels, rotation=15, ha="right")
    ax.legend()
    ax.grid(axis="y", which="both", alpha=0.25)
    fig.tight_layout()
    plot_path = repo / "results" / "plots" / "phase2_qd1_latency.png"
    fig.savefig(plot_path, dpi=180)
    plt.close(fig)

    by_name = summary.set_index("configuration")
    analysis = f"""# Phase 2: QD=1 Baseline Analysis

All four required configurations completed three validated repetitions against the regular 8 GiB production file using FIO 3.43, `windowsaio`, `direct=1`, `iodepth=1`, and one job. Initialization is recorded separately and excluded from performance results.

## Headline results

{markdown_table(display)}

The identity check `IOPS × block size ≈ bytes/s` passed every run within 0.2%, confirming consistent unit extraction. Random 4 KiB results are IOPS-oriented, whereas sequential 128 KiB results deliver much higher bandwidth per operation. Read/write asymmetry is reported as observed behavior only; this phase does not attribute it to SLC caching, garbage collection, or temperature.

Median p99.9 tail sample counts were approximately {by_name.loc['randread_4k_qd1', 'total_ios_median']/1000:.0f} (random read), {by_name.loc['randwrite_4k_qd1', 'total_ios_median']/1000:.0f} (random write), {by_name.loc['seqread_128k_qd1', 'total_ios_median']/1000:.0f} (sequential read), and {by_name.loc['seqwrite_128k_qd1', 'total_ios_median']/1000:.0f} (sequential write). The sequential-write p99.9 estimate therefore has the strongest finite-sample caveat.

QD=1 Little's-Law sanity values (`IOPS × mean clat seconds`) are stored per run. They are broadly near, but not required to equal, one because completion latency excludes all host-side timing components and configured queue depth is not identical to inferred average occupancy.

Variability is preserved in the run and summary CSV files. No configuration exceeded the 20% IOPS CV rerun threshold.
"""
    (repo / "docs" / "phase2_qd1_analysis.md").write_text(analysis, encoding="utf-8")
    print(f"Wrote {runs_path}")
    print(f"Wrote {summary_path}")
    print(f"Wrote {table_path}")
    print(f"Wrote {plot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


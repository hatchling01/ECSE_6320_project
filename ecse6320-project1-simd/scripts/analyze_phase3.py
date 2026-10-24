import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PILOT_SUMMARY = ROOT / "data" / "processed" / "pilot_summary_v2.csv"
PILOT_REPORT = ROOT / "results" / "tables" / "pilot_summary_v2.md"
STATS_PATH = ROOT / "data" / "processed" / "phase3_statistics.csv"
CORRECTED_SAMPLES = ROOT / "data" / "processed" / "phase3_samples_corrected.csv"
SCALAR_SIMD = ROOT / "results" / "tables" / "scalar_vs_simd.csv"
DATATYPE_TABLE = ROOT / "results" / "tables" / "datatype_summary.csv"
SCALAR_SIMD_MD = ROOT / "results" / "tables" / "scalar_vs_simd.md"
DATATYPE_TABLE_MD = ROOT / "results" / "tables" / "datatype_summary.md"
PHASE3_SUMMARY_MD = ROOT / "results" / "tables" / "phase3_summary.md"
ANOMALY_REPORT_MD = ROOT / "results" / "tables" / "phase3_anomalies.md"
VARIABILITY_DIAGNOSTIC = ROOT / "results" / "tables" / "phase3_variability_diagnostic.csv"
VARIABILITY_DIAGNOSTIC_MD = ROOT / "results" / "tables" / "phase3_variability_diagnostic.md"
PLOT_DIR = ROOT / "results" / "plots"


def load_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as source:
        return [
            {key.lower(): value for key, value in row.items()}
            for row in csv.DictReader(source)
        ]


def group_rows(rows, keys):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in keys)].append(row)
    return groups


def sample_stats(rows):
    values = [float(row["ns_per_element"]) for row in rows]
    median = statistics.median(values)
    mean = statistics.mean(values)
    stddev = statistics.stdev(values) if len(values) > 1 else 0.0
    cv = stddev / mean if mean else 0.0
    return {
        "samples": len(values),
        "median_ns_per_element": median,
        "mean_ns_per_element": mean,
        "stddev_ns_per_element": stddev,
        "min_ns_per_element": min(values),
        "max_ns_per_element": max(values),
        "coefficient_of_variation": cv,
        "median_elapsed_ns": statistics.median(float(row["elapsed_ns"]) for row in rows),
        "median_gflop_per_s": statistics.median(float(row["gflop_per_s"]) for row in rows),
        "median_effective_bandwidth_gib_per_s": statistics.median(
            float(row["effective_bandwidth_gib_per_s"]) for row in rows
        ),
    }


def write_csv(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def correct_derived_fields(rows):
    """Recompute accounting columns from kernel semantics without changing timings."""
    for row in rows:
        n = int(row["n"])
        batch = int(row["batching_count"])
        element_bytes = 4 if row["datatype"] == "float32" else 8
        kernel = row["kernel"]
        if kernel == "elementwise_multiply":
            operations_per_call = n
            useful_bytes_per_call = 3 * n * element_bytes
        elif kernel in ("axpy", "dot_product"):
            operations_per_call = 2 * n
            useful_bytes_per_call = (3 if kernel == "axpy" else 2) * n * element_bytes
        elif kernel == "stencil_1d_three_point":
            operations_per_call = 5 * max(0, n - 2)
            useful_bytes_per_call = (0 if n == 0 else 2 if n == 1 else 4 * n - 4) * element_bytes
        else:
            raise ValueError(f"Unsupported kernel in raw data: {kernel}")
        operations = operations_per_call * batch
        useful_bytes = useful_bytes_per_call * batch
        elapsed_ns = int(row["elapsed_ns"])
        if elapsed_ns <= 0:
            raise ValueError("Raw sample contains non-positive elapsed time")
        row["operations_performed"] = operations
        row["useful_bytes_processed"] = useful_bytes
        row["gflop_per_s"] = operations / elapsed_ns
        row["effective_bandwidth_gib_per_s"] = useful_bytes * 1.0e9 / elapsed_ns / (1024 ** 3)
    write_csv(CORRECTED_SAMPLES, rows, list(rows[0].keys()) if rows else [])
    return rows


def analyze_pilot(path, rerun_paths):
    rows = load_rows(path)
    groups = group_rows(rows, ["kernel", "datatype", "build", "n", "batching_count"])
    summary = []
    for key, samples in sorted(groups.items()):
        kernel, datatype, build, n, batch = key
        stats = sample_stats(samples)
        summary.append({
            "kernel": kernel,
            "datatype": datatype,
            "build": build,
            "n": int(n),
            "batching_count": int(batch),
            **stats,
        })
    columns = [
        "kernel", "datatype", "build", "n", "batching_count", "samples",
        "median_ns_per_element", "mean_ns_per_element", "stddev_ns_per_element",
        "min_ns_per_element", "max_ns_per_element", "coefficient_of_variation",
        "median_elapsed_ns", "median_gflop_per_s", "median_effective_bandwidth_gib_per_s",
    ]
    write_csv(PILOT_SUMMARY, summary, columns)
    cvs = [row["coefficient_of_variation"] for row in summary]
    max_cv = max(cvs, default=0.0)
    median_cv = statistics.median(cvs) if cvs else 0.0
    min_elapsed = min((row["median_elapsed_ns"] for row in summary), default=0.0)
    report = [
        "# Phase 3 Pilot Calibration",
        "",
        "Elementwise multiply only; this is calibration data, not a full matrix or performance conclusion.",
        "",
        f"- Raw samples: {len(rows)}; configurations: {len(summary)}.",
        "- Warmups: 3 per configuration.",
        "- Repetitions: 5 per configuration.",
        "- Batching: 128 calls for N <= 4096; 32 calls for N <= 65536; otherwise 1 call. Batch is recorded per raw sample.",
        "- Affinity: logical CPU 0, set on each benchmark process and recorded in the raw CSV.",
        f"- Median configuration CV: {median_cv:.4%}; maximum configuration CV: {max_cv:.4%}.",
        f"- Configurations above 10% CV: {sum(value > 0.10 for value in cvs)}/{len(cvs)}.",
        f"- Shortest median timed sample: {min_elapsed:.0f} ns.",
        "- Timer: `std::chrono::steady_clock`; non-positive elapsed samples are rejected.",
        "- Calibration conclusion: batching made the smallest samples resolvable, but per-configuration variability remained nonuniform; preserve and interpret CVs rather than treating the pilot as uniformly stable.",
        "- The highest-v2-CV configuration received one targeted rerun. No pilot configuration was repeatedly rerun for a preferred result.",
        "- Planned full-matrix repetitions: 10, chosen at the allowed maximum because pilot variability exceeded 10% in several configurations.",
        "",
        "| Datatype | Build | Target footprint (bytes) | N | Batch | Median ns/element | CV |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        target = next((r["target_working_set_bytes"] for r in rows
                       if r["datatype"] == row["datatype"] and r["build"] == row["build"]
                       and int(r["n"]) == row["n"] and int(r["batching_count"]) == row["batching_count"]), "")
        report.append(
            f"| {row['datatype']} | {row['build']} | {target} | {row['n']} | {row['batching_count']} | "
            f"{row['median_ns_per_element']:.6g} | {row['coefficient_of_variation']:.3%} |"
        )
    if rerun_paths:
        report.extend([
            "",
            "## Targeted Stability Reruns",
            "",
            "Reruns are preserved separately; they are not merged into the original five-sample configurations.",
            "",
            "| Raw file | Datatype | Build | N | Batch | Samples | Median ns/element | CV |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ])
        for rerun_path in rerun_paths:
            rerun_rows = load_rows(rerun_path)
            rerun_groups = group_rows(rerun_rows, ["datatype", "build", "n", "batching_count"])
            for key, samples in sorted(rerun_groups.items()):
                datatype, build, n, batch = key
                stats = sample_stats(samples)
                report.append(
                    f"| `{rerun_path.name}` | {datatype} | {build} | {n} | {batch} | "
                    f"{stats['samples']} | {stats['median_ns_per_element']:.6g} | "
                    f"{stats['coefficient_of_variation']:.3%} |"
                )
    PILOT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    PILOT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Pilot summary: {PILOT_REPORT}")
    print(f"Pilot median CV={median_cv:.4%}; maximum CV={max_cv:.4%}; shortest median sample={min_elapsed:.0f} ns")
    return max_cv


def aggregate_full(path):
    rows = correct_derived_fields(load_rows(path))
    keys = ["kernel", "datatype", "build", "n", "target_working_set_bytes"]
    groups = group_rows(rows, keys)
    summary = []
    for key, samples in sorted(groups.items(), key=lambda item: (
        item[0][0], item[0][1], int(item[0][4]), item[0][2]
    )):
        kernel, datatype, build, n, target_bytes = key
        summary.append({
            "kernel": kernel,
            "datatype": datatype,
            "build": build,
            "n": int(n),
            "target_working_set_bytes": int(target_bytes),
            **sample_stats(samples),
        })
    columns = list(summary[0].keys()) if summary else []
    write_csv(STATS_PATH, summary, columns)

    diagnostic_rows = []
    for dimension in ("target_working_set_bytes", "kernel", "datatype", "build"):
        for value, members in sorted(group_rows(summary, [dimension]).items(), key=lambda item: str(item[0])):
            values = [row["coefficient_of_variation"] for row in members]
            diagnostic_rows.append({
                "dimension": dimension,
                "value": value[0],
                "configurations": len(members),
                "above_10_percent_cv": sum(cv > 0.10 for cv in values),
                "above_20_percent_cv": sum(cv > 0.20 for cv in values),
                "median_cv": statistics.median(values),
                "max_cv": max(values),
            })
    diagnostic_columns = [
        "dimension", "value", "configurations", "above_10_percent_cv",
        "above_20_percent_cv", "median_cv", "max_cv",
    ]
    write_csv(VARIABILITY_DIAGNOSTIC, diagnostic_rows, diagnostic_columns)
    diagnostic_lines = [
        "# Phase 3 Variability Diagnostic", "",
        "CV is computed from the 10 raw repetitions for each configuration; group counts show how high-CV cases distribute by one dimension at a time.", "",
        "| Dimension | Value | Configurations | CV > 10% | CV > 20% | Median CV | Max CV |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in diagnostic_rows:
        diagnostic_lines.append(
            f"| {row['dimension']} | {row['value']} | {row['configurations']} | "
            f"{row['above_10_percent_cv']} | {row['above_20_percent_cv']} | "
            f"{row['median_cv']:.3%} | {row['max_cv']:.3%} |"
        )
    VARIABILITY_DIAGNOSTIC_MD.write_text("\n".join(diagnostic_lines) + "\n", encoding="utf-8")

    scalar_simd_rows = []
    datatype_rows = []
    representative_targets = {24576: "small", 25165824: "intermediate", 134217728: "large"}
    indexes = {
        (r["kernel"], r["datatype"], r["target_working_set_bytes"], r["build"]): r
        for r in summary
    }
    for base in summary:
        if base["build"] != "gcc-scalar" or base["target_working_set_bytes"] not in representative_targets:
            continue
        auto = indexes[(base["kernel"], base["datatype"], base["target_working_set_bytes"], "gcc-auto")]
        native = indexes[(base["kernel"], base["datatype"], base["target_working_set_bytes"], "gcc-native")]
        scalar_simd_rows.append({
            "kernel": base["kernel"], "datatype": base["datatype"],
            "working_set_bytes": base["target_working_set_bytes"],
            "working_set_class": representative_targets[base["target_working_set_bytes"]],
            "scalar_median_ns_per_element": base["median_ns_per_element"],
            "auto_median_ns_per_element": auto["median_ns_per_element"],
            "native_median_ns_per_element": native["median_ns_per_element"],
            "auto_speedup": base["median_ns_per_element"] / auto["median_ns_per_element"],
            "native_speedup": base["median_ns_per_element"] / native["median_ns_per_element"],
            "auto_gflop_per_s": auto["median_gflop_per_s"],
            "native_gflop_per_s": native["median_gflop_per_s"],
            "auto_effective_gib_per_s": auto["median_effective_bandwidth_gib_per_s"],
            "native_effective_gib_per_s": native["median_effective_bandwidth_gib_per_s"],
        })
    write_csv(SCALAR_SIMD, scalar_simd_rows, list(scalar_simd_rows[0].keys()))
    datatype_keys = {(r["kernel"], r["build"], r["target_working_set_bytes"])
                     for r in summary if r["target_working_set_bytes"] in representative_targets}
    for kernel, build, working_set in sorted(datatype_keys):
        float32 = next(r for r in summary if r["kernel"] == kernel and r["build"] == build
                       and r["target_working_set_bytes"] == working_set and r["datatype"] == "float32")
        float64 = next(r for r in summary if r["kernel"] == kernel and r["build"] == build
                       and r["target_working_set_bytes"] == working_set and r["datatype"] == "float64")
        datatype_rows.append({
            "kernel": kernel, "build": build, "working_set_bytes": working_set,
            "float32_median_ns_per_element": float32["median_ns_per_element"],
            "float64_median_ns_per_element": float64["median_ns_per_element"],
            "float64_over_float32_time_ratio": float64["median_ns_per_element"] / float32["median_ns_per_element"],
            "float32_median_gflop_per_s": float32["median_gflop_per_s"],
            "float64_median_gflop_per_s": float64["median_gflop_per_s"],
            "float32_effective_gib_per_s": float32["median_effective_bandwidth_gib_per_s"],
            "float64_effective_gib_per_s": float64["median_effective_bandwidth_gib_per_s"],
        })
    write_csv(DATATYPE_TABLE, datatype_rows, list(datatype_rows[0].keys()))
    scalar_lines = [
        "# Phase 3 Scalar vs SIMD Summary", "",
        "Measured medians from the full matrix; no data points are omitted from the processed statistics file.", "",
        "| Kernel | Type | Working set | Scalar median ns/element | Auto median ns/element | Native median ns/element | Auto speedup | Native speedup | Auto GFLOP/s | Native GFLOP/s | Auto effective GiB/s | Native effective GiB/s |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in scalar_simd_rows:
        scalar_lines.append(
            f"| {row['kernel']} | {row['datatype']} | {row['working_set_class']} ({row['working_set_bytes']:,} B) | "
            f"{row['scalar_median_ns_per_element']:.6g} | {row['auto_median_ns_per_element']:.6g} | "
            f"{row['native_median_ns_per_element']:.6g} | {row['auto_speedup']:.4f} | "
            f"{row['native_speedup']:.4f} | {row['auto_gflop_per_s']:.6g} | {row['native_gflop_per_s']:.6g} | "
            f"{row['auto_effective_gib_per_s']:.6g} | {row['native_effective_gib_per_s']:.6g} |"
        )
    SCALAR_SIMD_MD.write_text("\n".join(scalar_lines) + "\n", encoding="utf-8")

    datatype_lines = [
        "# Phase 3 Datatype Summary", "",
        "Measured float32/float64 medians at representative working sets.", "",
        "| Kernel | Build | Working set (bytes) | float32 ns/element | float64 ns/element | float64/float32 time ratio | float32 GFLOP/s | float64 GFLOP/s | float32 effective GiB/s | float64 effective GiB/s |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in datatype_rows:
        datatype_lines.append(
            f"| {row['kernel']} | {row['build']} | {row['working_set_bytes']:,} | "
            f"{row['float32_median_ns_per_element']:.6g} | {row['float64_median_ns_per_element']:.6g} | "
            f"{row['float64_over_float32_time_ratio']:.4f} | {row['float32_median_gflop_per_s']:.6g} | "
            f"{row['float64_median_gflop_per_s']:.6g} | {row['float32_effective_gib_per_s']:.6g} | "
            f"{row['float64_effective_gib_per_s']:.6g} |"
        )
    DATATYPE_TABLE_MD.write_text("\n".join(datatype_lines) + "\n", encoding="utf-8")
    return rows, summary, scalar_simd_rows, datatype_rows


def plot_full(rows, summary, scalar_simd_rows, datatype_rows):
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    kernels = sorted({row["kernel"] for row in summary})
    metrics = [
        ("speedup_vs_working_set", "speedup", "Speedup vs scalar", None, None),
        ("throughput_vs_working_set", "throughput", "GFLOP/s", None, None),
        ("effective_bandwidth_vs_working_set", "bandwidth", "Effective GiB/s", None, None),
        ("ns_per_element_vs_working_set", "time", "Median ns/element", None, None),
    ]
    for kernel in kernels:
        for file_stem, category, ylabel, auto_col, native_col in metrics:
            plt.figure(figsize=(8, 5))
            if category == "time":
                for datatype in ("float32", "float64"):
                    for build in ("gcc-scalar", "gcc-auto", "gcc-native"):
                        points = [r for r in summary if r["kernel"] == kernel and r["build"] == build and r["datatype"] == datatype]
                        points.sort(key=lambda r: r["target_working_set_bytes"])
                        plt.errorbar(
                            [r["target_working_set_bytes"] for r in points],
                            [r["median_ns_per_element"] for r in points],
                            yerr=[r["stddev_ns_per_element"] for r in points],
                            marker="o", label=f"{datatype} {build}",
                        )
            elif category == "speedup":
                for datatype in ("float32", "float64"):
                    for build in ("gcc-auto", "gcc-native"):
                        points = []
                        for scalar in summary:
                            if scalar["kernel"] != kernel or scalar["datatype"] != datatype or scalar["build"] != "gcc-scalar":
                                continue
                            vector = next(r for r in summary if r["kernel"] == kernel and r["datatype"] == datatype
                                          and r["target_working_set_bytes"] == scalar["target_working_set_bytes"] and r["build"] == build)
                            points.append((scalar["target_working_set_bytes"], scalar["median_ns_per_element"] / vector["median_ns_per_element"]))
                        points.sort()
                        plt.plot([p[0] for p in points], [p[1] for p in points], marker="o", label=f"{datatype} {build}")
            else:
                metric = "median_gflop_per_s" if category == "throughput" else "median_effective_bandwidth_gib_per_s"
                for datatype in ("float32", "float64"):
                    for build in ("gcc-scalar", "gcc-auto", "gcc-native"):
                        points = [r for r in summary if r["kernel"] == kernel and r["build"] == build and r["datatype"] == datatype]
                        points.sort(key=lambda r: r["target_working_set_bytes"])
                        plt.plot([r["target_working_set_bytes"] for r in points], [r[metric] for r in points], marker="o", label=f"{datatype} {build}")
            plt.xscale("log", base=2)
            plt.xlabel("Target logical working set (bytes)")
            plt.ylabel(ylabel)
            plt.title(f"{kernel}: {file_stem}")
            plt.grid(True, which="both", alpha=0.25)
            plt.legend()
            plt.tight_layout()
            plt.savefig(PLOT_DIR / f"{file_stem}_{kernel}.png", dpi=160)
            plt.close()

        plt.figure(figsize=(8, 5))
        for datatype in ("float32", "float64"):
            points = [r for r in summary if r["kernel"] == kernel and r["build"] == "gcc-native" and r["datatype"] == datatype]
            points.sort(key=lambda r: r["target_working_set_bytes"])
            plt.errorbar(
                [r["target_working_set_bytes"] for r in points],
                [r["median_ns_per_element"] for r in points],
                yerr=[r["stddev_ns_per_element"] for r in points],
                marker="o", label=datatype,
            )
        plt.xscale("log", base=2)
        plt.xlabel("Target logical working set (bytes)")
        plt.ylabel("Median ns/element")
        plt.title(f"{kernel}: float32 vs float64 (GCC native)")
        plt.grid(True, which="both", alpha=0.25)
        plt.legend()
        plt.tight_layout()
        plt.savefig(PLOT_DIR / f"float32_vs_float64_{kernel}.png", dpi=160)
        plt.close()


def analyze_full(path, rerun_paths):
    path = Path(path)
    rows, summary, scalar_simd_rows, datatype_rows = aggregate_full(path)
    plot_full(rows, summary, scalar_simd_rows, datatype_rows)
    cv = [row["coefficient_of_variation"] for row in summary]
    high_variability = [row for row in summary if row["coefficient_of_variation"] > 0.10]
    target_sizes = sorted({row["target_working_set_bytes"] for row in summary})
    phase3_report = [
        "# Phase 3 Core Performance Experiments",
        "",
        "Measured results from the configured native Windows GCC matrix. Interpret noisy configurations cautiously; this is not a Phase 4/5 analysis.",
        "",
        f"- Raw timed samples: {len(rows)} across {len(summary)} configurations.",
        f"- Working-set sizes: {len(target_sizes)}; target footprints: "
        + ", ".join(f"{size:,}" for size in target_sizes) + " bytes.",
        f"- Repetitions per configuration: {summary[0]['samples'] if summary else 0}; warmups: 3.",
        "- Affinity: one benchmark thread pinned to logical CPU 0; recorded in each raw row.",
        "- Main timing statistic: median; mean, standard deviation, minimum, maximum, and CV retained.",
        f"- Median configuration CV: {statistics.median(cv):.3%}; maximum CV: {max(cv):.3%}; above 10% CV: {len(high_variability)}/{len(summary)}.",
        "- All measurements use `std::chrono::steady_clock`; allocation, initialization, checksum traversal, and CSV writing are outside the timed interval.",
        "- Effective bandwidth is useful logical bytes / measured time, not direct DRAM-controller bandwidth.",
        "- Useful bytes per call: AXPY `3*N*sizeof(T)`; dot `2*N*sizeof(T)`; elementwise multiply `3*N*sizeof(T)`; stencil `4*(N-2)+4` elements for N>=2 and two elements for N=1.",
        f"- Canonical raw samples: `data/raw/{path.name}`. `phase3_raw.csv` and partial `phase3_raw_v2.csv` are retained as superseded datasets; `phase3_samples_corrected.csv` preserves v3 elapsed samples and recalculates only derived operation/useful-byte/throughput fields for exact stencil endpoint accounting.",
        "- No Phase 4 alignment/tail/stride/negative-case experiments, roofline analysis, or broad uProf collection were run.",
        "",
        "## Conservative Working-Set Notes",
        "",
        "Windows reports 16 MiB aggregate L2 and 64 MiB L3. Some kernels show broad changes around 24–64 MiB, but variability also rises in this region. The target footprint is the aggregate logical arrays for this single-thread workload. Treat behavior as cache-resident, intermediate-transition, or large-working-set/DRAM-sensitive only; no exact L3 boundary is inferred.",
        "",
        "## Representative Measured Speedups",
        "",
        "| Kernel | Type | Working set | Auto vs scalar | Native vs scalar |",
        "|---|---|---|---:|---:|",
    ]
    for row in scalar_simd_rows:
        phase3_report.append(
            f"| {row['kernel']} | {row['datatype']} | {row['working_set_class']} ({row['working_set_bytes']:,} B) | "
            f"{row['auto_speedup']:.3f}x | {row['native_speedup']:.3f}x |"
        )
    phase3_report.extend([
        "",
        f"Full representative tables are in `scalar_vs_simd.md` and `datatype_summary.md`; all measured configurations are in `phase3_statistics.csv` and raw samples remain in `data/raw/{path.name}`.",
    ])
    PHASE3_SUMMARY_MD.write_text("\n".join(phase3_report) + "\n", encoding="utf-8")

    anomaly_report = [
        "# Phase 3 Variability and Anomalies",
        "",
        f"Across {len(summary)} configurations, {len(high_variability)} exceeded 10% CV; max CV was {max(cv):.3%} and median CV was {statistics.median(cv):.3%}.",
        "The raw samples are preserved; no outlier was discarded. One highest-CV configuration was rerun once, as required.",
        "",
        "| Kernel | Type | Build | N | Target bytes | CV | Median ns/element | Min | Max |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(high_variability, key=lambda item: item["coefficient_of_variation"], reverse=True)[:20]:
        anomaly_report.append(
            f"| {row['kernel']} | {row['datatype']} | {row['build']} | {row['n']} | {row['target_working_set_bytes']:,} | "
            f"{row['coefficient_of_variation']:.3%} | {row['median_ns_per_element']:.6g} | "
            f"{row['min_ns_per_element']:.6g} | {row['max_ns_per_element']:.6g} |"
        )
    if rerun_paths:
        anomaly_report.extend(["", "## Targeted Reruns", "", "| Raw file | Configuration | Original median | Original CV | Rerun median | Rerun CV | Median difference | Speedup direction changed? |", "|---|---|---:|---:|---:|---:|---:|---|"])
        for rerun_path in rerun_paths:
            rerun_rows = load_rows(rerun_path)
            for key, samples in group_rows(rerun_rows, ["kernel", "datatype", "build", "n", "target_working_set_bytes"]).items():
                kernel, datatype, build, n, target_bytes = key
                stats_for_rerun = sample_stats(samples)
                original = next((row for row in summary
                                 if row["kernel"] == kernel and row["datatype"] == datatype
                                 and row["build"] == build and row["n"] == int(n)
                                 and row["target_working_set_bytes"] == int(target_bytes)), None)
                original_cv = "n/a" if original is None else f"{original['coefficient_of_variation']:.3%}"
                original_median = "n/a" if original is None else f"{original['median_ns_per_element']:.6g}"
                relative_difference = "n/a"
                speedup_changed = "n/a"
                if original is not None:
                    original_median_value = original["median_ns_per_element"]
                    rerun_median_value = stats_for_rerun["median_ns_per_element"]
                    relative_difference = f"{100 * (rerun_median_value / original_median_value - 1):+.2f}%"
                    scalar = next((row for row in summary
                                   if row["kernel"] == kernel and row["datatype"] == datatype
                                   and row["build"] == "gcc-scalar" and row["n"] == int(n)
                                   and row["target_working_set_bytes"] == int(target_bytes)), None)
                    if scalar is not None and build != "gcc-scalar":
                        old_speedup = scalar["median_ns_per_element"] / original_median_value
                        rerun_speedup = scalar["median_ns_per_element"] / rerun_median_value
                        speedup_changed = "yes" if (old_speedup >= 1.0) != (rerun_speedup >= 1.0) else "no"
                anomaly_report.append(
                    f"| `{rerun_path.name}` | {kernel} {datatype} {build}, N={n}, {int(target_bytes):,} B | "
                    f"{original_median} | {original_cv} | {stats_for_rerun['median_ns_per_element']:.6g} | "
                    f"{stats_for_rerun['coefficient_of_variation']:.3%} | {relative_difference} | {speedup_changed} |"
                )
    ANOMALY_REPORT_MD.write_text("\n".join(anomaly_report) + "\n", encoding="utf-8")
    print(f"Raw samples: {len(rows)}")
    print(f"Configurations: {len(summary)}")
    print(f"Median configuration CV: {statistics.median(cv):.4%}; max CV: {max(cv):.4%}")
    print(f"Configurations above 10% CV: {len(high_variability)}")
    print(f"Statistics: {STATS_PATH}")
    print(f"Scalar/SIMD table: {SCALAR_SIMD}")
    print(f"Datatype table: {DATATYPE_TABLE}")
    print(f"Plots: {PLOT_DIR}")
    print(f"Summary report: {PHASE3_SUMMARY_MD}")
    print(f"Anomaly report: {ANOMALY_REPORT_MD}")
    print(f"Variability diagnostic: {VARIABILITY_DIAGNOSTIC_MD} / {VARIABILITY_DIAGNOSTIC}")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pilot", type=Path)
    group.add_argument("--full", type=Path)
    parser.add_argument("--rerun", type=Path, action="append", default=[])
    args = parser.parse_args()
    if args.pilot:
        analyze_pilot(args.pilot, args.rerun)
    else:
        analyze_full(args.full, args.rerun)


if __name__ == "__main__":
    main()
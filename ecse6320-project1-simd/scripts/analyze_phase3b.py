import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RAW_V3 = ROOT / "data" / "raw" / "phase3_raw_v3.csv"
SELECTION = ROOT / "data" / "metadata" / "phase3b_rerun_selection.csv"
RERUNS = ROOT / "data" / "raw" / "phase3b_targeted_reruns.csv"
SAMPLES_OUT = ROOT / "data" / "processed" / "phase3b_samples.csv"
STATS_OUT = ROOT / "data" / "processed" / "phase3b_statistics.csv"
SPEEDUP_OUT = ROOT / "results" / "tables" / "phase3b_scalar_vs_simd.csv"
SPEEDUP_MD = ROOT / "results" / "tables" / "phase3b_scalar_vs_simd.md"
DATATYPE_OUT = ROOT / "results" / "tables" / "phase3b_datatype_summary.csv"
DATATYPE_MD = ROOT / "results" / "tables" / "phase3b_datatype_summary.md"
COMPARISON_OUT = ROOT / "data" / "processed" / "phase3b_rerun_comparison.csv"
SUMMARY_MD = ROOT / "results" / "tables" / "phase3b_summary.md"
ANOMALY_MD = ROOT / "results" / "tables" / "phase3b_anomalies.md"
PLOT_DIR = ROOT / "results" / "plots"


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as source:
        return [{key.lower(): value for key, value in row.items()}
                for row in csv.DictReader(source)]


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Refusing to write empty result table: {path}")
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def config_key(row):
    return (
        row["kernel"], row["datatype"], row["build"], int(row["n"]),
        int(row["target_working_set_bytes"]),
    )


def derived_fields(row):
    n = int(row["n"])
    batch = int(row["batching_count"])
    element_bytes = 4 if row["datatype"] == "float32" else 8
    kernel = row["kernel"]
    if kernel == "elementwise_multiply":
        operations = n
        useful_bytes = 3 * n * element_bytes
    elif kernel in ("axpy", "dot_product"):
        operations = 2 * n
        useful_bytes = (3 if kernel == "axpy" else 2) * n * element_bytes
    elif kernel == "stencil_1d_three_point":
        operations = 5 * max(0, n - 2)
        useful_bytes = (0 if n == 0 else 2 if n == 1 else 4 * n - 4) * element_bytes
    else:
        raise ValueError(f"Unexpected kernel {kernel}")
    elapsed_ns = int(row["elapsed_ns"])
    if elapsed_ns <= 0:
        raise ValueError("Found non-positive elapsed sample")
    operations *= batch
    useful_bytes *= batch
    row["operations_performed"] = operations
    row["useful_bytes_processed"] = useful_bytes
    row["ns_per_element"] = elapsed_ns / (n * batch)
    row["gflop_per_s"] = operations / elapsed_ns
    row["effective_bandwidth_gib_per_s"] = useful_bytes * 1.0e9 / elapsed_ns / (1024 ** 3)
    return row


def grouped(rows, key_fn):
    result = defaultdict(list)
    for row in rows:
        result[key_fn(row)].append(row)
    return result


def stats(rows):
    time_per_element = [float(row["ns_per_element"]) for row in rows]
    mean_value = statistics.mean(time_per_element)
    stddev = statistics.stdev(time_per_element) if len(time_per_element) > 1 else 0.0
    return {
        "samples": len(rows),
        "median_ns_per_element": statistics.median(time_per_element),
        "mean_ns_per_element": mean_value,
        "stddev_ns_per_element": stddev,
        "min_ns_per_element": min(time_per_element),
        "max_ns_per_element": max(time_per_element),
        "coefficient_of_variation": stddev / mean_value if mean_value else 0.0,
        "median_elapsed_ns": statistics.median(float(row["elapsed_ns"]) for row in rows),
        "median_gflop_per_s": statistics.median(float(row["gflop_per_s"]) for row in rows),
        "median_effective_bandwidth_gib_per_s": statistics.median(
            float(row["effective_bandwidth_gib_per_s"]) for row in rows
        ),
    }


def save_tables(merged_stats):
    stats_index = {
        (row["kernel"], row["datatype"], row["target_working_set_bytes"], row["build"]): row
        for row in merged_stats
    }
    representatives = {24576: "small", 25165824: "intermediate", 134217728: "large"}
    speedups = []
    for scalar in merged_stats:
        if scalar["build"] != "gcc-scalar" or scalar["target_working_set_bytes"] not in representatives:
            continue
        auto = stats_index[(scalar["kernel"], scalar["datatype"], scalar["target_working_set_bytes"], "gcc-auto")]
        native = stats_index[(scalar["kernel"], scalar["datatype"], scalar["target_working_set_bytes"], "gcc-native")]
        speedups.append({
            "kernel": scalar["kernel"], "datatype": scalar["datatype"],
            "working_set_bytes": scalar["target_working_set_bytes"],
            "working_set_class": representatives[scalar["target_working_set_bytes"]],
            "scalar_median_ns_per_element": scalar["median_ns_per_element"],
            "auto_median_ns_per_element": auto["median_ns_per_element"],
            "native_median_ns_per_element": native["median_ns_per_element"],
            "auto_speedup": scalar["median_ns_per_element"] / auto["median_ns_per_element"],
            "native_speedup": scalar["median_ns_per_element"] / native["median_ns_per_element"],
            "auto_gflop_per_s": auto["median_gflop_per_s"],
            "native_gflop_per_s": native["median_gflop_per_s"],
            "auto_effective_gib_per_s": auto["median_effective_bandwidth_gib_per_s"],
            "native_effective_gib_per_s": native["median_effective_bandwidth_gib_per_s"],
        })
    write_csv(SPEEDUP_OUT, speedups)
    speed_lines = [
        "# Phase 3B Scalar vs SIMD Summary", "",
        "Uses v3 original samples except explicitly rerun configurations, for which only the targeted rerun samples are used.", "",
        "| Kernel | Type | Working set | Scalar ns/element | Auto ns/element | Native ns/element | Auto speedup | Native speedup | Auto GFLOP/s | Native GFLOP/s | Auto effective GiB/s | Native effective GiB/s |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in speedups:
        speed_lines.append(
            f"| {row['kernel']} | {row['datatype']} | {row['working_set_class']} ({row['working_set_bytes']:,} B) | "
            f"{row['scalar_median_ns_per_element']:.6g} | {row['auto_median_ns_per_element']:.6g} | "
            f"{row['native_median_ns_per_element']:.6g} | {row['auto_speedup']:.3f}x | "
            f"{row['native_speedup']:.3f}x | {row['auto_gflop_per_s']:.6g} | "
            f"{row['native_gflop_per_s']:.6g} | {row['auto_effective_gib_per_s']:.6g} | "
            f"{row['native_effective_gib_per_s']:.6g} |"
        )
    SPEEDUP_MD.write_text("\n".join(speed_lines) + "\n", encoding="utf-8")

    datatype_rows = []
    representative_keys = sorted({
        (row["kernel"], row["build"], row["target_working_set_bytes"])
        for row in merged_stats if row["target_working_set_bytes"] in representatives
    })
    for kernel, build, working_set in representative_keys:
        f32 = stats_index[(kernel, "float32", working_set, build)]
        f64 = stats_index[(kernel, "float64", working_set, build)]
        datatype_rows.append({
            "kernel": kernel, "build": build, "working_set_bytes": working_set,
            "float32_median_ns_per_element": f32["median_ns_per_element"],
            "float64_median_ns_per_element": f64["median_ns_per_element"],
            "float64_over_float32_time_ratio": f64["median_ns_per_element"] / f32["median_ns_per_element"],
            "float32_median_gflop_per_s": f32["median_gflop_per_s"],
            "float64_median_gflop_per_s": f64["median_gflop_per_s"],
            "float32_effective_gib_per_s": f32["median_effective_bandwidth_gib_per_s"],
            "float64_effective_gib_per_s": f64["median_effective_bandwidth_gib_per_s"],
        })
    write_csv(DATATYPE_OUT, datatype_rows)

    return speedups, datatype_rows


def save_phase3b_plots(merged_stats):
    kernels = sorted({row["kernel"] for row in merged_stats})
    file_metrics = [
        ("speedup_vs_working_set", "speedup"),
        ("throughput_vs_working_set", "median_gflop_per_s"),
        ("effective_bandwidth_vs_working_set", "median_effective_bandwidth_gib_per_s"),
        ("ns_per_element_vs_working_set", "median_ns_per_element"),
    ]
    plot_paths = []
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    lookup = {(row["kernel"], row["datatype"], row["target_working_set_bytes"], row["build"]): row
              for row in merged_stats}
    for kernel in kernels:
        for stem, metric in file_metrics:
            plt.figure(figsize=(8, 5))
            for datatype in ("float32", "float64"):
                for build in ("gcc-scalar", "gcc-auto", "gcc-native"):
                    points = [row for row in merged_stats if row["kernel"] == kernel
                              and row["datatype"] == datatype and row["build"] == build]
                    points.sort(key=lambda row: row["target_working_set_bytes"])
                    if metric == "speedup":
                        if build == "gcc-scalar":
                            continue
                        x_values = []
                        y_values = []
                        for vector in points:
                            scalar = lookup[(kernel, datatype, vector["target_working_set_bytes"], "gcc-scalar")]
                            x_values.append(vector["target_working_set_bytes"])
                            y_values.append(scalar["median_ns_per_element"] / vector["median_ns_per_element"])
                        plt.plot(x_values, y_values, marker="o", label=f"{datatype} {build}")
                    else:
                        plt.errorbar(
                            [row["target_working_set_bytes"] for row in points],
                            [row[metric] for row in points],
                            yerr=[row["stddev_ns_per_element"] for row in points]
                            if metric == "median_ns_per_element" else None,
                            marker="o", label=f"{datatype} {build}",
                        )
            plt.xscale("log", base=2)
            plt.xlabel("Target logical working set (bytes)")
            ylabel = "Speedup vs scalar" if metric == "speedup" else {
                "median_gflop_per_s": "GFLOP/s",
                "median_effective_bandwidth_gib_per_s": "Effective GiB/s",
                "median_ns_per_element": "Median ns/element",
            }[metric]
            plt.ylabel(ylabel)
            plt.title(f"Phase 3B {kernel}: {stem.replace('_', ' ')}")
            plt.grid(True, which="both", alpha=0.25)
            plt.legend()
            plt.tight_layout()
            path = PLOT_DIR / f"phase3b_{stem}_{kernel}.png"
            plt.savefig(path, dpi=160)
            plt.close()
            plot_paths.append(path)

        plt.figure(figsize=(8, 5))
        for datatype in ("float32", "float64"):
            points = [row for row in merged_stats if row["kernel"] == kernel
                      and row["build"] == "gcc-native" and row["datatype"] == datatype]
            points.sort(key=lambda row: row["target_working_set_bytes"])
            plt.errorbar(
                [row["target_working_set_bytes"] for row in points],
                [row["median_ns_per_element"] for row in points],
                yerr=[row["stddev_ns_per_element"] for row in points],
                marker="o", label=datatype,
            )
        plt.xscale("log", base=2)
        plt.xlabel("Target logical working set (bytes)")
        plt.ylabel("Median ns/element")
        plt.title(f"Phase 3B {kernel}: float32 vs float64 (GCC native)")
        plt.grid(True, which="both", alpha=0.25)
        plt.legend()
        plt.tight_layout()
        path = PLOT_DIR / f"phase3b_float32_vs_float64_{kernel}.png"
        plt.savefig(path, dpi=160)
        plt.close()
        plot_paths.append(path)
    return plot_paths


def main():
    original = [derived_fields(row) for row in read_csv(RAW_V3)]
    selection_rows = read_csv(SELECTION)
    selection_keys = {config_key(row) for row in selection_rows}
    reruns = [derived_fields(row) for row in read_csv(RERUNS)]
    rerun_keys = {config_key(row) for row in reruns}
    if rerun_keys != selection_keys:
        raise ValueError("Selection manifest and targeted rerun configurations differ.")

    original_groups = grouped(original, config_key)
    rerun_groups = grouped(reruns, config_key)
    for key in selection_keys:
        if len(original_groups[key]) != 10 or len(rerun_groups[key]) != 10:
            raise ValueError(f"Rerun/original configuration must contain 10 samples: {key}")

    merged = []
    for row in original:
        key = config_key(row)
        if key in selection_keys:
            continue
        row["measurement_source"] = "phase3_raw_v3_original"
        merged.append(row)
    for row in reruns:
        row["measurement_source"] = "phase3b_targeted_rerun"
        merged.append(row)
    if len(merged) != len(original):
        raise ValueError(f"Merged sample count changed unexpectedly: {len(merged)} vs {len(original)}")
    write_csv(SAMPLES_OUT, merged)

    stats_groups = grouped(merged, config_key)
    merged_stats = []
    for key, samples in sorted(stats_groups.items(), key=lambda item: (
        item[0][0], item[0][1], item[0][4], item[0][2]
    )):
        kernel, datatype, build, n, target_bytes = key
        merged_stats.append({
            "kernel": kernel, "datatype": datatype, "build": build,
            "n": n, "target_working_set_bytes": target_bytes,
            "measurement_source": samples[0]["measurement_source"],
            **stats(samples),
        })
    write_csv(STATS_OUT, merged_stats)
    speedups, datatype_rows = save_tables(merged_stats)

    comparison = []
    old_stats = {key: stats(samples) for key, samples in original_groups.items()}
    new_stats = {key: stats(samples) for key, samples in stats_groups.items()}
    for row in selection_rows:
        key = config_key(row)
        old = old_stats[key]
        new = new_stats[key]
        relative_delta = 100 * (new["median_ns_per_element"] / old["median_ns_per_element"] - 1)
        kernel, datatype, build, n, working_set = key
        scalar_key = (kernel, datatype, "gcc-scalar", n, working_set)
        auto_key = (kernel, datatype, "gcc-auto", n, working_set)
        native_key = (kernel, datatype, "gcc-native", n, working_set)
        speedup_changes = {}
        for label, vector_key in (("auto", auto_key), ("native", native_key)):
            old_scalar = old_stats[scalar_key]["median_ns_per_element"]
            old_vector = old_stats[vector_key]["median_ns_per_element"]
            new_scalar = new_stats[scalar_key]["median_ns_per_element"]
            new_vector = new_stats[vector_key]["median_ns_per_element"]
            old_speedup = old_scalar / old_vector
            new_speedup = new_scalar / new_vector
            speedup_changes[label] = (old_speedup, new_speedup, (old_speedup >= 1) != (new_speedup >= 1))
        comparison.append({
            "kernel": kernel, "datatype": datatype, "build": build,
            "n": n, "target_working_set_bytes": working_set,
            "reason": row["selection_reason"],
            "original_median_ns_per_element": old["median_ns_per_element"],
            "original_cv": old["coefficient_of_variation"],
            "rerun_median_ns_per_element": new["median_ns_per_element"],
            "rerun_cv": new["coefficient_of_variation"],
            "relative_median_difference_percent": relative_delta,
            "auto_speedup_original": speedup_changes["auto"][0],
            "auto_speedup_phase3b": speedup_changes["auto"][1],
            "auto_speedup_direction_changed": speedup_changes["auto"][2],
            "native_speedup_original": speedup_changes["native"][0],
            "native_speedup_phase3b": speedup_changes["native"][1],
            "native_speedup_direction_changed": speedup_changes["native"][2],
        })
    write_csv(COMPARISON_OUT, comparison)

    cvs = [row["coefficient_of_variation"] for row in merged_stats]
    changed = [row for row in comparison if abs(row["relative_median_difference_percent"]) >= 5]
    phase_summary = [
        "# Phase 3B Stabilization and Validation",
        "",
        "This is a versioned reprocessing of the Phase 3 v3 dataset. Original raw v3 samples are unchanged. For only explicitly selected rerun configurations, Phase 3B uses the ten rerun samples instead of the ten original samples; every other configuration uses the original v3 samples.",
        "",
        f"- Original and Phase 3B configurations: {len(merged_stats)}.",
        f"- Configurations selectively rerun: {len(selection_keys)} (cap 40); targeted raw rows: {len(reruns)}.",
        f"- Phase 3B configurations above 10% CV: {sum(cv > .10 for cv in cvs)}; above 20% CV: {sum(cv > .20 for cv in cvs)}.",
        f"- Phase 3B median configuration CV: {statistics.median(cvs):.3%}; maximum CV: {max(cvs):.3%}.",
        f"- Rerun configurations with median-time shift >=5%: {len(changed)}/{len(comparison)}.",
        f"- Rerun configurations that changed a speedup direction across 1.0: {sum(row['auto_speedup_direction_changed'] or row['native_speedup_direction_changed'] for row in comparison)}.",
        "- No original sample was deleted or overwritten; see `data/processed/phase3b_samples.csv` for the merged source-labelled set.",
        "- Detailed original-versus-rerun medians, CVs, relative changes, and speedup-direction checks: `data/processed/phase3b_rerun_comparison.csv`.",
        "- Phase 3B statistics/tables: `data/processed/phase3b_statistics.csv`, `results/tables/phase3b_scalar_vs_simd.md`, and `results/tables/phase3b_datatype_summary.csv`.",
        "- Dot accuracy uses a separate N-dependent floating-point bound; see `data/processed/dot_accuracy_phase3b_v4.csv` and `results/tables/dot_accuracy_phase3b.md`. The largest float32 bound is valid but non-informative.",
        "- Because 31/40 rerun medians shifted by at least 5%, 20 separate `phase3b_*.png` plots were generated; original Phase 3 plots were left untouched.",
        "",
        "High-CV residual configurations remain explicitly unstable; do not repeatedly rerun them for a preferred result. No Phase 4 work was performed.",
    ]
    SUMMARY_MD.write_text("\n".join(phase_summary) + "\n", encoding="utf-8")

    residual = [row for row in merged_stats if row["coefficient_of_variation"] > 0.10]
    anomaly_lines = [
        "# Phase 3B Residual Variability",
        "",
        f"{len(residual)}/{len(merged_stats)} merged configurations remain above 10% CV; "
        f"{sum(row['coefficient_of_variation'] > 0.20 for row in merged_stats)} remain above 20% CV.",
        "No residual point was rerun more than once. Original and rerun samples are preserved separately.",
        "",
        "| Kernel | Type | Build | N | Target bytes | CV | Median ns/element | Min | Max | Source |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in sorted(residual, key=lambda item: item["coefficient_of_variation"], reverse=True)[:30]:
        anomaly_lines.append(
            f"| {row['kernel']} | {row['datatype']} | {row['build']} | {row['n']} | "
            f"{row['target_working_set_bytes']:,} | {row['coefficient_of_variation']:.3%} | "
            f"{row['median_ns_per_element']:.6g} | {row['min_ns_per_element']:.6g} | "
            f"{row['max_ns_per_element']:.6g} | {row['measurement_source']} |"
        )
    ANOMALY_MD.write_text("\n".join(anomaly_lines) + "\n", encoding="utf-8")

    material = len(changed) > 0 or any(
        row["auto_speedup_direction_changed"] or row["native_speedup_direction_changed"]
        for row in comparison
    )
    if material:
        phase3b_plots = save_phase3b_plots(merged_stats)
        print(f"Material timing changes detected in {len(changed)} rerun configurations; generated {len(phase3b_plots)} separate Phase 3B plots.")
    else:
        print("No rerun median shifts >=5%; existing Phase 3 plots remain representative, so no duplicate plots were generated.")

    print(f"Phase 3B samples={len(merged)}; configurations={len(merged_stats)}; reruns={len(selection_keys)}; CV>10={sum(cv > .10 for cv in cvs)}; CV>20={sum(cv > .20 for cv in cvs)}")
    print(f"Phase 3B statistics: {STATS_OUT}")
    print(f"Rerun comparison: {COMPARISON_OUT}")
    print(f"Phase 3B summary: {SUMMARY_MD}")
    print(f"Phase 3B residual anomalies: {ANOMALY_MD}")


if __name__ == "__main__":
    main()
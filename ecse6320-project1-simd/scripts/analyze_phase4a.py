import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
STATS_OUT = ROOT / "data" / "processed" / "phase4a_alignment_statistics.csv"
OVERHEAD_OUT = ROOT / "results" / "tables" / "phase4a_alignment_overhead.csv"
SUMMARY_OUT = ROOT / "results" / "tables" / "phase4a_alignment_summary.md"
PLOT_DIR = ROOT / "results" / "plots"
RERUN_SELECTION_OUT = ROOT / "data" / "metadata" / "phase4a_alignment_rerun_selection.csv"
SIZES = (24576, 25165824, 134217728)
KERNELS = ("axpy", "elementwise_multiply")
DATATYPES = ("float32", "float64")
BUILDS = ("gcc-scalar", "gcc-auto", "gcc-native")
CONDITIONS = ("aligned_64B", "offset_one_element", "cache_line_crossing")
REPRESENTATIVES = {24576: "small", 25165824: "intermediate", 134217728: "large"}


def read_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as source:
        return [{key.lower(): value for key, value in row.items()}
                for row in csv.DictReader(source)]


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"Refusing to write an empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def key_for(row):
    return (
        row["kernel"], row["datatype"], row["build"],
        int(row["target_working_set_bytes"]), row["alignment_condition"],
    )


def stats(samples):
    values = [float(row["ns_per_element"]) for row in samples]
    mean_value = statistics.mean(values)
    deviation = statistics.stdev(values) if len(values) > 1 else 0.0
    return {
        "samples": len(values),
        "median_ns_per_element": statistics.median(values),
        "mean_ns_per_element": mean_value,
        "stddev_ns_per_element": deviation,
        "min_ns_per_element": min(values),
        "max_ns_per_element": max(values),
        "coefficient_of_variation": deviation / mean_value if mean_value else 0.0,
        "median_elapsed_ns": statistics.median(float(row["elapsed_ns"]) for row in samples),
        "median_gflop_per_s": statistics.median(float(row["gflop_per_s"]) for row in samples),
        "median_effective_bandwidth_gib_per_s": statistics.median(
            float(row["effective_bandwidth_gib_per_s"]) for row in samples
        ),
    }


def validate_raw(rows, expected_repetitions, allowed_keys=None):
    expected_keys = {
        (kernel, datatype, build, size, condition)
        for kernel in KERNELS for datatype in DATATYPES for build in BUILDS
        for size in SIZES for condition in CONDITIONS
    }
    groups = defaultdict(list)
    for row in rows:
        if row["correctness"] != "pass":
            raise ValueError(f"Raw row did not pass correctness: {row}")
        key = key_for(row)
        groups[key].append(row)
        expected_mod = {
            "aligned_64B": 0,
            "offset_one_element": 4 if row["datatype"] == "float32" else 8,
            "cache_line_crossing": 60 if row["datatype"] == "float32" else 56,
        }[row["alignment_condition"]]
        for field in ("x_address_mod64", "y_address_mod64", "output_address_mod64"):
            if int(row[field]) != expected_mod:
                raise ValueError(f"Unexpected {field}={row[field]} for {key}; expected {expected_mod}")
        if int(row["elapsed_ns"]) <= 0:
            raise ValueError(f"Non-positive timed sample for {key}")

    required_keys = expected_keys if allowed_keys is None else allowed_keys
    if (allowed_keys is None and set(groups) != required_keys) or not set(groups).issubset(required_keys):
        missing = sorted(required_keys - set(groups)) if allowed_keys is None else []
        unexpected = sorted(set(groups) - required_keys)
        raise ValueError(f"Configuration matrix mismatch; missing={missing[:3]}, unexpected={unexpected[:3]}")
    for key, samples in groups.items():
        reps = sorted(int(row["repetition"]) for row in samples)
        if len(samples) != expected_repetitions or reps != list(range(1, expected_repetitions + 1)):
            raise ValueError(f"Expected repetitions 1..{expected_repetitions} for {key}, got {reps}")
    if len(rows) != len(groups) * expected_repetitions:
        raise ValueError(f"Raw row count mismatch: {len(rows)}")
    return groups


def build_outputs(groups, raw_path, expected_repetitions, initial_row_count, rerun_row_count=0):
    statistics_rows = []
    stats_index = {}
    for key, samples in sorted(groups.items()):
        kernel, datatype, build, target_size, condition = key
        summary = stats(samples)
        row = {
            "kernel": kernel,
            "datatype": datatype,
            "build": build,
            "target_working_set_bytes": target_size,
            "working_set_class": REPRESENTATIVES[target_size],
            "alignment_condition": condition,
            "N": int(samples[0]["n"]),
            "actual_working_set_bytes": int(samples[0]["working_set_bytes"]),
            "offset_elements": int(samples[0]["offset_elements"]),
            "offset_bytes": int(samples[0]["offset_bytes"]),
            "pointer_mod64": int(samples[0]["x_address_mod64"]),
            "measurement_source": "initial_plus_targeted_rerun" if len(samples) > expected_repetitions else "initial",
            **summary,
        }
        statistics_rows.append(row)
        stats_index[key] = row
    write_csv(STATS_OUT, statistics_rows)

    if rerun_row_count == 0:
        selection = [
            {
                "kernel": row["kernel"],
                "datatype": row["datatype"],
                "build": row["build"],
                "target_working_set_bytes": row["target_working_set_bytes"],
                "alignment_condition": row["alignment_condition"],
                "initial_cv": row["coefficient_of_variation"],
                "selection_reason": "initial_cv_gt_20_percent",
            }
            for row in statistics_rows
            if row["coefficient_of_variation"] > 0.20 and row["samples"] == expected_repetitions
        ]
        write_csv(RERUN_SELECTION_OUT, selection or [{
            "kernel": "", "datatype": "", "build": "", "target_working_set_bytes": "",
            "alignment_condition": "", "initial_cv": "", "selection_reason": "",
        }])

    overhead_rows = []
    for kernel in KERNELS:
        for datatype in DATATYPES:
            for build in BUILDS:
                for target_size in SIZES:
                    aligned_key = (kernel, datatype, build, target_size, "aligned_64B")
                    aligned = stats_index[aligned_key]
                    for condition in CONDITIONS[1:]:
                        offset = stats_index[(kernel, datatype, build, target_size, condition)]
                        overhead_ratio = offset["median_ns_per_element"] / aligned["median_ns_per_element"]
                        row = {
                            "kernel": kernel,
                            "datatype": datatype,
                            "build": build,
                            "target_working_set_bytes": target_size,
                            "working_set_class": REPRESENTATIVES[target_size],
                            "alignment_condition": condition,
                            "offset_bytes": offset["offset_bytes"],
                            "aligned_median_ns_per_element": aligned["median_ns_per_element"],
                            "offset_median_ns_per_element": offset["median_ns_per_element"],
                            "alignment_overhead_percent": (overhead_ratio - 1.0) * 100.0,
                            "aligned_cv": aligned["coefficient_of_variation"],
                            "offset_cv": offset["coefficient_of_variation"],
                            "offset_over_aligned_speedup": 1.0 / overhead_ratio,
                        }
                        if build != "gcc-scalar":
                            scalar = stats_index[(kernel, datatype, "gcc-scalar", target_size, condition)]
                            scalar_aligned = stats_index[(kernel, datatype, "gcc-scalar", target_size, "aligned_64B")]
                            simd_speedup = scalar["median_ns_per_element"] / offset["median_ns_per_element"]
                            aligned_simd_speedup = scalar_aligned["median_ns_per_element"] / aligned["median_ns_per_element"]
                            row["simd_speedup_at_condition"] = simd_speedup
                            row["simd_speedup_aligned"] = aligned_simd_speedup
                            row["simd_speedup_change_percent"] = (simd_speedup / aligned_simd_speedup - 1.0) * 100.0
                        else:
                            row["simd_speedup_at_condition"] = ""
                            row["simd_speedup_aligned"] = ""
                            row["simd_speedup_change_percent"] = ""
                        overhead_rows.append(row)
    write_csv(OVERHEAD_OUT, overhead_rows)
    save_plots(stats_index)
    save_summary(
        statistics_rows, overhead_rows, raw_path, expected_repetitions,
        initial_row_count, rerun_row_count,
    )
    return statistics_rows, overhead_rows


def save_plots(stats_index):
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    build_colors = {
        "gcc-scalar": "#4D4D4D",
        "gcc-auto": "#0072B2",
        "gcc-native": "#D55E00",
    }
    condition_styles = {"offset_one_element": "--", "cache_line_crossing": ":"}
    size_labels = ["24 KiB", "24 MiB", "128 MiB"]
    for kernel in KERNELS:
        figure, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
        for axis, datatype in zip(axes, DATATYPES):
            for build in BUILDS:
                for condition in CONDITIONS[1:]:
                    points = [
                        stats_index[(kernel, datatype, build, size, condition)]
                        for size in SIZES
                    ]
                    axis.plot(
                        range(len(SIZES)),
                        [100.0 * (point["median_ns_per_element"] /
                                  stats_index[(kernel, datatype, build, size, "aligned_64B")]["median_ns_per_element"] - 1.0)
                         for size, point in zip(SIZES, points)],
                        color=build_colors[build],
                        linestyle=condition_styles[condition],
                        marker="o",
                        label=f"{build.removeprefix('gcc-')} {condition.removeprefix('offset_').removeprefix('cache_line_')}",
                    )
            axis.axhline(0, color="#777777", linewidth=0.8)
            axis.set_xticks(range(len(SIZES)), size_labels)
            axis.set_title(datatype)
            axis.set_xlabel("Phase 3 target working set")
            axis.grid(True, alpha=0.25)
        axes[0].set_ylabel("Median time overhead vs aligned (%)")
        handles, labels = axes[0].get_legend_handles_labels()
        figure.legend(handles, labels, loc="lower center", ncol=3, frameon=False)
        figure.suptitle(f"Phase 4A {kernel}: alignment overhead")
        figure.tight_layout(rect=(0, 0.17, 1, 0.93))
        figure.savefig(PLOT_DIR / f"phase4a_alignment_overhead_{kernel}.png", dpi=160)
        plt.close(figure)


def save_summary(statistics_rows, overhead_rows, raw_path, expected_repetitions,
                 initial_row_count, rerun_row_count):
    cvs = [row["coefficient_of_variation"] for row in statistics_rows]
    high_cv = sorted(statistics_rows, key=lambda row: row["coefficient_of_variation"], reverse=True)[:10]
    overhead_by_group = defaultdict(list)
    for row in overhead_rows:
        overhead_by_group[(row["kernel"], row["datatype"], row["build"], row["alignment_condition"])].append(
            row["alignment_overhead_percent"]
        )
    lines = [
        "# Phase 4A Alignment Measurements",
        "",
        f"- Initial raw samples: `{raw_path.relative_to(ROOT).as_posix()}` ({initial_row_count} rows); targeted rerun rows: {rerun_row_count}.",
        f"- Summary: {len(statistics_rows)} configurations, {sum(row['samples'] for row in statistics_rows)} observations; initial repetitions {expected_repetitions}, maximum per configuration 10; 3 warmups; logical CPU 0.",
        "- Scope: AXPY and elementwise multiply, float32/float64, GCC scalar/auto/native, and the three selected Phase 3 working sets.",
        "- Alignment states: 64-byte aligned; one element offset (4/8 B); cache-line crossing (60/56 B). All input/output pointer residues were validated and every measured case passed correctness.",
        f"- Median configuration CV: {statistics.median(cvs):.3%}; maximum CV: {max(cvs):.3%}; CV >10%: {sum(value > 0.10 for value in cvs)}/{len(cvs)}; CV >20%: {sum(value > 0.20 for value in cvs)}/{len(cvs)}.",
        "- Alignment overhead is `(offset median ns/element / aligned median ns/element - 1) * 100`; negative values mean the offset case measured faster. Do not infer a causal benefit from small differences relative to CV.",
        "- SIMD speedup is scalar median / vector-build median at the same condition. The change in speedup is reported relative to the aligned condition.",
        "- Effective bandwidth is useful logical bytes/time, not measured memory-controller bandwidth. Phase 3 raw data and plots were not modified.",
        "",
        "## Median Alignment Overhead",
        "",
        "| Kernel | Type | Build | Condition | Size | Median overhead | CV aligned/offset |",
        "|---|---|---|---|---|---:|---:|",
    ]
    for row in overhead_rows:
        aligned_cv = row["aligned_cv"]
        offset_cv = row["offset_cv"]
        lines.append(
            f"| {row['kernel']} | {row['datatype']} | {row['build']} | {row['alignment_condition']} | "
            f"{row['working_set_class']} | {row['alignment_overhead_percent']:.3f}% | "
            f"{aligned_cv:.2%} / {offset_cv:.2%} |"
        )
    lines.extend([
        "",
        "## Highest Variability",
        "",
        "| Kernel | Type | Build | Size | Alignment | Median ns/element | CV |",
        "|---|---|---|---|---|---:|---:|",
    ])
    rerun_count = sum(row["samples"] > expected_repetitions for row in statistics_rows)
    if rerun_count:
        lines.insert(4, f"- One additional five-sample run was collected for {rerun_count} initial configurations with CV >20%; the separate file is `data/raw/phase4a_alignment_targeted_reruns.csv` and the selection is `data/metadata/phase4a_alignment_rerun_selection.csv`.")
    for row in high_cv:
        lines.append(
            f"| {row['kernel']} | {row['datatype']} | {row['build']} | {row['working_set_class']} | "
            f"{row['alignment_condition']} | {row['median_ns_per_element']:.6g} | "
            f"{row['coefficient_of_variation']:.2%} |"
        )
    lines.extend([
        "",
        "Plots: `results/plots/phase4a_alignment_overhead_axpy.png` and `results/plots/phase4a_alignment_overhead_elementwise_multiply.png`.",
        "",
        "Phase 4B (tails, stride, and negative case), Phase 5 (uProf/roofline), and Phase 6 are not included.",
    ])
    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--expected-repetitions", type=int, choices=range(1, 11), required=True)
    parser.add_argument("--rerun", type=Path)
    parser.add_argument("--rerun-repetitions", type=int, choices=range(1, 11), default=0)
    arguments = parser.parse_args()
    arguments.raw = arguments.raw.resolve()
    initial_rows = read_rows(arguments.raw)
    initial_groups = validate_raw(initial_rows, arguments.expected_repetitions)
    merged_groups = dict(initial_groups)
    rerun_rows = []
    if arguments.rerun is not None:
        if arguments.rerun_repetitions == 0:
            raise ValueError("--rerun-repetitions is required when --rerun is supplied.")
        arguments.rerun = arguments.rerun.resolve()
        rerun_rows = read_rows(arguments.rerun)
        rerun_groups = validate_raw(
            rerun_rows, arguments.rerun_repetitions, allowed_keys=set(initial_groups)
        )
        for key, samples in rerun_groups.items():
            if len(initial_groups[key]) + len(samples) > 10:
                raise ValueError(f"More than 10 total observations requested for {key}")
            if len(samples) != arguments.rerun_repetitions:
                raise ValueError(f"Unexpected targeted rerun repetition count for {key}")
            merged_groups[key] = initial_groups[key] + samples
    elif arguments.rerun_repetitions:
        raise ValueError("--rerun-repetitions cannot be used without --rerun.")
    statistics_rows, overhead_rows = build_outputs(
        merged_groups, arguments.raw, arguments.expected_repetitions,
        len(initial_rows), len(rerun_rows),
    )
    print(f"Validated {len(initial_groups)} initial configurations and {len(initial_rows)} initial timed samples.")
    if rerun_rows:
        print(f"Validated {len(rerun_rows)} separate targeted rerun samples; merged maximum is {max(row['samples'] for row in statistics_rows)} per configuration.")
    print(f"Wrote {STATS_OUT.relative_to(ROOT)}, {OVERHEAD_OUT.relative_to(ROOT)}, and {SUMMARY_OUT.relative_to(ROOT)}.")
    print(f"Wrote alignment plots for {', '.join(KERNELS)}.")


if __name__ == "__main__":
    main()
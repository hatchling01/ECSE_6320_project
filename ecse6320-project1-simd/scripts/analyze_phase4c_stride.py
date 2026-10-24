import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "experiment_config.json"
SAMPLES_OUT = ROOT / "data" / "processed" / "phase4c_stride_samples.csv"
STATS_OUT = ROOT / "data" / "processed" / "phase4c_stride_statistics.csv"
SUMMARY_CSV = ROOT / "results" / "tables" / "phase4c_stride_summary.csv"
SUMMARY_MD = ROOT / "results" / "tables" / "phase4c_stride_summary.md"
SELECTION_OUT = ROOT / "data" / "metadata" / "phase4c_stride_rerun_selection.csv"
PLOT_DIR = ROOT / "results" / "plots"


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as source:
        return [{key.lower(): value for key, value in row.items()}
                for row in csv.DictReader(source)]


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"Refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def config_index(config):
    return {span["name"]: span for span in config["spans"]}


def read_correctness(path):
    rows = read_csv(path)
    checks = defaultdict(list)
    for row in rows:
        key = (row["build"], row["span_name"], int(row["stride"]))
        if row["status"].upper() != "PASS":
            raise ValueError(f"Correctness preflight failed for {key}: {row}")
        checks[key].append(row)
    return checks


def validate_raw(rows, config, repetitions, correctness, allowed_keys=None):
    spans = config_index(config)
    expected = {
        (build, span["name"], stride)
        for build in config["builds"]
        for span in config["spans"]
        for stride in config["strides"]
    }
    groups = defaultdict(list)
    for row in rows:
        if row["kernel"] != config["kernel"] or row["datatype"] != config["datatype"]:
            raise ValueError(f"Unexpected kernel or datatype in stride raw data: {row}")
        span_name = next((name for name, span in spans.items()
                          if int(row["span_elements"]) == span["span_elements"]), None)
        if span_name is None:
            raise ValueError(f"Unknown fixed span in raw row: {row}")
        stride = int(row["stride"])
        useful_n = int(row["n"])
        key = (row["build"], span_name, stride)
        span = spans[span_name]
        expected_total = span["span_elements"] * config["array_count"] * 4
        expected_useful_bytes = useful_n * int(row["batching_count"]) * 3 * 4
        if key not in expected or useful_n != span["span_elements"] // stride:
            raise ValueError(f"Fixed-span N/stride mismatch: {row}")
        if int(row["allocated_span_bytes"]) != span["allocated_span_bytes_per_buffer"]:
            raise ValueError(f"Per-buffer allocation span mismatch: {row}")
        if (int(row["allocated_total_bytes"]) != expected_total or
                int(row["working_set_bytes"]) != expected_total or
                int(row["target_working_set_bytes"]) != span["allocated_total_bytes"]):
            raise ValueError(f"Aggregate allocation span mismatch: {row}")
        if int(row["useful_bytes_processed"]) != expected_useful_bytes:
            raise ValueError(f"Useful logical byte accounting mismatch: {row}")
        if int(row["elapsed_ns"]) <= 0 or key not in correctness:
            raise ValueError(f"Invalid time or missing correctness preflight for {key}")
        groups[key].append(row)

    required = expected if allowed_keys is None else allowed_keys
    if (allowed_keys is None and set(groups) != required) or not set(groups).issubset(required):
        missing = sorted(required - set(groups)) if allowed_keys is None else []
        unexpected = sorted(set(groups) - required)
        raise ValueError(f"Stride matrix mismatch; missing={missing[:3]}, unexpected={unexpected[:3]}")
    for key, samples in groups.items():
        sample_numbers = sorted(int(row["repetition"]) for row in samples)
        if len(samples) != repetitions or sample_numbers != list(range(1, repetitions + 1)):
            raise ValueError(f"Expected repetitions 1..{repetitions} for {key}; got {sample_numbers}")
    if len(rows) != len(groups) * repetitions:
        raise ValueError(f"Raw row count mismatch: {len(rows)}")
    return groups


def sample_stats(rows):
    ns_values = [float(row["ns_per_element"]) for row in rows]
    mean_ns = statistics.mean(ns_values)
    stddev_ns = statistics.stdev(ns_values) if len(ns_values) > 1 else 0.0
    return {
        "observations": len(rows),
        "median_elapsed_ns": statistics.median(float(row["elapsed_ns"]) for row in rows),
        "mean_elapsed_ns": statistics.mean(float(row["elapsed_ns"]) for row in rows),
        "median_ns_per_useful_element": statistics.median(ns_values),
        "mean_ns_per_useful_element": mean_ns,
        "stddev_ns_per_useful_element": stddev_ns,
        "coefficient_of_variation": stddev_ns / mean_ns if mean_ns else 0.0,
        "median_useful_elements_per_second": statistics.median(
            float(row["useful_elements_per_second"]) for row in rows
        ),
        "median_useful_effective_bandwidth_gib_per_s": statistics.median(
            float(row["effective_bandwidth_gib_per_s"]) for row in rows
        ),
    }


def merge_samples(initial_groups, rerun_groups, config, initial_repetitions):
    spans = config_index(config)
    records = []
    for source, groups in (("initial", initial_groups), ("targeted_rerun", rerun_groups)):
        for key, rows in groups.items():
            build, span_name, stride = key
            span = spans[span_name]
            for row in rows:
                record = dict(row)
                record.update({
                    "span_name": span_name,
                    "span_elements": span["span_elements"],
                    "stride": stride,
                    "useful_n": span["span_elements"] // stride,
                    "allocated_span_bytes_per_buffer": span["allocated_span_bytes_per_buffer"],
                    "allocated_total_bytes": span["allocated_total_bytes"],
                    "correctness": "PASS",
                    "measurement_source": source,
                    "initial_repetitions": initial_repetitions,
                })
                records.append(record)
    SAMPLES_OUT.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        raise ValueError("No Phase 4C samples to merge")
    with SAMPLES_OUT.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def save_selection(initial_groups, config):
    spans = config_index(config)
    selection = []
    for key, rows in sorted(initial_groups.items()):
        cv = sample_stats(rows)["coefficient_of_variation"]
        if cv > config["rerun_cv_threshold"]:
            build, span_name, stride = key
            span = spans[span_name]
            selection.append({
                "build": build,
                "span_name": span_name,
                "span_elements": span["span_elements"],
                "allocated_total_bytes": span["allocated_total_bytes"],
                "stride": stride,
                "useful_n": span["span_elements"] // stride,
                "initial_cv": cv,
                "selection_reason": "initial_cv_gt_20_percent",
            })
    write_csv(SELECTION_OUT, selection or [{
        "build": "", "span_name": "", "span_elements": "",
        "allocated_total_bytes": "", "stride": "", "useful_n": "",
        "initial_cv": "", "selection_reason": "",
    }])
    return selection


def build_statistics(initial_groups, rerun_groups, config):
    spans = config_index(config)
    merged = {}
    for key, rows in initial_groups.items():
        merged[key] = list(rows) + list(rerun_groups.get(key, []))
        if len(merged[key]) > config["maximum_repetitions"]:
            raise ValueError(f"Maximum observations exceeded for {key}")

    stats_index = {}
    stats_rows = []
    for key in sorted(merged):
        build, span_name, stride = key
        span = spans[span_name]
        result = sample_stats(merged[key])
        row = {
            "build": build,
            "span_name": span_name,
            "span_elements": span["span_elements"],
            "allocated_span_bytes_per_buffer": span["allocated_span_bytes_per_buffer"],
            "allocated_total_bytes": span["allocated_total_bytes"],
            "stride": stride,
            "useful_n": span["span_elements"] // stride,
            "initial_observations": len(initial_groups[key]),
            "targeted_rerun_observations": len(rerun_groups.get(key, [])),
            **result,
        }
        stats_index[key] = row
        stats_rows.append(row)

    for key, row in stats_index.items():
        build, span_name, stride = key
        scalar = stats_index[("gcc-scalar", span_name, stride)]
        row["scalar_speedup"] = 1.0
        row["auto_speedup_vs_scalar"] = (
            scalar["median_ns_per_useful_element"] /
            row["median_ns_per_useful_element"] if build == "gcc-auto" else ""
        )
        row["native_speedup_vs_scalar"] = (
            scalar["median_ns_per_useful_element"] /
            row["median_ns_per_useful_element"] if build == "gcc-native" else ""
        )
    write_csv(STATS_OUT, stats_rows)
    write_csv(SUMMARY_CSV, stats_rows)
    return stats_index, stats_rows


def save_plots(stats_index, config):
    colors = {"gcc-scalar": "#4D4D4D", "gcc-auto": "#0072B2", "gcc-native": "#D55E00"}
    metrics = (
        ("median_ns_per_useful_element", "ns_per_useful_element", "Median ns/useful element"),
        ("median_useful_effective_bandwidth_gib_per_s", "useful_effective_bandwidth", "Useful effective bandwidth (GiB/s)"),
    )
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    for span in config["spans"]:
        for metric, suffix, ylabel in metrics:
            figure, axis = plt.subplots(figsize=(8, 5))
            for build in config["builds"]:
                points = [stats_index[(build, span["name"], stride)] for stride in config["strides"]]
                axis.plot(
                    [row["stride"] for row in points],
                    [row[metric] for row in points],
                    marker="o", linewidth=1.8, color=colors[build], label=build,
                )
            axis.set_xticks(config["strides"])
            axis.set_xlabel("Element stride")
            axis.set_ylabel(ylabel)
            axis.set_title(f"Fixed-span strided multiply: {span['name']} ({span['allocated_total_bytes']:,} B)")
            axis.grid(True, alpha=0.25)
            axis.legend(frameon=False)
            figure.tight_layout()
            figure.savefig(PLOT_DIR / f"phase4c_stride_{suffix}_{span['name']}.png", dpi=160)
            plt.close(figure)


def save_summary(stats_index, stats_rows, config, initial_groups, rerun_rows, selection,
                 initial_raw, rerun_raw):
    initial_cvs = [sample_stats(rows)["coefficient_of_variation"] for rows in initial_groups.values()]
    final_cvs = [row["coefficient_of_variation"] for row in stats_rows]
    total_observations = sum(row["observations"] for row in stats_rows)
    rerun_description = (
        f"- Targeted reruns: {len(rerun_rows)} rows in `{rerun_raw.relative_to(ROOT).as_posix()}`; "
        f"{len(selection)} configurations selected by initial CV >20%."
        if rerun_rows else "- No targeted rerun file was needed."
    )
    lines = [
        "# Phase 4C Fixed-Span Stride Measurements",
        "",
        f"- Scope: `{config['kernel']}`, `{config['datatype']}`, GCC scalar/auto/native; {len(stats_rows)} configurations.",
        f"- Initial data: `{initial_raw.relative_to(ROOT).as_posix()}`; {len(initial_groups) * config['initial_repetitions']} timed samples.",
        rerun_description,
        f"- Total observations: {total_observations}; maximum per configuration: {config['maximum_repetitions']}.",
        "- Fixed allocated spans are per input/output buffer; aggregate bytes include all three float32 arrays. Useful N is span_elements/stride. Allocated span remains fixed as stride changes.",
        "- Initial CV median/max: " + f"{statistics.median(initial_cvs):.2%} / {max(initial_cvs):.2%}; >10%: {sum(cv > .1 for cv in initial_cvs)}/{len(initial_cvs)}; >20%: {sum(cv > .2 for cv in initial_cvs)}/{len(initial_cvs)}.",
        "- Final CV median/max: " + f"{statistics.median(final_cvs):.2%} / {max(final_cvs):.2%}; >10%: {sum(cv > .1 for cv in final_cvs)}/{len(final_cvs)}; >20%: {sum(cv > .2 for cv in final_cvs)}/{len(final_cvs)}.",
        "- Useful effective bandwidth counts only logical bytes (two useful float reads plus one useful float write per updated element). It is not physical memory bandwidth.",
        "- Speedups are scalar median ns/useful-element divided by auto/native median ns/useful-element for the same span and stride.",
        "",
        "## Fixed Spans",
        "",
        "| Span | Elements/buffer | Bytes/buffer | Aggregate allocated bytes |",
        "|---|---:|---:|---:|",
    ]
    for span in config["spans"]:
        lines.append(
            f"| {span['name']} | {span['span_elements']:,} | "
            f"{span['allocated_span_bytes_per_buffer']:,} | {span['allocated_total_bytes']:,} |"
        )
    lines.extend([
        "",
        "## Results by Stride",
        "",
        "| Span | Stride | Useful N | Build | Median ns/useful-element | Useful elements/s | Useful effective GiB/s | CV | Auto speedup | Native speedup |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in stats_rows:
        auto = row["auto_speedup_vs_scalar"]
        native = row["native_speedup_vs_scalar"]
        auto_text = f"{float(auto):.3f}x" if auto != "" else "-"
        native_text = f"{float(native):.3f}x" if native != "" else "-"
        lines.append(
            f"| {row['span_name']} | {row['stride']} | {row['useful_n']:,} | {row['build']} | "
            f"{row['median_ns_per_useful_element']:.8g} | "
            f"{row['median_useful_elements_per_second']:.6g} | "
            f"{row['median_useful_effective_bandwidth_gib_per_s']:.6g} | "
            f"{row['coefficient_of_variation']:.2%} | {auto_text} | {native_text} |"
        )
    lines.extend([
        "",
        "## SIMD Evidence and Interpretation",
        "",
        "Phase 2 GCC auto and native strided-multiply disassembly checks the runtime stride arguments. The packed XMM/ZMM path is guarded for unit strides; non-unit strides branch to scalar `mulss` loops. Therefore any loss of SIMD speedup for strides 2/4/8 reflects the emitted scalar path as well as lower useful cache-line utilization; it must not be attributed to cache behavior alone.",
        "",
        "Per-span plots: ns/useful-element and useful effective bandwidth. Treat changes smaller than CV as unresolved. No negative-case consolidation, roofline, broad uProf, or Phase 4D work is included.",
        "",
        "Statistics: `data/processed/phase4c_stride_statistics.csv`; merged rows with correctness/provenance: `data/processed/phase4c_stride_samples.csv`; rerun selection: `data/metadata/phase4c_stride_rerun_selection.csv`.",
    ])
    SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--correctness", type=Path, required=True)
    parser.add_argument("--expected-repetitions", type=int, required=True)
    parser.add_argument("--rerun", type=Path)
    parser.add_argument("--rerun-correctness", type=Path)
    parser.add_argument("--rerun-repetitions", type=int, default=0)
    arguments = parser.parse_args()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))["phase4c_stride"]
    if arguments.expected_repetitions != config["initial_repetitions"]:
        raise ValueError("Initial repetition count differs from configured protocol")
    initial_correctness = read_correctness(arguments.correctness.resolve())
    expected_keys = {
        (build, span["name"], stride)
        for build in config["builds"]
        for span in config["spans"]
        for stride in config["strides"]
    }
    if set(initial_correctness) != expected_keys:
        raise ValueError("Initial correctness manifest does not cover the configured 36 cases")
    initial_rows = read_csv(arguments.raw.resolve())
    initial_groups = validate_raw(
        initial_rows, config, arguments.expected_repetitions, initial_correctness,
    )
    rerun_rows = []
    rerun_groups = {}
    selection = []
    if arguments.rerun:
        if arguments.rerun_repetitions != config["rerun_repetitions"]:
            raise ValueError("Rerun repetition count differs from configuration")
        if not arguments.rerun_correctness:
            raise ValueError("Rerun correctness manifest is required")
        rerun_correctness = read_correctness(arguments.rerun_correctness.resolve())
        selection_rows = read_csv(SELECTION_OUT)
        selection_keys = {
            (row["build"], row["span_name"], int(row["stride"]))
            for row in selection_rows if row["build"]
        }
        if set(rerun_correctness) != selection_keys:
            raise ValueError("Rerun correctness manifest does not match selected configurations")
        rerun_rows = read_csv(arguments.rerun.resolve())
        rerun_groups = validate_raw(
            rerun_rows, config, arguments.rerun_repetitions,
            {**initial_correctness, **rerun_correctness}, allowed_keys=selection_keys,
        )
        if set(rerun_groups) != selection_keys:
            raise ValueError("Rerun raw file does not match selected configurations")
        selection = list(selection_keys)
    elif arguments.rerun_repetitions or arguments.rerun_correctness:
        raise ValueError("Rerun options require --rerun")

    merge_samples(initial_groups, rerun_groups, config, arguments.expected_repetitions)
    stats_index, stats_rows = build_statistics(initial_groups, rerun_groups, config)
    if not arguments.rerun:
        selection = save_selection(initial_groups, config)
    save_plots(stats_index, config)
    save_summary(
        stats_index, stats_rows, config, initial_groups, rerun_rows, selection,
        arguments.raw.resolve(),
        arguments.rerun.resolve() if arguments.rerun else arguments.raw.resolve(),
    )
    print(f"Validated {len(initial_groups)} configurations and {len(initial_rows)} initial samples.")
    print(f"Targeted reruns: {len(rerun_rows)} rows; max observations/config: {max(row['observations'] for row in stats_rows)}.")
    print(f"Wrote {SAMPLES_OUT.relative_to(ROOT)}, {STATS_OUT.relative_to(ROOT)}, {SUMMARY_CSV.relative_to(ROOT)}, and {SUMMARY_MD.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()

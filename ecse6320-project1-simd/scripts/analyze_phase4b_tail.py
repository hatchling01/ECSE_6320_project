import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "experiment_config.json"
SAMPLES_OUT = ROOT / "data" / "processed" / "phase4b_tail_samples.csv"
STATS_OUT = ROOT / "data" / "processed" / "phase4b_tail_statistics.csv"
OVERHEAD_OUT = ROOT / "results" / "tables" / "phase4b_tail_overhead.csv"
SUMMARY_OUT = ROOT / "results" / "tables" / "phase4b_tail_summary.md"
SELECTION_OUT = ROOT / "data" / "metadata" / "phase4b_tail_rerun_selection.csv"
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


def read_correctness(path):
    rows = read_csv(path)
    checks = defaultdict(list)
    for row in rows:
        key = (row["build"], int(row["base_n"]), int(row["remainder"]))
        if row["status"].upper() != "PASS":
            raise ValueError(f"Correctness preflight failed for {key}: {row}")
        checks[key].append(row)
    return checks


def configuration_for_n(n, base_sizes):
    matches = [base for base in base_sizes if base["base_n"] <= n <= base["base_n"] + 15]
    if len(matches) != 1:
        raise ValueError(f"N={n} does not map uniquely to a configured base size")
    base = matches[0]
    return base, n - base["base_n"]


def validate_raw(rows, repetitions, config, correctness, allowed_keys=None):
    bases = config["base_sizes"]
    builds = config["builds"]
    expected = {
        (build, base["base_n"], remainder)
        for build in builds for base in bases for remainder in config["remainders"]
    }
    groups = defaultdict(list)
    for row in rows:
        if row["kernel"] != "axpy" or row["datatype"] != "float32":
            raise ValueError(f"Unexpected kernel/datatype in tail data: {row}")
        n = int(row["n"])
        base, remainder = configuration_for_n(n, bases)
        key = (row["build"], int(base["base_n"]), remainder)
        if key not in expected or int(row["target_working_set_bytes"]) != n * 8:
            raise ValueError(f"Raw configuration metadata mismatch: {row}")
        if int(row["working_set_bytes"]) != n * 8:
            raise ValueError(f"Raw active working-set byte count mismatch: {row}")
        if int(row["elapsed_ns"]) <= 0 or int(row["batching_count"]) <= 0:
            raise ValueError(f"Invalid elapsed time or batch count: {row}")
        if key not in correctness:
            raise ValueError(f"No successful correctness preflight for {key}")
        groups[key].append(row)

    required = expected if allowed_keys is None else allowed_keys
    if (allowed_keys is None and set(groups) != required) or not set(groups).issubset(required):
        missing = sorted(required - set(groups)) if allowed_keys is None else []
        unexpected = sorted(set(groups) - required)
        raise ValueError(f"Tail configuration mismatch; missing={missing[:3]}, unexpected={unexpected[:3]}")
    for key, samples in groups.items():
        reps = sorted(int(row["repetition"]) for row in samples)
        if len(samples) != repetitions or reps != list(range(1, repetitions + 1)):
            raise ValueError(f"Expected repetitions 1..{repetitions} for {key}, got {reps}")
    if len(rows) != len(groups) * repetitions:
        raise ValueError(f"Raw row count mismatch: {len(rows)}")
    return groups


def sample_stats(rows):
    elapsed = [float(row["elapsed_ns"]) for row in rows]
    ns_per_element = [float(row["ns_per_element"]) for row in rows]
    mean_elapsed = statistics.mean(elapsed)
    stddev_elapsed = statistics.stdev(elapsed) if len(elapsed) > 1 else 0.0
    mean_ns = statistics.mean(ns_per_element)
    stddev_ns = statistics.stdev(ns_per_element) if len(ns_per_element) > 1 else 0.0
    return {
        "observations": len(rows),
        "median_elapsed_ns": statistics.median(elapsed),
        "mean_elapsed_ns": mean_elapsed,
        "stddev_elapsed_ns": stddev_elapsed,
        "median_ns_per_element": statistics.median(ns_per_element),
        "mean_ns_per_element": mean_ns,
        "stddev_ns_per_element": stddev_ns,
        "coefficient_of_variation": stddev_elapsed / mean_elapsed if mean_elapsed else 0.0,
        "median_gflop_per_s": statistics.median(float(row["gflop_per_s"]) for row in rows),
        "median_effective_bandwidth_gib_per_s": statistics.median(
            float(row["effective_bandwidth_gib_per_s"]) for row in rows
        ),
    }


def merge_samples(initial_groups, rerun_groups, config, initial_repetitions):
    records = []
    for source, groups in (("initial", initial_groups), ("targeted_rerun", rerun_groups)):
        for key, rows in groups.items():
            build, base_n, remainder = key
            base = next(item for item in config["base_sizes"] if item["base_n"] == base_n)
            for row in rows:
                record = dict(row)
                record.update({
                    "base_name": base["name"],
                    "base_n": base_n,
                    "remainder": remainder,
                    "observed_float32_lanes": config["observed_float32_lanes"][build],
                    "correctness": "pass",
                    "measurement_source": source,
                    "expected_repetition_count": (
                        initial_repetitions if source == "initial" else config["rerun_repetitions"]
                    ),
                })
                records.append(record)
    SAMPLES_OUT.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        raise ValueError("No measurement rows to merge")
    with SAMPLES_OUT.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    return records


def build_statistics(initial_groups, rerun_groups, config, initial_repetitions):
    merged = {}
    for key, rows in initial_groups.items():
        merged[key] = list(rows) + list(rerun_groups.get(key, []))
        if len(merged[key]) > config["maximum_repetitions"]:
            raise ValueError(f"Maximum observations exceeded for {key}")

    stats_index = {}
    statistics_rows = []
    for key in sorted(merged):
        build, base_n, remainder = key
        base = next(item for item in config["base_sizes"] if item["base_n"] == base_n)
        result = sample_stats(merged[key])
        row = {
            "build": build,
            "base_name": base["name"],
            "base_n": base_n,
            "remainder": remainder,
            "N": base_n + remainder,
            "observed_float32_lanes": config["observed_float32_lanes"][build],
            "initial_observations": len(initial_groups[key]),
            "targeted_rerun_observations": len(rerun_groups.get(key, [])),
            **result,
        }
        stats_index[key] = row
        statistics_rows.append(row)

    overhead_rows = []
    for build in config["builds"]:
        for base in config["base_sizes"]:
            base_key = (build, base["base_n"], 0)
            baseline = stats_index[base_key]
            for remainder in config["remainders"]:
                row = stats_index[(build, base["base_n"], remainder)]
                overhead_rows.append({
                    **row,
                    "baseline_median_elapsed_ns": baseline["median_elapsed_ns"],
                    "baseline_median_ns_per_element": baseline["median_ns_per_element"],
                    "normalized_time_overhead_percent": (
                        row["median_elapsed_ns"] / baseline["median_elapsed_ns"] - 1.0
                    ) * 100.0,
                    "normalized_ns_per_element_change_percent": (
                        row["median_ns_per_element"] / baseline["median_ns_per_element"] - 1.0
                    ) * 100.0,
                })

    write_csv(STATS_OUT, statistics_rows)
    write_csv(OVERHEAD_OUT, overhead_rows)
    return stats_index, statistics_rows, overhead_rows, merged


def save_selection(initial_groups, config):
    selection = []
    for key, rows in sorted(initial_groups.items()):
        cv = sample_stats(rows)["coefficient_of_variation"]
        if cv > config["rerun_cv_threshold"]:
            build, base_n, remainder = key
            base = next(item for item in config["base_sizes"] if item["base_n"] == base_n)
            selection.append({
                "build": build,
                "base_name": base["name"],
                "base_n": base_n,
                "remainder": remainder,
                "N": base_n + remainder,
                "initial_cv": cv,
                "selection_reason": "initial_cv_gt_20_percent",
            })
    write_csv(SELECTION_OUT, selection or [{
        "build": "", "base_name": "", "base_n": "", "remainder": "",
        "N": "", "initial_cv": "", "selection_reason": "",
    }])
    return selection


def save_plots(stats_index, config):
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    colors = {"gcc-scalar": "#4D4D4D", "gcc-auto": "#0072B2", "gcc-native": "#D55E00"}
    for base in config["base_sizes"]:
        figure, axis = plt.subplots(figsize=(8, 5))
        for build in config["builds"]:
            rows = [stats_index[(build, base["base_n"], remainder)]
                    for remainder in config["remainders"]]
            axis.plot(
                [row["remainder"] for row in rows],
                [100.0 * (row["median_elapsed_ns"] /
                          stats_index[(build, base["base_n"], 0)]["median_elapsed_ns"] - 1.0)
                 for row in rows],
                marker="o", linewidth=1.7, markersize=4,
                color=colors[build], label=build,
            )
        axis.axhline(0, color="#777777", linewidth=0.8)
        axis.set_xticks(config["remainders"])
        axis.set_xlabel("Remainder r (N = base N + r)")
        axis.set_ylabel("Normalized time overhead (%)")
        axis.set_title(f"AXPY tail overhead: {base['name']} base N={base['base_n']:,}")
        axis.grid(True, alpha=0.25)
        axis.legend(frameon=False)
        figure.tight_layout()
        figure.savefig(PLOT_DIR / f"phase4b_tail_overhead_{base['name']}.png", dpi=160)
        plt.close(figure)


def save_summary(stats_index, statistics_rows, overhead_rows, config, raw_path,
                 rerun_path, initial_rows, rerun_rows, selection):
    cvs = [row["coefficient_of_variation"] for row in statistics_rows]
    initial_cvs = [sample_stats(rows)["coefficient_of_variation"]
                   for rows in initial_rows.values()]
    overhead = [row["normalized_time_overhead_percent"] for row in overhead_rows]
    native_rows = [row for row in overhead_rows if row["build"] == "gcc-native"]
    small_base, large_base = config["base_sizes"]
    native_small = [row["normalized_time_overhead_percent"] for row in native_rows
                    if row["base_n"] == small_base["base_n"]]
    native_large = [row["normalized_time_overhead_percent"] for row in native_rows
                    if row["base_n"] == large_base["base_n"]]
    rerun_description = (
        f"- Targeted raw samples: {len(rerun_rows)} rows in `{rerun_path.relative_to(ROOT).as_posix()}`."
        if rerun_rows else "- No targeted rerun raw file was needed."
    )
    lines = [
        "# Phase 4B Tail-Handling Measurements",
        "",
        f"- Initial configurations: {len(initial_rows)}; initial timed samples: {len(initial_rows) * config['initial_repetitions']}.",
        f"- Initial raw samples: `{raw_path.relative_to(ROOT).as_posix()}`.",
        rerun_description,
        f"- Scope: AXPY float32, GCC scalar/auto/native; N=base+r for r=0..15; bases N={small_base['base_n']:,} (24 KiB) and N={large_base['base_n']:,} (4 MiB).",
        f"- Actual emitted widths from Phase 2: scalar 1 float/iteration; GCC auto 128-bit XMM (4 floats); GCC native 512-bit ZMM (16 floats). The native disassembly shows a masked ZMM epilogue plus a scalar fallback path; the auto disassembly shows vector chunks and scalar/short-vector cleanup.",
        f"- Timing: {config['initial_repetitions']} initial repetitions, {config['warmups']} warmups, CPU affinity logical CPU 0; small base batch 128, larger base batch 1. Maximum observations/configuration: {config['maximum_repetitions']}.",
        f"- Correctness: every timed configuration passed its verification-only reference check with existing float32 tolerances; see `data/processed/phase4b_tail_correctness.csv`.",
        f"- Initial CV median/max: {statistics.median(initial_cvs):.2%} / {max(initial_cvs):.2%}; CV >10%: {sum(cv > .10 for cv in initial_cvs)}/{len(initial_cvs)}; CV >20% and rerun: {len(selection)}.",
        f"- Final CV median/max: {statistics.median(cvs):.2%} / {max(cvs):.2%}; CV >10%: {sum(cv > .10 for cv in cvs)}/{len(cvs)}; CV >20%: {sum(cv > .20 for cv in cvs)}/{len(cvs)}.",
        f"- Measured normalized overhead across builds/bases/remainders: {min(overhead):.3f}% to {max(overhead):.3f}%. Native: small {min(native_small):.3f}% to {max(native_small):.3f}%; larger {min(native_large):.3f}% to {max(native_large):.3f}%.",
        f"- At r=15, added elements are {15 / small_base['base_n']:.3%} of the small base and {15 / large_base['base_n']:.4%} of the larger base; this is the expected first-order work increase before any cleanup cost.",
        "- No systematic positive native tail penalty was resolved: native overhead is non-monotonic across remainders, changes sign, and is not consistently larger than scalar/auto. The sample variability exceeds the expected added-work share; the result is inconclusive, not evidence of zero cost.",
        "- Remainders were collected in ascending order, with each build/configuration in a separate process rather than a fully interleaved sequence. Given Phase 3B's observed time/frequency drift, this ordering is an additional limitation on causal interpretation.",
        "- Compare `normalized_time_overhead_percent` for the requested ratio and `median_ns_per_element` for per-element cost. No penalty is claimed unless the effect is consistent and larger than the observed variability.",
        "",
        "## Remainder Statistics",
        "",
        "| Base | Build | r | N | Median elapsed (ns) | Median ns/element | GFLOP/s | CV | Tail overhead |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in overhead_rows:
        lines.append(
            f"| {row['base_name']} | {row['build']} | {row['remainder']} | {row['N']} | "
            f"{row['median_elapsed_ns']:.0f} | {row['median_ns_per_element']:.8g} | "
            f"{row['median_gflop_per_s']:.5g} | "
            f"{row['coefficient_of_variation']:.2%} | {row['normalized_time_overhead_percent']:.3f}% |"
        )
    lines.extend([
        "",
        "## Evidence and Interpretation",
        "",
        "The native path has two possible cleanup routes in the saved Phase 2 object: a masked 16-lane ZMM epilogue and a scalar loop fallback for the alias/versioning path. GCC auto processes four floats per XMM iteration, then uses short-vector/scalar cleanup. This timing matrix spans every native remainder and therefore the auto remainder classes as well.",
        "",
        "Do not attribute overhead to the cleanup instructions alone: the prescribed ratio also includes the extra r elements, and measurements are limited to these two cache-resident bases. Treat any differences smaller than the per-configuration CV as unresolved. No stride, negative-case, roofline, broad uProf, or Phase 4C work is included.",
        "",
        "Plots: `results/plots/phase4b_tail_overhead_small_cache.png` and `results/plots/phase4b_tail_overhead_larger_cache.png`.",
    ])
    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--correctness", type=Path, required=True)
    parser.add_argument("--expected-repetitions", type=int, required=True)
    parser.add_argument("--rerun", type=Path)
    parser.add_argument("--rerun-correctness", type=Path)
    parser.add_argument("--rerun-repetitions", type=int, default=0)
    arguments = parser.parse_args()

    import json

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))["phase4b_tail"]
    if arguments.expected_repetitions != config["initial_repetitions"]:
        raise ValueError("Initial repetition count differs from configured Phase 4B protocol")
    correctness = read_correctness(arguments.correctness.resolve())
    initial_rows = read_csv(arguments.raw.resolve())
    initial_groups = validate_raw(initial_rows, arguments.expected_repetitions, config, correctness)
    rerun_rows = []
    rerun_groups = {}
    selection = []
    if arguments.rerun:
        if arguments.rerun_repetitions != config["rerun_repetitions"]:
            raise ValueError("Targeted rerun repetition count differs from config")
        if not arguments.rerun_correctness:
            raise ValueError("Targeted rerun correctness manifest is required")
        rerun_correctness = read_correctness(arguments.rerun_correctness.resolve())
        rerun_rows = read_csv(arguments.rerun.resolve())
        selection_rows = read_csv(SELECTION_OUT)
        selection_keys = {
            (row["build"], int(row["base_n"]), int(row["remainder"]))
            for row in selection_rows if row["build"]
        }
        rerun_groups = validate_raw(
            rerun_rows, arguments.rerun_repetitions, config,
            {**correctness, **rerun_correctness}, allowed_keys=selection_keys,
        )
        if set(rerun_groups) != selection_keys:
            raise ValueError("Targeted rerun file does not match the original CV-based selection")
        for key in rerun_groups:
            if key not in rerun_correctness:
                raise ValueError(f"Missing targeted correctness preflight for {key}")
        selection = list(selection_keys)
    elif arguments.rerun_repetitions or arguments.rerun_correctness:
        raise ValueError("Rerun options require --rerun")

    merge_samples(initial_groups, rerun_groups, config, arguments.expected_repetitions)
    stats_index, statistics_rows, overhead_rows, merged = build_statistics(
        initial_groups, rerun_groups, config, arguments.expected_repetitions,
    )
    if not arguments.rerun:
        selection = save_selection(initial_groups, config)
    save_plots(stats_index, config)
    save_summary(
        stats_index, statistics_rows, overhead_rows, config,
        arguments.raw.resolve(),
        arguments.rerun.resolve() if arguments.rerun else arguments.raw.resolve(),
        initial_groups, rerun_rows, selection,
    )
    print(f"Validated {len(initial_groups)} configurations and {len(initial_rows)} initial samples.")
    print(f"Targeted rerun rows: {len(rerun_rows)}; maximum observations/config: {max(row['observations'] for row in statistics_rows)}.")
    print(f"Wrote {SAMPLES_OUT.relative_to(ROOT)}, {STATS_OUT.relative_to(ROOT)}, {OVERHEAD_OUT.relative_to(ROOT)}, and {SUMMARY_OUT.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
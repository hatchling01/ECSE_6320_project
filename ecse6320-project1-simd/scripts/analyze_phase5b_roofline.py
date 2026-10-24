import csv
import json
import math
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "experiment_config.json"
PHASE3B_STATS = ROOT / "data" / "processed" / "phase3b_statistics.csv"
PHASE5A_STATS = ROOT / "results" / "tables" / "uprof_summary.csv"
ROOFLINE_CSV = ROOT / "results" / "tables" / "roofline_summary.csv"
ROOFLINE_MD = ROOT / "results" / "tables" / "roofline_summary.md"
ANALYSIS_MD = ROOT / "docs" / "roofline_analysis.md"
PLOT_PATH = ROOT / "results" / "plots" / "roofline.png"
TARGET_SIZES = (24576, 25165824, 134217728)
KERNELS = ("axpy", "dot_product", "elementwise_multiply", "stencil_1d_three_point")
BUILDS = ("gcc-scalar", "gcc-auto", "gcc-native")
STREAM_KERNELS = ("axpy", "elementwise_multiply", "stencil_1d_three_point")

MAX_CLOCK_GHZ_ASSUMPTION = 4.3
LANES = {"float32": 16, "float64": 8}
FLOPS_PER_FMA = 2
ASSUMED_VECTOR_FMA_ISSUE_PER_CYCLE = 1
COMPUTE_CEILING = {
    datatype: LANES[datatype] * FLOPS_PER_FMA *
    ASSUMED_VECTOR_FMA_ISSUE_PER_CYCLE * MAX_CLOCK_GHZ_ASSUMPTION
    for datatype in LANES
}
COMPUTE_ASSUMPTION = (
    "Windows CIM reports 4.3 GHz max clock (not a measured benchmark/AVX-512 frequency); "
    "assume one 512-bit FMA per core cycle. This is an estimated theoretical single-core compute ceiling, not sustained performance."
)

COLORS = {
    "axpy": "#0072B2",
    "dot_product": "#D55E00",
    "elementwise_multiply": "#009E73",
    "stencil_1d_three_point": "#CC79A7",
}
SIZE_MARKERS = {24576: "o", 25165824: "s", 134217728: "^"}


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as source:
        return [{key.lower(): value for key, value in row.items()}
                for row in csv.DictReader(source)]


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"Refusing to write empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def useful_work(kernel, datatype, n):
    element_bytes = 4 if datatype == "float32" else 8
    if kernel == "axpy":
        flops = 2 * n
        useful_bytes = 3 * n * element_bytes
    elif kernel == "dot_product":
        flops = 2 * n
        useful_bytes = 2 * n * element_bytes
    elif kernel == "elementwise_multiply":
        flops = n
        useful_bytes = 3 * n * element_bytes
    elif kernel == "stencil_1d_three_point":
        flops = 5 * max(0, n - 2)
        useful_elements = 0 if n == 0 else (2 if n == 1 else 4 * n - 4)
        useful_bytes = useful_elements * element_bytes
    else:
        raise ValueError(f"Unsupported kernel: {kernel}")
    return flops, useful_bytes


def intensity_description(kernel, datatype, n):
    flops, useful_bytes = useful_work(kernel, datatype, n)
    bytes_per_element = useful_bytes / n if n else 0.0
    flops_per_element = flops / n if n else 0.0
    return flops, useful_bytes, flops_per_element, bytes_per_element, flops / useful_bytes


def bandwidth_references(stats_rows):
    result = {}
    components = {}
    for datatype in LANES:
        selected = [row for row in stats_rows
                    if row["datatype"] == datatype
                    and row["build"] == "gcc-native"
                    and int(row["target_working_set_bytes"]) == 134217728
                    and row["kernel"] in STREAM_KERNELS]
        if {row["kernel"] for row in selected} != set(STREAM_KERNELS):
            raise ValueError(f"Missing large-span native stream rows for {datatype}")
        if any(row["measurement_source"] != "phase3_raw_v3_original" for row in selected):
            raise ValueError(f"Expected preserved Phase 3B original rows for {datatype} reference")
        values = [float(row["median_effective_bandwidth_gib_per_s"]) for row in selected]
        result[datatype] = statistics.median(values)
        components[datatype] = {
            row["kernel"]: {
                "effective_bandwidth_gib_per_s": float(row["median_effective_bandwidth_gib_per_s"]),
                "cv": float(row["coefficient_of_variation"]),
                "n": int(row["n"]),
            }
            for row in selected
        }
    return result, components


def phase5a_index():
    rows = read_csv(PHASE5A_STATS)
    if len(rows) != 9:
        raise ValueError(f"Expected nine Phase 5A rows, found {len(rows)}")
    return {(row["kernel"], row["datatype"], row["build"], row["working_set_class"]): row
            for row in rows}


def build_roofline_rows(stats_rows, references):
    selected = [row for row in stats_rows
                if row["kernel"] in KERNELS
                and row["build"] in BUILDS
                and int(row["target_working_set_bytes"]) in TARGET_SIZES]
    expected = len(KERNELS) * len(BUILDS) * len(LANES) * len(TARGET_SIZES)
    if len(selected) != expected:
        raise ValueError(f"Expected {expected} Phase 3B roofline points, found {len(selected)}")
    by_key = {
        (row["kernel"], row["datatype"], int(row["target_working_set_bytes"]), row["build"]): row
        for row in selected
    }
    phase5a = phase5a_index()
    size_names = {24576: "small_cache_resident", 25165824: "intermediate_cache_scale", 134217728: "large_dram_sensitive"}
    lane_labels = {"float32": "GCC native: 512-bit ZMM, 16 float lanes", "float64": "GCC native: 512-bit ZMM, 8 double lanes"}
    rows = []
    for source in selected:
        kernel = source["kernel"]
        datatype = source["datatype"]
        build = source["build"]
        target_bytes = int(source["target_working_set_bytes"])
        n = int(source["n"])
        flops, useful_bytes, flops_per_element, bytes_per_element, ai = intensity_description(
            kernel, datatype, n
        )
        scalar_ns = float(by_key[(kernel, datatype, target_bytes, "gcc-scalar")]["median_ns_per_element"])
        median_ns = float(source["median_ns_per_element"])
        bw_ref = references[datatype]
        bandwidth_roof = ai * bw_ref * (1024 ** 3) / 1.0e9
        compute_roof = COMPUTE_CEILING[datatype]
        measured = float(source["median_gflop_per_s"])
        row = {
            "kernel": kernel,
            "datatype": datatype,
            "build": build,
            "target_working_set_bytes": target_bytes,
            "working_set_class": size_names[target_bytes],
            "N": n,
            "sample_count": int(source["samples"]),
            "measurement_source": source["measurement_source"],
            "median_elapsed_ns": float(source["median_elapsed_ns"]),
            "median_ns_per_element": median_ns,
            "median_gflop_per_s": measured,
            "effective_bandwidth_gib_per_s": float(source["median_effective_bandwidth_gib_per_s"]),
            "coefficient_of_variation": float(source["coefficient_of_variation"]),
            "flops_per_useful_element": flops_per_element,
            "useful_logical_bytes_per_element": bytes_per_element,
            "total_useful_flops_per_call": flops,
            "total_useful_logical_bytes_per_call": useful_bytes,
            "arithmetic_intensity_flop_per_byte": ai,
            "effective_streaming_bandwidth_reference_gib_per_s": bw_ref,
            "bandwidth_roof_gflop_per_s": bandwidth_roof,
            "compute_roof_gflop_per_s": compute_roof,
            "combined_roof_gflop_per_s": min(compute_roof, bandwidth_roof),
            "speedup_vs_scalar": scalar_ns / median_ns,
            "native_observed_width": lane_labels[datatype] if build == "gcc-native" else "",
            "native_fma_observed": kernel in ("axpy", "stencil_1d_three_point") if build == "gcc-native" else "",
            "compute_ceiling_assumption": COMPUTE_ASSUMPTION,
            "bandwidth_reference_definition": "median of large-span GCC-native Phase 3B useful effective bandwidth for AXPY, elementwise multiply, and stencil; not physical bandwidth",
        }
        if kernel == "elementwise_multiply" and datatype == "float32":
            class_name = size_names[target_bytes]
            row["phase5a_process_ipc"] = float(
                phase5a[(kernel, datatype, build, class_name)]["ipc"]
            )
            row["phase5a_process_instructions_per_useful_update"] = float(
                phase5a[(kernel, datatype, build, class_name)]["process_instructions_per_useful_update"]
            )
            row["phase5a_l2_requests_per_useful_update"] = float(
                phase5a[(kernel, datatype, build, class_name)]["l2_requests_per_useful_update"]
            )
        else:
            row["phase5a_process_ipc"] = ""
            row["phase5a_process_instructions_per_useful_update"] = ""
            row["phase5a_l2_requests_per_useful_update"] = ""
        rows.append(row)
    return rows


def intensity_table():
    lines = [
        "| Kernel | Type | FLOPs/useful element | Useful logical bytes/useful element | Intensity (FLOP/B) |",
        "|---|---|---:|---:|---:|",
    ]
    for datatype, element_bytes in (("float32", 4), ("float64", 8)):
        rows = [
            ("axpy", "2", 3 * element_bytes, 2 / (3 * element_bytes)),
            ("dot_product", "2", 2 * element_bytes, 1 / element_bytes),
            ("elementwise_multiply", "1", 3 * element_bytes, 1 / (3 * element_bytes)),
            ("stencil_1d_three_point", "5 interior; average 5(N-2)/N", f"{4 * element_bytes} asymptotic; average {4 * element_bytes}(1-1/N)", 5 / (4 * element_bytes)),
        ]
        for kernel, flops, useful_bytes, ai in rows:
            lines.append(f"| {kernel} | {datatype} | {flops} | {useful_bytes} | {ai:.6f} |")
    lines.extend([
        "",
        "Assumptions: AXPY counts one multiply plus one add (2 FLOPs); dot counts one multiply plus one accumulation add (2 FLOPs); elementwise multiply counts one multiply. For the three-point stencil, each interior output uses three multiplies and two adds (5 FLOPs); copied endpoints perform no floating-point operation. For N>=2 its useful-byte total is `(4N-4)*sizeof(T)` including three input values plus one output for each interior point and the two copied endpoints; the table gives the large-N per-element limit. All byte counts are useful logical algorithmic bytes, not measured physical traffic.",
    ])
    return lines


def save_plot(rows, references):
    figure, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    marker_labels = {24576: "24 KiB", 25165824: "24 MiB", 134217728: "128 MiB"}
    for axis, datatype in zip(axes, ("float32", "float64")):
        data = [row for row in rows if row["datatype"] == datatype and row["build"] == "gcc-native"]
        ai_values = [row["arithmetic_intensity_flop_per_byte"] for row in data]
        min_ai = min(ai_values) / 2
        max_ai = max(ai_values) * 2
        xs = [min_ai, max_ai]
        bw = references[datatype]
        axis.loglog(xs, [bw * x * (1024 ** 3) / 1.0e9 for x in xs],
                    color="#0072B2", linestyle="--", linewidth=1.8,
                    label=f"Effective streaming reference: {bw:.1f} GiB/s")
        axis.axhline(COMPUTE_CEILING[datatype], color="#D55E00", linestyle="-.", linewidth=1.8,
                     label=f"Estimated compute ceiling: {COMPUTE_CEILING[datatype]:.1f} GFLOP/s")
        for kernel in KERNELS:
            for target_bytes in TARGET_SIZES:
                point = next(row for row in data if row["kernel"] == kernel and row["target_working_set_bytes"] == target_bytes)
                axis.scatter(
                    point["arithmetic_intensity_flop_per_byte"],
                    point["median_gflop_per_s"],
                    color=COLORS[kernel],
                    marker=SIZE_MARKERS[target_bytes],
                    s=58,
                    edgecolor="black",
                    linewidth=0.4,
                    zorder=3,
                )
        axis.set_title(datatype)
        axis.set_xlabel("Algorithmic arithmetic intensity (useful FLOP / useful byte)")
        axis.set_ylabel("Measured achieved performance (GFLOP/s)")
        axis.grid(True, which="both", alpha=0.24)
    kernel_handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS[k],
                             markeredgecolor="black", label=k, markersize=7) for k in KERNELS]
    size_handles = [Line2D([0], [0], marker=SIZE_MARKERS[size], color="#444444", linestyle="None",
                           label=marker_labels[size], markersize=7) for size in TARGET_SIZES]
    line_handles, line_labels = axes[0].get_legend_handles_labels()
    figure.legend(kernel_handles + size_handles + line_handles,
                  list(KERNELS) + list(marker_labels.values()) + line_labels,
                  loc="lower center", ncol=4, frameon=False)
    figure.suptitle("Phase 3B GCC-native roofline-style view (useful-byte model)")
    figure.text(0.5, 0.015,
                "Dashed: useful effective-bandwidth reference (not physical DRAM). Dash-dot: estimated single-core ceiling. Points: Phase 3B medians.",
                ha="center", fontsize=9)
    figure.tight_layout(rect=(0, 0.14, 1, 0.92))
    PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(PLOT_PATH, dpi=180)
    plt.close(figure)


def save_reports(rows, references, components):
    native_rows = [row for row in rows if row["build"] == "gcc-native"]
    summary_lines = [
        "# Phase 5B Roofline-Style Analysis",
        "",
        "Analysis uses existing Phase 3B statistics only. No new benchmark, copy/stream study, or uProf profile was run.",
        "",
        "## Effective Streaming-Bandwidth Reference",
        "",
        "The existing 128 MiB GCC-native Phase 3B effective bandwidths provide a usable, large-working-set reference. For each datatype, the reference is the median of useful effective bandwidth for AXPY, elementwise multiply, and the three-point stencil. This is a useful-byte algorithmic reference, not a copy benchmark or physical DRAM bandwidth. No direct L3/DF/UMC counters are available.",
        "",
        "| Type | Reference (GiB/s) | Source kernels (GiB/s; CV) |",
        "|---|---:|---|",
    ]
    for datatype in ("float32", "float64"):
        comp = components[datatype]
        values = "; ".join(
            f"{kernel}: {comp[kernel]['effective_bandwidth_gib_per_s']:.3f} ({comp[kernel]['cv']:.1%} CV)"
            for kernel in STREAM_KERNELS
        )
        summary_lines.append(f"| {datatype} | {references[datatype]:.3f} | {values} |")
    summary_lines.extend([
        "",
        "## Compute Ceiling Assumption",
        "",
        f"The estimated theoretical single-core compute ceiling assumes the Windows CIM-reported 4.3 GHz maximum clock (not a measured sustained AVX-512 frequency), one 512-bit vector FMA per core cycle, and observed native widths of 16 float32 or 8 float64 lanes. That yields {COMPUTE_CEILING['float32']:.1f} GFLOP/s float32 and {COMPUTE_CEILING['float64']:.1f} GFLOP/s float64 under the stated assumption. The Phase 2 evidence observes packed FMA in native AXPY and stencil, but not in elementwise multiply or dot product; dot also has a reduction dependency. The common compute roof is an optimistic hardware upper bound for those kernels, not a measured or per-kernel sustained ceiling.",
        "",
        "## Arithmetic Intensity",
        "",
    ])
    summary_lines.extend(intensity_table())
    summary_lines.extend([
        "",
        "## Representative Native Points",
        "",
        "The roofline plot uses GCC-native Phase 3B medians at small (24 KiB), intermediate (24 MiB), and large (128 MiB) target footprints. The CSV retains scalar/auto/native data at all 72 selected kernel/type/build/size points, including runtime, ns/element, GFLOP/s, useful effective bandwidth, CV, and speedups.",
        "",
        "| Type | Kernel | Size | N | AI (useful FLOP/B) | Measured GFLOP/s | Useful effective GiB/s | Speedup vs scalar | Roof at point GFLOP/s | CV |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in native_rows:
        summary_lines.append(
            f"| {row['datatype']} | {row['kernel']} | {row['working_set_class']} | {row['N']:,} | "
            f"{row['arithmetic_intensity_flop_per_byte']:.5f} | {row['median_gflop_per_s']:.3f} | "
            f"{row['effective_bandwidth_gib_per_s']:.3f} | {row['speedup_vs_scalar']:.3f}x | "
            f"{row['combined_roof_gflop_per_s']:.3f} | {row['coefficient_of_variation']:.1%} |"
        )
    summary_lines.extend([
        "",
        "The curve is `P_roof = min(P_compute, AI × BW_reference)`, converting GiB/s to decimal GB/s for GFLOP/s. The plotted reference and intensities both use useful logical bytes. This is a roofline-style algorithmic comparison, not a physical DRAM roofline.",
        "",
        "The bandwidth reference is a large-working-set effective rate, not a cache-level bandwidth ceiling. Cache-resident Phase 3B points can exceed its slope because data supply differs by working set; do not treat that as a contradiction or infer an exact cache boundary. A multi-level physical roofline would require cache-level/physical bandwidth measurements that this project does not have.",
        "",
        "Plot: `results/plots/roofline.png`. Full machine-readable rows: `results/tables/roofline_summary.csv`.",
    ])
    ROOFLINE_MD.parent.mkdir(parents=True, exist_ok=True)
    ROOFLINE_MD.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    analysis_lines = [
        "# Phase 5B Effective Bandwidth, Roofline, and Synthesis",
        "",
        "## Scope and Data Sources",
        "",
        "This is analysis of existing Phase 3B and Phase 5A evidence. It performs no new benchmark, Phase 3 rerun, broad sweep, or additional uProf profile. Phase 3B supplies all runtime, ns/element, GFLOP/s, effective bandwidth, and scalar/auto/native speedups. The Phase 5A process-level counters are supporting architectural evidence only; profiler timings are not substituted for Phase 3B medians.",
        "",
        "Representative Phase 3B points use the existing target working sets 24 KiB, 24 MiB, and 128 MiB for all four kernels, float32/float64, and scalar/auto/native builds. Raw and processed Phase 3B data remain unchanged.",
        "",
        "## Arithmetic Intensity and Useful Traffic",
        "",
        "Arithmetic intensity is useful FLOPs divided by useful algorithmic bytes. Counts are: AXPY 2 FLOPs and 3 element transfers per useful element; dot product 2 FLOPs and 2 transfers; elementwise multiply 1 FLOP and 3 transfers; three-point stencil 5 interior FLOPs, with copied boundaries, and `(4N-4)*sizeof(T)` useful bytes for N>=2. The exact finite-N stencil intensity is `5(N-2)/((4N-4)*sizeof(T))`; the large-N limit is 5/(4*sizeof(T)). For float32/float64, the limiting intensities are AXPY 0.16667/0.08333, dot 0.25000/0.12500, elementwise 0.08333/0.04167, and stencil 0.31250/0.15625 FLOP/B.",
        "",
        "These are algorithmic/useful counts. They do not include cache-line overfetch, write-allocate traffic, reuse effects, or physical transactions. None of those traffic components was directly measured.",
        "",
        "## Bandwidth Reference and Compute Assumptions",
        "",
        f"No new copy/stream measurement was necessary. The effective streaming-bandwidth reference reuses the median GCC-native Phase 3B useful effective bandwidth at 128 MiB for the streaming kernels AXPY, elementwise multiply, and stencil: {references['float32']:.3f} GiB/s float32 and {references['float64']:.3f} GiB/s float64. The component kernel rates and CVs are listed in `results/tables/roofline_summary.md`. This reference is based on useful bytes/time and is not physical DRAM bandwidth.",
        "",
        f"The estimated theoretical single-core compute ceiling assumes the Windows CIM-reported 4.3 GHz maximum clock, one 512-bit FMA per core cycle, and the observed native 16-lane float32/8-lane float64 ZMM width, yielding {COMPUTE_CEILING['float32']:.1f}/{COMPUTE_CEILING['float64']:.1f} GFLOP/s. The 4.3 GHz value is a platform-reported maximum used as an explicit assumption, not an observed sustained or AVX-512 operating frequency. The single-FMA/cycle throughput is also assumed, not established by project measurements. Native AXPY/stencil disassembly contains packed FMA; elementwise multiply uses `vmulps/vmulpd`; dot product uses packed multiply/reduction without observed packed FMA. Thus the common compute line is an optimistic hardware roof, especially for non-FMA/reduction kernels.",
        "",
        "## Roofline and SIMD Compression",
        "",
        "The roofline-style figure plots measured native GCC GFLOP/s from Phase 3B against algorithmic intensity for representative working sets, with `P_roof=min(P_compute, AI×BW_reference)`. A 512-bit vector is 4× the lane width of GCC auto's 128-bit XMM and 16× scalar float lanes, but those ratios are not expected speedups: memory/data supply, operation mix, dependency chains, compiler-generated reductions, and large working-set behavior constrain achieved throughput.",
        "",
        "For float32 elementwise multiply, Phase 3B native speedup is 6.1375x at 24 KiB, 2.6522x at 24 MiB, and 0.9694x at 128 MiB. This compression accompanies lower useful effective bandwidth and the Phase 5A process-level observations: native instructions/update fall from 1.329 (small) to 0.900 (intermediate), then rise to 3.281 at large size (including harness activity); IPC declines from 2.618 to 1.113 to 0.983; L2 requests/update rise from 0.00475 to 0.1956 to 0.2063. The 128 MiB Phase 3B CV is 23.41%; these trends are consistent with increasing data-supply pressure and reduced arithmetic-side benefit, but do not prove exact L3/DRAM causality.",
        "",
        "Across kernels, low-intensity AXPY/elementwise behavior compresses toward 1× at large working sets. Dot product shows weak SIMD gains across sizes, consistent with its reduction dependency as well as low useful intensity. The stencil's higher useful intensity and native FMA correlate with sustained speedups in several Phase 3B points, though variability remains and no compute-bound classification is asserted solely from the roofline. Phase 4C further demonstrates that non-unit strides select scalar paths in GCC auto/native despite `-march=native`; SIMD width matters only when the compiler emits and executes packed instructions.",
        "",
        "## Limits",
        "",
        "The roof uses useful logical bytes and a reference derived from useful effective bandwidth. It is not a physical DRAM roofline. uProf reports no direct L3 PMCs, DF/UMC counters, or memory-controller bandwidth. Phase 5A counters are process-level, include setup/warmup/checksum/runtime work, use sampled event counts, and show sparse DTLB events. No exact cache-residency boundary, physical-bandwidth saturation, write-allocate traffic, or causal counter-to-speedup relation is claimed. Variability is preserved from Phase 3B; high-CV values should not support fine-grained conclusions.",
        "",
        "See `results/tables/roofline_summary.md`, `results/tables/roofline_summary.csv`, and `results/plots/roofline.png`. The Phase 6 final report and requirement audit are linked from `README.md`; Phase 6 adds no measurements.",
    ]
    ANALYSIS_MD.parent.mkdir(parents=True, exist_ok=True)
    ANALYSIS_MD.write_text("\n".join(analysis_lines) + "\n", encoding="utf-8")


def save_plot(rows, references):
    figure, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    marker_labels = {24576: "24 KiB", 25165824: "24 MiB", 134217728: "128 MiB"}
    for axis, datatype in zip(axes, ("float32", "float64")):
        data = [row for row in rows if row["datatype"] == datatype and row["build"] == "gcc-native"]
        ai_values = [row["arithmetic_intensity_flop_per_byte"] for row in data]
        min_ai = min(ai_values) / 2
        max_ai = max(ai_values) * 2
        xs = [min_ai, max_ai]
        bw = references[datatype]
        axis.loglog(xs, [bw * x * (1024 ** 3) / 1.0e9 for x in xs],
                    color="#0072B2", linestyle="--", linewidth=1.8,
                    label=f"Effective useful BW reference: {bw:.1f} GiB/s")
        axis.axhline(COMPUTE_CEILING[datatype], color="#D55E00", linestyle="-.", linewidth=1.8,
                     label=f"Estimated compute ceiling: {COMPUTE_CEILING[datatype]:.1f} GFLOP/s")
        for kernel in KERNELS:
            for target_bytes in TARGET_SIZES:
                point = next(row for row in data if row["kernel"] == kernel and row["target_working_set_bytes"] == target_bytes)
                axis.scatter(
                    point["arithmetic_intensity_flop_per_byte"],
                    point["median_gflop_per_s"],
                    color=COLORS[kernel],
                    marker=SIZE_MARKERS[target_bytes],
                    s=58,
                    edgecolor="black",
                    linewidth=0.4,
                    zorder=3,
                )
        axis.set_title(datatype)
        axis.set_xlabel("Algorithmic arithmetic intensity (useful FLOP / useful byte)")
        axis.set_ylabel("Measured achieved performance (GFLOP/s)")
        axis.grid(True, which="both", alpha=0.24)
    kernel_handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS[k],
                             markeredgecolor="black", label=k, markersize=7) for k in KERNELS]
    size_handles = [Line2D([0], [0], marker=SIZE_MARKERS[size], color="#444444", linestyle="None",
                           label=marker_labels[size], markersize=7) for size in TARGET_SIZES]
    line_handles, line_labels = axes[0].get_legend_handles_labels()
    legend_labels = list(KERNELS) + list(marker_labels.values()) + line_labels
    figure.legend(
        kernel_handles + size_handles + line_handles,
        legend_labels,
        loc="lower center", bbox_to_anchor=(0.5, 0.015), ncol=3, frameon=False,
    )
    figure.suptitle("Phase 3B GCC-native roofline-style view (useful-byte model; not physical DRAM)")
    figure.tight_layout(rect=(0, 0.20, 1, 0.92))
    PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(PLOT_PATH, dpi=180)
    plt.close(figure)


def main():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    phase3b_rows = read_csv(PHASE3B_STATS)
    references, components = bandwidth_references(phase3b_rows)
    rows = build_roofline_rows(phase3b_rows, references)
    write_csv(ROOFLINE_CSV, rows)
    save_plot(rows, references)
    save_reports(rows, references, components)
    print(f"Reused {len(rows)} Phase 3B points; no new measurement run.")
    print(f"Useful effective streaming references GiB/s: float32={references['float32']:.3f}, float64={references['float64']:.3f}")
    print(f"Compute ceilings GFLOP/s: float32={COMPUTE_CEILING['float32']:.1f}, float64={COMPUTE_CEILING['float64']:.1f}")
    print(f"Wrote {ROOFLINE_CSV.relative_to(ROOT)}, {ROOFLINE_MD.relative_to(ROOT)}, {ANALYSIS_MD.relative_to(ROOT)}, and {PLOT_PATH.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
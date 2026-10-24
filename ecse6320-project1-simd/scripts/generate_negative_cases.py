import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE3B = ROOT / "data" / "processed" / "phase3b_statistics.csv"
PHASE4C = ROOT / "data" / "processed" / "phase4c_stride_statistics.csv"
OUTPUT_CSV = ROOT / "results" / "tables" / "negative_cases.csv"
OUTPUT_MD = ROOT / "results" / "tables" / "negative_cases.md"


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as source:
        return [{key.lower(): value for key, value in row.items()}
                for row in csv.DictReader(source)]


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"Refusing to write an empty evidence table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def phase3b_case():
    rows = [row for row in read_csv(PHASE3B)
            if row["kernel"] == "elementwise_multiply"
            and row["datatype"] == "float32"
            and int(row["target_working_set_bytes"]) == 134217728]
    by_build = {row["build"]: row for row in rows}
    required = {"gcc-scalar", "gcc-auto", "gcc-native"}
    if set(by_build) != required:
        raise ValueError(f"Expected the three Phase 3B builds; found {sorted(by_build)}")
    scalar_ns = float(by_build["gcc-scalar"]["median_ns_per_element"])
    emitted = {
        "gcc-scalar": ("scalar instructions", "mulss"),
        "gcc-auto": ("128-bit XMM, 4 float lanes", "mulps"),
        "gcc-native": ("512-bit ZMM, 16 float lanes", "vmovups; vmulps; masked ZMM epilogue"),
    }
    result = []
    for build in ("gcc-scalar", "gcc-auto", "gcc-native"):
        row = by_build[build]
        width, instructions = emitted[build]
        result.append({
            "case_id": "vectorized_large_working_set",
            "kernel": row["kernel"],
            "datatype": row["datatype"],
            "build": build,
            "working_set_bytes": int(row["target_working_set_bytes"]),
            "allocated_total_bytes": int(row["target_working_set_bytes"]),
            "span_elements_per_buffer": "",
            "useful_n": int(row["n"]),
            "stride": 1,
            "median_ns_per_useful_element": float(row["median_ns_per_element"]),
            "speedup_vs_scalar": scalar_ns / float(row["median_ns_per_element"]),
            "useful_effective_bandwidth_gib_per_s": float(
                row["median_effective_bandwidth_gib_per_s"]
            ),
            "coefficient_of_variation": float(row["coefficient_of_variation"]),
            "observations": int(row["samples"]),
            "measurement_source": row["measurement_source"],
            "emitted_simd": width,
            "key_instructions": instructions,
            "evidence": "data/processed/phase3b_statistics.csv; results/disassembly/gcc-native-kernels.asm; results/tables/simd_verification.md",
        })
    return result, by_build


def phase4c_case():
    rows = read_csv(PHASE4C)
    result = []
    for row in rows:
        build = row["build"]
        stride = int(row["stride"])
        width = {
            "gcc-scalar": "scalar",
            "gcc-auto": "128-bit XMM for stride 1; scalar for non-unit stride",
            "gcc-native": "512-bit ZMM for stride 1; scalar for non-unit stride",
        }[build]
        instructions = {
            "gcc-scalar": "mulss",
            "gcc-auto": "movups; mulps" if stride == 1 else "movss; mulss",
            "gcc-native": "vmovups; vmulps" if stride == 1 else "vmovss; vmulss",
        }[build]
        result.append({
            "case_id": "runtime_stride_scalar_fallback",
            "kernel": "elementwise_multiply_strided",
            "datatype": "float32",
            "build": build,
            "working_set_bytes": int(row["allocated_total_bytes"]),
            "allocated_total_bytes": int(row["allocated_total_bytes"]),
            "span_elements_per_buffer": int(row["span_elements"]),
            "useful_n": int(row["useful_n"]),
            "stride": stride,
            "median_ns_per_useful_element": float(row["median_ns_per_useful_element"]),
            "speedup_vs_scalar": float(row["auto_speedup_vs_scalar"])
                if build == "gcc-auto" else (
                    float(row["native_speedup_vs_scalar"]) if build == "gcc-native" else 1.0
                ),
            "useful_effective_bandwidth_gib_per_s": float(
                row["median_useful_effective_bandwidth_gib_per_s"]
            ),
            "coefficient_of_variation": float(row["coefficient_of_variation"]),
            "observations": int(row["observations"]),
            "measurement_source": (
                f"initial={row['initial_observations']};rerun={row['targeted_rerun_observations']}"
            ),
            "emitted_simd": width,
            "key_instructions": instructions,
            "evidence": "data/processed/phase4c_stride_statistics.csv; results/disassembly/gcc-auto-kernels.asm; results/disassembly/gcc-native-kernels.asm",
        })
    expected = 3 * 4 * 3
    if len(result) != expected:
        raise ValueError(f"Expected {expected} Phase 4C rows, found {len(result)}")
    return result


def make_markdown(case1, case1_by_build, case2):
    scalar = case1_by_build["gcc-scalar"]
    native = case1_by_build["gcc-native"]
    speedup = float(scalar["median_ns_per_element"]) / float(native["median_ns_per_element"])
    lines = [
        "# Negative Cases: SIMD Expectations and Pitfalls",
        "",
        "This report reuses committed Phase 3B/4C measurements and Phase 2 code-generation evidence. No benchmark was run to prepare it.",
        "",
        "## Case 1: Vectorized but No Useful Large-Span Speedup",
        "",
        "| Kernel | Type | Aggregate working set | N | Build | Median ns/element | Speedup vs scalar | Useful effective GiB/s | CV | SIMD evidence |",
        "|---|---|---:|---:|---|---:|---:|---:|---:|---|",
    ]
    for row in case1:
        lines.append(
            f"| {row['kernel']} | {row['datatype']} | {row['working_set_bytes']:,} B | "
            f"{row['useful_n']:,} | {row['build']} | {row['median_ns_per_useful_element']:.9f} | "
            f"{row['speedup_vs_scalar']:.6f}x | {row['useful_effective_bandwidth_gib_per_s']:.3f} | "
            f"{row['coefficient_of_variation']:.2%} | {row['emitted_simd']}: `{row['key_instructions']}` |"
        )
    lines.extend([
        "",
        f"GCC native speedup is {speedup:.6f}x (scalar/native median ns/element). Phase 2 disassembly verifies packed 512-bit ZMM `vmulps` for 16 float lanes, followed by a masked ZMM epilogue. The loop is genuinely vectorized, but widening arithmetic does not yield substantial speedup at this 128 MiB working set: native and scalar CVs are {float(native['coefficient_of_variation']):.2%} and {float(scalar['coefficient_of_variation']):.2%}. This is consistent with memory/data-supply limitations, but does not establish direct DRAM saturation. Effective bandwidth is useful bytes/time; Phase 5 roofline/controller evidence has not been collected.",
        "",
        "Evidence: `data/processed/phase3b_statistics.csv`, `results/disassembly/gcc-native-kernels.asm`, and `results/tables/simd_verification.md`.",
        "",
        "## Case 2: Native ISA Does Not Guarantee Vectorization",
        "",
        "Phase 4C's unit-stride paths use packed XMM/ZMM instructions. For runtime strides 2, 4, and 8, GCC auto/native branch to scalar `mulss`/`vmulss` loops. The measured native/scalar speedups illustrate the resulting collapse (and occasional noisy reversal):",
        "",
        "| Aggregate span | Stride 1 | Stride 2 | Stride 4 | Stride 8 |",
        "|---|---:|---:|---:|---:|",
    ])
    span_names = ["small_cache", "intermediate_cache_scale", "large_dram_sensitive"]
    by_stride = {
        (row["span_name"], int(row["stride"])): row
        for row in read_csv(ROOT / "data" / "processed" / "phase4c_stride_statistics.csv")
        if row["build"] == "gcc-native"
    }
    for span_name, label in zip(span_names, ("Small (24 KiB)", "Intermediate (24 MiB)", "Large (~128 MiB)")):
        values = [float(by_stride[(span_name, stride)]["native_speedup_vs_scalar"])
                  for stride in (1, 2, 4, 8)]
        lines.append(f"| {label} | " + " | ".join(f"{value:.3f}x" for value in values) + " |")
    lines.extend([
        "",
        "The small-span native speedup falls from 5.380x at stride 1 to 0.891x, 0.825x, and 0.714x at strides 2, 4, and 8. Phase 2 `gcc-native-kernels.asm` and `gcc-auto-kernels.asm` show the packed path guarded on unit strides and scalar single-precision instructions on the non-unit fallback. `-march=native` identifies a target capability; it is not proof that this runtime access pattern vectorized.",
        "",
        "Evidence: `data/processed/phase4c_stride_statistics.csv`, `results/tables/phase4c_stride_summary.md`, and the two GCC Phase 2 disassemblies.",
        "",
        "## Sources",
        "",
        "- Phase 3B large-span measurements use original `phase3_raw_v3` rows; all ten samples and their CVs remain available in `data/processed/phase3b_statistics.csv` and `data/processed/phase3b_samples.csv`.",
        "- Phase 4C uses 180 initial rows plus 65 targeted rerun rows; 11/36 merged groups remain above 20% CV. No sample was discarded.",
        "- No Phase 5 roofline, direct physical bandwidth, or broad uProf claim is made.",
    ])
    return "\n".join(lines) + "\n"


def main():
    case1, case1_by_build = phase3b_case()
    case2 = phase4c_case()
    columns = [
        "case_id", "kernel", "datatype", "build", "working_set_bytes",
        "allocated_total_bytes", "span_elements_per_buffer", "useful_n", "stride",
        "median_ns_per_useful_element", "speedup_vs_scalar",
        "useful_effective_bandwidth_gib_per_s", "coefficient_of_variation",
        "observations", "measurement_source", "emitted_simd", "key_instructions", "evidence",
    ]
    rows = case1 + case2
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(make_markdown(case1, case1_by_build, case2), encoding="utf-8")
    print(f"Wrote {OUTPUT_MD.relative_to(ROOT)} and {OUTPUT_CSV.relative_to(ROOT)} from existing datasets only.")


if __name__ == "__main__":
    main()
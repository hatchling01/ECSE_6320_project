import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPROF_ROOT = ROOT / "results" / "uprof" / "phase5a"
MANIFEST = UPROF_ROOT / "command_manifest.csv"
PHASE3B_STATS = ROOT / "data" / "processed" / "phase3b_statistics.csv"
SUMMARY_CSV = ROOT / "results" / "tables" / "uprof_summary.csv"
SUMMARY_MD = ROOT / "results" / "tables" / "uprof_summary.md"
DOCS_OUT = ROOT / "docs" / "uprof_analysis.md"


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as source:
        return [{key.lower(): value for key, value in row.items()}
                for row in csv.DictReader(source)]


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"Refusing to write empty summary: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parse_report(report_path):
    with report_path.open(newline="", encoding="utf-8-sig") as source:
        report_rows = list(csv.reader(source))
    profile_duration = None
    process = None
    for index, row in enumerate(report_rows):
        if len(row) >= 2 and row[0].strip().startswith("Profile Duration"):
            match = re.search(r"([0-9]+(?:\.[0-9]+)?)", row[1])
            if match:
                profile_duration = float(match.group(1))
        if row and row[0].strip().startswith("10 HOTTEST PROCESSES"):
            if index + 1 >= len(report_rows):
                continue
            header = [item.strip() for item in report_rows[index + 1]]
            for data_row in report_rows[index + 2:]:
                if not data_row:
                    if process is not None:
                        break
                    continue
                if data_row[0].strip().startswith("10 HOTTEST"):
                    break
                if "benchmark_runner.exe" in data_row[0].lower():
                    process = {name: value.strip() if value else ""
                               for name, value in zip(header, data_row)}
                    break
    if process is None:
        raise ValueError(f"No benchmark_runner process row in uProf report: {report_path}")
    if profile_duration is None:
        raise ValueError(f"No profile duration in uProf report: {report_path}")
    return process, profile_duration


def number(row, field):
    value = row.get(field, "")
    if not value:
        return 0.0
    try:
        return float(value)
    except ValueError as error:
        raise ValueError(f"Invalid numeric uProf field {field}={value!r}") from error


def build_rows():
    manifest = [row for row in read_csv(MANIFEST)
                if row["collection_status"] == "complete"]
    expected_cases = 9
    if len(manifest) != expected_cases:
        raise ValueError(f"Expected {expected_cases} completed uProf profiles, found {len(manifest)}")
    phase3b_rows = read_csv(PHASE3B_STATS)
    phase3b = {
        (row["kernel"], row["datatype"], row["build"], int(row["target_working_set_bytes"])): row
        for row in phase3b_rows
    }
    result_rows = []
    for profile in manifest:
        report_path = Path(profile["report_csv"])
        report, duration = parse_report(report_path)
        kernel = profile["kernel"]
        datatype = profile["datatype"]
        build = profile["build"]
        target_bytes = int(profile["target_working_set_bytes"])
        n = int(profile["n"])
        batch = int(profile["batching_count"])
        repetitions = int(profile["profiler_repetitions"])
        warmups = 3
        total_profiled_updates = n * batch * (repetitions + warmups)
        simd_event = profile["simd_event"]
        scalar_key = (kernel, datatype, "gcc-scalar", target_bytes)
        base_key = (kernel, datatype, build, target_bytes)
        if scalar_key not in phase3b or base_key not in phase3b:
            raise ValueError(f"Missing Phase 3B cross-check for {base_key}")
        phase3_row = phase3b[base_key]
        phase3_scalar = phase3b[scalar_key]
        event_counts = {
            "cycles_not_in_halt": number(report, "CYCLES_NOT_IN_HALT"),
            "retired_instructions": number(report, "RETIRED_INST"),
            "simd_uops": number(report, simd_event),
            "l1_data_accesses": number(report, "L1_DC_ACCESSES_ALL"),
            "l2_requests_from_l1d_misses": number(report, "L2_CACHE_ACCESS_FROM_L1_DC_MISS"),
            "l1_dtlb_misses": number(report, "L1_DTLB_MISSES"),
        }
        result_rows.append({
            "case_name": profile["case_name"],
            "kernel": kernel,
            "datatype": datatype,
            "build": build,
            "working_set_class": profile["size_name"],
            "target_working_set_bytes": target_bytes,
            "N": n,
            "profile_duration_seconds": duration,
            "sampling_interval": int(profile["sampling_interval"]),
            "profile_repetitions": repetitions,
            "batching_count": batch,
            "profiled_useful_updates_including_warmups": total_profiled_updates,
            "cycles_not_in_halt": event_counts["cycles_not_in_halt"],
            "retired_instructions": event_counts["retired_instructions"],
            "IPC": number(report, "IPC"),
            "CPI": number(report, "CPI"),
            "process_cycles_per_useful_update": event_counts["cycles_not_in_halt"] / total_profiled_updates,
            "process_instructions_per_useful_update": event_counts["retired_instructions"] / total_profiled_updates,
            "simd_activity_event": simd_event,
            "simd_uops_retired": event_counts["simd_uops"],
            "simd_uops_per_useful_update": event_counts["simd_uops"] / total_profiled_updates,
            "l1_dc_accesses_all": event_counts["l1_data_accesses"],
            "l1_dc_accesses_per_useful_update": event_counts["l1_data_accesses"] / total_profiled_updates,
            "l1_dc_accesses_per_1000_retired_instructions": (
                event_counts["l1_data_accesses"] * 1000.0 /
                event_counts["retired_instructions"]
                if event_counts["retired_instructions"] else 0.0
            ),
            "l2_cache_access_from_l1_dc_miss": event_counts["l2_requests_from_l1d_misses"],
            "l2_requests_per_useful_update": event_counts["l2_requests_from_l1d_misses"] / total_profiled_updates,
            "l2_requests_per_1000_retired_instructions": (
                event_counts["l2_requests_from_l1d_misses"] * 1000.0 /
                event_counts["retired_instructions"]
                if event_counts["retired_instructions"] else 0.0
            ),
            "l1_dtlb_misses": event_counts["l1_dtlb_misses"],
            "l1_dtlb_misses_per_useful_update": event_counts["l1_dtlb_misses"] / total_profiled_updates,
            "l1_dtlb_misses_per_1000_retired_instructions": (
                event_counts["l1_dtlb_misses"] * 1000.0 /
                event_counts["retired_instructions"]
                if event_counts["retired_instructions"] else 0.0
            ),
            "phase3b_median_elapsed_ns": float(phase3_row["median_elapsed_ns"]),
            "phase3b_median_ns_per_element": float(phase3_row["median_ns_per_element"]),
            "phase3b_speedup_vs_scalar": (
                float(phase3_scalar["median_ns_per_element"]) /
                float(phase3_row["median_ns_per_element"])
            ),
            "phase3b_effective_bandwidth_gib_per_s": float(
                phase3_row["median_effective_bandwidth_gib_per_s"]
            ),
            "phase3b_coefficient_of_variation": float(phase3_row["coefficient_of_variation"]),
            "phase3b_measurement_source": phase3_row["measurement_source"],
            "uProf_report": str(report_path.relative_to(ROOT)).replace("\\", "/"),
            "uProf_raw_session_directory": profile["output_directory"],
        })
    return result_rows


def build_markdown(rows):
    lines = [
        "# Phase 5A Representative AMD uProf Profiles",
        "",
        "Nine representative profiles only: float32 elementwise multiply, GCC scalar/auto/native, and the 24 KiB, 24 MiB, and 128 MiB Phase 3B working-set sizes. No Phase 5B or Phase 6 work was performed.",
        "",
        "## Collection Configuration",
        "",
        "AMD uProf CLI 5.3.521.0 ran the Phase 3 `benchmark_runner` natively on Windows, with process affinity CPU 0, three warmup batches, and the profile-specific repetitions/batching recorded in the CSV. Each run used a custom six-core-PMC bundle at interval 250,000: `CYCLES_NOT_IN_HALT` (PMCx076), `RETIRED_INST` (PMCx0C0), one FP-uop event (`SCALAR_UOPS_RETIRED` for scalar, `PACK_128_UOPS_RETIRED` for GCC auto, `PACK_512_UOPS_RETIRED` for GCC native), `L1_DC_ACCESSES_ALL` (PMCx029), `L2_CACHE_ACCESS_FROM_L1_DC_MISS` (PMCx060), and `L1_DTLB_MISSES` (PMCx045). The command/configuration for every case is recorded in `results/uprof/phase5a/command_manifest.csv`; raw sessions and report CSVs are under `results/uprof/phase5a/`.",
        "",
        "uProf's process-level event totals include harness startup, allocation/initialization, warmups, checksums, and runtime overhead—not just the timed kernel loop. The per-useful-update counter columns normalize those whole-process counts by the configured useful updates and are architectural context, not kernel-exclusive cycles/instructions. PMC counts are sampled at the configured interval. Phase 3B times below remain the performance baseline; profiler timings do not replace them.",
        "",
        "## Cross-Check and Architectural Counts",
        "",
        "| Size | Build | Phase 3B median ms | Phase 3B ns/element | Phase 3B speedup | Phase 3B effective GiB/s | Phase 3B CV | Process cycles/update | Process instructions/update | IPC | FP-uops/update | L1 accesses/update | L1 accesses/kInst | L2 requests/update | L2 requests/kInst | DTLB misses/update | DTLB misses/kInst |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['working_set_class']} | {row['build']} | "
            f"{row['phase3b_median_elapsed_ns'] / 1e6:.3f} | "
            f"{row['phase3b_median_ns_per_element']:.6g} | "
            f"{row['phase3b_speedup_vs_scalar']:.3f}x | "
            f"{row['phase3b_effective_bandwidth_gib_per_s']:.3f} | "
            f"{row['phase3b_coefficient_of_variation']:.2%} | "
            f"{row['process_cycles_per_useful_update']:.4g} | "
            f"{row['process_instructions_per_useful_update']:.4g} | "
            f"{row['IPC']:.3f} | {row['simd_uops_per_useful_update']:.4g} | "
            f"{row['l1_dc_accesses_per_useful_update']:.4g} | "
            f"{row['l1_dc_accesses_per_1000_retired_instructions']:.3f} | "
            f"{row['l2_requests_per_useful_update']:.4g} | "
            f"{row['l2_requests_per_1000_retired_instructions']:.3f} | "
            f"{row['l1_dtlb_misses_per_useful_update']:.4g} | "
            f"{row['l1_dtlb_misses_per_1000_retired_instructions']:.3f} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The Phase 3B cross-check shows the strong small-working-set SIMD speedups and near-1x large-working-set elementwise results already documented in `results/tables/negative_cases.md`. uProf confirms retired-instruction/IPC and cache/TLB event samples are available for these runs. SIMD activity must be interpreted by each selected uop event: scalar FP uops for GCC scalar, 128-bit packed FP uops for auto, and 512-bit packed FP uops for native. Do not compare raw uop counts without the different element widths and useful-update normalization.",
        "",
        "The L2 event is `L2_CACHE_ACCESS_FROM_L1_DC_MISS`; uProf describes it as L2 requests due to L1 data-cache misses and notes it includes hardware/software prefetches. L1 DTLB misses count both L2-DTLB hits and misses. These are sampled event counts and can be sparse/noisy. The host reports only six core PMCs, so all six were used; no direct L3, DF/UMC, or memory-controller bandwidth metrics are available. No L3 miss rate, physical DRAM bandwidth, or exact cache-residency conclusion is claimed.",
        "",
        "## Collection Anomalies and Limits",
        "",
        "The first CLI attempt combining predefined `--config cpi` and custom `--event` options was rejected by uProf. A subsequent attempt combined mutually exclusive `--show-event-count` and `--show-sample-count` flags; uProf warned and selected its default display. A small-scalar smoke attempt produced a report but no harness timing CSV and is retained as incomplete in the manifest; the successful retry uses a numbered attempt directory and whitespace-free runner metadata arguments. These setup attempts are retained but excluded from the nine valid profiles. A small number of event rows, especially L1 DTLB, are zero or sparse at interval 250,000; do not interpret zero samples as proof that the underlying event never occurred. Hyper-V is reported active by uProf; these profiles are native Windows observations on the supplied host, not a cross-machine comparison.",
        "",
        "Raw profile databases, report exports, and profiler-instrumented timing files are under `results/uprof/phase5a/`. The machine-readable comparison is `results/tables/uprof_summary.csv`; exact commands and per-case options are in `command_manifest.csv`.",
        "",
        "Phase 5A is representative architectural evidence only. No roofline analysis, broad uProf sweep, or Phase 5B work is included.",
    ])
    return "\n".join(lines) + "\n"


def main():
    rows = build_rows()
    fields = list(rows[0])
    write_csv(SUMMARY_CSV, rows)
    SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_MD.write_text(build_markdown(rows), encoding="utf-8")
    DOCS_OUT.write_text(build_markdown(rows), encoding="utf-8")
    print(f"Analyzed {len(rows)} completed uProf profiles; wrote {SUMMARY_CSV.relative_to(ROOT)} and {SUMMARY_MD.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()

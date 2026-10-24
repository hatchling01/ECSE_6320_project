"""Run the one tiny, regular-file-only FIO functionality validation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from safe_target import repository_root, validate_fio_target


CLASSIFICATION = "NOT FOR PERFORMANCE ANALYSIS"
FILE_SIZE_BYTES = 16 * 1024 * 1024
IO_SIZE_BYTES = 4 * 1024 * 1024
BLOCK_SIZE_BYTES = 4 * 1024


def latency_percentiles(stats: dict[str, Any]) -> dict[str, Any]:
    for key in ("clat_ns", "clat_us", "clat_ms", "clat"):
        block = stats.get(key)
        if isinstance(block, dict) and isinstance(block.get("percentile"), dict):
            return block["percentile"]
    return {}


def actual_smoke_validation(
    payload: dict[str, Any], target: Path, fio_working_directory: Path
) -> dict[str, Any]:
    jobs = payload.get("jobs", [])
    if payload.get("fio version") != "fio-3.43":
        raise RuntimeError(f"unexpected FIO version: {payload.get('fio version')!r}")
    if len(jobs) != 1:
        raise RuntimeError(f"expected one FIO job, found {len(jobs)}")

    job = jobs[0]
    options = {**payload.get("global options", {}), **job.get("job options", {})}
    expected = {
        "ioengine": "windowsaio",
        "direct": "1",
        "rw": "randrw",
        "iodepth": "1",
        "numjobs": "1",
    }
    for name, expected_value in expected.items():
        if str(options.get(name)) != expected_value:
            raise RuntimeError(f"actual JSON {name}={options.get(name)!r}; expected {expected_value!r}")

    reported_filename = Path(str(options.get("filename", "")))
    actual_filename = (
        reported_filename
        if reported_filename.is_absolute()
        else fio_working_directory / reported_filename
    ).resolve(strict=False)
    if actual_filename != target:
        raise RuntimeError(f"actual JSON filename {actual_filename} does not equal validated target {target}")

    percentiles: dict[str, list[str]] = {}
    io_bytes: dict[str, int] = {}
    for direction in ("read", "write"):
        stats = job.get(direction, {})
        io_bytes[direction] = int(stats.get("io_bytes", 0))
        if io_bytes[direction] <= 0:
            raise RuntimeError(f"actual FIO JSON reports no {direction} I/O")
        values = latency_percentiles(stats)
        available = sorted(values, key=float)
        for required in (50.0, 95.0, 99.0, 99.9):
            if not any(abs(float(item) - required) < 1e-6 for item in available):
                raise RuntimeError(f"actual FIO JSON lacks {direction} p{required} completion latency")
        percentiles[direction] = available

    return {
        "regular_file_target": str(actual_filename),
        "ioengine": options["ioengine"],
        "direct": int(options["direct"]),
        "iodepth": int(options["iodepth"]),
        "numjobs": int(options["numjobs"]),
        "read_io_bytes": io_bytes["read"],
        "write_io_bytes": io_bytes["write"],
        "read_percentile_keys": percentiles["read"],
        "write_percentile_keys": percentiles["write"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path)
    parser.add_argument("--fio", type=Path, default=Path(r"C:\Program Files\fio\fio.exe"))
    parser.add_argument("--keep-target", action="store_true")
    args = parser.parse_args()

    repo = repository_root()
    requested = args.target or repo / "benchmark_data" / "fio_smoke_test.bin"
    target = validate_fio_target(requested, repo, allow_nonexistent=True)
    if target.exists():
        raise RuntimeError(f"refusing to overwrite existing smoke target: {target}")

    fio = args.fio.resolve(strict=True)
    config = (repo / "configs" / "fio" / "smoke.fio").resolve(strict=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    raw_path = repo / "data" / "raw" / "smoke" / f"smoke_{stamp}.json"
    parsed_path = repo / "data" / "parsed" / "smoke" / f"smoke_{stamp}.csv"
    metadata_path = repo / "data" / "metadata" / "smoke" / f"smoke_{stamp}.json"
    log_path = repo / "logs" / "smoke" / f"smoke_{stamp}.log"
    for directory in (raw_path.parent, parsed_path.parent, metadata_path.parent, log_path.parent):
        directory.mkdir(parents=True, exist_ok=True)

    displayed = {
        "classification": CLASSIFICATION,
        "resolved_path": str(target),
        "file_size_bytes": FILE_SIZE_BYTES,
        "io_range_bytes": FILE_SIZE_BYTES,
        "total_io_bytes": IO_SIZE_BYTES,
        "fio_executable": str(fio),
        "engine": "windowsaio",
        "direct": 1,
        "workload": "randrw (50/50 read/write)",
        "block_size_bytes": BLOCK_SIZE_BYTES,
        "iodepth": 1,
        "numjobs": 1,
    }
    print("SAFE REGULAR-FILE TARGET VERIFIED", flush=True)
    for key, value in displayed.items():
        print(f"{key}={value}", flush=True)

    command = [
        str(fio),
        f"--output={raw_path}",
        "--output-format=json",
        f"--filename={target.name}",
        str(config),
    ]
    log_lines = ["SAFE REGULAR-FILE TARGET VERIFIED"]
    log_lines.extend(f"{key}={value}" for key, value in displayed.items())
    log_lines.append(f"command={subprocess.list2cmdline(command)}")
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    try:
        # FIO treats ':' in filename values as a multi-file separator. Running
        # from the already validated benchmark directory and passing only the
        # leaf name prevents drive-letter parsing from creating an extra file.
        subprocess.run(command, cwd=target.parent, check=True)
        with raw_path.open("r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
        validation = actual_smoke_validation(payload, target, target.parent)

        parser_command = [
            sys.executable,
            str(repo / "scripts" / "python" / "parse_fio.py"),
            "--input",
            str(raw_path),
            "--output",
            str(parsed_path),
            "--expect-smoke",
        ]
        subprocess.run(parser_command, cwd=repo, check=True)
        metadata = {
            **displayed,
            "timestamp_utc": stamp,
            "fio_command_argv": command,
            "fio_working_directory": str(target.parent),
            "parser_command_argv": parser_command,
            "actual_json_validation": validation,
            "target_cleanup": "retained by explicit switch" if args.keep_target else "deleted after validation",
        }
        with metadata_path.open("x", encoding="utf-8") as handle:
            json.dump(metadata, handle, indent=2)
            handle.write("\n")
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write("JSON/PERCENTILE VALIDATION PASSED\n")
            handle.write("PARSER VALIDATION PASSED\n")
            handle.write(f"raw_json={raw_path}\nparsed_csv={parsed_path}\n")
        print(f"Raw JSON: {raw_path}")
        print(f"Parsed CSV: {parsed_path}")
        print("SMOKE VALIDATION PASSED — NOT FOR PERFORMANCE ANALYSIS")
    finally:
        if not args.keep_target and target.exists():
            validated_existing = validate_fio_target(target, repo)
            validated_existing.unlink()
            print(f"Deleted validated disposable smoke file: {validated_existing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


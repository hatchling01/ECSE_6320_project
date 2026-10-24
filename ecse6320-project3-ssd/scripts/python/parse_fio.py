#!/usr/bin/env python3
"""Parse FIO JSON into a tidy one-row-per-job/direction CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


PERCENTILES = (50.0, 95.0, 99.0, 99.9)


def latency_block(stats: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    for key in ("clat_ns", "clat_us", "clat_ms", "clat"):
        value = stats.get(key)
        if isinstance(value, dict):
            return key, value
    return "", {}


def percentile_value(values: dict[str, Any], requested: float) -> Any:
    numeric: list[tuple[float, Any]] = []
    for key, value in values.items():
        try:
            numeric.append((float(key), value))
        except (TypeError, ValueError):
            continue
    if not numeric:
        return ""
    exact = [value for key, value in numeric if abs(key - requested) < 1e-9]
    return exact[0] if exact else min(numeric, key=lambda pair: abs(pair[0] - requested))[1]


def parse_jobs(payload: dict[str, Any]) -> list[dict[str, Any]]:
    global_options = payload.get("global options", {})
    rows: list[dict[str, Any]] = []
    for job_index, job in enumerate(payload.get("jobs", [])):
        job_options = job.get("job options", {})
        options = {**global_options, **job_options}
        for direction in ("read", "write"):
            stats = job.get(direction, {})
            latency_key, latency = latency_block(stats)
            percentiles = latency.get("percentile", {}) if latency else {}
            row = {
                "classification": "NOT FOR PERFORMANCE ANALYSIS" if options.get("name") == "smoke_validation" or job.get("jobname") == "smoke_validation" else "PROJECT DATA",
                "fio_version": payload.get("fio version", ""),
                "timestamp": payload.get("timestamp", ""),
                "job_index": job_index,
                "jobname": job.get("jobname", ""),
                "direction": direction,
                "rw": options.get("rw", ""),
                "bs": options.get("bs", options.get("blocksize", "")),
                "iodepth": options.get("iodepth", ""),
                "numjobs": options.get("numjobs", ""),
                "effective_qd_configuration": f"{options.get('iodepth', '')}x{options.get('numjobs', '')}",
                "rwmixread": options.get("rwmixread", ""),
                "direct": options.get("direct", ""),
                "ioengine": options.get("ioengine", ""),
                "size": options.get("size", ""),
                "io_size": options.get("io_size", ""),
                "runtime_ms": stats.get("runtime", ""),
                "io_bytes": stats.get("io_bytes", ""),
                "iops": stats.get("iops", ""),
                "bw_fio_reported": stats.get("bw", ""),
                "bw_bytes_per_s": stats.get("bw_bytes", ""),
                "clat_source_unit": latency_key,
                "mean_clat_source_unit": latency.get("mean", ""),
            }
            for percentile in PERCENTILES:
                label = str(percentile).replace(".", "_")
                row[f"p{label}_clat_source_unit"] = percentile_value(percentiles, percentile)
            rows.append(row)
    return rows


def validate_smoke(payload: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    if payload.get("fio version") != "fio-3.43":
        raise ValueError(f"Unexpected FIO version: {payload.get('fio version')!r}")
    jobs = payload.get("jobs", [])
    if len(jobs) != 1:
        raise ValueError(f"Expected exactly one smoke job, found {len(jobs)}")
    options = {**payload.get("global options", {}), **jobs[0].get("job options", {})}
    expected = {"ioengine": "windowsaio", "direct": "1", "iodepth": "1", "numjobs": "1"}
    for key, value in expected.items():
        if str(options.get(key)) != value:
            raise ValueError(f"Smoke option {key}={options.get(key)!r}, expected {value!r}")
    for direction in ("read", "write"):
        stats = jobs[0].get(direction, {})
        if float(stats.get("io_bytes", 0)) <= 0:
            raise ValueError(f"Smoke job completed no {direction} I/O")
        _, latency = latency_block(stats)
        values = latency.get("percentile", {}) if latency else {}
        for percentile in PERCENTILES:
            if percentile_value(values, percentile) == "":
                raise ValueError(f"Missing {direction} p{percentile} completion latency")
    if not rows:
        raise ValueError("Parser produced no rows")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--expect-smoke", action="store_true")
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    rows = parse_jobs(payload)
    if args.expect_smoke:
        validate_smoke(payload, rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Parsed {len(rows)} rows: {args.output}")
    if args.expect_smoke:
        print("SMOKE JSON/PERCENTILE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


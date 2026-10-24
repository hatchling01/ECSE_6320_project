"""Collect validated FIO JSON plus metadata into one tidy run-level CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from fio_runner import combine_options, repository_root


PCTS = (50.0, 95.0, 99.0, 99.9)


def clat(stats: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    for key in ("clat_ns", "clat_us", "clat_ms", "clat"):
        value = stats.get(key)
        if isinstance(value, dict):
            return key, value
    return "", {}


def pct(block: dict[str, Any], requested: float) -> Any:
    values = block.get("percentile", {})
    for key, value in values.items():
        if abs(float(key) - requested) < 1e-6:
            return value
    return ""


def direction_fields(prefix: str, stats: dict[str, Any]) -> dict[str, Any]:
    unit, block = clat(stats)
    result: dict[str, Any] = {
        f"{prefix}_io_bytes": stats.get("io_bytes", 0),
        f"{prefix}_total_ios": stats.get("total_ios", 0),
        f"{prefix}_iops": stats.get("iops", 0),
        f"{prefix}_bw_fio": stats.get("bw", 0),
        f"{prefix}_bw_bytes_s": stats.get("bw_bytes", 0),
        f"{prefix}_runtime_ms": stats.get("runtime", 0),
        f"{prefix}_clat_unit": unit,
        f"{prefix}_mean_clat": block.get("mean", 0),
    }
    for value in PCTS:
        result[f"{prefix}_p{str(value).replace('.', '_')}"] = pct(block, value)
    return result


def collect_phase(phase: str) -> list[dict[str, Any]]:
    repo = repository_root()
    rows: list[dict[str, Any]] = []
    for metadata_path in sorted((repo / "data" / "metadata" / phase).glob("*.json")):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
        if metadata.get("status") != "VALID":
            continue
        raw_path = repo / metadata["raw_json"]
        payload = json.loads(raw_path.read_text(encoding="utf-8-sig"))
        job = payload["jobs"][0]
        options = combine_options(payload, job)
        spec = metadata["spec"]
        read = job.get("read", {})
        write = job.get("write", {})
        read_ios = int(read.get("total_ios", 0))
        write_ios = int(write.get("total_ios", 0))
        total_ios = read_ios + write_ios
        read_mean = float(clat(read)[1].get("mean", 0))
        write_mean = float(clat(write)[1].get("mean", 0))
        weighted_mean_ns = (
            (read_mean * read_ios + write_mean * write_ios) / total_ios
            if total_ios
            else 0
        )
        row: dict[str, Any] = {
            "phase": phase,
            "run_id": metadata["run_id"],
            "classification": metadata["classification"],
            "configuration": spec["configuration"],
            "repetition": spec["repetition"],
            "rw": spec["rw"],
            "bs": spec["bs"],
            "iodepth": spec["iodepth"],
            "numjobs": spec["numjobs"],
            "configured_aggregate_qd": spec["iodepth"] * spec["numjobs"],
            "rwmixread": spec.get("rwmixread", ""),
            "direct": spec["direct"],
            "ioengine": options.get("ioengine", ""),
            "size_bytes": spec["size_bytes"],
            "requested_io_size_bytes": spec.get("io_size_bytes") or "",
            "runtime_s": spec.get("runtime_s") or "",
            "ramp_s": spec.get("ramp_s") or 0,
            "total_ios": total_ios,
            "total_iops": float(read.get("iops", 0)) + float(write.get("iops", 0)),
            "total_bw_bytes_s": int(read.get("bw_bytes", 0)) + int(write.get("bw_bytes", 0)),
            "weighted_mean_clat_ns": weighted_mean_ns,
            "logical_bytes_written": int(write.get("io_bytes", 0)),
            "raw_json": metadata["raw_json"],
        }
        row.update(direction_fields("read", read))
        row.update(direction_fields("write", write))
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    rows = collect_phase(args.phase)
    if not rows:
        raise RuntimeError(f"No validated metadata found for {args.phase}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Collected {len(rows)} validated runs into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


"""Safety-gated FIO production runner for Project 3."""

from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from safe_target import repository_root, validate_fio_target


GIB = 1024**3
MIB = 1024**2
MIN_FREE_BYTES = 100 * GIB
WRITE_BUDGET_BYTES = 80 * GIB
FIO_PATH = Path(r"C:\Program Files\fio\fio.exe")
PRODUCTION_FILENAME = "fio_production.bin"
PRODUCTION_SIZE_BYTES = 8 * GIB


class SafetyGateError(RuntimeError):
    pass


@dataclass(frozen=True)
class ExperimentSpec:
    phase: str
    configuration: str
    repetition: int
    rw: str
    bs: str
    iodepth: int
    numjobs: int = 1
    size_bytes: int = PRODUCTION_SIZE_BYTES
    io_size_bytes: int | None = None
    runtime_s: int | None = None
    ramp_s: int = 0
    direct: int = 1
    rwmixread: int | None = None
    classification: str = "PRODUCTION"
    target_filename: str = PRODUCTION_FILENAME
    extra_args: tuple[str, ...] = field(default_factory=tuple)
    bandwidth_log: bool = False

    @property
    def may_write(self) -> bool:
        return self.rw in {"write", "randwrite", "rw", "randrw"}

    @property
    def projected_max_write_bytes(self) -> int:
        if not self.may_write:
            return 0
        if self.io_size_bytes is None:
            raise SafetyGateError("Every write-capable job must be size bounded")
        return self.io_size_bytes


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%S%fZ")


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")


def current_free_bytes(repo: Path) -> int:
    return shutil.disk_usage(repo).free


def budget_path(repo: Path) -> Path:
    return repo / "data" / "metadata" / "write_budget.csv"


def read_cumulative_writes(repo: Path) -> int:
    path = budget_path(repo)
    if not path.exists():
        return 0
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    return int(rows[-1]["cumulative_logical_bytes_written"]) if rows else 0


def append_write_budget(
    repo: Path,
    spec: ExperimentSpec,
    run_id: str,
    logical_bytes_written: int,
) -> int:
    path = budget_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    prior = read_cumulative_writes(repo)
    cumulative = prior + logical_bytes_written
    if cumulative > WRITE_BUDGET_BYTES:
        raise SafetyGateError("Actual logical writes exceeded the 80 GiB project budget")
    new_file = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "phase",
            "configuration",
            "repetition",
            "run_id",
            "logical_bytes_written",
            "cumulative_logical_bytes_written",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if new_file:
            writer.writeheader()
        writer.writerow(
            {
                "phase": spec.phase,
                "configuration": spec.configuration,
                "repetition": spec.repetition,
                "run_id": run_id,
                "logical_bytes_written": logical_bytes_written,
                "cumulative_logical_bytes_written": cumulative,
            }
        )
    return cumulative


def snapshot_files(repo: Path) -> set[Path]:
    return {
        path.relative_to(repo)
        for path in repo.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }


def prepare_sparse_container(target: Path, size_bytes: int) -> None:
    if target.exists():
        if target.stat().st_size != size_bytes:
            raise SafetyGateError(
                f"Existing production target size {target.stat().st_size} != {size_bytes}"
            )
        return
    with target.open("xb") as handle:
        handle.truncate(size_bytes)
    if target.stat().st_size != size_bytes:
        raise SafetyGateError("Could not create the requested production file size")


def combine_options(payload: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
    return {**payload.get("global options", {}), **job.get("job options", {})}


def validate_actual_json(
    payload: dict[str, Any], spec: ExperimentSpec, expected_target: Path
) -> dict[str, Any]:
    if payload.get("fio version") != "fio-3.43":
        raise SafetyGateError(f"Unexpected FIO version {payload.get('fio version')!r}")
    jobs = payload.get("jobs", [])
    if len(jobs) != 1:
        raise SafetyGateError(f"Expected one job in JSON, found {len(jobs)}")
    job = jobs[0]
    options = combine_options(payload, job)
    expected_options = {
        "filename": expected_target.name,
        "ioengine": "windowsaio",
        "direct": str(spec.direct),
        "rw": spec.rw,
        "bs": spec.bs,
        "iodepth": str(spec.iodepth),
        "numjobs": str(spec.numjobs),
    }
    for key, expected in expected_options.items():
        if str(options.get(key)) != expected:
            raise SafetyGateError(
                f"Actual JSON {key}={options.get(key)!r}, expected {expected!r}"
            )
    reported = Path(str(options["filename"]))
    if reported.is_absolute() or reported.name != str(options["filename"]):
        raise SafetyGateError("FIO JSON did not report a basename-only target")
    reconstructed = (expected_target.parent / reported).resolve(strict=False)
    validated = validate_fio_target(reconstructed, repository_root())
    if validated != expected_target:
        raise SafetyGateError(
            f"Actual FIO target {validated} differs from validated target {expected_target}"
        )
    read_bytes = int(job.get("read", {}).get("io_bytes", 0))
    write_bytes = int(job.get("write", {}).get("io_bytes", 0))
    if read_bytes + write_bytes <= 0:
        raise SafetyGateError("FIO JSON reports zero completed I/O")
    return {
        "fio_version": payload["fio version"],
        "reported_filename": str(reported),
        "reconstructed_target": str(validated),
        "read_io_bytes": read_bytes,
        "write_io_bytes": write_bytes,
        "total_io_bytes": read_bytes + write_bytes,
        "read_total_ios": int(job.get("read", {}).get("total_ios", 0)),
        "write_total_ios": int(job.get("write", {}).get("total_ios", 0)),
    }


def run_experiment(spec: ExperimentSpec, *, create_target: bool = False) -> dict[str, Any]:
    repo = repository_root()
    if spec.direct not in (0, 1):
        raise SafetyGateError("direct must be exactly 0 or 1")
    if spec.direct == 0 and spec.phase != "phase7":
        raise SafetyGateError("Buffered I/O is permitted only for the explicit Phase 7 pitfall")
    benchmark_dir = (repo / "benchmark_data").resolve(strict=True)
    requested = benchmark_dir / spec.target_filename
    target = validate_fio_target(
        requested, repo, allow_nonexistent=create_target
    )
    if target.name != spec.target_filename or target.parent != benchmark_dir:
        raise SafetyGateError("Target is not the exact basename in benchmark_data")
    if ":" in target.name:
        raise SafetyGateError("Colon-containing target basename is forbidden")
    if create_target:
        prepare_sparse_container(target, spec.size_bytes)
        target = validate_fio_target(target, repo)
    elif target.stat().st_size < spec.size_bytes:
        raise SafetyGateError("Production target is smaller than the requested range")

    free_before = current_free_bytes(repo)
    if spec.may_write and free_before < MIN_FREE_BYTES:
        raise SafetyGateError("Free space is below the 100 GiB write-phase gate")
    prior_writes = read_cumulative_writes(repo)
    if prior_writes + spec.projected_max_write_bytes > WRITE_BUDGET_BYTES:
        raise SafetyGateError("Planned job could exceed the 80 GiB logical-write budget")

    fio = FIO_PATH.resolve(strict=True)
    run_id = (
        f"{slug(spec.phase)}_{slug(spec.configuration)}_"
        f"rep{spec.repetition}_{utc_stamp()}"
    )
    raw_dir = repo / "data" / "raw" / spec.phase
    metadata_dir = repo / "data" / "metadata" / spec.phase
    log_dir = repo / "logs" / spec.phase
    for directory in (raw_dir, metadata_dir, log_dir):
        directory.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{run_id}.json"
    metadata_path = metadata_dir / f"{run_id}.json"
    log_path = log_dir / f"{run_id}.log"
    for path in (raw_path, metadata_path, log_path):
        if path.exists():
            raise SafetyGateError(f"Immutable output already exists: {path}")

    command = [
        str(fio),
        f"--name={spec.configuration}",
        f"--output={raw_path}",
        "--output-format=json",
        f"--filename={target.name}",
        "--ioengine=windowsaio",
        f"--direct={spec.direct}",
        "--thread=1",
        "--group_reporting=1",
        f"--rw={spec.rw}",
        f"--bs={spec.bs}",
        f"--iodepth={spec.iodepth}",
        f"--numjobs={spec.numjobs}",
        f"--size={spec.size_bytes}",
        "--percentile_list=50:95:99:99.9",
        "--randrepeat=1",
        "--refill_buffers=1",
        "--buffer_compress_percentage=0",
    ]
    if spec.rwmixread is not None:
        command.append(f"--rwmixread={spec.rwmixread}")
    if spec.runtime_s is not None:
        command.extend(
            [
                "--time_based=1",
                f"--runtime={spec.runtime_s}",
                f"--ramp_time={spec.ramp_s}",
            ]
        )
    else:
        if spec.io_size_bytes is None:
            raise SafetyGateError("Size-bounded job is missing io_size_bytes")
        command.extend(["--time_based=0", f"--io_size={spec.io_size_bytes}"])
    command.extend(spec.extra_args)
    if spec.bandwidth_log:
        command.extend(
            [
                f"--write_bw_log={run_id}",
                "--log_avg_msec=1000",
            ]
        )

    displayed = {
        "classification": spec.classification,
        "run_id": run_id,
        "resolved_target": str(target),
        "file_range_bytes": spec.size_bytes,
        "fio_executable": str(fio),
        "engine": "windowsaio",
        "direct": spec.direct,
        "workload": spec.rw,
        "block_size": spec.bs,
        "iodepth": spec.iodepth,
        "numjobs": spec.numjobs,
        "working_directory": str(benchmark_dir),
        "filename_argument": target.name,
        "free_bytes_before": free_before,
        "logical_writes_before": prior_writes,
        "projected_max_write_bytes": spec.projected_max_write_bytes,
    }
    print("SAFE REGULAR-FILE TARGET VERIFIED", flush=True)
    for key, value in displayed.items():
        print(f"{key}={value}", flush=True)
    log_path.write_text(
        "SAFE REGULAR-FILE TARGET VERIFIED\n"
        + "\n".join(f"{key}={value}" for key, value in displayed.items())
        + f"\ncommand={subprocess.list2cmdline(command)}\n",
        encoding="utf-8",
    )

    before_files = snapshot_files(repo)
    budget_recorded = False
    try:
        subprocess.run(command, cwd=benchmark_dir, check=True)
        after_files = snapshot_files(repo)
        generated_logs = (
            [path for path in benchmark_dir.glob(f"{run_id}_bw*.log") if path.is_file()]
            if spec.bandwidth_log
            else []
        )
        if spec.bandwidth_log and not generated_logs:
            raise SafetyGateError("Requested bandwidth log was not produced")
        allowed_new = {raw_path.relative_to(repo)} | {
            path.relative_to(repo) for path in generated_logs
        }
        unexpected = after_files - before_files - allowed_new
        if unexpected:
            raise SafetyGateError(
                "SAFETY GATE FAILED: unexpected files appeared: "
                + ", ".join(sorted(map(str, unexpected)))
            )

        with raw_path.open("r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
        actual = validate_actual_json(payload, spec, target)
        relocated_logs: list[str] = []
        for generated in generated_logs:
            destination = log_dir / generated.name
            if destination.exists():
                raise SafetyGateError(f"Immutable bandwidth log already exists: {destination}")
            generated.replace(destination)
            relocated_logs.append(str(destination.relative_to(repo)))
        cumulative = append_write_budget(
            repo, spec, run_id, actual["write_io_bytes"]
        )
        budget_recorded = True
        metadata = {
            "spec": asdict(spec),
            "run_id": run_id,
            "classification": spec.classification,
            "command_argv": command,
            "working_directory": str(benchmark_dir),
            "validated_target": str(target),
            "raw_json": str(raw_path.relative_to(repo)),
            "actual_validation": actual,
            "bandwidth_logs": relocated_logs,
            "free_bytes_before": free_before,
            "free_bytes_after": current_free_bytes(repo),
            "cumulative_logical_bytes_written": cumulative,
            "status": "VALID",
        }
        with metadata_path.open("x", encoding="utf-8") as handle:
            json.dump(metadata, handle, indent=2)
            handle.write("\n")
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write("ACTUAL JSON TARGET VALIDATED\n")
            handle.write(f"logical_bytes_written={actual['write_io_bytes']}\n")
            handle.write(f"cumulative_logical_bytes_written={cumulative}\n")
            handle.write("RUN VALIDATED\n")
        print(
            f"RUN VALIDATED {run_id}: read={actual['read_io_bytes']} "
            f"write={actual['write_io_bytes']} cumulative_write={cumulative}",
            flush=True,
        )
        return metadata
    except Exception as exc:
        recovered_write_bytes = 0
        if raw_path.exists():
            try:
                failed_payload = json.loads(raw_path.read_text(encoding="utf-8-sig"))
                recovered_write_bytes = sum(
                    int(job.get("write", {}).get("io_bytes", 0))
                    for job in failed_payload.get("jobs", [])
                )
            except Exception:
                recovered_write_bytes = 0
        if not budget_recorded and recovered_write_bytes:
            try:
                append_write_budget(repo, spec, run_id, recovered_write_bytes)
            except Exception:
                pass
        invalid = {
            "spec": asdict(spec),
            "run_id": run_id,
            "classification": spec.classification,
            "command_argv": command,
            "working_directory": str(benchmark_dir),
            "validated_target": str(target),
            "raw_json": str(raw_path.relative_to(repo)) if raw_path.exists() else None,
            "recovered_logical_bytes_written": recovered_write_bytes,
            "status": "INVALID",
            "error": f"{type(exc).__name__}: {exc}",
        }
        if not metadata_path.exists():
            with metadata_path.open("x", encoding="utf-8") as handle:
                json.dump(invalid, handle, indent=2)
                handle.write("\n")
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"RUN INVALID: {type(exc).__name__}: {exc}\n")
        print(f"RUN INVALID {run_id}: {exc}", flush=True)
        raise


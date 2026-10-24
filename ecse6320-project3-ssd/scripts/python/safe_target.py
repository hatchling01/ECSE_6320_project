"""Canonical regular-file target validation for every active FIO workflow."""

from __future__ import annotations

import os
import re
from pathlib import Path


DEVICE_PATTERN = re.compile(
    r"(?i)(^\\\\\.\\|^\\\\\?\\(?:GLOBALROOT|Volume\{)|^\\Device\\|PhysicalDrive|HarddiskVolume|Volume\{)"
)
DRIVE_ONLY_PATTERN = re.compile(r"^[A-Za-z]:[\\/]?$")


class UnsafeTargetError(ValueError):
    """Raised when a proposed FIO target is not a safe repository file."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def validate_fio_target(
    candidate: str | os.PathLike[str] | None,
    repo_root: str | os.PathLike[str] | None = None,
    *,
    allow_nonexistent: bool = False,
) -> Path:
    """Return a canonical target or raise before any storage workload can start."""

    if candidate is None or not str(candidate).strip():
        raise UnsafeTargetError("target is empty")

    raw = str(candidate).strip()
    if DRIVE_ONLY_PATTERN.fullmatch(raw):
        raise UnsafeTargetError("drive roots and drive-only targets are forbidden")
    if DEVICE_PATTERN.search(raw):
        raise UnsafeTargetError("device, physical-drive, partition, and volume paths are forbidden")
    if ":" in Path(raw).name:
        raise UnsafeTargetError("alternate data streams and colon-containing leaf names are forbidden")

    repo = Path(repo_root).resolve(strict=True) if repo_root else repository_root()
    benchmark_root = (repo / "benchmark_data").resolve(strict=True)
    target = Path(raw).resolve(strict=False)

    if target == Path(target.anchor):
        raise UnsafeTargetError("filesystem roots are forbidden")
    if target == benchmark_root:
        raise UnsafeTargetError("benchmark_data itself is a directory, not a file")

    try:
        common = Path(os.path.commonpath((benchmark_root, target)))
    except ValueError as exc:
        raise UnsafeTargetError("target is on a different filesystem root") from exc
    if os.path.normcase(str(common)) != os.path.normcase(str(benchmark_root)):
        raise UnsafeTargetError("canonical target is outside benchmark_data")

    if target.exists():
        if not target.is_file():
            raise UnsafeTargetError("existing target is not a regular file")
    elif not allow_nonexistent:
        raise UnsafeTargetError("target does not exist; controlled creation was not enabled")

    if not target.name or target.name in {".", ".."}:
        raise UnsafeTargetError("target has no regular-file leaf name")
    return target


"""Lightweight no-FIO repository, evidence, and Markdown audit."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from fio_runner import GIB, PRODUCTION_SIZE_BYTES, WRITE_BUDGET_BYTES
from safe_target import repository_root


EXPECTED_RUNS = {
    "phase2": 13,
    "phase3": 72,
    "phase4": 12,
    "phase5": 69,
    "phase6": 22,
    "phase7": 9,
}


def main() -> int:
    repo = repository_root()
    target = repo / "benchmark_data" / "fio_production.bin"
    assert target.is_file() and target.stat().st_size == PRODUCTION_SIZE_BYTES

    for phase, expected in EXPECTED_RUNS.items():
        metadata_paths = sorted((repo / "data" / "metadata" / phase).glob("*.json"))
        raw_paths = sorted((repo / "data" / "raw" / phase).glob("*.json"))
        assert len(metadata_paths) == len(raw_paths) == expected, phase
        for path in metadata_paths:
            metadata = json.loads(path.read_text(encoding="utf-8-sig"))
            assert metadata["status"] == "VALID", path
            assert metadata["actual_validation"]["reported_filename"] == "fio_production.bin", path
            assert Path(metadata["actual_validation"]["reconstructed_target"]).resolve() == target.resolve(), path
            assert (repo / metadata["raw_json"]).is_file(), path

    with (repo / "data" / "metadata" / "write_budget.csv").open(encoding="utf-8-sig", newline="") as handle:
        budget_rows = list(csv.DictReader(handle))
    cumulative = int(budget_rows[-1]["cumulative_logical_bytes_written"])
    assert cumulative <= WRITE_BUDGET_BYTES

    broken: list[str] = []
    link_pattern = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")
    for markdown in repo.rglob("*.md"):
        if ".git" in markdown.parts:
            continue
        for destination in link_pattern.findall(markdown.read_text(encoding="utf-8-sig")):
            destination = destination.split("#", 1)[0]
            if not destination or "://" in destination or destination.startswith("mailto:"):
                continue
            if not (markdown.parent / destination).resolve().exists():
                broken.append(f"{markdown.relative_to(repo)} -> {destination}")
    assert not broken, "Broken local Markdown links:\n" + "\n".join(broken)

    print(f"Repository audit passed: {sum(EXPECTED_RUNS.values())} production/prep runs")
    print(f"Production file: {target.stat().st_size / GIB:.0f} GiB (Git tracking checked separately)")
    print(f"Cumulative logical writes: {cumulative / GIB:.3f} GiB / 80 GiB")
    print("All production JSON targets reconstruct to benchmark_data/fio_production.bin")
    print("All local Markdown links resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Execute explicitly selected stages of the Phase 5 concurrency study."""

from __future__ import annotations

import argparse

from fio_runner import MIB, ExperimentSpec, run_experiment


PRIMARY_QDS = (1, 2, 4, 8, 16, 32, 64)
SEQUENTIAL_QDS = (1, 2, 4, 8, 16, 32)


def parse_qds(value: str) -> tuple[int, ...]:
    qds = tuple(int(part) for part in value.split(","))
    if not qds or any(qd < 1 or qd > 256 for qd in qds):
        raise argparse.ArgumentTypeError("QDs must be in the inclusive range 1..256")
    return qds


def read_specs(qds: tuple[int, ...]) -> list[ExperimentSpec]:
    return [
        ExperimentSpec(
            phase="phase5",
            configuration=f"random_read_4k_qd{qd}",
            repetition=rep,
            rw="randread",
            bs="4k",
            iodepth=qd,
            runtime_s=6,
            ramp_s=1,
        )
        for rep in range(1, 4)
        for qd in qds
    ]


def mixed_specs(qds: tuple[int, ...]) -> list[ExperimentSpec]:
    return [
        ExperimentSpec(
            phase="phase5",
            configuration=f"mixed_read70_write30_4k_qd{qd}",
            repetition=rep,
            rw="randrw",
            bs="4k",
            iodepth=qd,
            io_size_bytes=256 * MIB,
            rwmixread=70,
        )
        for rep in range(1, 4)
        for qd in qds
    ]


def sequential_specs(qds: tuple[int, ...]) -> list[ExperimentSpec]:
    return [
        ExperimentSpec(
            phase="phase5",
            configuration=f"sequential_read_128k_qd{qd}",
            repetition=rep,
            rw="read",
            bs="128k",
            iodepth=qd,
            runtime_s=6,
            ramp_s=1,
        )
        for rep in range(1, 4)
        for qd in qds
    ]


def write_specs(qds: tuple[int, ...]) -> list[ExperimentSpec]:
    return [
        ExperimentSpec(
            phase="phase5",
            configuration=f"random_write_4k_qd{qd}",
            repetition=rep,
            rw="randwrite",
            bs="4k",
            iodepth=qd,
            io_size_bytes=256 * MIB,
        )
        for rep in range(1, 4)
        for qd in qds
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("primary", "extension", "mixed", "sequential", "write"))
    parser.add_argument("--qds", type=parse_qds)
    args = parser.parse_args()

    if args.stage == "primary":
        if args.qds:
            parser.error("primary has the fixed staged sequence through QD64")
        specs = read_specs(PRIMARY_QDS)
    elif args.stage == "extension":
        specs = read_specs(args.qds or (128,))
    elif args.stage == "mixed":
        specs = mixed_specs(args.qds or PRIMARY_QDS)
    elif args.stage == "sequential":
        specs = sequential_specs(args.qds or SEQUENTIAL_QDS)
    else:
        if not args.qds:
            parser.error("write requires the evidence-selected --qds subset")
        specs = write_specs(args.qds)

    for spec in specs:
        run_experiment(spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

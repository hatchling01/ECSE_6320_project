"""Run the read-only direct-versus-buffered benchmark pitfall demonstration."""

from __future__ import annotations

from fio_runner import MIB, ExperimentSpec, run_experiment


def spec(configuration: str, repetition: int, direct: int) -> ExperimentSpec:
    return ExperimentSpec(
        phase="phase7",
        configuration=configuration,
        repetition=repetition,
        rw="read",
        bs="128k",
        iodepth=1,
        size_bytes=512 * MIB,
        io_size_bytes=512 * MIB,
        direct=direct,
    )


def main() -> int:
    for repetition in range(1, 4):
        run_experiment(spec("pitfall_direct", repetition, 1))
        run_experiment(spec("pitfall_buffered_first", repetition, 0))
        run_experiment(spec("pitfall_buffered_second", repetition, 0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

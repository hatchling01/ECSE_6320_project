"""Execute only Phase 2: production initialization and four QD1 baselines."""

from __future__ import annotations

from fio_runner import GIB, ExperimentSpec, PRODUCTION_SIZE_BYTES, run_experiment


def main() -> int:
    phase = "phase2"
    run_experiment(
        ExperimentSpec(
            phase=phase,
            configuration="production_init",
            repetition=1,
            rw="write",
            bs="1m",
            iodepth=8,
            io_size_bytes=PRODUCTION_SIZE_BYTES,
            classification="PREPARATION_NOT_PERFORMANCE",
        ),
        create_target=True,
    )

    specs: list[ExperimentSpec] = []
    for repetition in range(1, 4):
        specs.extend(
            [
                ExperimentSpec(
                    phase=phase,
                    configuration="randread_4k_qd1",
                    repetition=repetition,
                    rw="randread",
                    bs="4k",
                    iodepth=1,
                    runtime_s=15,
                    ramp_s=3,
                ),
                ExperimentSpec(
                    phase=phase,
                    configuration="randwrite_4k_qd1",
                    repetition=repetition,
                    rw="randwrite",
                    bs="4k",
                    iodepth=1,
                    io_size_bytes=1 * GIB,
                ),
                ExperimentSpec(
                    phase=phase,
                    configuration="seqread_128k_qd1",
                    repetition=repetition,
                    rw="read",
                    bs="128k",
                    iodepth=1,
                    runtime_s=15,
                    ramp_s=3,
                ),
                ExperimentSpec(
                    phase=phase,
                    configuration="seqwrite_128k_qd1",
                    repetition=repetition,
                    rw="write",
                    bs="128k",
                    iodepth=1,
                    io_size_bytes=4 * GIB,
                ),
            ]
        )
    for spec in specs:
        run_experiment(spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


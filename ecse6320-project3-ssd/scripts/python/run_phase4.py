"""Execute Phase 4's fixed 4 KiB random QD8 read/write mix sweep."""

from __future__ import annotations

from fio_runner import MIB, ExperimentSpec, run_experiment


def main() -> int:
    for repetition in range(1, 4):
        specs = [
            ExperimentSpec(
                phase="phase4",
                configuration="mix_read100_write0_4k_qd8",
                repetition=repetition,
                rw="randread",
                bs="4k",
                iodepth=8,
                runtime_s=8,
                ramp_s=2,
                rwmixread=100,
            ),
            ExperimentSpec(
                phase="phase4",
                configuration="mix_read70_write30_4k_qd8",
                repetition=repetition,
                rw="randrw",
                bs="4k",
                iodepth=8,
                io_size_bytes=512 * MIB,
                rwmixread=70,
            ),
            ExperimentSpec(
                phase="phase4",
                configuration="mix_read50_write50_4k_qd8",
                repetition=repetition,
                rw="randrw",
                bs="4k",
                iodepth=8,
                io_size_bytes=512 * MIB,
                rwmixread=50,
            ),
            ExperimentSpec(
                phase="phase4",
                configuration="mix_read0_write100_4k_qd8",
                repetition=repetition,
                rw="randwrite",
                bs="4k",
                iodepth=8,
                io_size_bytes=512 * MIB,
                rwmixread=0,
            ),
        ]
        for spec in specs:
            run_experiment(spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


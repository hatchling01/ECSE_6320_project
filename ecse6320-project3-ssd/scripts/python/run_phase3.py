"""Execute Phase 3's required block-size/pattern/direction matrix."""

from __future__ import annotations

from fio_runner import MIB, ExperimentSpec, run_experiment


BLOCK_SIZES = ("4k", "16k", "32k", "64k", "128k", "256k")


def main() -> int:
    for block_size in BLOCK_SIZES:
        for pattern, read_rw, write_rw in (
            ("sequential", "read", "write"),
            ("random", "randread", "randwrite"),
        ):
            for direction, rw in (("read", read_rw), ("write", write_rw)):
                configuration = f"{pattern}_{direction}_{block_size}_qd1"
                for repetition in range(1, 4):
                    if direction == "read":
                        spec = ExperimentSpec(
                            phase="phase3",
                            configuration=configuration,
                            repetition=repetition,
                            rw=rw,
                            bs=block_size,
                            iodepth=1,
                            runtime_s=8,
                            ramp_s=2,
                        )
                    else:
                        spec = ExperimentSpec(
                            phase="phase3",
                            configuration=configuration,
                            repetition=repetition,
                            rw=rw,
                            bs=block_size,
                            iodepth=1,
                            io_size_bytes=256 * MIB,
                        )
                    run_experiment(spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


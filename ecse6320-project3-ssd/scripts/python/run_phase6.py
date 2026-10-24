"""Execute selected Phase 6 tail, working-set, and device-state stages."""

from __future__ import annotations

import argparse

from fio_runner import GIB, MIB, ExperimentSpec, run_experiment


def tail_specs() -> list[ExperimentSpec]:
    specs: list[ExperimentSpec] = []
    for repetition in range(1, 4):
        for qd in (8, 16):
            specs.append(
                ExperimentSpec(
                    phase="phase6", configuration=f"tail_random_read_4k_qd{qd}",
                    repetition=repetition, rw="randread", bs="4k", iodepth=qd,
                    runtime_s=30, ramp_s=2,
                )
            )
            specs.append(
                ExperimentSpec(
                    phase="phase6", configuration=f"tail_mixed70_30_4k_qd{qd}",
                    repetition=repetition, rw="randrw", bs="4k", iodepth=qd,
                    io_size_bytes=GIB, rwmixread=70,
                )
            )
    return specs


def working_set_specs() -> list[ExperimentSpec]:
    ranges = ((256 * MIB, "256m"), (2 * GIB, "2g"), (8 * GIB, "8g"))
    return [
        ExperimentSpec(
            phase="phase6", configuration=f"working_set_{label}_random_read_4k_qd16",
            repetition=rep, rw="randread", bs="4k", iodepth=16,
            size_bytes=size, runtime_s=8, ramp_s=1,
        )
        for rep in range(1, 4)
        for size, label in ranges
    ]


def device_state_specs() -> list[ExperimentSpec]:
    return [
        ExperimentSpec(
            phase="phase6", configuration="device_state_sequential_write_1m_qd8",
            repetition=1, rw="write", bs="1m", iodepth=8,
            io_size_bytes=8 * GIB, bandwidth_log=True,
        )
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("tail", "working-set", "device-state"))
    args = parser.parse_args()
    specs = {
        "tail": tail_specs,
        "working-set": working_set_specs,
        "device-state": device_state_specs,
    }[args.stage]()
    for spec in specs:
        run_experiment(spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

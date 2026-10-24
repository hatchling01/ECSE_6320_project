"""Regenerate cross-platform tables and plots from committed Project 2 data.

This script performs analysis only; it never executes either benchmark.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
MAC_CSV = ROOT / "data" / "processed" / "summary.csv"
WIN_CSV = ROOT.parent / "ecse6320-project2-memory" / "data" / "parsed" / "summary.csv"
OUT = ROOT / "results" / "comparison"
PLOTS = OUT / "plots"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def select(rows: list[dict[str, str]], **criteria: object) -> dict[str, str]:
    matches = [r for r in rows if all(r.get(k, "") == str(v) for k, v in criteria.items())]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one row for {criteria}, found {len(matches)}")
    return matches[0]


def style(ax: plt.Axes, ylabel: str, title: str) -> None:
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(PLOTS / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    mac, win = read_csv(MAC_CSV), read_csv(WIN_CSV)
    OUT.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []

    def add(category: str, metric: str, platform: str, value: float, unit: str,
            source: str, comparability: str, note: str) -> None:
        records.append({"category": category, "metric": metric, "platform": platform,
                        "value": f"{value:.9g}", "unit": unit, "source": source,
                        "comparability": comparability, "note": note})

    # Working-set latency: same dependent-load concept, different node spacing/topology.
    mac_ws = sorted((r for r in mac if r["experiment"] == "working_set"), key=lambda r: f(r, "bytes"))
    win_ws = sorted((r for r in win if r["phase"] == "phase4" and r["mode"] == "latency"),
                    key=lambda r: f(r, "working_set_bytes"))
    for r in mac_ws:
        add("working_set_latency", f"{int(f(r, 'bytes'))}_bytes", "Mac", f(r, "ns_per_op_mean"),
            "ns/access", "data/processed/summary.csv", "MODERATE",
            "128 B node spacing; arithmetic mean of three trials")
    for r in win_ws:
        add("working_set_latency", f"{int(f(r, 'working_set_bytes'))}_bytes", "Windows",
            f(r, "ns_per_load_median"), "ns/load", "../ecse6320-project2-memory/data/parsed/summary.csv",
            "MODERATE", "64 B node spacing; median of three trials")

    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.plot([f(r, "bytes") / 1024 for r in mac_ws], [f(r, "ns_per_op_mean") for r in mac_ws],
            "o-", label="Mac M4 Pro (128 B nodes)")
    ax.plot([f(r, "working_set_bytes") / 1024 for r in win_ws],
            [f(r, "ns_per_load_median") for r in win_ws], "s-", label="Windows / Ryzen 9 9950X (64 B nodes)")
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Working set (KiB, log2 scale)")
    style(ax, "Dependent-load latency (ns/access)", "Working-set latency (moderate comparability)")
    save(fig, "working_set_latency.png")

    # Sequential/random 64 B spacing, normalized within each platform.
    mac_seq = select(mac, experiment="pattern_bandwidth", bytes="268435456", stride="64", pattern="sequential")
    mac_rnd = select(mac, experiment="pattern_bandwidth", bytes="268435456", stride="64", pattern="random")
    win_seq = select(win, phase="phase2", mode="stream", working_set_bytes="1073741824.0",
                     stride_bytes="64.0", pattern="sequential", requested_read_pct="100.0")
    win_rnd = select(win, phase="phase2", mode="stream", working_set_bytes="1073741824.0",
                     stride_bytes="64.0", pattern="random", requested_read_pct="100.0")
    seq_random = {
        "Mac": [1.0, f(mac_rnd, "useful_GB_s_mean") / f(mac_seq, "useful_GB_s_mean")],
        "Windows": [1.0, f(win_rnd, "useful_gib_per_s_median") / f(win_seq, "useful_gib_per_s_median")],
    }
    for platform, vals in seq_random.items():
        add("access_pattern_normalized", "sequential_64B", platform, vals[0], "ratio", "derived", "LOW",
            "Normalized within platform; useful-byte accounting and footprints differ")
        add("access_pattern_normalized", "random_64B", platform, vals[1], "ratio", "derived", "LOW",
            "Normalized within platform; useful-byte accounting and footprints differ")
    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    x = [0, 1]
    width = 0.36
    ax.bar([i - width / 2 for i in x], seq_random["Mac"], width, label="Mac")
    ax.bar([i + width / 2 for i in x], seq_random["Windows"], width, label="Windows")
    ax.set_xticks(x, ["Sequential", "Random"])
    ax.set_xlabel("64 B spacing read pattern")
    style(ax, "Bandwidth / sequential bandwidth", "Pattern sensitivity (low absolute comparability)")
    save(fig, "normalized_sequential_random.png")

    # Sequential read stride degradation.
    strides = [64, 256, 1024]
    mac_stride = [f(select(mac, experiment="pattern_bandwidth", bytes="268435456", stride=str(s),
                           pattern="sequential"), "useful_GB_s_mean") for s in strides]
    win_stride = [f(select(win, phase="phase2", mode="stream", working_set_bytes="1073741824.0",
                           stride_bytes=f"{s}.0", pattern="sequential", requested_read_pct="100.0"),
                    "useful_gib_per_s_median") for s in strides]
    mac_norm = [v / mac_stride[0] for v in mac_stride]
    win_norm = [v / win_stride[0] for v in win_stride]
    for platform, vals in (("Mac", mac_norm), ("Windows", win_norm)):
        for stride, value in zip(strides, vals):
            add("stride_normalized", f"{stride}_bytes", platform, value, "ratio", "derived", "MODERATE",
                "Normalized to that platform's 64 B sequential read")
    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    ax.plot(strides, mac_norm, "o-", label="Mac")
    ax.plot(strides, win_norm, "s-", label="Windows")
    ax.set_xscale("log", base=2)
    ax.set_xticks(strides, [str(s) for s in strides])
    ax.set_xlabel("Stride / spacing (bytes)")
    style(ax, "Bandwidth / 64 B bandwidth", "Normalized sequential-read stride response")
    save(fig, "normalized_stride_degradation.png")

    # Software read/write mix, normalized to pure read.
    mixes = [100, 70, 50, 0]
    mac_mix_raw = [f(select(mac, experiment="rw_bandwidth", bytes="268435456", stride="8",
                            pattern="sequential", read_percent=str(m)), "useful_GB_s_mean") for m in mixes]
    win_mix_raw = [f(select(win, phase="phase2", mode="mix", working_set_bytes="1073741824.0",
                            stride_bytes="64.0", pattern="sequential", requested_read_pct=f"{m}.0"),
                     "useful_gib_per_s_median") for m in mixes]
    mac_mix = [v / mac_mix_raw[0] for v in mac_mix_raw]
    win_mix = [v / win_mix_raw[0] for v in win_mix_raw]
    for platform, vals in (("Mac", mac_mix), ("Windows", win_mix)):
        for mix, value in zip(mixes, vals):
            add("read_write_mix_normalized", f"{mix}_percent_read", platform, value, "ratio", "derived", "LOW",
                "Different operation size, footprint, compiler paths, and useful-byte accounting")
    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    mix_positions = list(range(len(mixes)))
    ax.plot(mix_positions, mac_mix, "o-", label="Mac")
    ax.plot(mix_positions, win_mix, "s-", label="Windows")
    ax.set_xticks(mix_positions, [f"{m}%" for m in mixes])
    ax.set_xlabel("Software read percentage")
    style(ax, "Useful bandwidth / pure-read bandwidth", "Normalized read/write mix response")
    save(fig, "normalized_read_write_mix.png")

    # Loaded-concurrency response normalized within platform.
    mac_load = sorted((r for r in mac if r["experiment"] == "intensity"), key=lambda r: f(r, "workers"))
    win_load = sorted((r for r in win if r["phase"] == "phase3"), key=lambda r: f(r, "workers"))
    mac_max_bw = max(f(r, "background_GB_s_mean") for r in mac_load)
    win_max_bw = max(f(r, "worker_gib_per_s_median") for r in win_load)
    mac_base = f(mac_load[0], "probe_ns_mean")
    win_base = f(win_load[0], "probe_ns_per_load_median")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.2))
    ax1.plot([f(r, "workers") for r in mac_load], [f(r, "background_GB_s_mean") / mac_max_bw for r in mac_load],
             "o-", label="Mac")
    ax1.plot([f(r, "workers") for r in win_load], [f(r, "worker_gib_per_s_median") / win_max_bw for r in win_load],
             "s-", label="Windows")
    ax1.set_xlabel("Background workers")
    style(ax1, "Bandwidth / observed maximum", "Throughput response")
    ax2.plot([f(r, "workers") for r in mac_load], [f(r, "probe_ns_mean") / mac_base for r in mac_load],
             "o-", label="Mac")
    ax2.plot([f(r, "workers") for r in win_load], [f(r, "probe_ns_per_load_median") / win_base for r in win_load],
             "s-", label="Windows")
    ax2.set_xlabel("Background workers")
    style(ax2, "Probe latency / unloaded latency", "Latency response")
    save(fig, "normalized_loaded_concurrency.png")
    for platform, rows, max_bw, base, bw_key, lat_key in (
        ("Mac", mac_load, mac_max_bw, mac_base, "background_GB_s_mean", "probe_ns_mean"),
        ("Windows", win_load, win_max_bw, win_base, "worker_gib_per_s_median", "probe_ns_per_load_median"),
    ):
        for r in rows:
            workers = int(f(r, "workers"))
            add("loaded_bandwidth_normalized", f"{workers}_workers", platform, f(r, bw_key) / max_bw,
                "ratio", "derived", "LOW", "Different worker kernels, core counts, footprints, and byte units")
            add("loaded_latency_normalized", f"{workers}_workers", platform, f(r, lat_key) / base,
                "ratio", "derived", "LOW", "Dependent probe normalized to platform unloaded baseline")

    # Raw headline values needed by the narrative and tables.
    for metric, row, key, unit in (
        ("64B_sequential_read", mac_seq, "useful_GB_s_mean", "GB/s"),
        ("64B_random_read", mac_rnd, "useful_GB_s_mean", "GB/s"),
    ):
        add("pattern_bandwidth", metric, "Mac", f(row, key), unit, "data/processed/summary.csv", "LOW",
            "256 MiB span; 8 useful bytes per operation")
    for metric, row in (("64B_sequential_read", win_seq), ("64B_random_read", win_rnd)):
        add("pattern_bandwidth", metric, "Windows", f(row, "useful_gib_per_s_median"), "GiB/s",
            "../ecse6320-project2-memory/data/parsed/summary.csv", "LOW",
            "1 GiB working set; 64 logical useful bytes per operation")
    mac_tlb = [r for r in mac if r["experiment"] == "page_locality"]
    win_tlb = [r for r in win if r["phase"] == "phase4" and r["mode"] == "tlb"]
    for r in mac_tlb:
        add("page_locality", f"{r['nodes']}_nodes_{r['layout']}", "Mac", f(r, "ns_per_op_mean"),
            "ns/access", "data/processed/summary.csv", "LOW",
            "16 KiB native pages; cache effects not isolated; no validated TLB counts")
    for r in win_tlb:
        pages = int(f(r, "working_set_bytes") / f(r, "spacing_bytes"))
        add("page_locality", f"{pages}_pages", "Windows", f(r, "ns_per_load_median"), "ns/load",
            "../ecse6320-project2-memory/data/parsed/summary.csv", "LOW",
            "4 KiB pages; one node per page")

    fields = ["category", "metric", "platform", "value", "unit", "source", "comparability", "note"]
    with (OUT / "mac_windows_project2_comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    print(f"wrote {len(records)} comparison records and 5 plots to {OUT}")


if __name__ == "__main__":
    main()

"""Aggregate actual trials, draw compact plots, and produce a data-backed report."""
import csv
import json
from pathlib import Path
import statistics as stats

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
RUN = RAW / (RAW / 'latest.txt').read_text().strip()
PROCESSED, PLOTS, REPORT = ROOT/'data'/'processed', ROOT/'plots', ROOT/'report'
for p in [PROCESSED, PLOTS, REPORT]:
    p.mkdir(parents=True, exist_ok=True)
rows = [json.loads(line) for line in (RUN/'measurements.jsonl').read_text().splitlines()]
KEYS = ['experiment', 'bytes', 'stride', 'pattern', 'read_percent', 'workers', 'nodes', 'layout']
METRICS = ['seconds', 'ns_per_op', 'useful_GB_s', 'background_GB_s', 'probe_ns']
groups = {}
for row in rows:
    groups.setdefault(tuple(row.get(k, '') for k in KEYS), []).append(row)
summary = []
for key, values in groups.items():
    result = dict(zip(KEYS, key), n=len(values))
    assert result['n'] == 3, f'Incomplete trials: {key}'
    for metric in METRICS:
        sample = [r[metric] for r in values]
        result.update({metric+'_mean': stats.mean(sample), metric+'_sd': stats.stdev(sample),
                       metric+'_median': stats.median(sample)})
    summary.append(result)
with (PROCESSED/'summary.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)
(PROCESSED/'source-run.txt').write_text(RUN.name+'\n')


def select(experiment, **filters):
    return [r for r in summary if r['experiment'] == experiment and all(r[k] == v for k, v in filters.items())]


def line(ax, data, x, metric, **kwargs):
    ax.errorbar([x(r) for r in data], [r[metric+'_mean'] for r in data],
                yerr=[r[metric+'_sd'] for r in data], marker='o', capsize=3, **kwargs)


def save(fig, name):
    for ax in fig.axes:
        ax.grid(True, alpha=.22, axis='y')
    fig.tight_layout()
    fig.savefig(PLOTS/(name+'.png'), dpi=170)
    fig.savefig(PLOTS/(name+'.pdf'))
    plt.close(fig)


plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
MiB = 1024**2
ws = sorted(select('working_set'), key=lambda r:r['bytes'])
ss = sorted(select('stream_size'), key=lambda r:r['bytes'])
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, data, metric, ylabel in [(axes[0], ws, 'ns_per_op', 'Dependent access latency (ns)'),
                                (axes[1], ss, 'useful_GB_s', 'Useful read throughput (GB/s)')]:
    line(ax, data, lambda r:r['bytes']/MiB, metric)
    ax.set_xscale('log', base=2); ax.set_xlabel('Working set (MiB)'); ax.set_ylabel(ylabel)
    ax.axvline(.125, color='tab:green', ls='--', label='P-core L1D 128 KiB')
    ax.axvline(16, color='tab:orange', ls='--', label='P-cluster L2 16 MiB')
    ax.legend(fontsize=8)
axes[0].set_title('Random pointer chain, 128 B node spacing')
axes[0].set_yscale('log', base=2)
axes[0].set_yticks([1,2,4,8,16,32,64,128], [1,2,4,8,16,32,64,128])
axes[0].axvspan(64,512,alpha=.08,color='tab:blue',label='Large memory-dominated region')
axes[0].legend(fontsize=8,loc='upper left')
axes[1].set_title('Dense sequential reads, 8 B payload/access')
save(fig, 'working_set')

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for pattern in ['sequential', 'random']:
    for ax, experiment, metric in [(axes[0], 'pattern_latency', 'ns_per_op'),
                                   (axes[1], 'pattern_bandwidth', 'useful_GB_s')]:
        data = sorted(select(experiment, pattern=pattern), key=lambda r:r['stride'])
        line(ax, data, lambda r:r['stride'], metric, label=pattern)
        ax.set_xscale('log', base=2); ax.set_xticks([64,128,256,1024], [64,128,256,1024]); ax.legend()
        ax.set_xlabel('Stride / node spacing (bytes)')
axes[0].set_ylabel('Pointer-chain latency (ns)')
axes[1].set_ylabel('Useful streaming throughput (GB/s)')
axes[0].set_title('256 MiB, dependent loads')
axes[1].set_title('256 MiB; random includes index-array overhead')
save(fig, 'patterns')

mixes = [100,70,50,0]
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, experiment, metric, ylabel in [(axes[0], 'rw_bandwidth', 'useful_GB_s', 'Useful throughput (GB/s)'),
                                      (axes[1], 'rw_latency', 'probe_ns', 'Separate read-probe latency (ns)')]:
    data = [select(experiment, read_percent=r)[0] for r in mixes]
    ax.bar(range(4), [r[metric+'_mean'] for r in data],
           yerr=[r[metric+'_sd'] for r in data], capsize=4)
    ax.set_xticks(range(4), ['100/0','70/30','50/50','0/100']); ax.set_xlabel('Software reads/writes (%)'); ax.set_ylabel(ylabel)
axes[0].set_title('One dense sequential stream, 256 MiB')
axes[1].set_title('Four background streams, 128 MiB each')
save(fig, 'read_write')

intensity = sorted(select('intensity'), key=lambda r:r['workers'])
loaded = [r for r in intensity if r['workers']]
maximum = max(r['background_GB_s_mean'] for r in loaded)
candidate = next(r for r in loaded if r['background_GB_s_mean'] >= .9*maximum)
later = [r for r in loaded if r['workers'] > candidate['workers']]
resolved = bool(later and any(r['probe_ns_mean'] > 1.15*candidate['probe_ns_mean'] for r in later))
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
line(axes[0], intensity, lambda r:r['workers'], 'background_GB_s')
axes[0].set_xlabel('Background workers (probe is an additional thread)')
axes[0].set_ylabel('Background useful read throughput (GB/s)')
line(axes[1], intensity, lambda r:r['background_GB_s_mean'], 'probe_ns',
     xerr=[r['background_GB_s_sd'] for r in intensity])
for r in intensity:
    offset = {4:(-18,-17),7:(-18,7)}.get(r['workers'],(5,5))
    axes[1].annotate(str(r['workers']), (r['background_GB_s_mean'],r['probe_ns_mean']), xytext=offset,textcoords='offset points')
axes[1].scatter([candidate['background_GB_s_mean']], [candidate['probe_ns_mean']], s=100, facecolors='none',edgecolors='red',label='First sampled ≥90% of observed maximum')
axes[1].set_xlabel('Background useful read throughput (GB/s)'); axes[1].set_ylabel('Dependent read-probe latency (ns)'); axes[1].legend(fontsize=7)
save(fig, 'intensity')

fig, ax = plt.subplots(figsize=(7,4))
for layout in ['compact','spread']:
    data = sorted(select('page_locality', layout=layout), key=lambda r:r['nodes'])
    line(ax, data, lambda r:r['nodes'], 'ns_per_op', label=layout)
ax.set_xscale('log',base=2); ax.set_xlabel('Randomly linked nodes (one 128 B line per node)')
ax.set_ylabel('Dependent load latency (ns)'); ax.legend(); ax.set_title('Native 16 KiB pages; spread rotates offsets within each page')
save(fig, 'page_locality')

small = next(r for r in ss if r['bytes']==32*1024)
large = next(r for r in ss if r['bytes']==512*MiB)
fig, ax = plt.subplots(figsize=(6,4))
ax.bar(['32 KiB (cache reuse)','512 MiB (large footprint)'],
       [small['useful_GB_s_mean'],large['useful_GB_s_mean']],
       yerr=[small['useful_GB_s_sd'],large['useful_GB_s_sd']],capsize=5)
ax.set_ylabel('Useful read throughput (GB/s)'); ax.set_title('Pitfall: cache bandwidth is not DRAM bandwidth')
save(fig, 'pitfall')

kernel = sorted(select('kernel'), key=lambda r:(r['bytes'],r['stride']))
klabels = ['96 KiB dense','24 MiB dense','192 MiB dense','192 MiB sparse']
counter_path = RUN/'counters'/'summary.json'
profiles = json.loads(counter_path.read_text()) if counter_path.exists() else []
fig, axes = plt.subplots(1, 2, figsize=(11,4))
axes[0].bar(range(4), [r['ns_per_op_mean'] for r in kernel], yerr=[r['ns_per_op_sd'] for r in kernel],capsize=3)
axes[0].set_xticks(range(4),klabels,rotation=18); axes[0].set_ylabel('Uninstrumented time per multiplied element (ns)')
profile_summary = []
for case in ['kernel_small','kernel_medium','kernel_large','kernel_sparse','pages_compact','pages_spread']:
    values = [r for r in profiles if r['case']==case]
    if not values: continue
    p = dict(case=case, n=len(values))
    for metric in ['critical_l1d_pct','critical_l1d_while_executing_pct','noncritical_l1d_pct',
                   'execution_latency_pct','executing_pct','ns_per_op','p_core_pct','e_core_pct']:
        sample = [r[metric] for r in values]
        p[metric+'_mean'] = stats.mean(sample)
        p[metric+'_sd'] = stats.stdev(sample) if len(sample)>1 else 0
    profile_summary.append(p)
kprofiles = [p for p in profile_summary if p['case'].startswith('kernel_')]
if len(kprofiles)==4:
    axes[1].bar(range(4), [p['critical_l1d_pct_mean'] for p in kprofiles],
                 yerr=[p['critical_l1d_pct_sd'] for p in kprofiles],capsize=3,color='tab:orange')
    axes[1].set_xticks(range(4),klabels,rotation=18); axes[1].set_ylabel('Critical L1D cache-miss stall metric (%)')
    axes[1].set_title('Instruments; measured region only, not miss counts')
else:
    axes[1].text(.5,.5,'Counter collection incomplete\nSee raw counter logs',ha='center',va='center',transform=axes[1].transAxes)
save(fig, 'kernel_counters')
if profile_summary:
    with (PROCESSED/'counter_summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(profile_summary[0]));w.writeheader();w.writerows(profile_summary)


def table(headers, body):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |',
                       *['| '+' | '.join(map(str,row))+' |' for row in body]])


baseline = []
for size, label in [(64*1024,'L1-compatible'),(4*MiB,'L2-compatible'),(64*MiB,'Beyond cluster L2; mixed SLC/translation'),(512*MiB,'Large, memory-dominated')]:
    r=next(r for r in ws if r['bytes']==size)
    baseline.append([label,f'{size/MiB:g}',f'{r["ns_per_op_mean"]:.2f} ± {r["ns_per_op_sd"]:.2f}'])
unloaded = intensity[0]
max_latency = max(r['probe_ns_mean'] for r in intensity)
proxy_bytes = candidate['background_GB_s_mean'] * candidate['probe_ns_mean']
page_pair = [select('page_locality',layout=l,nodes=8192)[0] for l in ['compact','spread']]
rw_table = [[f'{r}/{100-r}',
             f'{select("rw_bandwidth",read_percent=r)[0]["useful_GB_s_mean"]:.2f}',
             f'{select("rw_latency",read_percent=r)[0]["probe_ns_mean"]:.2f}'] for r in mixes]
load_table = [[r['workers'],f'{r["background_GB_s_mean"]:.2f}',f'{r["probe_ns_mean"]:.2f}'] for r in intensity]
kernel_table = [[label,f'{r["ns_per_op_mean"]:.3f}',f'{r["useful_GB_s_mean"]:.2f}'] for label,r in zip(klabels,kernel)]
counter_table = table(['Profile','Trials','Critical L1D stall (%)','P-core sampled time (%)'],
                      [[p['case'],p['n'],f'{p["critical_l1d_pct_mean"]:.2f} ± {p["critical_l1d_pct_sd"]:.2f}',f'{p["p_core_pct_mean"]:.1f}'] for p in profile_summary]) if profile_summary else 'Counter profiles unavailable; see raw failure logs.'
max_small = next(r for r in ws if r['bytes']==64*1024)
kernel_ratio = kernel[2]['ns_per_op_mean']/kernel[0]['ns_per_op_mean']
page_profiles = {p['case']:p for p in profile_summary if p['case'].startswith('pages_')}
page_counter_observation = (
    f"For the profiled 8192-node pair, the critical-L1D stall fraction is "
    f"{page_profiles['pages_compact']['critical_l1d_pct_mean']:.1f}% compact versus "
    f"{page_profiles['pages_spread']['critical_l1d_pct_mean']:.1f}% spread. "
    "A fraction can fall because other stalls grow; it does not establish that miss counts fell. "
    "Translation effects cannot be inferred by treating that cache-stall percentage as a TLB counter."
    if len(page_profiles)==2 else 'Page-locality counter profiles were not completed.')
ws_by_size = {r['bytes']:r for r in ws}
sequential_256 = select('pattern_latency',pattern='sequential',stride=256)[0]
sequential_1024 = select('pattern_latency',pattern='sequential',stride=1024)[0]
pages_256 = [select('page_locality',layout=l,nodes=256)[0] for l in ['compact','spread']]
correlation = (stats.correlation([r['ns_per_op_mean'] for r in kernel],
                               [p['critical_l1d_pct_mean'] for p in kprofiles])
               if len(kprofiles)==4 else None)
power_before = next(r['stdout'].strip().replace('\n', '; ') for r in json.loads((RUN/'system-before.json').read_text())
                    if r['command']==['pmset','-g','batt'])
swap_after = next(r['stdout'].split('vm.swapusage: ')[-1].strip()
                  for r in json.loads((RUN/'system-after.json').read_text())
                  if r['command'][0]=='sysctl')
report = f'''# Project #2 — Compact Cache & Memory Profiling

**Platform:** Apple M4 Pro, 24 GB unified memory, macOS 26.6.2.  
**Scope:** time-boxed targeted sweeps, not an exhaustive factorial experiment.  
**Raw run:** `{RUN.name}`; {len(rows)} uninstrumented measurements; three trials per setting.

## 1. Questions, hypotheses, and method

`HYPOTHESES.md` was written before this suite. The expected trends were cache-capacity
steps, sequential/prefetch advantages, diminishing bandwidth returns under load,
and worse locality when nodes span more pages. Unexpected trends are retained.

The native C benchmark is built with Clang `-O3 -g -std=c11 -pthread`, with warnings
treated as errors. Timing uses `CLOCK_MONOTONIC`; latency is reported in nanoseconds,
not converted using an assumed CPU frequency. The ARM timer frequency is not the CPU
clock. Pointer chasing has one dependent chain, so it suppresses intentional
memory-level parallelism and approximates an unloaded baseline, not guaranteed
hardware zero-queue latency. The ring is traversed before timing to warm mappings
and validate a single cycle. Arrays are initialized before timing; page faults are
not intentionally included. C assertions validate ring topology, mixed read/write
operations against a scalar reference, and every accessed multiply result.

All plots use arithmetic mean ± sample standard deviation over three independent
process runs. These are variability bars, not confidence intervals. Trials use
recorded seeds and shuffled order with a 0.1 s inter-run pause. Most timed regions
last at least 0.18 s; load tests last at least 0.4 s. A streaming pass is never cut
short, so some actual durations exceed the requested minimum. Each profile lasts
2 s, with setup excluded using signposts.

**Hardware/control:** 8 performance and 4 efficiency cores; 12 physical and 12
logical cores (no SMT). P-core L1D: 128 KiB/core; P-cluster L2: 16 MiB per four-core
group. E-core L1D: 64 KiB/core; E-cluster L2: 4 MiB. Cache lines: 128 B; native pages:
16 KiB. A user-interactive QoS hint is requested, not hard CPU pinning. Frequency
and thermals are not locked; OS activity is not isolated. No NUMA binding was
applied on this unified-memory host. Exact power-source/policy, memory-pressure,
swap, tool-version, and before/after system records are in the raw run directory.
**Recorded power source:** {power_before}. **Swap at the end:** {swap_after}.
The host had other applications running; Instruments also observed unrelated
background signposts. No privileged settings or security controls were changed.

## 2. Near-unloaded latency and working-set transitions

{table(['Interpretation, not guaranteed residency','Footprint (MiB)','Mean latency ± SD (ns)'],baseline)}

![Working-set sweeps](../plots/working_set.png)

The 64 KiB result is {max_small['ns_per_op_mean']:.2f} ns/access. At 512 MiB the
dependent chain reaches {baseline[-1][2]} ns/access. The known 128 KiB and 16 MiB
capacity boundaries are annotated, but capacity alone does not prove residency.
The shared L2 has competing occupants, and translation/prefetch/system-level-cache
effects can blur transitions. Apple does not expose a conventional Intel-style
L3 here; the 64 MiB region is not relabeled L3 or presented as an isolated SLC hit.
Large-footprint latency still includes address translation and loop overhead.
The sharp change from 128 KiB ({ws_by_size[128*1024]['ns_per_op_mean']:.2f} ns)
to 256 KiB ({ws_by_size[256*1024]['ns_per_op_mean']:.2f} ns) is consistent with
leaving P-core L1D. The 8/16/32 MiB points are
{ws_by_size[8*MiB]['ns_per_op_mean']:.2f}/{ws_by_size[16*MiB]['ns_per_op_mean']:.2f}/{ws_by_size[32*MiB]['ns_per_op_mean']:.2f} ns,
showing a broader shared-cache/translation transition, not three separately
identified cache levels.

For AMAT-style reasoning, use
`T ≈ L1_hit + m1 × (L2_increment + m2 × memory_increment)` under a consistent
conditional-miss definition. The measured small and large regimes show the size
of potential miss penalties. We do not fit numerical miss probabilities because
raw per-level miss counts were not recovered. Overlap and prefetching also mean
streaming runtime is not simply one AMAT multiplied by the number of accesses.

## 3. Patterns, strides, and software read/write mixes

![Pattern and stride sweeps](../plots/patterns.png)

Each access carries 8 useful bytes. At 64 B spacing, two adjacent nodes can share
one 128 B line; at 256/1024 B, most bytes fetched with a line are unused. Sequential
chains are prefetch-friendly; shuffled chains are dependent and irregular. Random
streaming additionally reads a shuffled index array, whose footprint is
`8 × node_count` bytes and whose traffic is **not** included in useful bandwidth.
Thus its result measures the indexed algorithm, not an isolated DRAM transaction.
The 256 MiB backing address span is fixed, not the unique touched-line footprint:
at 128/256/1024 B spacing, one pass touches about 256/128/32 MiB of cache lines.
Consequently a stride-dependent change can include cache reuse, not only wasted
line bytes. No claim that every sparse point measures purely DRAM is made.
One non-monotonic result is the sequential chain at 256 B versus 1024 B spacing:
{sequential_256['ns_per_op_mean']:.2f} versus {sequential_1024['ns_per_op_mean']:.2f} ns.
Fewer touched lines, prefetch behavior, and translation/cache indexing can explain
why a larger stride is not necessarily slower; this suite does not separate them.

![Read/write sweep](../plots/read_write.png)

{table(['Software R/W (%)','One-stream useful GB/s','Read-probe ns under four workers'],rw_table)}

These are separate experiments: the left panel measures throughput of a single
stream; the right uses a dependent read probe alongside four background streams
with the named mix. It does not report store-completion latency or pretend that
the two panels share the same concurrency. Mixed kernels issue the requested
operation proportions in groups of ten (with a tiny partial-group tail).
Loads and stores can generate write allocations, dirty evictions, and writeback;
100% software writes is not 100% DRAM write traffic. The fence orders stores but
does not flush all dirty lines to DRAM. Compiler/code-path differences and loop
overhead also contribute to mix differences. Compiler optimization remarks
(`vectorization.log`) show mixed-read inner loops were not vectorized while
pure streaming paths have optimized/interleaved versions. The mixed-stream
results therefore cannot be interpreted as pure DRAM mix penalties.

All bandwidth values are **application useful GB/s**, with `GB = 10^9 bytes`;
footprints use binary KiB/MiB. Physical DRAM bus bandwidth was not measured.

## 4. Loaded latency, saturation candidate, and Little's Law

![Throughput-latency tradeoff](../plots/intensity.png)

{table(['Background workers','Useful background GB/s','Read-probe ns'],load_table)}

Each worker scans its own 128 MiB array; the independent probe uses 256 MiB.
Up to 11 workers plus the probe use roughly 1.63 GiB of backing arrays. Workers
check a stop flag between 512 KiB chunks. The probe interval and the background
finish interval differ by at most the stop/drain tail; their timings are recorded
separately. More workers are not the same as a known number of outstanding requests.
At the largest count both core types can participate, and scheduler contention
can raise probe latency as well as memory queuing.

The first sampled level reaching at least 90% of the observed maximum is
**{candidate['workers']} workers**, at **{candidate['background_GB_s_mean']:.2f} GB/s**
and **{candidate['probe_ns_mean']:.2f} ns**. This is a predefined, discrete
**saturation candidate**, not proof of a hardware queue-depth knee.
{'Later sampled load raises latency by more than 15%, consistent with diminishing returns.' if resolved else 'A convincing post-knee latency rise was not established by this small sweep; no sharp knee is claimed.'}
The largest observed probe latency is {max_latency:.2f} ns versus
{unloaded['probe_ns_mean']:.2f} ns without background workers. A higher worker
count can change core placement and instruction overhead, so causality is qualified.
The 11-worker point also has larger latency variability; its error bar is retained
rather than interpreting the mean alone as a pure DRAM queuing penalty.

Little's Law is `Q = λW`, or `bytes_in_flight = bandwidth × mean_request_latency`
for the **same steady-state request population**. At the candidate,
`{candidate['background_GB_s_mean']:.2f} GB/s × {candidate['probe_ns_mean']:.2f} ns`
equals approximately **{proxy_bytes:.0f} bytes**, or **{proxy_bytes/128:.1f} 128-B-line
equivalents**. This is an illustrative pressure proxy only: useful background bytes
are not measured physical traffic, and dependent probe latency need not equal
background-request latency. It is not a measured MLP/queue-occupancy result.

## 5. Cache-related counter evidence and kernel performance

![Multiply kernel and cache-related stalls](../plots/kernel_counters.png)

{table(['Multiply footprint/access','ns per element','Useful GB/s (24 B/element)'],kernel_table)}

The kernel is `z[i] = x[i] * y[i]`; its footprint is the sum of all three arrays.
Sparse access uses a 128 B stride in each array, versus 8 B dense access. Every
computed result is checked outside timing. The dense large/small time-per-element
ratio is {kernel_ratio:.2f}×; this includes instruction throughput, locality, and bandwidth
effects and is not assigned exclusively to cache misses.
{'The dense large kernel did not show the expected slowdown relative to the small kernel. This is a retained negative result: efficient streaming, instruction-issue limits, and per-pass overhead can mask a capacity effect in ns/element. The sparse large kernel is much slower and has a less locality-friendly access regime.' if kernel_ratio <= 1.1 else 'The dense large kernel is slower per element than the small one, consistent with reduced locality, but instruction throughput and loop overhead remain alternative contributors.'}
Compiler remarks mark the runtime-stride multiply loop as not loop-vectorized;
the scalar/unrolled instruction stream may limit dense throughput even in cache.

{counter_table}

Apple Instruments' guided **Instruction Processing** mode supplies the table's
hardware-derived stall percentages. Exported metric legends identify Executing,
Execution Latency, Critical L1D Cache Miss, Critical L1D Cache Miss While Executing,
and Non-Critical L1D Cache Miss. Integer arrays are basis-point metrics; the parser
checks their length and normalization and duration-weights them over the marked
measurement interval. “Critical L1D” is a stall attribution, **not a miss count,
miss probability, or cycles-per-miss measurement**. The raw XML, legends, traces,
profiled runtimes, and sampled P/E-core fractions are retained. Correlation across
footprints/patterns is informative but does not by itself establish causality.
The profile window differs from the shorter uninstrumented run; profiler timing
is not substituted into the baseline measurements.
The descriptive Pearson correlation across the four kernel settings between
uninstrumented ns/element and the critical-L1D stall metric is
**{f'{correlation:.4f}' if correlation is not None else 'unavailable'}**. This is
dominated by the sparse point. With only
four different kernels/access regimes, this is a descriptive association, not
a statistical or causal proof. Low stall fraction does not imply few misses:
overlap, code generation, store work, and execution limits affect the denominator.

The manual raw-event configuration recorded, but its export aborted with a
`NSNull`/`NSString` cast error. The successful guided path is partial counter
coverage: direct cache/TLB miss counts, instruction counts, CPU cycles, and DRAM
controller traffic are not claimed. This leaves part of the rubric's requested
counter correlation incomplete, particularly data-TLB attribution.

**Why data-TLB miss counts are missing:** the local CPU event database exposes
data-TLB events, including `L1D_TLB_MISS_NONSPEC` and `L2_TLB_MISS_DATA`.
The custom configuration requested these events and recording completed, but the
command-line exporter crashed before individual counts could be extracted and
validated. This does **not** establish that the M4 lacks TLB counters. The failure
may involve the generated template or Instruments compatibility; the root cause
has not been established. The working guided mode exports cache-related stall
percentages, not data-TLB miss counts. Page-locality timing differences are
therefore not labeled as measured TLB misses.

## 6. Page locality and huge-page limitation

![Page-locality sweep](../plots/page_locality.png)

For 8192 nodes, compact versus spread latency is
**{page_pair[0]['ns_per_op_mean']:.2f} versus {page_pair[1]['ns_per_op_mean']:.2f} ns**.
Both touch 8192 lines and the same useful pointer bytes, but compact storage spans
1 MiB (64 native pages) and spread storage 128 MiB (8192 pages). Spread rotates
the within-page line offset instead of placing every node at offset zero. This
reduces a naive same-cache-set confound but cannot equalize all cache indexing,
physical placement, or prefetch behavior. Any slowdown is a page-locality result,
not a measured isolated TLB-miss penalty. Cache stall profiles for the pair help
expose residual cache confounding, but do not replace data-TLB counts.
At only 256 nodes, both layouts touch about 32 KiB of cache lines, while spanning
2 compact pages versus 256 spread pages. Their measured latencies are already
{pages_256[0]['ns_per_op_mean']:.2f} versus {pages_256[1]['ns_per_op_mean']:.2f} ns.
That is consistent with translation pressure appearing before a data-cache capacity
change, but is not enough to assign an exact TLB capacity or miss penalty.
{page_counter_observation}

Native pages are 16 KiB, not 4 KiB. Earlier feasibility checks accepted an ordinary
allocation and rejected explicit 2 MiB superpages with `KERN_INVALID_ARGUMENT`.
No huge-page result is invented. The PDF makes huge-page evaluation conditional
on availability; page locality is still tested on the real platform.

**Availability, not a longer-running benchmark:** the tested explicit 2 MiB
allocation path failed. Waiting longer would not make that request succeed.
No supported alternative allocation method has been established on this setup;
this is not proof that every possible large-page mechanism is unavailable.

### Follow-up estimates and grading implications (not measured results)

- On an already-configured bare-metal Linux machine with verified huge-page
  support, budget roughly **10–20 minutes** to adapt the test, verify actual
  huge-page allocation, run three trials, and plot the comparison. This is a
  planning estimate, not a measured runtime, and excludes machine/tool setup.
- On this Mac, there is **no reliable huge-page completion estimate** until a
  supported allocation method is found. Repeating a rejected allocation for
  longer is not useful.
- A further TLB-counter attempt could use an Instruments GUI-saved configuration
  or another collector, which may require administrator access. Budget
  **15–30 minutes of investigation**, with **no guarantee of success**. Neither
  alternative was validated in this compact study.
- The PDF explicitly conditions huge-page evaluation on availability. Missing
  direct TLB-counter evidence is the more important unresolved grading risk:
  it weakens the **35-point working-set/cache/TLB analysis category**. The PDF
  does not specify deductions within that category, so losing all 35 points
  is not assumed. No additional measurements are claimed by this update.

## 7. A deliberately misleading bandwidth claim

![Cache-reuse pitfall](../plots/pitfall.png)

The same dense read loop delivers **{small['useful_GB_s_mean']:.2f} GB/s** at
32 KiB versus **{large['useful_GB_s_mean']:.2f} GB/s** at 512 MiB
({small['useful_GB_s_mean']/large['useful_GB_s_mean']:.2f}× ratio).
Repeated passes over the small footprint reuse cache. Reporting its speed as
DRAM bandwidth would therefore be wrong. The correction is to sweep footprint,
use a large working set, retain the cache-resident control, and label useful
traffic rather than claim unmeasured memory-controller bandwidth. The full plot
is retained even if the expected bandwidth ordering is weak or reversed.

## 8. Limitations and AI-use transparency

- Three short trials give limited statistical power. No confidence or full-credit claim is made.
- Background OS work, DVFS, thermal drift, core migration, shared caches, and profiling
  overhead can affect results. QoS is not pinning, and no isolation was achieved.
- Apple system-level caching and native 16 KiB pages differ from a typical x86/Linux lab.
- Application bandwidth and stall metrics do not replace physical DRAM traffic or
  raw cache/TLB miss rates. No conventional L3, huge-page comparison, AMAT fit, or
  actual queue occupancy is fabricated.
- This compact suite deliberately avoids a full cross-product of all knobs. The
  read/write latency probe and throughput tests use different concurrency, as labeled.
- AI assistance (OpenAI GPT-6.1 Sol Fast through OpenCode) wrote the benchmark,
  scripts, plots, and this report and executed the automated checks/measurements.
  The failed manual-counter approach was rejected in favor of exportable guided
  metrics. Student understanding and independent review are still required before
  submission; automated AI-run assertions are not represented as human validation.

## Reproduction and evidence

See `README.md`, `Makefile`, `src/bench.c`, and `scripts/`. Raw commands, trial
outputs, system snapshots, profiler XML/trace files, and the shuffled plan are
under `data/raw/{RUN.name}/`. Aggregates are under `data/processed/`, with PNG
and PDF plots under `plots/`. Prior feasibility failures are retained separately
under `validation/`. The assignment source is
`ECSE4320_6320_Class-wide_Projects.pdf`, pages 1 and 4–5.
'''
(REPORT/'REPORT.md').write_text(report)
analysis = {'source_run':RUN.name, 'measurements':len(rows), 'profiles':len(profiles),
             'saturation_candidate_workers':candidate['workers'], 'post_candidate_latency_rise':resolved,
             'little_law_illustrative_bytes':proxy_bytes, 'counter_scope':'L1D-related stall metrics only; no raw data-TLB misses',
             'huge_page_status':'Not measured: explicit 2 MiB allocation rejected with KERN_INVALID_ARGUMENT; native pages are 16 KiB. No supported alternative was established.',
             'tlb_count_status':'Event definitions exist and custom recording completed, but export aborted with an NSNull/NSString cast error. Individual data-TLB counts were not extracted or validated; this does not show hardware counters are absent.',
             'follow_up_estimates':'Planning only: 10–20 minutes for a comparison on already-configured Linux with verified huge pages; no reliable Mac huge-page estimate; 15–30 minutes to investigate alternative TLB collection, without guaranteed success.',
             'grading_risk':'Huge pages are conditional on availability; missing direct TLB-counter evidence weakens the 35-point working-set/cache/TLB category. Exact deductions are unspecified.'}
(PROCESSED/'analysis.json').write_text(json.dumps(analysis,indent=2)+'\n')
assert len(ws)==12 and len(intensity)==6 and len(select('rw_bandwidth'))==4
print(json.dumps(analysis,indent=2))
print(f'Report: {REPORT/"REPORT.md"}')

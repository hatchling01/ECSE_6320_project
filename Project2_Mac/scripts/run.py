"""Run targeted sweeps sequentially; never overwrite an earlier run."""
import csv
import datetime
import json
import os
from pathlib import Path
import random
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
RUN = RAW / datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
RUN.mkdir(parents=True)
BENCH = ROOT / 'build' / 'bench'


def command(args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=60)
    return {'command': args, 'exit_status': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr}


def snapshot():
    commands = [
        ['sysctl', 'hw.model', 'machdep.cpu.brand_string', 'hw.memsize', 'hw.pagesize',
         'hw.cachelinesize', 'hw.physicalcpu', 'hw.logicalcpu', 'hw.perflevel0', 'hw.perflevel1', 'vm.swapusage'],
        ['sw_vers'], ['uname', '-srm'], ['clang', '--version'], ['pmset', '-g', 'custom'],
        ['pmset', '-g', 'batt'], ['pmset', '-g', 'therm'], ['vm_stat'], ['xcode-select', '-p'],
    ]
    return [command(c) for c in commands]


start = time.monotonic()
(RUN / 'system-before.json').write_text(json.dumps(snapshot(), indent=2))
trials = []


def add(experiment, mode, size, stride, pattern='random', reads=100, seconds=0.18, **extra):
    for trial in range(1, 4):
        trials.append(dict(experiment=experiment, mode=mode, bytes=size, stride=stride,
                           pattern=pattern, reads=reads, duration=seconds, trial=trial, **extra))


KiB, MiB = 1024, 1024 ** 2
for size in [16*KiB, 64*KiB, 128*KiB, 256*KiB, MiB, 4*MiB, 8*MiB, 16*MiB,
             32*MiB, 64*MiB, 256*MiB, 512*MiB]:
    add('working_set', 'chase', size, 128)
for size in [32*KiB, 128*KiB, MiB, 16*MiB, 256*MiB, 512*MiB]:
    add('stream_size', 'stream', size, 8, 'sequential')
for stride in [64, 128, 256, 1024]:
    for pattern in ['sequential', 'random']:
        add('pattern_latency', 'chase', 256*MiB, stride, pattern)
        add('pattern_bandwidth', 'stream', 256*MiB, stride, pattern)
for reads in [100, 70, 50, 0]:
    add('rw_bandwidth', 'stream', 256*MiB, 8, 'sequential', reads)
    add('rw_latency', 'loaded', 256*MiB, 128, reads=reads, seconds=0.4, workers=4)
for workers in [0, 1, 2, 4, 7, 11]:
    add('intensity', 'loaded', 256*MiB, 128, seconds=0.4, workers=workers)
page = os.sysconf('SC_PAGE_SIZE')
for nodes in [64, 256, 1024, 4096, 8192]:
    add('page_locality', 'chase', nodes*128, 128, nodes=nodes, layout='compact')
    add('page_locality', 'pages', nodes*page, page, nodes=nodes, layout='spread')
for elements, stride in [(4096, 8), (2**20, 8), (2**23, 8), (2**23, 128)]:
    add('kernel', 'kernel', elements*24, stride, 'sequential')

# Shuffle with a recorded seed to reduce systematic drift across footprint/load order.
random.Random(20261023).shuffle(trials)
(RUN / 'plan.json').write_text(json.dumps(trials, indent=2))
rows = []
with (RUN / 'measurements.jsonl').open('w') as raw:
    for index, trial in enumerate(trials, 1):
        seed = 42 + trial['trial']
        if trial['mode'] == 'loaded':
            args = [BENCH, 'loaded', trial['workers'], trial['reads'], trial['duration'], seed]
        elif trial['mode'] == 'kernel':
            args = [BENCH, 'kernel', trial['bytes'], trial['stride'], trial['duration']]
        else:
            args = [BENCH, trial['mode'], trial['bytes'], trial['stride'], trial['pattern'],
                    trial['reads'], trial['duration'], seed]
        args = [str(a) for a in args]
        result = subprocess.run(args, capture_output=True, text=True, timeout=45, check=True)
        measured = json.loads(result.stdout)
        assert measured['operations'] > 0 and measured['seconds'] >= trial['duration']
        row = dict(trial, **{k: v for k, v in measured.items() if k not in trial},
                   command=args, seed=seed, stderr=result.stderr)
        # Measured times/metrics override planned fields only where appropriate.
        row.update(measured)
        row['experiment'] = trial['experiment']
        row['pattern'] = trial['pattern']
        raw.write(json.dumps(row) + '\n'); raw.flush()
        rows.append(row)
        if index % 20 == 0:
            print(f'{index}/{len(trials)} measurements; {time.monotonic()-start:.0f}s elapsed', flush=True)
        time.sleep(0.1)

(RUN / 'system-after.json').write_text(json.dumps(snapshot(), indent=2))
fields = [k for k in rows[0] if k not in ['command', 'stderr']]
fields += sorted({k for r in rows for k in r} - set(fields) - {'command', 'stderr'})
with (RUN / 'measurements.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    writer.writeheader(); writer.writerows(rows)
(RUN / 'run-info.json').write_text(json.dumps({'duration_seconds': time.monotonic()-start,
                                               'trials': len(rows), 'order_seed': 20261023}, indent=2))
(RAW / 'latest.txt').write_text(RUN.name + '\n')
print(f'Completed {len(rows)} measurements in {time.monotonic()-start:.1f}s: {RUN}')

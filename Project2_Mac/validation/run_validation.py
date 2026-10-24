"""Small feasibility check, not the project's final benchmark methodology."""
import datetime
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent
results = root / ('results-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
results.mkdir()
env = dict(os.environ, DEVELOPER_DIR='/Applications/Xcode.app/Contents/Developer')
subprocess.run(['clang', '-O2', '-Wall', '-Wextra', '-Werror',
                str(root / 'memory_probe.c'), '-o', str(root / 'memory_probe')], check=True)
subprocess.run([sys.executable, str(root / 'make_template.py')], check=True)
summary = {'native_trials': [], 'miss_counter_validation': 'NOT PASSED'}
for mode in ['cache', 'memory', 'tlb-local', 'tlb-spread']:
    for trial in range(1, 4):
        run = subprocess.run([str(root / 'memory_probe'), mode], check=True,
                             capture_output=True, text=True, timeout=15)
        (results / f'{mode}-{trial}.txt').write_text(run.stdout)
        values = dict(item.split('=', 1) for item in run.stdout.split())
        summary['native_trials'].append(dict(values, trial=trial))
        print(run.stdout.strip(), flush=True)
medians = {mode: statistics.median(float(t['ns_per_load']) for t in summary['native_trials']
                                  if t['mode'] == mode)
           for mode in ['cache', 'memory', 'tlb-local', 'tlb-spread']}
summary['median_ns_per_load'] = medians
assert medians['cache'] < medians['memory'], 'Cache/large-footprint sanity check failed'
trace = results / 'memory.trace'
record = subprocess.run(['xcrun', 'xctrace', 'record', '--template',
                         str(root / 'Memory Counters.tracetemplate'), '--output', str(trace),
                         '--time-limit', '10s', '--target-stdout', '-', '--launch', '--',
                         str(root / 'memory_probe'), 'memory'],
                        env=env, capture_output=True, text=True, timeout=30)
(results / 'record.log').write_text(record.stdout + record.stderr)
summary['record_exit_status'] = record.returncode
if record.returncode == 0:
    export = subprocess.run(['xcrun', 'xctrace', 'export', '--input', str(trace), '--toc'],
                            env=env, capture_output=True, text=True, timeout=30)
    (results / 'export.xml').write_text(export.stdout)
    (results / 'export.log').write_text(export.stderr)
    summary['export_exit_status'] = export.returncode
    if export.returncode == 0:
        tables = ET.fromstring(export.stdout).findall('.//table')
        summary['counter_tables'] = [t.attrib for t in tables if 'counter' in t.get('schema', '')]
        summary['miss_counter_validation'] = 'EXPORT WORKS; EVENT VALUES STILL NEED CHECKING'
    else:
        summary['blocker'] = export.stderr.strip()
(results / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
print(f'Evidence: {results}')
sys.exit(0 if summary.get('export_exit_status') == 0 else 1)

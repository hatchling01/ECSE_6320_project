"""Collect the exportable guided stall metrics; do not call them miss counts."""
import json
import os
from pathlib import Path
import plistlib
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
RUN = RAW / (RAW / 'latest.txt').read_text().strip()
OUT = RUN / 'counters'
OUT.mkdir(exist_ok=True)
ENV = dict(os.environ, DEVELOPER_DIR='/Applications/Xcode.app/Contents/Developer')
SOURCE = Path(ENV['DEVELOPER_DIR']).parent / 'Applications/Instruments.app/Contents/Resources/templates/CPU Counters.tracetemplate'
LABELS = ['executing_pct', 'execution_latency_pct', 'critical_l1d_pct',
          'critical_l1d_while_executing_pct', 'noncritical_l1d_pct']


def resolve_elements(root):
    references = {e.attrib['id']: e for e in root.iter() if 'id' in e.attrib}

    def resolve(e):
        return references[e.attrib['ref']] if 'ref' in e.attrib else e
    return resolve


def measurement_interval(xml):
    root = ET.fromstring(xml)
    resolve = resolve_elements(root)
    begins = {}
    for row in root.findall('.//row'):
        name, subsystem = row.find('signpost-name'), row.find('subsystem')
        if name is None or subsystem is None:
            continue
        if resolve(name).text != 'Measurement' or resolve(subsystem).text != 'edu.ecse.memory':
            continue
        key = (resolve(row.find('process')).get('fmt'), resolve(row.find('os-signpost-identifier')).text)
        timestamp = int(resolve(row.find('event-time')).text)
        event = resolve(row.find('event-type')).text
        if event == 'Begin':
            begins[key] = timestamp
        elif event == 'End' and key in begins:
            assert timestamp > begins[key]
            return begins[key], timestamp
    raise ValueError('No Measurement signpost interval found; refuse to include initialization')


def summarize(xml, interval):
    root = ET.fromstring(xml)
    resolve = resolve_elements(root)
    totals = [0.0] * 5
    total = p_core = e_core = 0
    rows = 0
    for row in root.findall('.//row'):
        timestamp = row.find('start-time')
        duration = row.find('duration')
        values = row.find('uint64-array')
        core = row.find('core')
        if any(e is None for e in [timestamp, duration, values, core]):
            continue
        start = int(resolve(timestamp).text)
        end = start + int(resolve(duration).text)
        weight = max(0, min(end, interval[1]) - max(start, interval[0]))
        if not weight:
            continue
        v = [int(n) for n in resolve(values).text.split()]
        assert len(v) == 5 and 9900 <= sum(v) <= 10100, v
        for i, value in enumerate(v):
            totals[i] += weight * value / 100.0
        total += weight
        name = resolve(core).get('fmt', '')
        p_core += weight if 'P Core' in name else 0
        e_core += weight if 'E Core' in name else 0
        rows += 1
    assert rows > 100 and total > 0, 'Not enough measured-region samples'
    return dict(zip(LABELS, [v / total for v in totals]), sample_rows=rows,
                sampled_seconds=total / 1e9, p_core_pct=p_core / total * 100,
                e_core_pct=e_core / total * 100)


def xctrace(args, timeout=40):
    result = subprocess.run(['xcrun', 'xctrace', *args], env=ENV,
                            capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'xctrace returned {result.returncode}: {result.stderr}\n{result.stdout[:1000]}')
    return result


template = plistlib.loads(SOURCE.read_bytes())
changed = 0
for i, obj in enumerate(template['$objects']):
    if not isinstance(obj, bytes):
        continue
    try:
        options = json.loads(obj)
    except (ValueError, UnicodeDecodeError):
        continue
    if 'selectedCountingMode' in options:
        options['selectedCountingMode'] = {'analysisMode': 'bottleneck', 'countingMode': 'processing'}
        options['selectedCountingModeDisplayName'] = 'Instruction Processing'
        template['$objects'][i] = json.dumps(options).encode()
        changed += 1
assert changed == 1
# shortcut: the installed Xcode 26 guided-template archive is private; revalidate after updates.
path = OUT / 'Instruction Processing.tracetemplate'
path.write_bytes(plistlib.dumps(template, fmt=plistlib.FMT_BINARY))
cases = [
    ('kernel_small', ['kernel', 4096*24, 8, 2]),
    ('kernel_medium', ['kernel', (2**20)*24, 8, 2]),
    ('kernel_large', ['kernel', (2**23)*24, 8, 2]),
    ('kernel_sparse', ['kernel', (2**23)*24, 128, 2]),
    ('pages_compact', ['chase', 8192*128, 128, 'random', 100, 2, 43]),
    ('pages_spread', ['pages', 8192*os.sysconf('SC_PAGE_SIZE'), os.sysconf('SC_PAGE_SIZE'), 'random', 100, 2, 43]),
]
summary_path = OUT / 'summary.json'
summary = json.loads(summary_path.read_text()) if summary_path.exists() else []
try:
    for name, args in cases:
        for trial in range(1, 4):
            if any(r['case'] == name and r['trial'] == trial for r in summary):
                continue
            prefix = OUT / f'{name}-{trial}'
            trace = prefix.with_suffix('.trace')
            record_log = prefix.with_suffix('.record.log')
            if not trace.exists():
                record = xctrace(['record', '--template', str(path), '--output', str(trace),
                                  '--time-limit', '10s', '--target-stdout', '-', '--launch', '--',
                                  str(ROOT / 'build' / 'bench'), *map(str, args)])
                record_log.write_text(record.stdout + record.stderr)
            measured = next(json.loads(line) for line in record_log.read_text().splitlines() if line.startswith('{'))
            toc = xctrace(['export', '--input', str(trace), '--toc']).stdout
            prefix.with_suffix('.toc.xml').write_text(toc)
            # Keep the event/metric legend as evidence for interpreting basis-point arrays.
            assert 'Critical L1D Cache Miss' in toc and 'Executing' in toc
            exports = {}
            for schema in ['os-signpost', 'CounterMetricByThread']:
                xml = xctrace(['export', '--input', str(trace), '--xpath',
                               f'/trace-toc/run[@number="1"]/data/table[@schema="{schema}"]']).stdout
                prefix.with_suffix(f'.{schema}.xml').write_text(xml)
                exports[schema] = xml
            interval = measurement_interval(exports['os-signpost'])
            metrics = summarize(exports['CounterMetricByThread'], interval)
            summary.append(dict(case=name, trial=trial, **measured, **metrics,
                                measurement_start_ns=interval[0], measurement_end_ns=interval[1]))
            (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
            print(f'{name} trial {trial}: critical L1D stall {metrics["critical_l1d_pct"]:.1f}%, P-core {metrics["p_core_pct"]:.1f}%', flush=True)
except (RuntimeError, ValueError, AssertionError, subprocess.TimeoutExpired) as exc:
    (OUT / 'failure.txt').write_text(str(exc) + '\n')
    raise

# Parser sanity checks against a synthetic measured interval and reference reuse.
fixture = '''<result><row><start-time id="t">10</start-time><duration id="d">10</duration>
<core id="c" fmt="CPU 1 (P Core)">1</core><uint64-array id="v">1000 2000 3000 2000 2000</uint64-array></row>'''
fixture += ''.join('<row><start-time ref="t"/><duration ref="d"/><core ref="c"/><uint64-array ref="v"/></row>' for _ in range(101)) + '</result>'
test = summarize(fixture, (10, 20))
assert test['critical_l1d_pct'] == 30 and test['p_core_pct'] == 100
print(f'Collected {len(summary)} counter profiles: {OUT}')
(OUT / 'status.json').write_text(json.dumps({'status':'complete', 'profiles':len(summary),
                                            'scope':'guided L1D stall percentages; no raw data-TLB counts'}, indent=2))
if (OUT / 'failure.txt').exists() and not (OUT / 'recovered-parser-failure.txt').exists():
    (OUT / 'failure.txt').rename(OUT / 'recovered-parser-failure.txt')

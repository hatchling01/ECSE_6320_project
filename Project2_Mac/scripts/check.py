"""Small end-to-end checks of outputs and benchmark boundary handling."""
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
bench = ROOT/'build'/'bench'
subprocess.run([str(bench), 'selftest'], check=True, capture_output=True)
for args in [[], ['loaded','12','100','.01','42'], ['loaded','1','71','.01','42'],
             ['chase','1024','0','random','100','.01','42'],
             ['kernel','100','8','.01'], ['stream','1024','8','random','100','nan','42']]:
    result = subprocess.run([str(bench),*args], capture_output=True, timeout=5)
    assert result.returncode != 0, args
raw = ROOT/'data'/'raw'
run = raw/(raw/'latest.txt').read_text().strip()
rows = [json.loads(line) for line in (run/'measurements.jsonl').read_text().splitlines()]
assert len(rows) == 186
groups = {}
for row in rows:
    assert row['operations'] > 0 and row['seconds'] >= row['duration']
    assert math.isclose(row['ns_per_op'], row['seconds']*1e9/row['operations'], rel_tol=2e-5)
    payload = 24 if row['experiment']=='kernel' else 8
    assert math.isclose(row['useful_GB_s'], row['operations']*payload/row['seconds']/1e9,
                        rel_tol=2e-5,abs_tol=1e-6)
    assert row['background_GB_s'] >= 0 and row['probe_ns'] >= 0
    if row['experiment']=='intensity' and row['workers']==0:
        assert row['background_GB_s']==0
    key=tuple(row.get(k,'') for k in ['experiment','bytes','stride','pattern','read_percent','workers','nodes','layout'])
    groups.setdefault(key,[]).append(row['trial'])
assert len(groups)==62 and all(sorted(trials)==[1,2,3] for trials in groups.values())
profiles=json.loads((run/'counters'/'summary.json').read_text())
assert len(profiles)==18
for profile in profiles:
    assert profile['sample_rows']>100
    assert 1.5 < profile['sampled_seconds'] < 2.2
    assert abs(profile['p_core_pct']+profile['e_core_pct']-100)<.1
    metrics=['executing_pct','execution_latency_pct','critical_l1d_pct',
             'critical_l1d_while_executing_pct','noncritical_l1d_pct']
    assert 99 <= sum(profile[m] for m in metrics) <= 101
    assert profile['measurement_end_ns'] > profile['measurement_start_ns']
for filename in ['working_set','patterns','read_write','intensity','page_locality','pitfall','kernel_counters']:
    for extension in ['png','pdf']:
        assert (ROOT/'plots'/f'{filename}.{extension}').stat().st_size > 1000
assert (ROOT/'report'/'REPORT.md').stat().st_size>1000
print(f'PASS: native self-checks, six invalid-input cases, {len(rows)} timing rows, '
      f'{len(groups)} complete settings, {len(profiles)} signpost-filtered counter profiles, seven plot pairs.')

"""Copy the installed Instruments template; do not modify the Xcode installation."""
import base64
import json
import pathlib
import plistlib

source = pathlib.Path('/Applications/Xcode.app/Contents/Applications/Instruments.app/Contents/Resources/templates/CPU Counters.tracetemplate')
# shortcut: this private archive layout targets Xcode 26, revalidate after an Xcode update.
events = ['FIXED_CYCLES', 'FIXED_INSTRUCTIONS', 'L1D_CACHE_MISS_LD_NONSPEC',
          'L1D_TLB_MISS_NONSPEC', 'L2_TLB_MISS_DATA']
with source.open('rb') as f:
    template = plistlib.load(f)
# Only keep the counter instrument; the stock template also adds several profilers.
template['$objects'][template['$top']['$0'].data] = 1
for key in ['$3', '$4', '$5', '$6', '$7', '$8']:
    del template['$top'][key]
changed = 0
for i, obj in enumerate(template['$objects']):
    if not isinstance(obj, bytes):
        continue
    try:
        options = json.loads(obj)
    except (ValueError, UnicodeDecodeError):
        continue
    if 'allEventsAndFormulas' not in options:
        continue
    options['configurationType'] = {'manual': {}}
    options['allEventsAndFormulas'] = []
    for event in events:
        archive = {
            '$version': 100000, '$archiver': 'NSKeyedArchiver',
            '$top': {'root': plistlib.UID(1)},
            '$objects': ['$null', {
                '$class': plistlib.UID(3),
                '_aliasOrMnemonic': plistlib.UID(4),
                '_mnemonic': plistlib.UID(2),
                '_displayName': plistlib.UID(2),
                '_formulaText': plistlib.UID(0),
                '_formulaEvaluator': plistlib.UID(0),
                '_explanation': plistlib.UID(2),
                '_beingEdited': False,
            }, event, {
                '$classname': 'XRCountersSetupEventOrFormula',
                '$classes': ['XRCountersSetupEventOrFormula', 'NSObject'],
            }, {'FIXED_CYCLES': 'Cycles', 'FIXED_INSTRUCTIONS': 'Instructions'}.get(event, event)],
        }
        options['allEventsAndFormulas'].append(base64.b64encode(
            plistlib.dumps(archive, fmt=plistlib.FMT_BINARY)).decode())
    template['$objects'][i] = json.dumps(options).encode()
    changed += 1
assert changed == 1, f'Expected one counter configuration, found {changed}'
destination = pathlib.Path(__file__).with_name('Memory Counters.tracetemplate')
with destination.open('wb') as f:
    plistlib.dump(template, f, fmt=plistlib.FMT_BINARY)
print(destination)

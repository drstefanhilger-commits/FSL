#!/usr/bin/env python3
"""Convert a PX4 build's parameters.json (firmware parameter metadata) into the
DB format used by check_params.py.

Usage: fw_paramdb.py <build_dir>/parameters.json <out.json>
"""
import json, sys

if len(sys.argv) != 3:
    sys.exit(__doc__)
j = json.load(open(sys.argv[1]))
db = {}
for p in j['parameters']:
    d = {'type': 'float' if p['type'] == 'Float' else 'int32', 'src': 'fw:' + p.get('group', '')}
    if 'min' in p: d['min'] = p['min']
    if 'max' in p: d['max'] = p['max']
    if 'values' in p: d['values'] = {str(v['value']): v['description'] for v in p['values']}
    if 'bitmask' in p: d['bits'] = {str(v['index']): v['description'] for v in p['bitmask']}
    if p.get('rebootRequired'): d['reboot'] = True
    db[p['name']] = d
json.dump(db, open(sys.argv[2], 'w'), indent=1, sort_keys=True)
print(len(db), 'parameters in firmware metadata')

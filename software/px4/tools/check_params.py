#!/usr/bin/env python3
"""Validate QGC .params files against a PX4 parameter DB (name, type, range, enum/bitmask).

Usage: check_params.py <db.json> <file.params> [...]
Exit code 1 if any error was found.
"""
import json, sys
if len(sys.argv) < 3:
    sys.exit(__doc__)
db = json.load(open(sys.argv[1]))
errors = 0; seen = {}
for path in sys.argv[2:]:
    for ln, line in enumerate(open(path), 1):
        if not line.strip() or line.startswith('#'): continue
        parts = line.rstrip('\n').split('\t')
        if len(parts) != 5:
            print(f'{path}:{ln}: expected 5 TAB fields, got {len(parts)}: {line!r}'); errors += 1; continue
        vid, cid, name, val, typ = parts
        if (path, name) in seen:
            print(f'{path}:{ln}: duplicate {name} (also line {seen[(path,name)]})'); errors += 1
        seen[(path, name)] = ln
        d = db.get(name)
        if d is None:
            print(f'{path}:{ln}: UNKNOWN parameter {name}'); errors += 1; continue
        want = '6' if d['type'] == 'int32' else '9'
        if typ != want:
            print(f'{path}:{ln}: {name} type {typ}, PX4 defines {d["type"]} ({want})'); errors += 1
        v = float(val)
        if d['type'] == 'int32' and v != int(v):
            print(f'{path}:{ln}: {name} int param with non-integer value {val}'); errors += 1
        if d.get('min') is not None and v < float(d['min']):
            print(f'{path}:{ln}: {name}={val} below min {d["min"]}'); errors += 1
        if d.get('max') is not None and v > float(d['max']):
            print(f'{path}:{ln}: {name}={val} above max {d["max"]}'); errors += 1
        if d.get('values') and str(int(v)) not in d['values']:
            print(f'{path}:{ln}: {name}={val} not an allowed enum value {sorted(d["values"])}'); errors += 1
        if d.get('bits'):
            maxmask = sum(1 << int(b) for b in d['bits'])
            if int(v) & ~maxmask:
                print(f'{path}:{ln}: {name}={val} sets undefined bits'); errors += 1
        if d.get('boolean') and v not in (0, 1):
            print(f'{path}:{ln}: {name}={val} boolean must be 0/1'); errors += 1
        note = ' (reboot required)' if d.get('reboot') else ''
        print(f'ok  {name:20s} = {val:>8s}  [{d["src"]}]{note}')
print('ERRORS:', errors)
sys.exit(1 if errors else 0)

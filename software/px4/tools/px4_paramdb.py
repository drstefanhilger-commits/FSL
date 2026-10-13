#!/usr/bin/env python3
"""Extract PX4 parameter definitions (name, type, min, max, default, enum values)
from PX4 source (*_params.c / parameters.c PARAM_DEFINE_* and *.yaml).

Usage: px4_paramdb.py <PX4-Autopilot>/src <out.json>   (needs PyYAML)
"""
import re, sys, json, os, yaml

if len(sys.argv) != 3:
    sys.exit(__doc__)
root = sys.argv[1]
db = {}

def add(name, **kw):
    # A parameter can be defined in several places (e.g. PWM_MAIN_TIMx in pwm_out
    # with DShot and in px4io without). Which one a board compiles depends on the
    # board, so merge leniently: union of enum values/bits, widest min/max.
    # The strict per-board check is fw_paramdb.py (build metadata).
    d = db.setdefault(name, {})
    for k, v in kw.items():
        if v is None:
            continue
        if k in ('values', 'bits') and isinstance(d.get(k), dict):
            d[k] = {**d[k], **v}
        elif k == 'min' and d.get('min') is not None:
            d['min'] = min(float(d['min']), float(v))
        elif k == 'max' and d.get('max') is not None:
            d['max'] = max(float(d['max']), float(v))
        else:
            d[k] = v

pd = re.compile(r'/\*\*((?:(?!\*/).)*?)\*/\s*PARAM_DEFINE_(INT32|FLOAT)\(\s*(\w+)\s*,\s*([^)]*)\)', re.S)
for dp, dn, fn in os.walk(root):
    for f in fn:
        p = os.path.join(dp, f)
        if f.endswith('.c') or f.endswith('.h'):
            try: s = open(p, errors='ignore').read()
            except: continue
            if 'PARAM_DEFINE_' not in s: continue
            for m in pd.finditer(s):
                doc, typ, name, default = m.groups()
                mn = re.search(r'@min\s+(\S+)', doc); mx = re.search(r'@max\s+(\S+)', doc)
                vals = dict(re.findall(r'@value\s+(-?\d+)\s+(.*)', doc))
                bits = dict(re.findall(r'@bit\s+(\d+)\s+(.*)', doc))
                add(name, type='float' if typ=='FLOAT' else 'int32',
                    min=float(mn.group(1)) if mn else None, max=float(mx.group(1)) if mx else None,
                    default=default.strip().rstrip('f'), values=vals or None, bits=bits or None,
                    boolean='@boolean' in doc or None, src=os.path.relpath(p, root),
                    reboot='@reboot_required true' in doc or None)
            # params without doc comment
            for m in re.finditer(r'PARAM_DEFINE_(INT32|FLOAT)\(\s*(\w+)\s*,', s):
                if m.group(2) not in db:
                    add(m.group(2), type='float' if m.group(1)=='FLOAT' else 'int32', src=os.path.relpath(p, root))
        elif f.endswith('.yaml'):
            try: y = yaml.safe_load(open(p))
            except Exception as e:
                print('YAML fail', p, e, file=sys.stderr); continue
            if not y: continue
            for sc in y.get('serial_config', []) or []:
                pc = sc.get('port_config_param', {})
                n = pc.get('name')
                if n:
                    ninst = sc.get('num_instances', 1); st = sc.get('instance_start', 0)
                    for i in range(st, st+ninst):
                        add(n.replace('${i}', str(i)), type='int32', serial_config=True, src=os.path.relpath(p, root))
            for grp in y.get('parameters', []) or []:
                for name, d in (grp.get('definitions') or {}).items():
                    ninst = d.get('num_instances', 1); start = d.get('instance_start', 0)
                    names = [name] if '${i}' not in name else [name.replace('${i}', str(i)) for i in range(start, start+ninst)]
                    t = d.get('type')
                    for n in names:
                        add(n, type='float' if t=='float' else 'int32', min=d.get('min'), max=d.get('max'),
                            default=d.get('default'), values={str(k):v for k,v in (d.get('values') or {}).items()} or None,
                            bits={str(k):v for k,v in (d.get('bit') or {}).items()} or None,
                            boolean=(t=='boolean') or None, src=os.path.relpath(p, root),
                            reboot=d.get('reboot_required'))
            ao = y.get('actuator_output')
            if ao:
                for g in ao.get('output_groups', []):
                    pref = g.get('param_prefix', '')
                    for pref_r in ([pref.replace('${PWM_MAIN_OR_AUX}', 'PWM_MAIN'), pref.replace('${PWM_MAIN_OR_AUX}', 'PWM_AUX')] if '${' in pref else [pref]):
                        nch = g.get('num_channels', 16)
                        for i in range(1, nch+1):
                            for suf in ('FUNC', 'DIS', 'MIN', 'MAX', 'FAIL', 'CENT'):
                                add(f'{pref_r}_{suf}{i}', type='int32', src=os.path.relpath(p, root))
                        add(f'{pref_r}_REV', type='int32', src=os.path.relpath(p, root))
                        if g.get('pwm_timer_param'):
                            tp = g['pwm_timer_param']
                            for i in range(0, 8):
                                add(f'{pref_r}_TIM{i}', type='int32', values={str(k):v for k,v in tp.get('values', {}).items()}, src=os.path.relpath(p, root))
json.dump(db, open(sys.argv[2], 'w'), indent=1, sort_keys=True)
print(len(db), 'params')

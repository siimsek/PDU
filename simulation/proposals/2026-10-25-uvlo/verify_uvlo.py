#!/usr/bin/env python3
"""Independent verifier for WP2 2026-10-25-uvlo. Parses ngspice logs (results/logs/), applies the acceptance rules
below (limits are FIXED constants, never relaxed), checks the known-failing regressions, records SHA-256 of every
input and the git HEAD. Exit: 0 = all acceptance PASS and all regressions FAIL as expected; 1 = any acceptance FAIL
or a regression that unexpectedly passes, or ANY non-regression case (PASS or INFO) breaching a hard limit
(O1 <= 12.0 V, stable-window bus/O1 <= 11.1605 V) or missing its hard-limit measurement, or an invalid case
classification; 2 = any deck missing/incomplete (acceptance cannot be decided) OR the logs are not bound to a fresh,
complete, successful run (results/run-manifest.json: case table SHA-256, deck set, deck/log SHA-256, rc == 0, completed,
optional --run-id / env UVLO_RUN_ID; with --run-id the manifest git HEAD must equal the current HEAD, otherwise the
package inputs must be unchanged between the manifest HEAD and the current HEAD).
Tur-2 (ChatGPT review 6395614957): restart-delay (60 ms) and V_f (18.0 V) checks are fail-closed (a missing / failed /
non-finite measurement is an error); dip restarts are gated with the same 60 ms after the last VIN-OK (OUTA) rise;
the PROVISIONAL WP3 R-DIP screen (review proposal UVLO-06, not a requirement) is reported per dip case and does NOT
change the exit code.
Tur-3 (ChatGPT combined review 6396616875): MANDATORY gates apply to every non-regression case, PASS *and* INFO:
  (M1) every EN rise EN_R1..EN_R4 / EN_RLAST must be >= 60 ms after the latest VIN-OK (OUTA) rise before it (after the
       start of the dip that precedes it, for dip kinds) - not conditional on a measured EN_F1; missing / failed /
       non-finite measurements, > 5 OUTA rises before an EN rise or > 4 EN rises are errors (fail-closed);
  (M2) V_f: VIN_AT_SHUTDOWN >= 18.0 V whenever EN fell (ramp_down / mb_hold), fail-closed.
The case kind is validated before the regression classification; runner_exit_code must be exactly 0; ngspice
'nan' / 'inf' / '-inf' values are parsed and treated as non-finite (fail-closed), never crash the verifier.
Tur-4 (ChatGPT combined review 6398375361, WP2 part):
  (M0) every regime metric of every stable window (and RUN_VIN_MIN when V_f is set, INP_MIN_AFTER_ON for seq) must be
       present, not 'failed' and finite - for PASS *and* INFO cases (regime() / regime_seq() use fin());
  (S)  seq cases are STIMULUS-ONLY benches (ideal DRIVE source, no UVLO block, no measured OUTA->EN edge): the configured
       DRIVE delay is schema-validated (real, finite, >= T_SEQ_MIN, inclusive) for every non-regression seq case and the
       evidence is labelled info.seq_evidence = 'stimulus-only';
  (M3) when the case requests en_force_max: every VIN-OK loss (OUTA fall) while EN is high must be followed by an EN fall
       within en_force_max (1 us); (M4) when the case requests vgs_at_en_min: VGS >= vgs_at_en_min at every EN rise.
       Both fail-closed. R-DIP report: event = rode_through | restart.
NOTE: GitHub Actions (workflow proposal-ngspice) is DISABLED by the user since 2026-10-25 13:3x TSI; CI gating is not active.
The evidence is local runs (box ngspice) with the run manifest + SHA-256 recorded in results/.
Usage: python3 verify_uvlo.py [--run-id ID]
"""
import json, re, sys, hashlib, subprocess, math, os
from pathlib import Path
HERE = Path(__file__).absolute().parent
O1_PEAK_MAX = 12.0          # O1 instantaneous peak (hard)
BUS_NORMAL_MAX = 11.1605    # normal-regime bus max (hard)
V_FALL_MIN = 18.0           # over-discharge: buck must be off before VIN < 18.0 V (3.0 V/cell under load, see REQUIREMENTS)
T_SEQ_MIN = 0.060           # buck restart delay after VIN OK >= 60 ms (> TDRV_EN worst 50.8 ms + margin)
RAW_REG = (10.8, BUS_NORMAL_MAX)
# PROVISIONAL WP3 R-DIP screen (ChatGPT review 6395614957 UVLO-06 proposal; report-only, NOT an acceptance limit)
RDIP_PEAK_MAX = 11.50       # bus peak after a dip
RDIP_T_ABOVE_MAX = 1.0e-3   # integrated time above BUS_NORMAL_MAX
RDIP_RETURN_MAX = 5.0e-3    # last fall through BUS_NORMAL_MAX no later than dip end (VIN restoration) + 5 ms
REG_OK = dict(en=2.0, vgs=6.0, inp=2.5)
REGIME_METRICS = ('BUS_MAX', 'O1_MAX', 'RAW_AVG', 'EN_MIN', 'VGS_MIN', 'INP_MIN')
SEQ_METRICS = ('RUN_BUS_MAX', 'RUN_O1_MAX', 'RUN_RAW_AVG', 'RUN_VGS_MIN', 'RUN_INP_MIN')   # seq bench: no EN_BUCK node
OUTA_FALLS = ('OUTA_F1', 'OUTA_F2')
EN_FALLS = ('EN_F1', 'EN_F2', 'EN_F3', 'EN_F4')

def parse(log):
    t = log.read_text(errors='replace')
    m = {}
    # Tur-3 T3-06: accept nan / inf / -inf tokens (ngspice prints them); non-finite values are rejected by fin()
    for k, v in re.findall(r'^([a-z0-9_]+)\s+=\s+([-+]?(?:nan|inf(?:inity)?|[0-9.]+(?:[eE][-+]?[0-9]+)?))', t, re.M | re.I):
        try:
            m[k.upper()] = float(v)
        except ValueError:
            m[k.upper()] = float('nan')
    failed = set(k.upper() for k in re.findall(r'\.meas tran (\S+) .* failed!', t))
    # an aborted transient (e.g. 'Timestep too small') still prints 'Total analysis time': treat it as NOT done
    done = 'Total analysis time' in t and 'simulation(s) aborted' not in t and 'Timestep too small' not in t
    return m, failed, done, t

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def regime(m, w, f):
    """normal regime in window w: EN high, FETs enhanced, comparator high, RAW regulated, bus/O1 below the normal limit."""
    # Tur-4 T4-01: fail-closed via fin() (missing / ngspice 'failed' / NaN / +-Inf are errors, never pass a comparison)
    req = [f'{w}_{q}' for q in REGIME_METRICS]
    bad = [k for k in req if fin(m, f, k) is None]
    if bad:
        return [f'window {w}: {k} missing/failed/non-finite' for k in bad]
    e = []
    if m[f'{w}_EN_MIN'] < REG_OK['en']: e.append(f'{w}: EN low ({m[w+"_EN_MIN"]:.3f} V) -> not running')
    if m[f'{w}_VGS_MIN'] < REG_OK['vgs']: e.append(f'{w}: OVP FET not enhanced (VGS min {m[w+"_VGS_MIN"]:.3f} V)')
    if m[f'{w}_INP_MIN'] < REG_OK['inp']: e.append(f'{w}: OVP comparator low')
    if not (RAW_REG[0] <= m[f'{w}_RAW_AVG'] <= RAW_REG[1]): e.append(f'{w}: RAW avg {m[w+"_RAW_AVG"]:.4f} V not regulated')
    if m[f'{w}_BUS_MAX'] > BUS_NORMAL_MAX: e.append(f'{w}: bus max {m[w+"_BUS_MAX"]:.5f} > {BUS_NORMAL_MAX}')
    if m[f'{w}_O1_MAX'] > BUS_NORMAL_MAX: e.append(f'{w}: O1 max {m[w+"_O1_MAX"]:.5f} > {BUS_NORMAL_MAX}')
    return e

# Hard limits H1/H2 are enforced for EVERY non-regression case, independent of its PASS/INFO classification
# (ChatGPT review 6395284882, WP2 Tur-1 P0). Stable (normal-regime) windows defined per case kind:
HARD_WINDOWS = {'start': ('RUN',), 'ramp_up': ('RUN',), 'hotplug': ('RUN',), 'rsweep': ('RUN',), 'seq': ('RUN',),
                'ramp_down': ('PRE',), 'mb_hold': ('PRE',), 'dip': ('PRE', 'POST'), 'dip2': ('PRE', 'POST')}
DIP_KINDS = ('dip', 'dip2')
OUTA_RISES = ('OUTA_R1', 'OUTA_R2', 'OUTA_R3', 'OUTA_R4', 'OUTA_R5', 'OUTA_RLAST')
EN_RISES = ('EN_R1', 'EN_R2', 'EN_R3', 'EN_R4', 'EN_RLAST')
VALID_EXPECT = ('PASS', 'INFO', 'FAIL')

def hard_limit_errors(c, m):
    """H1: O1_GLOBAL_PEAK <= 12.0 V; H2: bus and O1 max <= 11.1605 V in every stable window of the case kind.
    A missing or non-finite hard-limit measurement is an error (fail-closed)."""
    e = []
    v = m.get('O1_GLOBAL_PEAK')
    if v is None or not math.isfinite(v): e.append('HARD H1: O1_GLOBAL_PEAK missing/non-finite')
    elif v > O1_PEAK_MAX: e.append(f'HARD H1: O1 peak {v:.5f} > {O1_PEAK_MAX}')
    wins = HARD_WINDOWS.get(c.get('kind'))
    if wins is None:
        e.append(f'HARD: unknown case kind {c.get("kind")!r} (no stable windows defined)')
        return e
    for w in wins:
        for q in ('BUS_MAX', 'O1_MAX'):
            v = m.get(f'{w}_{q}')
            if v is None or not math.isfinite(v): e.append(f'HARD H2: {w}_{q} missing/non-finite')
            elif v > BUS_NORMAL_MAX: e.append(f'HARD H2: {w}_{q} {v:.5f} > {BUS_NORMAL_MAX}')
    return e

def fin(m, failed, k):
    """value of measurement k if present, not 'failed!' and finite, else None (fail-closed callers)."""
    v = m.get(k)
    return v if (v is not None and k not in failed and math.isfinite(v)) else None

def restoration(m, failed, t_en, after=None):
    """latest VIN-OK (OUTA rise) at or before the EN rise t_en (and after `after` if given), or None."""
    ts = [fin(m, failed, k) for k in OUTA_RISES]
    ts = [t for t in ts if t is not None and t <= t_en and (after is None or t > after)]
    return max(ts) if ts else None

def held_since_only_restoration(m, failed, t_en):
    """Tur-3 (full run box-tur3-20261025-1432): a later dip may not drop VIN-OK at all (VIN held behind the ideal diode),
    so no OUTA rise follows its start. Returns OUTA_R2 only if ngspice PROVES OUTA never fell again: OUTA_F1 < OUTA_R2 <=
    t_en, OUTA_F2 and OUTA_R3 reported 'failed' (= event absent in the whole transient), OUTA_RLAST == OUTA_R2. Then VIN-OK
    is continuously high from OUTA_R2 to the end of the run and OUTA_R2 is the latest VIN-OK before t_en. Else None."""
    f1, r2, rl = fin(m, failed, 'OUTA_F1'), fin(m, failed, 'OUTA_R2'), fin(m, failed, 'OUTA_RLAST')
    if None in (f1, r2, rl) or not (f1 < r2 <= t_en) or abs(rl - r2) > 1e-9:
        return None
    if 'OUTA_F2' not in failed or 'OUTA_R3' not in failed:
        return None
    return r2

def dip_starts(c):
    if c.get('kind') == 'dip2': return sorted(d[0] for d in c.get('dips') or [])
    return [c['t0']] if 't0' in c else []

def num_field(c, k):
    v = c.get(k)
    return v if (not isinstance(v, bool) and isinstance(v, (int, float)) and math.isfinite(v) and v > 0) else None

def m3_m4_errors(c, m, failed):
    """Tur-4 T4-05 (opt-in per case, all candidate dip cases request it):
    M3 every OUTA fall (VIN-OK loss) while EN is high -> an EN fall within en_force_max after it;
    M4 VGS >= vgs_at_en_min at every EN rise (VGS_AT_<rise>). Fail-closed."""
    e = []
    if 'en_force_max' in c:
        lim = num_field(c, 'en_force_max')
        if lim is None:
            e.append(f'MANDATORY M3: invalid en_force_max {c.get("en_force_max")!r}'); lim = 0.0
        ev, badk = [], []
        for k in EN_RISES[:-1] + EN_FALLS:
            if k in m and k not in failed:
                v = fin(m, failed, k)
                if v is None: badk.append(k)
                else: ev.append((v, 1 if '_R' in k else -1))
        for k in OUTA_FALLS:
            if k in failed: continue
            t = fin(m, failed, k)
            if t is None:
                if k == 'OUTA_F1' or k in m: e.append(f'MANDATORY M3: {k} missing/non-finite -> EN forcing not provable')
                continue
            if badk:
                e.append(f'MANDATORY M3: {badk} non-finite -> EN state at {k} not determinable'); continue
            before = [x for x in ev if x[0] < t]
            if not before or max(before)[1] < 0:
                continue   # EN already low (or never enabled) at the VIN-OK loss
            fl = [x[0] for x in ev if x[1] < 0 and t <= x[0]]
            if not fl:
                e.append(f'MANDATORY M3: {k} at {t:.6g} s with EN high but no EN fall after it'); continue
            d = min(fl) - t
            if d > lim:
                e.append(f'MANDATORY M3: EN fell {d*1e6:.3f} us after {k} > {lim*1e6:.3f} us')
    if 'vgs_at_en_min' in c:
        lim = num_field(c, 'vgs_at_en_min')
        if lim is None:
            e.append(f'MANDATORY M4: invalid vgs_at_en_min {c.get("vgs_at_en_min")!r}'); lim = float('inf')
        for k in EN_RISES:
            if k not in m or k in failed: continue
            v = fin(m, failed, 'VGS_AT_' + k)
            if v is None: e.append(f'MANDATORY M4: VGS_AT_{k} missing/failed/non-finite')
            elif v < lim: e.append(f'MANDATORY M4: VGS {v:.3f} V at {k} < {lim} V (OVP FET not on when the buck starts)')
    return e

def mandatory_errors(c, m, failed):
    """Tur-3 UVLO-T3-01: gates that hold for EVERY non-regression case (PASS and INFO); fail-closed.
    M1: each EN rise >= T_SEQ_MIN after the latest OUTA rise before it (after the latest dip start before it; if that dip
        did not drop VIN-OK, only with ngspice proof that OUTA never fell again, see held_since_only_restoration).
    M2: V_f >= 18.0 V at shutdown (ramp_down / mb_hold)."""
    e, det = [], {}
    kind = c.get('kind')
    if kind not in HARD_WINDOWS:
        return e, det
    # M0 (Tur-4 T4-01): regime / gate measurement validity for PASS and INFO
    if kind == 'seq':
        keys = list(SEQ_METRICS) + ['INP_MIN_AFTER_ON']
    else:
        keys = [f'{w}_{q}' for w in HARD_WINDOWS[kind] for q in REGIME_METRICS]
        if kind in ('start', 'ramp_up', 'hotplug', 'rsweep') and c.get('vf'):
            keys.append('RUN_VIN_MIN')
    for k in keys:
        if fin(m, failed, k) is None:
            e.append(f'MANDATORY M0: {k} missing/failed/non-finite')
    if kind == 'seq':
        # S (Tur-4 T4-01): stimulus-only bench; the configured DRIVE delay is the only sequencing evidence
        if not c.get('regression'):
            d = c.get('delay')
            if isinstance(d, bool) or not isinstance(d, (int, float)) or not math.isfinite(d):
                e.append(f'SEQ schema: configured delay {d!r} missing/non-numeric/non-finite (stimulus-only bench)')
            elif d < T_SEQ_MIN:
                e.append(f'SEQ schema: configured delay {d*1e3:.3f} ms < {T_SEQ_MIN*1e3:.0f} ms (stimulus-only bench)')
        return e, det
    e += m3_m4_errors(c, m, failed)
    # ngspice 'failed' on a WHEN RISE=k measurement = the k-th event did not occur (absent); a printed but non-finite
    # value (nan / inf) is an error
    present = [k for k in EN_RISES if k in m and k not in failed]
    for k in present:
        t = fin(m, failed, k)
        if t is None:
            e.append(f'MANDATORY M1: {k} non-finite -> 60 ms VIN-OK->EN gate not provable'); continue
        after = max([s for s in dip_starts(c) if s < t], default=None) if kind in DIP_KINDS else None
        r5, rl = fin(m, failed, 'OUTA_R5'), fin(m, failed, 'OUTA_RLAST')
        if r5 is not None and rl is not None and rl > r5 and t > r5 and t < rl:
            e.append(f'MANDATORY M1: {k} at {t:.6g} s lies between OUTA_R5 and OUTA_RLAST (untracked VIN-OK rises)'); continue
        bad = [x for x in OUTA_RISES if x in m and x not in failed and not math.isfinite(m[x])]
        if bad:
            e.append(f'MANDATORY M1: {bad} non-finite -> latest VIN-OK before {k} not determinable'); continue
        rs = restoration(m, failed, t, after)
        if rs is None and after is not None:
            rs = held_since_only_restoration(m, failed, t)
        if rs is None:
            e.append(f'MANDATORY M1: {k} at {t:.6g} s without a VIN-OK (OUTA) rise before it'
                     + (f' after the dip start {after:.6g} s' if after is not None else '') + ' -> 60 ms gate not provable')
            continue
        det[k] = t - rs
        if t - rs < T_SEQ_MIN:
            e.append(f'MANDATORY M1: {k} {(t-rs)*1e3:.3f} ms after VIN-OK < {T_SEQ_MIN*1e3:.0f} ms')
    r4, rl = fin(m, failed, 'EN_R4'), fin(m, failed, 'EN_RLAST')
    if r4 is not None and rl is not None and rl > r4:
        e.append('MANDATORY M1: more than 4 EN rises (EN_RLAST after EN_R4; intermediate rises untracked)')
    if kind in ('start', 'ramp_up', 'hotplug', 'rsweep') and not present:
        e.append('MANDATORY M1: EN_R1 missing/failed/non-finite -> start/gate not provable')
    # M2: ramp_down must shut down (EN_F1 finite); mb_hold only when it shut down (EN_F1 'failed' = no shutdown event)
    shut = 'EN_F1' in m and 'EN_F1' not in failed
    if shut and not math.isfinite(m['EN_F1']):
        e.append('MANDATORY M2: EN_F1 non-finite')
    elif kind == 'ramp_down' and not shut:
        e.append('MANDATORY M2: no shutdown (EN_F1 missing/failed) on a ramp-down to 16 V -> V_f not provable')
    elif kind in ('ramp_down', 'mb_hold') and shut:
        v = fin(m, failed, 'VIN_AT_SHUTDOWN')
        if v is None: e.append('MANDATORY M2: VIN_AT_SHUTDOWN missing/failed/non-finite -> V_f >= 18.0 V not provable')
        elif v < V_FALL_MIN: e.append(f'MANDATORY M2: shutdown at VIN {v:.4f} < {V_FALL_MIN}')
    return e, det

def rdip_screen(c, m, failed):
    """PROVISIONAL R-DIP screen (report-only). PASS / FAIL / UNDETERMINED; never PASS on a missing measurement."""
    pk = fin(m, failed, 'RD_PEAK')
    # Tur-4 T4-06: event classification (EN fell = the buck was shut down and restarted; else it rode through)
    ev = 'restart' if fin(m, failed, 'EN_F1') is not None else 'rode_through'
    r = dict(event=ev, vin_ok_lost=fin(m, failed, 'OUTA_F1') is not None, peak=pk, t_above=fin(m, failed, 'RD_T_ABOVE'), first_above=fin(m, failed, 'RD_ABOVE_FIRST'),
             last_downward_crossing=fin(m, failed, 'RD_ABOVE_LAST'), peak_o1=fin(m, failed, 'RD_PEAK_O1'),
             t_above_o1=fin(m, failed, 'RD_T_ABOVE_O1'), reasons=[])
    if pk is None:
        r.update(status='UNDETERMINED', reasons=['RD_PEAK missing']); return r
    if pk <= BUS_NORMAL_MAX:
        r.update(status='PASS', t_above=r['t_above'] or 0.0, return_after_dip_end=None); return r
    if r['t_above'] is None or r['last_downward_crossing'] is None:
        r.update(status='UNDETERMINED', reasons=['peak above 11.1605 V but time-above / last-crossing measurement missing'])
        return r
    # Tur-3 T3-09: RD_ABOVE_LAST is the LAST DOWNWARD crossing of 11.1605 V (not the last exceedance instant)
    r['span_above'] = r['last_downward_crossing'] - r['first_above'] if r['first_above'] is not None else None
    r['return_after_dip_end'] = r['last_downward_crossing'] - c['t1']
    if pk > RDIP_PEAK_MAX: r['reasons'].append(f'peak {pk:.4f} > {RDIP_PEAK_MAX}')
    if r['t_above'] > RDIP_T_ABOVE_MAX: r['reasons'].append(f'time above {r["t_above"]*1e3:.3f} ms > 1.0 ms')
    if r['return_after_dip_end'] > RDIP_RETURN_MAX:
        r['reasons'].append(f'back below 11.1605 V {r["return_after_dip_end"]*1e3:.3f} ms after dip end > 5 ms')
    r['status'] = 'FAIL' if r['reasons'] else 'PASS'
    return r

def judge(name, c, m, failed):
    e, info = [], {}
    has = lambda k: fin(m, failed, k) is not None
    if 'O1_GLOBAL_PEAK' not in m:
        return ['O1_GLOBAL_PEAK missing'], info
    if m['O1_GLOBAL_PEAK'] > O1_PEAK_MAX: e.append(f'O1 peak {m["O1_GLOBAL_PEAK"]:.5f} > {O1_PEAK_MAX}')
    info['O1_GLOBAL_PEAK'] = m['O1_GLOBAL_PEAK']
    for k in ('BUS_GLOBAL_MAX', 'RAW_GLOBAL_MAX', 'VIN_GLOBAL_MAX', 'S_MINUS_V5_MAX', 'SWD_MINUS_V5_MAX', 'EN_R1', 'EN_F1', 'EN_R2',
              'OUTA_R1', 'FET_ON1', 'FET_OFF1', 'FET_ON2'):
        if has(k): info[k] = m[k]
    k = c['kind']
    if k in ('start', 'ramp_up', 'hotplug', 'rsweep'):
        if not has('EN_R1'):
            e.append('buck never enabled (no start)')
        else:
            if 't_start_max' in c and m['EN_R1'] > c['t_start_max']: e.append(f'start late {m["EN_R1"]:.4f} s')
            if has('EN_F1'): e.append(f'EN fell at {m["EN_F1"]:.4f} s (shutdown/motorboat)')
            # Tur-2 UVLO-03: fail-closed; delay from the last VIN-OK rise before EN_R1
            rs = restoration(m, failed, m['EN_R1'])
            if rs is None: e.append('VIN-OK (OUTA_R1) measurement missing/failed -> 60 ms restart-delay gate not provable')
            elif m['EN_R1'] - rs < T_SEQ_MIN: e.append(f'restart delay {m["EN_R1"]-rs:.4f} s < {T_SEQ_MIN}')
            if has('FET_ON1') and m['FET_ON1'] > m['EN_R1']: e.append('buck enabled before the OVP FET was on (sequencing)')
            if not has('FET_ON1'): e.append('OVP FET never on')
            info['delay_after_vin_ok'] = m['EN_R1'] - rs if rs is not None else None
            info['seq_margin_s'] = m['EN_R1'] - m['FET_ON1'] if has('FET_ON1') else None
        e += regime(m, 'RUN', failed)
        vmin = fin(m, failed, 'RUN_VIN_MIN')
        if vmin is not None:
            info['RUN_VIN_MIN'] = vmin
            if c.get('vf') and vmin <= c['vf']: e.append(f'VIN under load {vmin:.4f} <= V_f {c["vf"]:.4f}')
            if c.get('vf'): info['run_margin_to_vf'] = vmin - c['vf']
        elif c.get('vf'):
            e.append('RUN_VIN_MIN missing/failed/non-finite -> V_f run margin not provable')
        if 'VIN_PP_RUN' in m: info['VIN_PP_RUN'] = m['VIN_PP_RUN']
    elif k in ('ramp_down', 'mb_hold'):
        e += regime(m, 'PRE', failed)
        if k == 'ramp_down' and not has('EN_F1'): e.append('no shutdown at low input')
        if has('EN_F1'):
            v = fin(m, failed, 'VIN_AT_SHUTDOWN'); info['VIN_AT_SHUTDOWN'] = v
            # Tur-2 UVLO-03: fail-closed
            if v is None: e.append('VIN_AT_SHUTDOWN missing/failed/non-finite -> V_f >= 18.0 V not provable')
            elif v < V_FALL_MIN: e.append(f'shutdown at VIN {v:.4f} < {V_FALL_MIN}')
        if has('EN_R2'): e.append(f'restart at {m["EN_R2"]:.4f} s while E stays low (motorboat)')
        for x in ('EMF_AT_SHUTDOWN', 'VIN_AT_OUTA_FALL', 'VIN_MAX_AFTER', 'VIN_MIN_HOLD'):
            if x in m: info[x] = m[x]
        if k == 'mb_hold': info['shut_down'] = has('EN_F1'); info['e_hold'] = c['e_hold']
    elif k in DIP_KINDS:
        e += regime(m, 'PRE', failed) + regime(m, 'POST', failed)
        nd = len(dip_starts(c))
        if has(f'EN_F{nd+1}'): e.append(f'more shutdowns than dips (EN_F{nd+1}, chatter)')
        if has(f'EN_R{nd+2}'): e.append(f'more enables than dips + 1 (EN_R{nd+2}, chatter)')
        if has('EN_F1') and not has('EN_R2'): e.append('no restart after the dip')
        ends = sorted(d[1] for d in c['dips']) if k == 'dip2' else [c['t1']]
        for x in ('EN_R2', 'EN_R3', 'EN_R4', 'EN_RLAST'):
            if has(x) and any(s <= m[x] < t1 for s, t1 in zip(dip_starts(c), ends)): e.append(f'{x} restart during a dip')
        for x in ('BUS_RESTART_MAX', 'RAW_RESTART_MAX', 'INP_RESTART_MIN', 'RAW_AT_DIP_END', 'T_AT_DIP_END', 'O1_DIP_MAX'):
            if x in m: info[x] = m[x]
        info['rode_through'] = not has('EN_F1')
        info['provisional_rdip_screen'] = rdip_screen(c, m, failed)
        for x in ('VT_AT_OUTA_R1', 'VT_AT_OUTA_R2', 'VT_AT_OUTA_R3', 'VT_AT_OUTA_RLAST', 'VT_AT_EN_R2', 'VT_AT_EN_R3', 'VT_AT_REL',
                  'T_REL', 'VT_MIN_POST', 'V5_MIN_DIP', 'OUTA_R4', 'OUTA_R5', 'EN_R3', 'EN_F2'):
            if has(x): info[x] = m[x]
        if has('EN_R2'):
            info['restart_delay_after_dip_end'] = m['EN_R2'] - ends[-1]
            # Tur-2 UVLO-05 / Tur-3 T3-01: the 60 ms gate on EVERY EN rise is enforced in mandatory_errors() (M1);
            # report-only: Tur-3 design target 65 ms after the latest VIN-OK
            rs = restoration(m, failed, m['EN_R2'], after=max([s for s in dip_starts(c) if s < m['EN_R2']], default=None))
            if rs is not None:
                info['restart_delay_after_vin_ok'] = m['EN_R2'] - rs
                info['design_target_65ms_met'] = m['EN_R2'] - rs >= 0.065
            # P0-03 related INFO (open item, WP1-K): did the buck restart before the OVP FET was back on?
            if has('FET_OFF1'):
                info['P0_03_buck_before_fet'] = (not has('FET_ON2')) or m['FET_ON2'] > m['EN_R2']
    elif k == 'seq':
        d = c.get('delay')
        d = d if (not isinstance(d, bool) and isinstance(d, (int, float)) and math.isfinite(d)) else None
        info['seq_evidence'] = 'stimulus-only'   # Tur-4 T4-01: ideal DRIVE delay, no measured OUTA->EN edge
        info['configured_delay'] = d
        if d is None: e.append('configured DRIVE delay missing/non-finite')
        if not has('FET_ON1'): e.append('FET never on')
        elif d is not None and d > 0 and m['FET_ON1'] > d: e.append('FET not on before DRIVE starts')
        if has('FET_OFF1'): e.append(f'FET turned off at {m["FET_OFF1"]:.5f} s (start-up false trip / P0-03)')
        inp = fin(m, failed, 'INP_MIN_AFTER_ON')
        if inp is None: e.append('INP_MIN_AFTER_ON missing/failed/non-finite')
        elif inp < 2.5: e.append('comparator tripped (INP low)')
        e += regime_seq(m, failed)
        for x in ('RAW_MAX', 'BUS_STARTUP_MAX', 'INP_MIN_AFTER_ON'):
            if x in m: info[x] = m[x]
    return e, info

def regime_seq(m, failed):
    e = []
    bad = [x for x in SEQ_METRICS if fin(m, failed, x) is None]
    if bad: return [f'{x} missing/failed/non-finite' for x in bad]
    if not (RAW_REG[0] <= m['RUN_RAW_AVG'] <= RAW_REG[1]): e.append(f'RUN: RAW avg {m["RUN_RAW_AVG"]:.4f} V not regulated')
    if m['RUN_VGS_MIN'] < 6 or m['RUN_INP_MIN'] < 2.5: e.append('RUN: FET/comparator not in normal state')
    if m['RUN_BUS_MAX'] > BUS_NORMAL_MAX or m['RUN_O1_MAX'] > BUS_NORMAL_MAX: e.append('RUN: bus/O1 above normal limit')
    return e

def git(*a):
    try:
        r = subprocess.run(['git', *a], cwd=HERE, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else '', r.returncode
    except OSError:
        return '', -1

def provenance(cases, run_id):
    """Tur-2 UVLO-04: bind the logs to one fresh, complete, successful run. Returns (errors, manifest summary)."""
    e = []
    mfp = HERE / 'results' / 'run-manifest.json'
    if not mfp.exists():
        return ['results/run-manifest.json missing (logs not bound to a run)'], {}
    try:
        mf = json.loads(mfp.read_text())
    except ValueError as x:
        return [f'run-manifest.json unreadable: {x}'], {}
    runs = mf.get('runs') or {}
    if run_id and mf.get('run_id') != run_id:
        e.append(f'run id mismatch: manifest {mf.get("run_id")!r} != expected {run_id!r}')
    if mf.get('partial'): e.append('manifest is from a partial (filtered) run')
    if mf.get('error'): e.append(f'runner error: {mf["error"]}')
    # Tur-3 T3-06: must be present and exactly integer 0 (missing / null / non-zero / bool -> error)
    rc = mf.get('runner_exit_code')
    if type(rc) is not int or rc != 0: e.append(f'runner_exit_code must be exactly 0 (got {rc!r})')
    if mf.get('cases_sha256') != sha(HERE / 'test-cases-uvlo.json'): e.append('case table changed after the run (cases_sha256)')
    head, _ = git('rev-parse', 'HEAD')
    mh = mf.get('git_head')
    if mh is None: e.append('manifest has no git_head')
    elif run_id:
        if mh != head: e.append(f'manifest git_head {mh[:12]!r} != current HEAD {head[:12]!r} (CI run must verify its own checkout)')
    elif mh != head:
        out, rc = git('diff', '--name-only', mh, 'HEAD', '--', '.', ':(exclude)results')
        if rc != 0: e.append(f'cannot compare package inputs between manifest HEAD {mh[:12]} and HEAD')
        elif out: e.append(f'package inputs changed since the run (manifest HEAD {mh[:12]}): {out.splitlines()[:5]}')
    if mf.get('package_inputs_dirty_at_run'): e.append('package inputs were dirty when the run started')
    decks = {p.stem: p for p in (HERE / 'decks').glob('*.cir')}
    want = {f'uvlo-{n}' for n in cases}
    if set(runs) != set(decks): e.append(f'manifest deck set != decks/ (missing {sorted(set(decks)-set(runs))[:5]}, extra {sorted(set(runs)-set(decks))[:5]})')
    if not want <= set(decks): e.append(f'cases without a deck: {sorted(want-set(decks))[:5]}')
    for n in sorted(set(runs) & set(decks)):
        r = runs[n]; log = HERE / 'results' / 'logs' / f'{n}.log'
        if r.get('rc') != 0: e.append(f'{n}: rc {r.get("rc")!r}')
        if r.get('completed') is not True: e.append(f'{n}: not completed')
        if r.get('deck_sha256') != sha(decks[n]): e.append(f'{n}: deck SHA-256 differs from the run')
        if not log.exists() or r.get('log_sha256') != sha(log): e.append(f'{n}: log missing or SHA-256 differs from the run')
    extra_logs = sorted(p.stem for p in (HERE / 'results' / 'logs').glob('*.log') if p.stem not in runs)
    if extra_logs: e.append(f'logs not produced by this run: {extra_logs[:5]}')
    return e, dict(run_id=mf.get('run_id'), git_head=mh, started_utc=mf.get('started_utc'), ngspice=mf.get('ngspice'),
                   n_runs=len(runs))

def main():
    argv = sys.argv[1:]; run_id = os.environ.get('UVLO_RUN_ID') or ''
    if argv[:1] == ['--run-id'] and len(argv) > 1: run_id = argv[1]
    elif argv: print(f'usage: verify_uvlo.py [--run-id ID]  (got {argv})', file=sys.stderr); sys.exit(2)
    cases = json.loads((HERE / 'test-cases-uvlo.json').read_text())['cases']
    prov_err, prov = provenance(cases, run_id)
    out, acc_fail, reg_bad, incomplete = {}, [], [], []
    for name, c in cases.items():
        log = HERE / 'results' / 'logs' / f'uvlo-{name}.log'
        if not log.exists():
            out[name] = dict(status='INCOMPLETE', reason='log missing'); incomplete.append(name); continue
        m, failed, done, _ = parse(log)
        if not done:
            st = 'INCOMPLETE'
            res = dict(status=st, reason='simulation did not complete', last_meas=m)
            # strict (2026-10-25): an aborted/unfinished deck never counts as a reproduced regression
            incomplete.append(name)
            out[name] = res; continue
        # Tur-3 T3-05: the kind is validated BEFORE the regression classification (an unknown kind never counts as a
        # reproduced regression)
        if c.get('kind') not in HARD_WINDOWS:
            out[name] = dict(status='FAIL', errors=[f'invalid case kind {c.get("kind")!r} (known: {sorted(HARD_WINDOWS)})'],
                             expect=c.get('expect')); acc_fail.append(name); continue
        errs, info = judge(name, c, m, failed)
        hard = hard_limit_errors(c, m)
        mand, mdet = mandatory_errors(c, m, failed)
        info['vin_ok_to_en_delays'] = mdet
        errs = errs + [h for h in hard + mand if h not in errs]
        st = 'PASS' if not errs else 'FAIL'
        res = dict(status=st, errors=errs, info=info, expect=c.get('expect'), hard_limit_errors=hard, mandatory_errors=mand)
        if c.get('expect') not in VALID_EXPECT or (c.get('expect') == 'FAIL') != bool(c.get('regression')):
            res['status'] = 'FAIL'; res['errors'] = errs + [f'invalid classification expect={c.get("expect")!r} regression={c.get("regression")!r}']
            acc_fail.append(name)
        elif c.get('regression'):
            res['regression_reproduced'] = st == 'FAIL'
            if st != 'FAIL': reg_bad.append(name)
        elif hard or mand:
            # fail-closed (Tur-1 P0, Tur-3 T3-01): PASS *and* INFO cases fail on any H1/H2 breach, any mandatory gate (M1 60 ms
            # VIN-OK->EN on every EN rise, M2 V_f) or a missing / failed / non-finite gate measurement
            acc_fail.append(name)
        elif c['expect'] == 'PASS' and st != 'PASS':
            acc_fail.append(name)
        out[name] = res
    head_now = git('rev-parse', 'HEAD')[0]
    dirty = subprocess.run(['git', 'status', '--porcelain', '.'], cwd=HERE, capture_output=True, text=True).stdout.strip() != ''
    # inputs = everything in the package except results/ (logs are rewritten by run_uvlo.py before the verifier runs)
    inputs_dirty = subprocess.run(['git', 'status', '--porcelain', '--', '.', ':(exclude)results'], cwd=HERE, capture_output=True,
                                  text=True).stdout.strip() != ''
    files = sorted([p for p in HERE.glob('*.py')] + [p for p in HERE.glob('*.inc')] + [p for p in HERE.glob('*.lib')]
                   + [HERE / 'test-cases-uvlo.json', HERE / 'results' / 'uvlo-budget.json'] + list((HERE / 'decks').glob('*.cir'))
                   + [HERE.parent.parent / 'pdu-behavioral.lib', HERE.parent.parent / 'pdu-inductor-ng.lib',
                      HERE.parent / '2026-10-25-o1-ovp' / 'pdu-o1ovp-behavioral.lib', HERE.parent / '2026-10-25-o1-ovp' / 'pdu-o1ovp-block.inc',
                      HERE.parent / '2026-10-25-o1-ovp' / 'pdu-circuit-o1ovp.inc', HERE.parent / '2026-10-25-o1-ovp' / 'pdu-efuse-block-o1ovp.inc'])
    logs = sorted((HERE / 'results' / 'logs').glob('*.log'))
    code = 2 if (incomplete or prov_err) else (1 if acc_fail or reg_bad else 0)
    rd = {n: r['info']['provisional_rdip_screen'] for n, r in out.items() if r.get('info', {}).get('provisional_rdip_screen')}
    rdip = dict(note='PROVISIONAL WP3 screen proposed in ChatGPT review 6395614957 (UVLO-06); report-only, NOT an acceptance '
                     'limit and NOT a requirement change; simulation, not measurement',
                limits=dict(peak_max=RDIP_PEAK_MAX, t_above_max=RDIP_T_ABOVE_MAX, return_after_dip_end_max=RDIP_RETURN_MAX,
                            threshold=BUS_NORMAL_MAX),
                cases={n: dict(status=v['status'], event=v.get('event'), vin_ok_lost=v.get('vin_ok_lost'), peak=v['peak'], t_above=v.get('t_above'),
                               return_after_dip_end=v.get('return_after_dip_end'), reasons=v['reasons']) for n, v in rd.items()},
                counts={s: sum(1 for v in rd.values() if v['status'] == s) for s in ('PASS', 'FAIL', 'UNDETERMINED')},
                counts_by_event={f'{ev}/{s}': sum(1 for v in rd.values() if v.get('event') == ev and v['status'] == s)
                                 for ev in ('rode_through', 'restart') for s in ('PASS', 'FAIL', 'UNDETERMINED')})
    summary = dict(exit_code=code, git_head=head_now, provenance_errors=prov_err, run_manifest=prov, expected_run_id=run_id or None,
                   provisional_rdip_screen=rdip, worktree_dirty_at_verify=dirty, package_inputs_dirty=inputs_dirty, n_cases=len(cases),
                   n_pass=sum(1 for r in out.values() if r['status'] == 'PASS'),
                   acceptance_fail=acc_fail, regression_not_reproduced=reg_bad, incomplete=incomplete,
                   info_cases=[n for n, c in cases.items() if c.get('expect') == 'INFO'],
                   hard_limit_gate='H1/H2 enforced for every non-regression case (PASS and INFO)',
                   mandatory_gate='M0 (regime measurement validity), M1 (60 ms VIN-OK->EN on every EN rise), M2 (V_f >= 18.0 V), M3 (EN low <= en_force_max after VIN-OK loss, opt-in), M4 (VGS >= vgs_at_en_min at every EN rise, opt-in) and the seq delay schema enforced for every non-regression case (PASS and INFO)',
                   seq_evidence='seq cases are stimulus-only benches (ideal DRIVE delay, configured delay schema-validated >= 60 ms); not a measured OUTA->EN edge',
                   ci_status='GitHub Actions workflow proposal-ngspice DISABLED by the user (2026-10-25); CI gating not active; evidence = local runs + run manifest SHA-256',
                   per_variant={v: dict(n=sum(1 for n, c in cases.items() if c.get('variant', 'C3') == v),
                                        n_pass=sum(1 for n, c in cases.items() if c.get('variant', 'C3') == v and out[n]['status'] == 'PASS'),
                                        acceptance_fail=[n for n in acc_fail if cases[n].get('variant', 'C3') == v],
                                        regression_not_reproduced=[n for n in reg_bad if cases[n].get('variant', 'C3') == v])
                                for v in sorted({c.get('variant', 'C3') for c in cases.values()})},
                   limits=dict(O1_PEAK_MAX=O1_PEAK_MAX, BUS_NORMAL_MAX=BUS_NORMAL_MAX, V_FALL_MIN=V_FALL_MIN, T_SEQ_MIN=T_SEQ_MIN))
    (HERE / 'results' / 'uvlo-verify.json').write_text(json.dumps(dict(summary=summary, cases=out,
        input_sha256={str(p.relative_to(HERE.parent.parent)): sha(p) for p in files},
        log_sha256={p.name: sha(p) for p in logs}), indent=1, default=str))
    for n, r in out.items():
        print(f'{r["status"]:10s} {"(regression, reproduced)" if r.get("regression_reproduced") else ""} {n} {"; ".join(r.get("errors", [])) or r.get("reason", "")}')
    for x in prov_err:
        print('PROVENANCE', x)
    print(json.dumps(summary, indent=1))
    sys.exit(code)

if __name__ == '__main__':
    main()

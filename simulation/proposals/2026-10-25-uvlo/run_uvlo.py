#!/usr/bin/env python3
"""Run every WP2 UVLO ngspice deck (parallel), store logs in results/logs/, write results/run-manifest.json.
Usage: python3 run_uvlo.py [-j N] [name-substring ...]. Exit 0 = every deck process returned 0 and printed
'Total analysis time'; 2 = at least one deck did not complete (the verifier decides PASS/FAIL)."""
import subprocess, sys, json, time, hashlib, os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE = Path(__file__).absolute().parent
NG = os.environ.get('PDU_NGSPICE', 'ngspice')
DECKS = HERE / 'decks'; LOGS = HERE / 'results' / 'logs'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run(deck):
    log = LOGS / (deck.stem + '.log')
    t0 = time.time()
    try:
        r = subprocess.run([NG, '-b', '-D', 'ngbehavior=ltpsa', deck.name], cwd=DECKS, capture_output=True, text=True, timeout=3000)
        out, rc = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or '') if isinstance(e.stdout, str) else '', 'timeout'
    log.write_text(out)
    done = 'Total analysis time' in out
    return deck.stem, dict(rc=rc, completed=done, elapsed_s=round(time.time() - t0, 1), deck_sha256=sha(deck), log_sha256=sha(log))

def main():
    args = sys.argv[1:]; j = 6
    if args[:1] == ['-j']:
        j = int(args[1]); args = args[2:]
    LOGS.mkdir(parents=True, exist_ok=True)
    decks = sorted(d for d in DECKS.glob('*.cir') if not args or any(a in d.name for a in args))
    ver = subprocess.run([NG, '-v'], capture_output=True, text=True).stdout.strip().splitlines()
    res = {}
    with ThreadPoolExecutor(j) as ex:
        for name, r in ex.map(run, decks):
            res[name] = r; print(name, r['rc'], r['completed'], r['elapsed_s'], flush=True)
    mf = HERE / 'results' / 'run-manifest.json'
    old = json.loads(mf.read_text())['runs'] if mf.exists() else {}
    old.update(res)
    mf.write_text(json.dumps(dict(ngspice=[l for l in ver if 'ngspice' in l], command='ngspice -b -D ngbehavior=ltpsa <deck>',
                                  cpus=os.cpu_count(), runs=old), indent=1))
    sys.exit(0 if all(r['rc'] == 0 and r['completed'] for r in res.values()) else 2)

if __name__ == '__main__':
    main()

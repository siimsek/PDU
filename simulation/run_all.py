"""Rebuild/run both engines from Konnect exports and record each attempt.

No KiCad source access. A failed or interrupted attempt cannot silently reuse
the previous acceptance report. Exit1 means completed electrical acceptance
failed; exit2 means execution/verification did not complete.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ltspice',default=os.environ.get(
        'PDU_LTSPICE',r'C:\Program Files\ADI\LTspice\LTspice.exe'))
    parser.add_argument('--timeout',type=int,default=300)
    args = parser.parse_args()
    state = dict(status='in_progress',started_UTC=datetime.now(timezone.utc).isoformat(),
                 ltspice_completed=[],ngspice_completed=False)

    def persist():
        (HERE/'latest-run.json').write_text(json.dumps(state,indent=2)+'\n',
                                            encoding='utf-8',newline='\n')

    def script(name):
        subprocess.run([sys.executable,str(HERE/name)],cwd=HERE,check=True)

    persist()
    try:
        for path in (Path(args.ltspice),Path(os.environ.get(
                'PDU_NGSPICE',r'F:\Spice64\bin\ngspice_con.exe'))):
            if not path.is_file():
                raise RuntimeError(f'Simulator executable missing: {path}')
        if args.timeout<=0:
            raise ValueError('Process timeout must be positive')
        script('build_models.py')
        script('build_benches.py')
        cases = json.loads((HERE/'test-cases.json').read_text())
        state['case_count'] = len(cases)
        state['export_sha256'] = hashlib.sha256((HERE/'pdu-current.net').read_bytes()).hexdigest()
        persist()
        for name,case in cases.items():
            deck = HERE/case['file']
            started = time.time_ns()
            proc = subprocess.run([args.ltspice,'-b',str(deck)],cwd=HERE,
                                  timeout=args.timeout,capture_output=True)
            log = deck.with_suffix('.log')
            if proc.returncode or not log.is_file() or log.stat().st_mtime_ns<started:
                raise RuntimeError(f'{name}: LTspice failed or log is stale')
            state['ltspice_completed'].append(name)
            persist()
            print(name,'LTspice finished; acceptance checked below',flush=True)
        script('run_ngspice.py')
        state['ngspice_completed'] = True
        persist()
        started = time.time_ns()
        verdict = subprocess.run([sys.executable,str(HERE/'verify_results.py')],cwd=HERE)
        report = HERE/'verification-results.json'
        if verdict.returncode not in (0,1) or not report.is_file() or report.stat().st_mtime_ns<started:
            raise RuntimeError('No fresh acceptance report was produced')
        data = json.loads(report.read_text())
        if data['artifact_sha256']['pdu-current.net']!=state['export_sha256']:
            raise RuntimeError('Acceptance report source changed during the run')
        execution_checks = [c for c in data['checks'] if c['check'].endswith('/execution')]
        if len(execution_checks)!=2*len(cases) or not all(c['pass'] for c in execution_checks):
            raise RuntimeError('Simulator execution checks failed or coverage is incomplete')
        state.update(status='completed',passed=data['passed'],failed=data['failed'],
                     engine_runs=data['engine_runs'],acceptance_passed=data['failed']==0,
                     finished_UTC=datetime.now(timezone.utc).isoformat())
        persist()
        return verdict.returncode
    except (OSError,RuntimeError,ValueError,subprocess.SubprocessError) as exc:
        state.update(status='execution_failed',error=str(exc),
                     finished_UTC=datetime.now(timezone.utc).isoformat())
        persist()
        print(f'Incomplete run: {exc}',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())

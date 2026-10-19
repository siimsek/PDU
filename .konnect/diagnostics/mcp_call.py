"""Use the installed Konnect MCP server over its documented stdio transport.

No KiCad source parsing/writing. Input is a JSON list of tool calls; output is
the complete MCP responses. This bypasses only a client's stale tools/list UI,
not Konnect's validation, document binding, locking, or mutation guards.
"""
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading

EXE = os.environ.get('PDU_KONNECT_EXE', str(Path.home() / 'Documents/KiCad/10.0/3rdparty/plugins/com_github_mixelpixx_konnect/bin/konnect.exe'))

def main():
    calls = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
    out = Path(sys.argv[2])
    args = [EXE, '--client', 'codex']
    if len(sys.argv) > 3:
        args += ['--config', sys.argv[3]]
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, encoding='utf-8',
                            creationflags=subprocess.CREATE_NO_WINDOW)
    responses = queue.Queue()
    errors = []
    def reader():
        for line in proc.stdout:
            try:
                responses.put(json.loads(line))
            except json.JSONDecodeError:
                errors.append(line[:500])
    def err_reader():
        for line in proc.stderr:
            errors.append(line[:1000])
    threading.Thread(target=reader, daemon=True).start()
    threading.Thread(target=err_reader, daemon=True).start()
    serial = 0
    def send(method, params, notify=False, timeout=180):
        nonlocal serial
        serial += 1
        msg = dict(jsonrpc='2.0', method=method, params=params)
        if not notify:
            msg['id'] = serial
        proc.stdin.write(json.dumps(msg) + '\n')
        proc.stdin.flush()
        if notify:
            return None
        while True:
            r = responses.get(timeout=timeout)
            if r.get('id') == serial:
                return r
    results = []
    try:
        init = send('initialize', {'protocolVersion':'2024-11-05',
                    'capabilities':{}, 'clientInfo':{'name':'PDU-Konnect-diagnostics','version':'1'}})
        if 'error' in init:
            raise RuntimeError(init['error'])
        send('notifications/initialized', {}, notify=True)
        for call in calls:
            if call.get('method') == 'tools/list':
                r = send('tools/list', {})
            else:
                r = send('tools/call', {'name':call['name'], 'arguments':call.get('arguments',{})})
            results.append({'request':call, 'response':r})
            out.write_text(json.dumps({'results':results,'stderr':errors}, indent=2), encoding='utf-8')
            print(json.dumps({'tool':call.get('name',call.get('method')),
                              'rpc_error':r.get('error'),
                              'isError':r.get('result',{}).get('isError',False)}), flush=True)
    finally:
        proc.stdin.close()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.terminate()
        out.write_text(json.dumps({'results':results,'stderr':errors}, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Limited -b adapter for local libngspice bench diagnostics; not ngspice CLI."""
import ctypes, sys, os, pathlib, shutil, re
lib = ctypes.CDLL('/usr/lib/x86_64-linux-gnu/libngspice.so.0')
CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
EXIT = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
status = {'exit': 0}
capture = None
if os.environ.get('PDU_CAPTURE_DIR') and len(sys.argv) == 5 and pathlib.Path('b.cir').is_file():
    root = pathlib.Path(os.environ['PDU_CAPTURE_DIR'])
    root.mkdir(parents=True, exist_ok=True)
    title = pathlib.Path('b.cir').read_text().splitlines()[0].strip('* ').lower()
    title = re.sub(r'[^a-z0-9]+', '-', title).strip('-')
    shutil.copyfile('b.cir', root / (title + '.cir'))
    capture = (root / (title + '.log')).open('w')
@CB
def output(raw, ident, user):
    msg = raw.decode(errors='replace')
    prefix, _, body = msg.partition(' ')
    if capture:
        capture.write(msg + '\n')
        capture.flush()
    print(body if prefix in ('stdout', 'stderr') else msg, file=sys.stderr if prefix == 'stderr' else sys.stdout, flush=True)
    return 0
@EXIT
def exiting(code, immediate, quitexit, ident, user):
    status['exit'] = code if code else status['exit']
    return 0
lib.ngSpice_Init.argtypes = [CB, CB, EXIT, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
lib.ngSpice_Command.argtypes = [ctypes.c_char_p]
lib.ngSpice_Command.restype = ctypes.c_int
lib.ngSpice_Init(output, output, exiting, None, None, None, None)
if sys.argv[1:] == ['-v']:
    sys.exit(lib.ngSpice_Command(b'version') or status['exit'])
if len(sys.argv) != 5 or sys.argv[1:4] != ['-b','-D','ngbehavior=ltpsa'] or sys.argv[4] != 'b.cir':
    print('unsupported adapter invocation', file=sys.stderr); sys.exit(2)
for command in (b'set ngbehavior=ltpsa', b'source b.cir', b'run'):
    rc = lib.ngSpice_Command(command)
    if rc or status['exit']:
        sys.exit(rc or status['exit'])

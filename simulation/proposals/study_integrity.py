"""Fail-closed provenance and exact printed-decimal checks for proposal-only studies.

Diagnostic infrastructure: these checks do not certify circuit correctness or physical hardware.
"""
from decimal import Decimal, InvalidOperation
from pathlib import Path
import hashlib
import re
import subprocess
import sys
import time

LIMITS = {'time': Decimal('0.0000001'), 'voltage': Decimal('0.005')}
SHA256_RE = re.compile(r'^[0-9a-f]{64}$')


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare_printed(a, b, kind):
    """Return (exact difference, exceeds limit, equals limit); equality is PASS."""
    if kind not in LIMITS or not isinstance(a, str) or not isinstance(b, str):
        raise ValueError('unknown measurement kind or missing raw printed values')
    try:
        x, y = Decimal(a), Decimal(b)
    except InvalidOperation as exc:
        raise ValueError('invalid printed measurement') from exc
    if not (x.is_finite() and y.is_finite()):
        raise ValueError('nonfinite printed measurement')
    difference = abs(x - y)
    return difference, difference > LIMITS[kind], difference == LIMITS[kind]


def raw_measures(row, pkg, regex):
    """Use raw log strings, verifying stored log SHA when reconstructing older JSON."""
    raw = row.get('measures_raw')
    if raw is not None:
        if not isinstance(raw, dict):
            raise ValueError('malformed measures_raw')
        return raw
    rel = Path(row['log'])
    root = Path(pkg).resolve()
    log = (root / rel).resolve()
    if rel.is_absolute() or not log.is_relative_to(root):
        raise ValueError('log outside proposal package')
    expected = row.get('log_sha256')
    if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
        raise ValueError('missing or invalid historical log hash')
    if file_sha256(log) != expected:
        raise ValueError('historical log hash mismatch')
    return {k.lower(): v for k, v in regex.findall(log.read_text(errors='replace'))}


def _git(cwd, *args):
    p = subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, check=True)
    return p.stdout


def snapshot(pkg, runner):
    """Read full-repo status, not just the runner directory; reject untracked inputs."""
    pkg, runner = Path(pkg).resolve(), Path(runner).resolve()
    root = Path(_git(pkg, 'rev-parse', '--show-toplevel').strip()).resolve()
    relative = runner.relative_to(root).as_posix()
    helper = Path(__file__).resolve()
    helper_rel = helper.relative_to(root).as_posix()
    tracked_runner = subprocess.run(['git', 'ls-files', '--error-unmatch', '--', relative],
                                    cwd=root, capture_output=True).returncode == 0
    tracked_helper = subprocess.run(['git', 'ls-files', '--error-unmatch', '--', helper_rel],
                                    cwd=root, capture_output=True).returncode == 0
    return dict(runner_sha256=file_sha256(runner), helper_sha256=file_sha256(helper),
                git_head=_git(root, 'rev-parse', 'HEAD').strip(),
                git_root=str(root),
                git_status_porcelain=_git(root, 'status', '--porcelain=v1', '--untracked-files=all'),
                runner_tracked=tracked_runner, helper_tracked=tracked_helper,
                argv=[sys.executable] + sys.argv, time=time.strftime('%Y-%m-%d %H:%M:%S %z'))


def consistent(start, end, rows, pkg, out_dir):
    """Allow only *new untracked* whitelisted run logs with matching recorded SHA-256.

    Every other git change (including a changed tracked output), unknown output,
    runner/helper modification and untracked input fails closed. Existing evidence
    is never treated as a free pass for an overwritten log.
    """
    keys = ('git_head', 'git_root', 'runner_sha256', 'helper_sha256')
    if any(start.get(k) != end.get(k) or not start.get(k) for k in keys):
        return False
    if not all(start.get(k) is True and end.get(k) is True
               for k in ('runner_tracked', 'helper_tracked')):
        return False
    if start.get('git_status_porcelain') or not isinstance(end.get('git_status_porcelain'), str):
        return False
    try:
        root = Path(start['git_root']).resolve()
        pkg = Path(pkg).resolve()
        out = Path(out_dir).resolve()
        if not pkg.is_relative_to(root) or not out.is_relative_to(pkg):
            return False
        expected = {}
        if not rows:
            return False
        for row in rows:
            rel = Path(row['log'])
            path = (pkg / rel).resolve()
            digest = row['log_sha256']
            if rel.is_absolute() or not path.is_relative_to(out) or not isinstance(digest, str):
                return False
            if not SHA256_RE.fullmatch(digest) or not path.is_file() or file_sha256(path) != digest:
                return False
            key = path.relative_to(root).as_posix()
            if key in expected:
                return False
            expected[key] = digest
        for entry in end['git_status_porcelain'].splitlines():
            if not entry.startswith('?? ') or entry[3:] not in expected:
                return False
    except (KeyError, ValueError, OSError, TypeError):
        return False
    return True

"""Build a two-commit *temporary* Git history for synthetic UVLO historical tests."""
import json
import subprocess
from pathlib import Path


def bind_historical_fixture_git(here):
    """Bind a *temporary synthetic* historical manifest to two real Git commits.

    Commit A records fixture inputs and an unbound manifest; commit B changes only
    results/run-manifest.json to reference A. The real verifier compares A..B
    excluding results/, so no falsely fabricated HEAD or acceptance run is needed.
    This helper is for temporary fixture trees, never for a real source checkout.
    """
    here = Path(here).resolve()
    if here.name != '2026-10-25-uvlo' or here.parent.name != 'proposals' or here.parent.parent.name != 'simulation':
        raise ValueError('expected a synthetic simulation/proposals/2026-10-25-uvlo fixture')
    root = here.parents[2]
    if (root / '.git').exists():
        raise ValueError('temporary Git fixture already initialized')

    def git(*args):
        proc = subprocess.run(['git', *args], cwd=root, capture_output=True, text=True)
        if proc.returncode:
            raise RuntimeError(f'fixture git {" ".join(args)} failed: {proc.stderr}')
        return proc.stdout.strip()

    (root / '.gitignore').write_text('**/__pycache__/\n**/*.pyc\n')
    git('init', '-q')
    git('config', 'user.name', 'UVLO Synthetic Fixture')
    git('config', 'user.email', 'fixture@localhost')
    git('add', '-A')
    git('commit', '-qm', 'synthetic historical fixture baseline')
    base = git('rev-parse', 'HEAD')
    manifest = here / 'results' / 'run-manifest.json'
    if not manifest.is_file():
        return base
    data = json.loads(manifest.read_text())
    data['git_head'] = base
    manifest.write_text(json.dumps(data, sort_keys=True) + '\n')
    git('add', '--', str(manifest.relative_to(root)))
    git('commit', '-qm', 'bind historical output only to prior synthetic input tree')
    head = git('rev-parse', 'HEAD')
    diff = subprocess.run(['git', 'diff', '--name-only', base, head, '--', '.', ':(exclude)results'],
                          cwd=here, capture_output=True, text=True, check=True).stdout.strip()
    if head == base or diff:
        raise AssertionError('synthetic historical provenance changed package inputs: ' + diff)
    if git('status', '--porcelain', '--untracked-files=all'):
        raise AssertionError('synthetic historical fixture not clean')
    return base

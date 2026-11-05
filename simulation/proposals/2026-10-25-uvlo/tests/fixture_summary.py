"""Read the final verifier JSON summary from stdout (synthetic historical fixtures only)."""
import json
import re


def summary_from_stdout(stdout):
    """Return {'summary': ...} or {}. Never synthesize a passing result."""
    for match in reversed(list(re.finditer(r'(?m)^\{', stdout))):
        try:
            summary = json.loads(stdout[match.start():])
        except (ValueError, TypeError):
            continue
        if (isinstance(summary, dict) and
                {'mode', 'exit_code', 'n_cases', 'provenance_errors'} <= summary.keys()):
            return {'summary': summary}
    return {}

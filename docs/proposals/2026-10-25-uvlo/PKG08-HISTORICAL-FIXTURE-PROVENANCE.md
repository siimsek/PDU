# PKG-08 — Historical mini-fixture Git provenance: verified partial integration fix

Date: **2026-11-06 (Europe/Istanbul)**. Working branch: `wp/baseline-2026-10-24`. Start HEAD: `41d88eb115182c5e784404aa7dcc15678f2205f6`. PR #1 is a **draft**, CI remains disabled.

## Reproduced defect

The PKG-06 migration changed the small `tests/test_uvlo_tur2.py` and `tests/test_uvlo_gates.py` electrical-gate fixtures from `--run-id` to read-only `--historical`. Those temporary fixtures nevertheless set `run-manifest.json.git_head = ""` and were not Git repositories.

The **actual verifier source** `verify_uvlo.py`, `provenance()` lines 467–475, obtains the current Git HEAD. In historical mode, when the manifest HEAD is different, it executes `git diff --name-only <manifest-head> HEAD -- . :(exclude)results`. For an empty manifest HEAD this invocation cannot prove input continuity. This was independently demonstrated using **real Git** in a temporary repository: `git diff --name-only '' HEAD -- . ':(exclude)results'` returned **exit 128**, `fatal: bad revision ''`. Therefore an expected electrical PASS in these old mini-fixtures could turn into an unrelated provenance FAIL (usually exit 2), masking the electrical assertion.

## Tests-first implementation

1. Created `tests/fixture_historical.py` with `bind_historical_fixture_git(here)`. This function refuses an already initialized Git checkout and incorrect fixture paths, initializes a temporary Git repository, commits the synthetic inputs as **commit A**, records A in `results/run-manifest.json`, then commits **only that result manifest** as **commit B**. It checks that `git diff A B -- . ':(exclude)results'` from the package cwd is empty and the synthetic repository is clean. This is an explicit **historical mini-fixture**, not a newly simulated PDU acceptance run.
2. Added `tests/test_fixture_historical.py` with 7 real-Git regression tests: A must equal the bound manifest head and differ from B; A→B modifies only the historical result manifest; the package is clean; rebind is rejected; missing manifest remains missing; malformed JSON fails; wrong fixture location is rejected.
3. The test helper first had 4/13 failing tests due to a **test-helper bug**: the `:(exclude)results` pathspec was evaluated at the repository root rather than the `2026-10-25-uvlo` package cwd. Corrected this to match the verifier's `git(..., cwd=HERE)` behavior; then **13/13 PASS** (7 new Git tests + 6 retained stdout parser tests). This red/green sequence is captured in local log files. This was a **fixture correctness correction**, not a change to the product or acceptance limits.
4. `tests/test_uvlo_tur2.py` now binds its temporary fixture after writing the manifest and before verifying it. `tests/test_uvlo_gates.py` does the same. Negative tests with missing manifest remain missing; all mini-fixtures remain isolated and never modify the PR's tracked historical evidence.

GitHub file content verified against the locally tested byte snapshots using **Git blob SHA-1**:

| File | Git blob SHA-1 |
|---|---|
| `tests/fixture_historical.py` | `9e01b467d9d4bc1c478c9d93c3bc40e36f0a0bed` |
| `tests/test_fixture_historical.py` | `0bc6e90e16bc14b76691f091225bb5aefb0ca9fe` |

The two existing fixture harnesses were updated in commits `9e925a79` (`test_uvlo_tur2.py`) and `685ced5a` (`test_uvlo_gates.py`).

## Executed local tests — NOT full integration

- **13/13 PASS**: `python -m unittest -v test_fixture_historical test_fixture_summary` using exactly the GitHub-verified new fixture helper/test code. Includes real local Git initialization and two-commit provenance.
- **11/11 PASS**: `test_locked_runner.py` from the PKG-07 evidence ZIP, verified at the prior GitHub blob. Uses a **fake** ngspice stub and 259 **synthetic** decks; never real electrical simulation.
- Combined this turn: **24/24 executed local unit/synthetic tests**. Do not add counts from previous sessions or represent them as complete verifier tests.

## Explicit remaining blockers

- The full 44537-character `verify_uvlo.py` is accessible via the connected GitHub action, but is **not available as a locally verifiable complete source file**. The previous PKG-07 ZIP contains the exact runner and its tests only. Direct `git ls-remote` or clone via container failed `Could not resolve host: github.com`; no local full private repository clone. Thus **`verify_uvlo.py` full CLI integration, `tests/test_uvlo_tur2..6.py`, `tests/test_uvlo_gates.py`, and `test_locked_verifier.py` remain UNRUN**. Source-level Git provenance analysis does **not** substitute for this execution.
- `ngspice` is not installed locally and no active local ngspice process was found. **No new 259-deck Gear/tmax100n acceptance, 23-case regression rerun, 20×2 50/25 ns convergence, M3 causal waveform capture, or physical bench measurement** was performed.
- Existing 259 locked decks and 25 protocol inputs are not changed by this fixture-only fix. WP2 historic classification **161 PASS / 69 acceptance FAIL / 6 incomplete** is unchanged; old 20×2 Decimal reanalysis **6/20**, with 9 real method aborts, is unchanged. WP1 has 4 incomplete ESL deck simulations. P0 hardware/UVLO deficiencies remain OPEN.

**Decision:** PKG-08 historical fixture Git provenance **code and 13 focused tests COMPLETE**. Full integrated verifier and product acceptance **remain OPEN**; no CI activation, no PR comment, no merge, no main change.

**Next:** In an authenticated runtime with a full, Git-SHA-matching checkout, run all actual verifier and existing UVLO test scripts. Preserve failed assertions and fix only supported causes; acceptance cannot be declared until that full integration + genuine ngspice run. Avoid requesting user-run commands in this workflow.

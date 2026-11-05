# PKG-06 — UVLO synthetic fixture compatibility; full verifier gate OPEN

Date: **2026-11-05 (Europe/Istanbul)**. Branch `wp/baseline-2026-10-24`.
Verified source HEAD before changes: `1c51c28ff4bb28ba25a92fe44f42789eb9640ae3`.

## Reproduced incompatibilities (code inspection)

1. `tests/test_uvlo_tur2.py` and `tests/test_uvlo_gates.py` instantiated small 1–3 deck fake manifests, invoked `verify_uvlo.py --run-id ...` and read the tracked `results/uvlo-verify.json`. PKG-03/05 now **correctly** requires a complete isolated 259-deck run; PKG-05B makes `--historical` read-only (final JSON on stdout). The legacy fixture contract cannot be treated as acceptance.
2. `test_uvlo_tur5.py` and `test_uvlo_tur6.py` used an acceptance run-id for small synthetic gate cases; tests could exit early at preflight instead of exercising M3/M4. V53b formerly parsed a now-forbidden historical output file.
3. Tur-2 runner checks expected stale log deletion and a single overwriteable manifest. This contradicted the mandatory immutable history and `results/runs/<ID>` runner design.

## Tests-first and fixes

- Add `tests/fixture_summary.py` and six `tests/test_fixture_summary.py` cases. The parser requires a **terminal, complete** JSON object with `mode`, `exit_code`, `n_cases`, and `provenance_errors`; missing/partial/unrelated output becomes `{}`, never a synthetic PASS. GitHub blob SHA-1 matches the locally tested files: helper `e587a9914b0ff9a42080704c5b30319f407c6cab`, tests `6e556594130badde87f30bfd721c27756ff6e9d3`.
- `test_uvlo_tur2.py`: default small fixture runs `--historical` and reads parsed stdout; test fails if the expected historical summary is absent. M4/M4b explicitly require unknown/unlocked run-id to fail at `LOCKED_RUN_PRECHECK`. The old three runner checks now reuse `test_locked_runner.LockedRunnerTests` with all **259 fake decks**; require preserved historical log/manifest, missing-executable rejection, abort = `INCOMPLETE`, success = isolated `COMPLETE` with Gear/100n. Their desired protections were not deleted.
- `test_uvlo_gates.py`: read-only historical stdout parsing, no write to `results/uvlo-verify.json`.
- `test_uvlo_tur5.py` and `test_uvlo_tur6.py`: small electrical gate fixtures use historical mode, avoiding false nonzero outcomes from the missing locked-run precheck. V53a missing run-id still requires exit 2; V53b historical is now checked from stdout; V53c correctly expects exit 2 for its unprovisioned mini-fixture. This is **not** a new acceptance PASS.
- `test_locked_verifier.py`: added full-code **planned** CLI tests with 259 synthetic complete-log decks lacking electrical measurements (must fail acceptance with exit 1, not false PASS) and incomplete manifest (must exit 2). Required dummy model/budget files are committed into the *temporary test fixture before fake run* to keep provenance clean. These tests were added but **not executed** in this session.

## Tests actually run this turn

| Executed locally | Verified |
|---|---:|
| `tests/test_fixture_summary.py` | **6/6 PASS** |
| Existing `test_locked_runner.py`, original local copy | **9/9 PASS** |
| `test_study_integrity.py`, original local copy | **27/27 PASS** |
| Existing extracted `test_verifier_provenance.py`, NOT full verifier | **7/7 PASS** |
| Existing `test_pkg05_run_selection.py`, helper-only | **9/9 PASS** |
| Existing `test_pkg05_historical_readonly.py`, helper-only | **8/8 PASS** |

Total **66/66 locally executed unit/synthetic tests**. These are *not* 66 tests of the modified complete GitHub verifier. Seven modified/added GitHub test files were checked by matching their remote blob SHAs and 16 source structure/flow assertions; this is **static verification, not executing those files**.

## Explicitly not verified

- The **full** `verify_uvlo.py` and the newly migrated Tur-2/Tur-5/Tur-6/Gates scripts have not been run as one integrated suite: no complete private repository checkout is locally available, and direct container GitHub clone cannot resolve github.com. `ngspice` is absent.
- The newly added full-CLI tests in `test_locked_verifier.py` are **pending**; electrical acceptance cannot be inferred from their expected assertions.
- No new 259 Gear/100n acceptance simulation, 20×2 50/25 ns convergence study, M3 causal trace experiment, WP1 A/B/C or 23/23 new regression run.
- Historical WP2 remains **161 PASS / 69 acceptance FAIL / 6 incomplete**; `num-study-tmax100n` reanalysis **6/20** and 9 actual solver aborts remain; WP1 **4 ESL missing**.
- H1 O1 instantaneous ≤12.0 V; H2 stable PRE/RUN/POST ≤11.1605 V; Vf≥18.0 V; M1 VIN-OK→EN≥60 ms; M3 inclusive [0,1.000] µs with any negative FAIL; M4 VGS≥6 V. No thresholds changed; R-DIP report-only.

**Decision:** PKG-06 fixture code migration committed; **full integrated verifier gate OPEN**. CI disabled, draft PR stays open, no merge or hardware approval.

**Next dependency:** run complete `test_locked_verifier.py` and all migrated legacy UVLO suites against a clean authenticated repo checkout. Fix actual failures without relaxing gates, then only consider a new frozen 259-deck ngspice acceptance run. Keep separate numerical/M3 diagnostics.

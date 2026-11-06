# PKG-10 — verifier integration on a hash-verified partial snapshot

Date: 2026-11-06, Europe/Istanbul. Starting remote HEAD: `31aec96124adcfc57111528c792849bf6ac4f932`. Test fixture repair commit: `53b097bc67bffeb76d4a82a53e0afe40ef126ca8`. PR #1 is draft. No merge or CI activation.

## Source and environment boundaries

Direct `git ls-remote https://github.com/siimsek/PDU.git refs/heads/wp/baseline-2026-10-24` returned HTTP 403 from the environment's network proxy; `gh auth status` says no host login. This was **not a complete Git checkout**, and clean-HEAD/integrity of the entire source tree cannot be asserted. Selected files were retrieved at the starting commit using the GitHub connector and locally checked as Git blobs. `evidence/pkg10-20261106/source-inventory.json` lists 42 inputs with Git blob and SHA-256. Of those, 41 match the starting HEAD; the one difference is the intentional fixture fix, whose local Git blob `ae2239cba47d1e41da230321f09b4f5ec9433212` matches commit `53b097bc67bffeb76d4a82a53e0afe40ef126ca8`. Tests after the fix used those local bytes before they were committed. This is a partial source snapshot, not a new clean full-tree acceptance run.

Actual verifier Git blob `589f4a5c2a80322631868a7a7fc083773ee4a6c0`; SHA-256 `383e73ab716f42c47866442393cec510864b60aaab62835c6837e06ccef70626`. `test_locked_verifier.py` blob `84ee5e8e5ebcd59cd93afaa92832d2bedfa3cd6a`, SHA-256 `03053187a8261fab80d70ff018e57f76d058f54205fd330193eefb1977312e0e`. Python 3.12.14, Git 2.52.0, KiCad CLI 9.0.2. `ngspice` executable absent; `libngspice` shared library present, reports 44.2, SHA-256 `8b24e526865425243ee57efa9dcbdde99e7220393eb77a1ab863e849a2e0d761`. `pytest` unavailable; these tests use Python stdlib. All logs and output locations below are relative to `docs/proposals/2026-10-25-uvlo/evidence/pkg10-20261106/`.

## Finding and fix: historical fixture dropped case evidence

Initial `tests/test_uvlo_tur4.py` returned **254/257, exit 1**, with W01s0, W06a and W06b failing: the helper parsed only stdout summary and omitted the actual case results. This was a fixture migration defect, not proof of an electrical defect. Raw RED: `tur4.log`, SHA-256 `2e9e993135c0a1345122aef033a7f356ffc9d9646a4a368159236be933d36fa8`.

`tests/test_uvlo_tur2.py` now wraps the actual verifier's `write_verification`: it calls the unmodified real writer first, captures its historical in-memory artifact in the temporary fixture, requires exactly one capture and equality with the printed terminal summary, and exposes its actual case map. Historical remains read-only; locked-run exclusive-write behavior remains delegated to the real writer. No verifier code, electrical acceptance limit, locked model or historical output was changed. Green `tur4-after.log`: **257/257, exit 0**, SHA-256 `ef63766f749ca5621f16335373c8edb6ac26b0ccd597043142c2563d3a9b5b35`.

## Test evidence and classification

All commands run in `simulation/proposals/2026-10-25-uvlo`, using the selected source snapshot. Unless specified, synthetic temporary Git/deck/log fixtures were used; they do not demonstrate the 259-deck acceptance. Exit is the Python process exit, not an electrical product verdict. Tests use custom row counters; no skip/error rows were reported in completed runs.

| Command | Time, TSİ | Actual result | Raw output |
|---|---|---|---|
| `python3 -m unittest -v test_locked_verifier test_pkg05_historical_readonly test_pkg05_run_selection` | 08:49:11–08:49:18 | 28 tests PASS, 0 FAIL/ERROR/SKIP, exit 0; includes 11 full-verifier synthetic fixture tests and False, 0.0, string and null deck RC rejection | `unit.log` |
| `python3 -u tests/test_uvlo_gates.py` | 08:54:32–08:55:59 | 13/13 PASS, exit 0; electrical judgement fixtures + computational budget | `gates-full.log` |
| `python3 -u tests/test_uvlo_tur2.py` | 08:53:21–08:53:24 | 31/31 PASS, exit 0 | `tur2-after.log` |
| `python3 -u tests/test_uvlo_tur3.py` | 08:53:21–08:53:23 | 45/45 PASS, exit 0 | `tur3-after.log` |
| `python3 -u tests/test_uvlo_tur4.py` | 08:53:21–08:53:33 | 257/257 PASS, exit 0 | `tur4-after.log` |
| `python3 -u tests/test_uvlo_tur5.py` (no executable) | 08:53:22–08:53:23 | 57 PASS, 3 FAIL, exit 1: L51/L52/L53 report `ngspice not found`; no solver was run | `tur5-after.log` |
| `PDU_CAPTURE_DIR=<evidence>/benches PDU_NGSPICE=<evidence>/ngspice-lib-adapter.py python3 -u tests/test_uvlo_tur5.py` | 08:54:23; end timestamp in log | 60/60 PASS, exit 0; 57 fixture/static/budget checks + 3 small **real libngspice-44.2 behavioral-model bench simulations**, using the limited local adapter | `tur5-libngspice-captured.log`, `benches/` |
| `python3 -u tests/test_uvlo_tur6.py` | 08:53:22–08:53:22 | 17/17 PASS, exit 0 | `tur6-after.log` |

All Tur/Gates commands above were wrapped with `timeout 150s` except Gates, wrapped with `timeout 300s`; Tur-5 library run used `timeout 120s`. `PYTHONDONTWRITEBYTECODE=1` was set. The tests ran before commit `53b097b`, from the same local fixture blob. One earlier full Gates attempt was interrupted while evaluating the E96 budget. A 35 s diagnostic (`gates-diagnostic.log`, timeout exit 124) showed `start_guarantee_status` → `search_c3` → `eval_c3`; the subsequent full run completed normally. No FAIL was reclassified as PASS.

The adapter is an experimental ctypes invocation of the actual installed shared solver, supporting only `-v` and this test's exact `-b -D ngbehavior=ltpsa b.cir` invocation. It is **not** the ngspice CLI, is not validated for the locked runner, and must not be used as a 259-deck acceptance substitute. The three original generated decks and solver callback stdout/stderr are retained under `benches/`; source `.include` paths reflect this local snapshot. Solver warned `can't find the initialization file spinit`; the models produced the recorded measurements. These behavioral benches are not physical measurements or proof of silicon latch behavior. The `PRE# = CLR# = low` simulated outputs both high, preserving the open U27 safety concern.

## Outstanding gates

No fresh locked 259-deck run or fresh 23-regression run was performed; no 20×2 convergence study, new OVP matrix, PCB validation or physical bench test was performed. Electrical acceptance remains **NOT VERIFIED / OPEN**, not PASS. The historical 161 PASS / 69 acceptance FAIL / 6 incomplete and 23 expected regressions are historical re-evaluation data, not these test results. WP1's 4 incomplete ESL cases and O1 no-latch limit failure, WP2 M3 causality, Bpath, O3 continuity, gate-ready and U27 CLR# all remain open. Simulations are not physical measurements.

Next: obtain a genuine full checkout at the latest branch HEAD and a genuine supported ngspice executable, verify the clean tree, locked 259 deck and 25 source blob identities, re-run the listed full tests, then only if prerequisites pass run the isolated locked 259-deck acceptance with no historical overwrite. Investigate physical-model failures with raw waveforms, not just helper tests. Keep CI disabled and PR draft.

The local evidence manifest is `evidence/pkg10-20261106/MANIFEST-SHA256.txt`; its SHA-256 is `70425643bb5460977dfaa094195c804d28510d4e1bea80b738f7be8c532653cd`. `sha256sum -c MANIFEST-SHA256.txt` returned all OK after excluding the manifest itself.

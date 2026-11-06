# PKG-11 — complete shallow checkout and integration retest

Date 2026-11-06, Europe/Istanbul. Source PR head: `0d0667511ad66683150c97fd8693b73b314ca02e`, tree `a0321ad8f291c56ad76df178efcba3211b258ba3`. PR draft, no merge or CI activation.

## Full working tree obtained and verified

Direct GitHub Git transport returned proxy HTTP 403 and `gh` is not authenticated. Instead, the authenticated GitHub connector retrieved the recursive tree and file blobs for the exact source commit. Every downloaded blob was hashed as a Git object before import. All 61 tree objects were built and matched their GitHub SHAs; the original commit object was reconstructed and checked to the exact GitHub HEAD SHA. Git's shallow boundary explicitly marks that commit: the working tree includes **all 2420 tracked paths**, but earlier commit history has not been fetched. This is a full working tree with shallow history, not a full-history clone. Do not use it as proof that historical commit-dependent provenance checks can run.

At 09:56:43 and 10:00:33 TSİ the actual HEAD and tree matched, `git status --porcelain=v1` was empty, and final `git fsck --full --no-reflogs` returned 0. Both complete proposal `sha256sum -c` manifests returned 0: WP2 704 lines, WP1 1244 lines (`manifest-uvlo.log`, `manifest-ovp.log`). An independent scan of all 2420 tracked paths found **2419 raw-byte blob matches and one raw mismatch** for `hardware/functional-blocks.kicad_sch`: `.gitattributes` explicitly checks it out with CRLF. `git hash-object` applies the clean filter, producing the correct indexed blob; normalized comparison **2420/2420**, exit 0. Both raw and filtered scan logs are preserved.

The real `run_uvlo.locked_inputs()` verified **259/259 deck Git blobs**, **25/25 locked input blobs**, and exact case identities. `stage_text()` verified all **259** deck staging transformations and include paths; `clean_status()` returned true. This is static staging, not a solver run or electrical verdict. Details and timestamps: `evidence/pkg11-20261106/lock-preflight.log`.

## Tests on the clean full tree

All listed commands ran against the source HEAD above with `PYTHONDONTWRITEBYTECODE=1`; captured raw output and timestamps are in `evidence/pkg11-20261106/`. Tur/Gates commands used `timeout 300s`. The exact source was clean before/after testing.

| Command | Actual result | Classification / output |
|---|---|---|
| `python3 -m unittest -v test_locked_verifier test_pkg05_historical_readonly test_pkg05_run_selection test_locked_runner` | 39 PASS / 0 FAIL / 0 ERROR / 0 SKIP; exit 0 | Synthetic fixtures, fake solver; `unit.log` |
| `python3 tests/test_uvlo_gates.py` | 13/13 PASS, exit 0 | Synthetic judgement and analytical budget; `gates.log` |
| `python3 tests/test_uvlo_tur2.py` | 31/31 PASS, exit 0 | Synthetic, static and analytical; `tur2.log` |
| `python3 tests/test_uvlo_tur3.py` | 45/45 PASS, exit 0 | Synthetic, static and analytical; `tur3.log` |
| `python3 tests/test_uvlo_tur4.py` | 257/257 PASS, exit 0 | Synthetic, static and analytical; `tur4.log` |
| `python3 tests/test_uvlo_tur5.py` | 57 PASS / 3 FAIL, exit 1 | L51/L52/L53 report `ngspice not found`; `tur5.log` |
| `python3 tests/test_uvlo_tur5.py` with `PDU_NGSPICE=<PKG10 lib adapter>` and `PDU_CAPTURE_DIR=<temporary benches>` | 60/60 PASS, exit 0 | Three actual `libngspice-44.2` behavioral-model bench runs, other checks synthetic/static; **not ngspice CLI**; `tur5-shared-lib.log`, `benches/` |
| `python3 tests/test_uvlo_tur6.py` | 17/17 PASS, exit 0 | Synthetic checks; `tur6.log` |
| `python3 -m unittest discover -s simulation/proposals/2026-10-25-uvlo/tests -p 'test_fixture_*.py' -v` | 13 PASS / 0 FAIL / 0 ERROR / 0 SKIP, exit 0 | Temporary real-Git fixtures; `helpers.log` |
| `python3 simulation/proposals/test_study_integrity.py` | 27/27 PASS, exit 0 | Synthetic provenance and Decimal boundaries; `study-integrity.log` |

An initial attempt to run `test_study_integrity.py` with `unittest discover` produced an ERROR/exit 1 because the standalone script executes checks and exits during module import. The original invocation and traceback are retained in `helpers.log`; its documented direct-script invocation above ran successfully. No product safety limit was altered.

## Acceptance remains blocked

The standard `ngspice` executable is not installed. Direct distribution network access is blocked. The installed shared library reports ngspice 44.2, but the PKG-10 ctypes bench adapter handles only a constrained invocation and is not validated as the product runner's executable. With `PDU_NGSPICE=/nonexistent/ngspice`, actual `run_uvlo.py --run-id pkg11-missing-exe-preflight -j 1` exited **3** with `PRECONDITION FAILED`; no run directory was created (`missing-ngspice-preflight.log`). This is an intentional negative preflight, not a 259-deck simulation.

Consequently new 259-deck acceptance, expected 23 regressions, 20×2 numerical convergence, WP1 OVP acceptance, electronics design closure, PCB acceptance and physical bench validation remain **NOT RUN / OPEN**. Historical 161 PASS / 69 acceptance FAIL / 6 incomplete is not a new result. No design or production acceptance is claimed. Old logs and model files were not overwritten.

Next: provide a genuine verified ngspice CLI executable in the local environment; confirm its provenance/version and perform Tur-5 without the adapter, then run the fixed 259-deck Gear/100 ns protocol on a fresh clean source HEAD with unique run ID, followed by independent verifier. Before running, verify current HEAD, no active process, all lock inputs and manifest/output isolation; account for the shallow Git history if historical comparisons are required. Do not substitute the shared-library adapter for an unvalidated acceptance runner.

Evidence manifest `evidence/pkg11-20261106/MANIFEST-SHA256.txt`, SHA-256 `0252dba46743e25aa294575e1c68b4924a205681a688981ead06ed3cb3af6b67`, `sha256sum -c` exit 0. Git, Python and KiCad versions are in `start.txt`; ngspice CLI was unavailable. The three behavioral benches are simulations, not physical measurements.

The evidence directory `.gitattributes` marks `*.log -text` so Git preserves the exact recorded solver-output bytes, including mixed CRLF/LF.

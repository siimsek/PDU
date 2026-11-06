# PKG-09 — UVLO per-deck return-code provenance type check

Date **2026-11-06**, Europe/Istanbul. Initial remote PR #1 HEAD: `3637d2abd2d4ab7f7653a5f07f553b1287a53c3d`. Branch `wp/baseline-2026-10-24`. PR open **draft**, no merge and no CI activation.

## Specific defect found in the actual GitHub verifier

The old `verify_uvlo.py` Git blob SHA-1 was `e0e3d7270209f0aed58c938ed813745806a5fae2`. In `provenance(cases, run_id)`, the individual deck process return code had been checked as:

```python
if r.get('rc') != 0: e.append(f'{n}: rc {r.get("rc")!r}')
```

This condition accepts `False` and floating `0.0` as if they were integer zero, since Python implements `False == 0` and `0.0 == 0`. An externally corrupted/edited manifest can therefore report a noninteger process code without this specific check raising any provenance error. This is a **P1 evidence-schema / provenance defect**, not a new electrical design failure; no acceptance criteria were modified. In contrast, the top-level `runner_exit_code` and the locked runner already use exact integer checking.

## Tests-first repair

1. **Regression test committed first**: `test_locked_verifier.py::VerifierProvenanceTests.test_deck_rc_must_be_exact_integer_zero` tries `False`, `0.0`, `"0"`, and `None` on the `uvlo-case000` row of the existing 259-deck fake fixture. It requires an explicit per-deck `rc` provenance error and retains aggregate runner return code 0. Commit `257590a176eb3a59aa30526683a3d4c71a51fee0`, test Git blob SHA-1 `84ee5e8e5ebcd59cd93afaa92832d2bedfa3cd6a`. **Full test is added but NOT EXECUTED** in the current environment.
2. **Verifier correction**: one predicate change to `type(r.get('rc')) is not int or r.get('rc') != 0`. Commit `96cea00891c467ae369b2ca4c61467b445351a3a`, new verifier Git blob SHA-1 `589f4a5c2a80322631868a7a7fc083773ee4a6c0`.
3. **Input lock**: `PKG02-PROTOCOL-LOCK.json` now binds the new verifier blob, preserving all other inputs and the same 259-deck matrix. Commit `6f0c6d6c716632ac3439d3ec9099b364e1e45258`. Re-read **259/259 deck and 25/25 source entries** through GitHub directory metadata and checked their Git blob SHA-1: **0 mismatch**.

## Actually executed, with precise qualification

| Test code | Actual result | Interpretation |
|---|---:|---|
| `test_deck_rc_policy.py`, using the exact Python predicate semantics before and after fix | **4/4 PASS** | **Isolated truth table**, not a `verify_uvlo.py` import or CLI integration run |
| Previously saved `PKG08-fixture-evidence.zip` historical fixture test `test_fixture_historical.py` | **7/7 PASS** | Real local Git, isolated test helper |
| Previously saved PKG08/P07 `test_locked_runner.py` | **11/11 PASS** | 259 synthetic decks and fake ngspice, not product electrical simulation |
| **Total executed this turn** | **22/22 PASS** | Isolated/synthetic only |
| Actual `test_locked_verifier.py` including new falsified-code cases | **NOT RUN** | Complete `verify_uvlo.py` local Git checkout unavailable |
| `tests/test_uvlo_tur2..6.py` and `test_uvlo_gates.py` complete integration | **NOT RUN** | Complete private checkout unavailable |
| Real ngspice / new acceptance | **NOT RUN** | No ngspice executable; no user hardware connected |

The GitHub file was inspected and the new code/test Git blobs confirmed, but a static inspection is **not an integration test**. An attempt to stage the complete 44537-character verifier locally was **not completed or validated**, and no claims rely on such a file. Direct container DNS to `github.com` fails, and the authorized GitHub connector exposes text in its own separate runtime rather than a local executable checkout.

A ZIP with the actual 22 test results, source snapshots of the already available synthetic helper files, and an evidence statement is available as a conversation attachment `PKG09-test-evidence.zip` (not part of repository proof).

## Engineering status remains unchanged

WP2 historical **161 PASS / 69 acceptance FAIL / 6 incomplete**; old 20×2 hash-verified Decimal reanalysis **6/20**, **9** real method aborts over **6** distinct cases; WP1 **4 ESL** incomplete. No new simulation, convergence, M3 causal edge trace, 23 regression rerun, PCB measurement or BOM procurement approval. H1 O1 instantaneous ≤12.0 V, H2 normal bus/O1 ≤11.1605 V, M1 ≥60 ms, M3 inclusive 0…1.000 µs with any negative/NaN/Inf FAIL, M4 ≥6 V; no relaxation.

**Decision:** A specific provenance-schema flaw has been corrected in code and protected by a committed unrun full-verifier regression; local isolated type semantics PASS. **Full verifier integration and product acceptance remain OPEN.** Preserve GitHub PR as draft; CI disabled; no PR comment/merge.

**Next step PKG-10:** obtain a genuine SHA-matching full verifier + test checkout via an authorized runtime and run the committed `test_locked_verifier.py` and historical Tur-2..6/Gates tests, including the new bool/float forged-manifest cases; fix any actual failing tests before scheduling a real frozen 259-deck acceptance simulation.

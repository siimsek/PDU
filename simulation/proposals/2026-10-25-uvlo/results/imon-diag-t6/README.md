# IMON-kink hypothesis diagnostic (Tur-6 UVLO-T6-02 / Tur-12 WP1-T12-01, review step 1) - NOT acceptance

Runner: `../../imon_diag.py` (commit with this README; provenance in `imon-diag.json`). Committed decks unchanged except
`.meas` removed, `.tran 10n <tstop> <tstart> <deck tmax> uic` window around the known abort, one `.print` line.
Behavioural baseline eFuse model `simulation/pdu-behavioral.lib` (read only, not modified). Simulation, not silicon.

## WP2 `dip0v-50us-typ-ttyp` (deck tmax 1 us)
* Abort reproduced: t = 0.26059 s, step 1.25e-18, node `imon_o1`.
* I(Vsense, XU3) crosses zero twice: +0.61 A -> -0.45 A at 260580.8 us, then -10.417 A -> +1.19e-11 A at 260589.9 us.
* `ena` 1->0->1 at 260587.2 us with `done` = 0.427 (< 0.5, soft-start branch of `Bpath`).
* In that branch `Bpath` drives the CLAMPED -2.1*ITRIP = -10.417 A REVERSE current while O1 is ~5.0 V and VOUT rises
  11.25 -> 16.90 V: energy is pushed from the 5 V output into the higher-voltage input -> the soft-start law of the
  baseline behavioural model is NON-PASSIVE here (model artefact, not a physical prediction).
* At V(P1,P4) = 16.9 V the hard `Bena` OVP threshold drops ena -> I(Vsense) ~ +1e-11 A; VOUT sticks at 16.9000 V and
  IMON toggles 0 <-> 2.358e-12 V (the `max(I,0)` kink) until the step collapses.
* Verdict: the review hypothesis is NOT rejected (zero crossing + IMON chatter at the kink present), but it is NOT the only
  discontinuity: the trigger chain is ena glitch -> non-passive reverse clamp -> 16.9 V `Bena` comparator. Smoothing `Bmon`
  alone is therefore not expected to be sufficient; this is not proven (eps study not run).

## WP1 `buck-short-c165-esr12m5-esl2n-typ` (deck tmax 100 ns)
* Abort time reproduced: 0.0122646 s, step 1.25e-19; the reported node is `pu_ovp` in this run vs `imon_s2e` in the
  committed acceptance log -> the "trouble with node" label is not a stable identifier of the cause.
* XU4 `ena` 0->1 at ~12.2642 ms; I(Vsense, XU4) crosses zero 30 times (range -1.197 .. +0.046 A); VOUT rings
  8.26 -> 13.33 -> 9.67 -> 12.37 V within ~0.2 us (2 nH ESL bank, unresolvable at tmax 100 ns).
* At the abort I(Vsense) = +0.046 A (away from the kink), IMON = 9.2 mV -> the kink is not the immediate cause in this
  deck; ESL ringing + hard comparator thresholds (pu_ovp) are the more likely mechanism (not proven).
* WP1 ESL decks remain INCOMPLETE; H1 with U3-removed is NOT shown; no conclusion from these decks.

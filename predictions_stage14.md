# Stage 14 predictions: what a venting cell can deliver to its neighbour

Committed and pushed before any Stage 14 bound is computed (brief of 16 November 2026; DECISIONS.md D150 to D157). Stage 14 asks what physics allows, path by path, for the rig of Fransson et al. (J. Power Sources 617, 234916, 2024): how much of what the trigger ejects can reach the half of the neighbour's can that faces it, and how fast, from published inputs alone, as a lower and an upper bound for each of six paths: radiation from the jet or flame of a cap-end vent (A1), heat from vented gas that passes the neighbour (A2), the jet of a sidewall breach (A3), solids and melt that land on or stay against the neighbour (A4), conduction through the holder (A5), and, in the parallel tests, the neighbour's own discharge into the shorted trigger (A6). Part A0 (the rig, the calorimetry, the tests' needs and the survey with its second reading) is recorded in D150 to D152 and in `results/stage14_survey.md`, `results/stage14_inputs.csv` and `results/stage14_needs.csv`; the design of every bound is D153.

## The predictions (the brief's, word for word)

- **P1.** The upper bound of radiation from a cap-end vent to the facing half is below 2 % of 76.74 kJ. Expectation: likely.
- **P2.** The upper bounds of the cap-end paths that are determinable (A1, A2, A5) sum to less than 5.96 kJ, the largest need among the seven matched times. Expectation: uncertain.
- **P3.** They sum to more than 0.26 kJ, the smallest. Expectation: likely.
- **P4.** The upper bound of a breach's jet facing the neighbour exceeds 5.96 kJ delivered within 21.39 s. Expectation: likely.
- **P5.** At least one of the six paths is not determinable from published inputs for this cell. Expectation: likely.
- **P6.** For the parallel tests the circuit's upper bound on the neighbour's own heating exceeds 1 kJ. Expectation: uncertain.

The expectations are the brief's and are not scored.

## Scoring (D155)

- **P1** holds if A1's upper bound on the total energy it delivers to the facing half, over the longest published duration of a flame, is below 0.02 times 76,741.25 J, that is 1,534.8 J.
- **P2** holds if the sum of the upper bounds within 21.39 s of those among A1, A2 and A5 that are determinable is below 5,962.4 J, M50_PP_Exp2's need at 21.39 s (`results/stage14_needs.csv`). The window is the one over which that need was read.
- **P3** holds if the same sum exceeds 263.5 J, M50_SP_Exp3's need at 21.39 s.
- **P4** holds if A3's upper bound for a breach whose jet faces the neighbour, within 21.39 s, exceeds 5,962.4 J.
- **P5** holds if at least one of A1 to A6 is not determinable under the rule of D153 (3).
- **P6** holds if A6's upper bound on the heat released inside the neighbour, in total, exceeds 1,000 J.

Each verdict is reported with the numbers it rests on and with the other readings beside it, unscored: P1 within 21.39 s, P2 and P3 with the totals, P6 within 21.39 s.

## What the design already fixes

D153 is written before any bound is computed, and its rules decide some outcomes before the ray tracing gives its numbers. They are stated here so that no verdict reads as a discovery it is not.

- No source places the flame relative to the neighbour, so A1's energy term takes the largest share of an emitter's directions that strike the facing half anywhere beyond the trigger's end plane. An emitter at the facing half's end edge sees the surface in a quarter of all directions, so that share is at least 1/4, and the energy term at least a quarter of the energy the ejecta can release in the rig (D153 (2)). A1's total bound is the smaller of that and its rate term over the longest published flame; the rate term could fall below 1,534.8 J only if the facing half saw almost nothing beyond the end plane. P1 is therefore expected to fail; its numbers show by how much, and the ray tracing shows what a flame held on the vent's axis would give.
- No source gives the share of the vent gas that passes the neighbour, so A2's energy term is the whole energy the ejecta can release, and its bound within 21.39 s is its rate term, a convective and radiative flux from published velocity and temperature over the facing half. That term is expected to exceed 5.96 kJ by a wide margin: P2 is expected to fail and P3 to hold.
- The share of the ejecta that leaves through a breach has no source (no breach occurred in the Databank's ten M50 tests), so A3's bound for a breach that faces the neighbour is the whole energy the ejecta can release, and the shortest published runaway (about 1.1 s, measured on an 18650 cell; about 2 s in nail tests that include the M50) lets it arrive within 21.39 s: P4 is expected to hold.
- A5 is not determinable by D153 (3): no source gives the material of the holder's inlets, their contact or the heat the holder receives. P5 is expected to hold.
- A6's energy term is the neighbour's stored energy, 65,520 J: P6 is expected to hold.

A failure counts as foreseen if this file records it as fixed by the design (the rule of the supplement's S2). What Stage 14 measures is how wide the bounds are and what would narrow each: the ray tracing of A1 and A2 (D153 (4), (5)), the shares of breach positions whose jets and melt strike the facing half (D153 (6), (7)) and the bounds of Part C.

## The run

No model run is made. The ray tracing (`src/stage14_view.py`), tested before this file on configurations whose answers are known (`src/test_stage14.py`, D157), is run for the rig only after this file is pushed, with the seeds and ray counts of D153.

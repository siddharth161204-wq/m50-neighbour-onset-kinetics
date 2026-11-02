# Stage 11 predictions: the bands the manuscript states

Written on 2 November 2026, after Part A0 (DECISIONS.md D111, pushed before this file was written, in commit f131c81) and before any run of the Stage 11 list. This file, the Stage 11 decisions (D112 to D117), the code that will make the runs (`src/stage11_run.py`, `src/stage11_inputs.py`, `src/stage11_laptop.py`, `run_stage11_windows.cmd`), the scoring (`src/stage11_score.py`), the checks (`src/stage11_checks.py`) and the tests (`src/test_stage11.py`, all passing) are committed and pushed together, before any run of the list.

Stage 11 asks whether the kinetic posterior and the published thermal ranges could account for three numbers the manuscript rests on: the spread of the fraction a test needs, the far face's overshoot with no delivery, and the whole-cell clock's reproduced times. It is small by design: four kinetic draws and four thermal draws chosen by rank before these predictions (D111), a few tests, no fitting. Its bands are over four draws a side, not over the posterior.

## The inputs

- **The kinetic draws** (D111 (1)): Stage 3's joint posterior draws ranked by the hottest node's onset at 33.2 kJ, 30 s and 500 mW/K, at the brief's ranks 5, 50, 151 and 196: draws 188 (6.25 s), 83 (10.23 s), 40 (16.04 s) and 184 (17.02 s), against the posterior mean's 11.48 s.
- **The thermal draws** (D111 (2)): of Stage 3's 30 Latin hypercube draws of the roll's published properties, the smallest and the largest conductivity across the layers, draws 2 (1.008 W/(m K)) and 1 (1.375 W/(m K)), and the smallest and the largest specific heat, draws 20 (849 J/(kg K), the cell 52.0 J/K) and 27 (1109 J/(kg K), 66.6 J/K), against the central 1.3 W/(m K) and 61.75 J/K. A thermal draw sets the neighbour's roll, resolved and lumped; the trigger's history stays at the central properties (D112 (2)).
- **The tests** (D111 (3)): of Stage 8's A4 set, the smallest trigger energy, M50_PT_Exp1, the largest, M50_SP_Exp3, and, the brief's "one nearest the median" being a tie, both M50_PP_Exp3 and M50_ST_Exp2 (on the author's answer). So the brief's "three tests" read "four tests" below.
- **The posterior-mean values** (Stage 8, `results/stage8_thresholds.csv`; Stage 9, `results/stage9_fractions.csv`): f*(C1) and f*(C2) of the four tests, (0.15, 0.1625] and (0.45, 0.4625] for M50_PT_Exp1, (0, 0.0125] and (0.0125, 0.025] for M50_PP_Exp3, 0 and (0.0125, 0.025] for M50_ST_Exp2, 0 and 0 for M50_SP_Exp3; f_max at the far face 0.075 for M50_PT_Exp1 and 0 for the other four low-maximum tests; the nine propagated tests' f_t(C2) (D111 (5)).

## What was known when these were written

- **P4 is already fixed by Stage 7's records.** At the low contact (200 W/(m2 K), central properties, f = 0) Stage 7's runs to 900 s put the far face of M50_PT_Exp3 at 100.39 C against its measured 118 C, of M50_ST_Exp1 at 126.96 C against 128 C and of M50_ST_Exp2 at 120.15 C against 133 C; only M50_PP_Exp3's exceeds its maximum there (121.63 C against 105 C). So the far face does not exceed the measured maximum at the low contact in three of the four tests, and P4, which asks that it do so at both contacts, fails before any Stage 11 run (D111 (4)). The thermal draws and the high contact are run and reported all the same. At the high contact Stage 7's run of M50_PT_Exp3 peaks at 137.87 C (above 118 C); the other three are new runs.
- **The posterior mean's E*(C2)**, from Stage 8's midpoints and the central ratio: M50_PT_Exp1 0.45625 of 27,875 J, 12,718 J; M50_PP_Exp3 0.01875 of 136,308 J, 2,556 J; M50_ST_Exp2 0.01875 of 144,261 J, 2,705 J; M50_SP_Exp3 0. Across the four tests at the posterior mean E*(C2) ranges over 12,718 J. For P3 to fail under a draw, one test's E*(C2) would have to move by more than that draw's range across the tests.
- **P5 and the zeros.** M50_SP_Exp3's f*(C2) is 0 at the posterior mean (its lumped neighbour crosses 255.7 C with no delivery, Stage 7). If it stays 0 under every draw of both kinds, both its bands are zero, the thermal one is not narrower, and P5 fails on that test. In the passive two-cell case Stage 3 found the hottest node's onset 0.027 times as variable over the thermal draws as over the kinetic posterior (standard deviations; README, Stage 3); a threshold under a delivery was not compared there, and no Stage 11 configuration was run for it.
- **P6.** Stage 9 found that near the measured times 0.001 of f moves the whole-cell crossing by 3.6 to 13.6 s. While the code was tested, one Part D run was made in full before these predictions (D116 (3)): M50_PT_Exp4 at 0.040625 under draw 188, whose lumped neighbour crossed at 191.0 s against 215.6 s at the posterior mean, 24.6 s earlier. M50_PT_Exp4 ended at its threshold in Stage 9 and is not among the six tests P6 counts.
- **Parts A, B, C2 and E3.** Nothing else of a Stage 11 configuration was computed: the short test runs went to 2 and 3 s.

## Definitions used for scoring

f* and E* are D113 (2)'s (the bracket's midpoint, the delivered energy at the central ratio), found by D113 (1)'s search from Stage 8's bracket to an interval of 0.02. The far face's peak, its overshoot and f_max are D114's (Stage 9's rule and search). The crossings are D115's. E1 to E4 are D116 (1)'s. A threshold above 1 enters as an unbounded value (D116 (2)).

## The predictions

The brief's predictions, word for word but for "three tests", which reads "four tests" (D111 (3)), each with its expectation as the brief gives it; they are not scored here.

- **P1.** For each of the four tests, f*(C2) under every kinetic draw lies within a factor of two of its posterior-mean value, or within 0.025 of it where the posterior-mean value is 0. Expectation: likely.
- **P2.** The same for f*(C1). Expectation: uncertain; the hot spot's onset is local and the kinetics set it.
- **P3.** Under every one of the eight draws, the range of E*(C2) across the four tests exceeds the largest within-test band of E*(C2) across the draws: the between-test spread is not a kinetic or thermal artefact. Expectation: likely.
- **P4.** In the four tests whose f_max is 0 at the posterior mean, the far face with no delivery still exceeds the measured maximum under at least three of the four thermal draws and at both contacts. Expectation: uncertain; the low contact and the smallest radial conductivity are the two that could remove it.
- **P5.** In each of the four tests the band of f*(C2) across the four thermal draws is narrower than its band across the four kinetic draws. Expectation: uncertain.
- **P6.** In at least two of the six tests whose time the posterior mean reproduced within 10 s, the crossing at that same fraction under at least one kinetic draw either does not occur by 900 s or moves by more than 60 s: the reproduced time sits on the knife edge Stage 9 found in f, and the kinetics move the edge. Expectation: likely.

### How each is scored

- **P1.** Holds if, for each of the four tests and each of the four kinetic draws, f*(C2) under the draw lies between half and twice its posterior-mean value (ends included), or, where that value is 0 (M50_SP_Exp3), is at most 0.025. A threshold above 1, or a chain that breaks, fails it. Each of the sixteen is reported with its bracket.
- **P2.** The same for f*(C1); the posterior-mean value is 0 for M50_ST_Exp2 and M50_SP_Exp3.
- **P3.** Holds if, under each of the eight draws, the range of E*(C2) across the four tests (the largest less the smallest) exceeds the largest within-test band of E*(C2) (over the four tests, the largest less the smallest of a test's nine values: the eight draws and the posterior mean). The ranges, the bands and their ratios are reported, and the same for C1, unscored.
- **P4.** Holds if, in each of M50_PT_Exp3, PP_Exp3, ST_Exp1 and ST_Exp2, the far face at f = 0 peaks above the measured maximum under at least three of the four thermal draws (central contact), and above it at the low contact and at the high contact (central properties). Every peak and overshoot is reported, with whether f_max stays 0 by Stage 9's rule.
- **P5.** Holds if, in each of the four tests, the band of f*(C2) over the four thermal draws (the largest less the smallest) is smaller than the band over the four kinetic draws; equal bands, both zero included, are not narrower.
- **P6.** Holds if, in at least two of M50_PP_Exp1, PP_Exp2, PP_Exp4, SP_Exp1, SP_Exp2 and SP_Exp3, at least one of the four kinetic draws gives no crossing by 900 s or a crossing more than 60 s from the posterior mean's at the same fraction. Every crossing, its shift from the posterior mean's and from the measured time, and D2's counts are reported.

E1 to E4, C2's f_max and E3 are reported, not scored.

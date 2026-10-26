# Stage 8 predictions: how much of the ejected energy the outcomes require

Written on 26 October 2026, before any Stage 8 run. This file, the Stage 8 decisions (DECISIONS.md D77 to D84), the code that will make the runs (`src/stage8_run.py`, `src/stage8_model.py`, `src/stage8_search.py`, `src/stage8_inputs.py`), the scoring script (`src/stage8_score.py`) and the checks (`src/stage8_checks.py`) are committed and pushed to the public repository before any Stage 8 run, and the commit hash and push time are recorded in the README and in `provenance/`. The eight predictions are the brief's, word for word, each with the brief's expectation; the rules below fix what the brief leaves open.

When this was written, no run of the neighbour in a Stage 8 configuration had been made. The code was tested on synthetic inputs only, and five sizing runs with cell 1 held at the ambient temperature (no trigger) were made (D83 (5)). But Stage 7's records, an energy balance and the sizing runs already bear on most of these predictions, and the next section says how, prediction by prediction, so that a verdict that was foreseeable is read as one.

## The inputs

- **Measured** (D64; `inputs/fransson2024/m50_tests_stage7.csv`). Fransson et al., Journal of Power Sources 617 (2024) 234916, Tables 3 (parallel) and 4 (series): sixteen tests, nine propagated (five in series, four in parallel) at 147 to 342 s.
- **The triggers** (D65, Stage 7's, read): 8,976.8 J (M50_PT_Exp1) to 54,303.7 J (M50_SP_Exp3), released over 21.39 s, at the central contact.
- **The ratio** (D77 (2)): the ejected-to-body ratio of the Databank's ten M50 nail tests, central their median, 3.105285, bracket 2.218460 (RUN194) and 4.156163 (RUN197). The ejected energy E_e = r E_b runs from 27.9 kJ (M50_PT_Exp1) to 168.6 kJ (M50_SP_Exp3).
- **The delivery** (D77 (4)): f E_e from the start of the trigger's release, a triangular pulse over 21.39 s (10 and 60 s, conditional), as a uniform flux over the half of the can facing the trigger (the bracket: the quarter of it nearest the cap); the lumped neighbour receives the same energy.
- **The electrical path** (D80): f_e = 0.05 and 0.2 of the stored 65.52 kJ, in the roll by volume over the trigger's release, in the eight parallel tests.
- **The gas layer** (D82): Hoelle, Zimmermann and Hinrichsen (2023), Eq. 28, Table V and Table VI's cell 2, on the split cell, in the three tests nearest the median trigger energy at f = 0.2.

## What was known when these were written

From Stage 7's records at the central contact (`results/stage7_runs/`, read and not recomputed), from hand estimates, which are marked as such, and from the sizing runs (`provenance/stage8_cost_test_*.json`), which lie outside every Stage 8 configuration:

- **f = 0 (Stage 7).** C1 (the hot spot at 255.7 C) is met in eight tests (M50_PP_Exp1, PP_Exp4, SP_Exp1, SP_Exp2, SP_Exp3, ST_Exp1, ST_Exp2 and ST_Exp4), so their f*(C1) is 0 by the brief's own rule; six are the hits of P1 and two (ST_Exp1, ST_Exp2) the false alarms of P2. C2 (the lumped neighbour at 255.7 C) is met in two (M50_PP_Exp1 and SP_Exp3), C3 (the lumped neighbour at 150 C) in fourteen. Where C1 is not met, the hot spot peaked at 248.0 C (PP_Exp3), 245.3 (PT_Exp2), 232.2 (PP_Exp2), 227.1 (PT_Exp4), 225.4 (SP_Exp4), 183.5 (PT_Exp3), 108.9 (ST_Exp3) and 71.0 C (PT_Exp1), at 29.7 to 113.9 s; the lumped neighbour, where C2 is not met, peaked at 67.8 C (PT_Exp1) to 233.2 C (ST_Exp1), at 248 to 337 s.
- **The delivery at the hot spot** (sizing runs, no trigger). 3 kJ over 21.39 s through the facing half took the hot spot from 25 C to 177.3 C at 13.9 s (a rise of 152.3 K), the face away to 69.6 C and the lumped neighbour to 71.5 C; at 37 s the hot spot was back at 70 C. 20 kJ took the hot spot to 255.7 C at 4.49 s, when 1.76 kJ had been delivered, and the lumped neighbour at 13.3 s, with 14.4 kJ delivered. By proportion (a hand estimate, as if the rise were linear in the energy), a neighbour heated by nothing else needs about 4.5 kJ delivered over 21.39 s for its hot spot to reach 255.7 C: f of about 0.16 of M50_PT_Exp1's E_e and 0.09 of M50_ST_Exp3's, less where the trigger's own heating adds to it. In the five tests whose hot spot peaked within 31 K of 255.7 C at f = 0, some hundreds of joules are expected to suffice, which is f below 0.0125, the search's smallest bracket from (0, 0.1].
- **The lumped neighbour** (an energy balance, a hand estimate: (255.7 C less the lumped neighbour's Stage 7 peak) times 61.75 J/K over E_e, with no loss, no reaction heat and no account of the delivery coming early). f*(C2) is about 0.42 (M50_PT_Exp1), 0.19 (ST_Exp3), 0.063 (PT_Exp3), between 0.017 and 0.038 in eleven others (0.009 for ST_Exp1), and 0 in PP_Exp1 and SP_Exp3.
- **At f = 0.2** (the same balance). f E_e over 61.75 J/K is 90 K (M50_PT_Exp1), 167 K (ST_Exp3) and 318 to 546 K in the other fourteen tests, delivered within 21.39 s: in those fourteen the lumped neighbour is expected to reach 255.7 C within the delivery, more than 120 s before any measured time to propagation (147 to 342 s); in ST_Exp3, whose own lumped peak was 100.1 C at 299 s, it is expected to reach it later, if at all.
- **The electrical path.** 13,104 J (f_e = 0.2) in a 61.75 J/K cell is 212 K before any loss, released over the trigger's release: every parallel test's hot spot is expected to reach 255.7 C with no delivery at all, so f*(C1) at f_e = 0.2 is expected to be 0, and the lowering to equal Part A's f*(C1): about 0.16 for M50_PT_Exp1 by the estimate above, under 0.05 for the other five parallel tests with f*(C1) above 0. 3,276 J (f_e = 0.05) is 53 K.
- **The cap end.** The same energy on a quarter of the area is four times the flux there, so the hot spot there is expected to reach 255.7 C with less delivered energy, where the facing half needs any. The lumped neighbour has no geometry, so f*(C2) cannot change with it (D79 (1)).
- **Monotonicity.** In each connection a larger trigger energy raises cell 1's temperature at every time (Stage 7's P6 held: the lumped neighbour's peaks follow the trigger energies without inversion), and E_e is in proportion to E_b; so f* is expected to fall with the trigger energy, with ties within the search's resolution among tests close in energy.
- **The gas layer** (sizing, no trigger, 20 kJ over 21.39 s, the split cell with the layer). The roll's hot spot peaked at 170.5 C at 17.5 s and did not reach 255.7 C within the 60 s run, while the can reached 1,702 C at 11.2 s; the same delivery without the layer took the hot spot to 255.7 C at 4.49 s. So in Part D the layer is expected to delay the hot spot's crossing at f = 0.2 by far more than the seconds the delivery takes, or to remove it. In the first form of the split (the lateral wall alone, D82 (3)) the roll's hot spot reached 255.7 C at 5.56 s at the bottom edge of the wall, where the delivered flux still entered nodes the roll and the can shared. None of the sizing runs' numbers enters a verdict.

## Definitions used for scoring

- **f\*** (D78 (2)): the bracket (lo, hi] in which the threshold lies, lo the largest fraction tried that does not meet the criterion and hi the smallest that does, at most 0.02 wide; 0 where Stage 7's run at f = 0 meets the criterion; above 1 where f = 1 does not. **f\* below x**: the criterion is met at a fraction at or below x (hi ≤ x, or f* = 0); **not below x**: it is not met at x or above (lo ≥ x, or above 1 for x ≤ 1). Every bound a prediction names (0.05, 0.3, 0.5) is decided this way (D78 (2)).
- **Criteria** (D81): C1, the hot spot reaches 255.7 C within 900 s (the run's own stop); C2, the lumped neighbour reaches 255.7 C (its own stop); C3, the lumped neighbour reaches 150 C (the stored series' crossing, D67 (1)).
- **Classes** (D81): hit, miss, false alarm, correct rejection, against the sixteen outcomes; the score is the hits and correct rejections over 16; a hit's time error is the predicted time less the measured time to propagation (model from the start of cell 1's release, paper from the trigger's runaway, D34).
- **Range of f\*(C1) over a group** (P2): from the smallest lower end (0 for a test at 0) to the largest upper end (unbounded if a test is above 1). Two ranges overlap if they share a point.
- **Inversion** (P6): two tests of one connection, the one with the larger trigger energy having its f* established higher: its lower end at or above the other's upper end (both ends of a 0 are 0; above 1 lies above every bracket). Brackets that overlap are a tie within the resolution, not an inversion.
- **Lowering** (P7, P8; D79 (3)): f*(Part A) less f*(variant), as the interval the two brackets allow. "Lowered" (P8) means established lower: where a variant ends in Part A's own bracket, both are halved on to an eighth of it (D79 (3)), and the variant must meet C1 at a fraction where Part A does not.

## The predictions

| | Prediction (the brief's, word for word) | Brief's expectation | Known before registration (above) | Study's expectation |
|---|---|---|---|---|
| P1 | Of the nine propagated tests, f*(C1) is 0 in the six Stage 7 hits and below 0.3 in the other three. | Likely; the hot spot is close to 255.7 C in several misses. | The first part by construction; for the second, the sizing estimate puts M50_ST_Exp3's f*(C1) near 0.09 or below, and PT_Exp4's and PP_Exp2's below 0.0125. | Holds. |
| P2 | Of the seven non-propagated tests, at least three have f*(C1) below 0.3 (the two Stage 7 false alarms at 0 among them), so the range of f*(C1) over the propagated tests and the range over the non-propagated tests overlap. | Likely. | The two false alarms at 0 by construction, and the six hits at 0, so the ranges share 0; by the sizing estimate every non-propagated test lies below 0.3, M50_PT_Exp1 (about 0.16) the highest. | Holds, with all seven below 0.3. |
| P3 | f*(C2) lies between 0.05 and 0.5 in at least twelve of the sixteen tests. | Uncertain. | By the energy balance, three tests (M50_PT_Exp1, ST_Exp3, PT_Exp3) lie between 0.05 and 0.5; eleven lie below 0.05 and two at 0. | Fails. |
| P4 | At f = 0.2 for every test, the whole-cell clock C2 predicts propagation in at least nine tests, and its crossing time lies within 60 s of the measured time in at least four of the propagated tests it predicts. | Uncertain; Stage 7 had one of eight within 60 s for C3 at f = 0. | By the balance at f = 0.2, fourteen or fifteen tests, crossing within the delivery in all but M50_ST_Exp3: more than 120 s before any measured time. | Fails on its second part. |
| P5 | At every common fraction of Part C, no criterion scores more than 12 of 16: the delivered heat moves the predicted count but not past the cap the outcomes set. | Likely. | Each criterion is expected to predict fourteen to sixteen tests at every common fraction; one that predicts all sixteen scores 9, and one that predicts all but M50_PT_Exp1 scores 10. | Holds. |
| P6 | Within each connection, f*(C1) and f*(C2) never increase with trigger energy (no inversion). | Likely; a check on the mapping. | By construction in the trigger and in E_e, unless the model's reaction or the delivery's timing breaks it. | Holds, with ties. |
| P7 | The electrical bracket at f_e = 0.2 lowers f*(C1) of the parallel tests by less than 0.1 in every test. | Uncertain. | 212 K of Joule heat is expected to take every parallel hot spot to 255.7 C with no delivery, so the lowering equals Part A's f*(C1), about 0.16 for M50_PT_Exp1. | Fails, on M50_PT_Exp1. |
| P8 | The cap-end geometry lowers f*(C1) in every sensitivity test where f* is above 0 and raises f*(C2) in none. | Likely for the first part, uncertain for the second. | The second part holds by construction (the lumped neighbour has no geometry); the first, four times the flux on a quarter of the area. | Holds. |

### How each is scored

- **P1.** The nine propagated tests. Holds if f*(C1) is 0 in the six Stage 7 hits (M50_PP_Exp1, PP_Exp4, SP_Exp1, SP_Exp2, SP_Exp3, ST_Exp4) and below 0.3 in the other three (M50_PT_Exp4, PP_Exp2, ST_Exp3). Each f* is reported.
- **P2.** The seven non-propagated tests. Holds if at least three have f*(C1) below 0.3, the two Stage 7 false alarms (M50_ST_Exp1, ST_Exp2) at 0 among them, and the range of f*(C1) over the nine propagated tests overlaps the range over the seven. Both ranges and the count are reported.
- **P3.** All sixteen tests. Holds if f*(C2) lies between 0.05 and 0.5 (not below 0.05, and below 0.5) in at least twelve; a test at 0 lies below 0.05. The count and each f* are reported.
- **P4.** The first-round runs at f = 0.2. Holds if C2 predicts propagation in at least nine tests and, among its hits, at least four have an absolute time error of at most 60 s. The count, the hits and every signed error are reported.
- **P5.** The first-round runs at f = 0.1, 0.2 and 0.3. Holds if each of C1, C2 and C3 scores at most 12 of 16 at each of the three fractions. All nine scores are reported, with Stage 7's at f = 0 beside them.
- **P6.** Within each connection, every pair of tests, for f*(C1) and for f*(C2). Holds if there is no inversion. Ties within the resolution are reported.
- **P7.** The eight parallel tests. Holds if, in every one, the largest lowering the two brackets allow (Part A's f*(C1) less that at f_e = 0.2) is at most 0.1. Each lowering is reported, with those at f_e = 0.05.
- **P8.** The five A4 tests. First part: in every one whose f*(C1) is above 0, the cap-end f*(C1) is established lower (D79 (3)). Second part: the cap end raises f*(C2) in none (by construction). Holds if both hold. Each shift is reported.

## Reported, not scored

- `results/stage8_thresholds.csv`: per test, f*(C1), f*(C2), the exploratory f*(C3) (A5), and, where they apply, the shifts with the 10 and 60 s deliveries, the cap end, the ratio's bracket and the electrical path.
- `results/stage8_scorecard.json`: Part C's scorecard at f = 0.1, 0.2 and 0.3, with Stage 7's at f = 0.
- `results/stage8_partd.json`: Part D, the hot spot's crossing with and without the layer, the split's own effect and the can's peak.
- V1 to V4 (D83), and any run that failed or chain that did not end.
- If P2's overlap appears, an exploratory line, written after the results, may fit the probability of propagation against the trigger energy (brief, pitfalls).

## Order of work

1. Commit and push this file with D77 to D84 and the code; record the hash and the push time.
2. `python3 src/stage8_run.py ejected` (A1); V1.
3. The runs on the cloud machine (`python3 src/stage8_run.py work`, two workers).
4. Score with `src/stage8_score.py`; V2, V3 and V4; the figure and the quoted numbers; an independent read of every registered number and verdict; then the note's Stage 8 lines.

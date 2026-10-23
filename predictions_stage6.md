# Stage 6 predictions: why the model does not propagate where the tests did

Written on 23 and 24 October 2026, before any Stage 6 computation. This file, the Stage 6 decisions (DECISIONS.md D50 to D59), the code that will compute Parts A and B (`src/stage6_crossings.py`, `src/stage6_run.py`), the scoring script (`src/stage6_score.py`) and the checks (`src/stage6_checks.py`) are committed and pushed to the public repository before any Stage 6 quantity is computed, and the commit hash and push time are recorded in the README and in `provenance/`. The seven predictions are the brief's, word for word, each with the brief's expectation; the rules below fix what the brief leaves open.

When this was written, no Part A quantity had been computed from the archived Stage 5 histories, no Stage 6 history of cell 1, and no run of the neighbour in the Stage 6 configuration. The code was tested on synthetic inputs only (D56 (4)). But Stage 5's published records already fix much of what these predictions ask, and the next section says what they fix, prediction by prediction, so that a verdict that was foreseeable is read as one.

## The inputs

- **Measured** (D33, D51 (4); `inputs/fransson2024/m50_tests.csv`). Fransson et al., Journal of Power Sources 617 (2024) 234916, Tables 3 and 4: the nine times to propagation, 147 to 342 s; the neighbour maxima of the seven tests that did not propagate, 71, 105, 118, 128, 133, 626 and 808 C; the sixteen trigger maxima, 164 to 832 C, median 704.5 C.
- **Release durations** (D52). 17.53, 21.39 and 25.24 s: the lengths of Section I, from the trigger's runaway to its maximum, of the two tests in the paper's supplementary Figure 10 (the trigger's maximum in Table 3 less a start at 25 C, over the Section I rate printed in the figure), and their median. Conditional.
- **Trigger energies** (D53). 33.2 kJ, Stage 5's: the Battery Failure Databank's largest cell-body energy of the ten LG M50 nail tests at 100 % state of charge. 107.0 kJ: the median corrected total energy of the same tests, ejecta included; bracket 91.2 to 110.8 kJ, conditional. In the model each is released in cell 1; the ejected part sizes cell 1's peak and reaches the neighbour only through cell 1.
- **Matched case** (D54). A pair of energy level and release whose cell-1 peak, at the central case, lies within 164 to 832 C in both connections. The central matched case is the median release with the qualifying energy (the total if both qualify). Exploratory, not scored: the energy that puts cell 1 at 704.5 C.

## What was known when these were written

From Stage 5's published results (`results/v12_numbers.json`, `results/v12_results.json`, D48), not recomputed here:

- **Cell 1.** At 33.2 kJ, cell 1 peaks at 547.6 C (9.84 s) with the 10 s release and 520.7 C (28.66 s) with the 30 s release in the central case, series (547.3 and 520.0 C in parallel), and at 513.3 to 552.5 C over every 33.2 kJ run. With the 30 s release its peak rose nearly in proportion to the energy, about 15 K per kJ: 307.8, 414.5 and 520.7 C at 18.67, 25.88 and 33.22 kJ (series). The matched releases lie between Stage 5's two, so at 33.2 kJ cell 1 should peak between 520 and 548 C, inside the measured range: 33.2 kJ is expected to qualify at all three releases.
- **Hand estimates, not runs.** 107.0 kJ released in cell 1 (61.75 J/K) would raise it 1,733 K adiabatically; the same proportion puts its peak near 1,600 C, less the stronger radiation at that temperature, far above the measured 832 C, so the total is expected not to qualify. The proportion puts the exploratory energy for 704.5 C near 45 kJ.
- **The neighbour.** Over all 5,248 Stage 5 runs the hottest node peaked at 112.2 to 226.7 C and the lumped neighbour at 104.5 to 180.6 C; neither reached 255.7 C. At 33.2 kJ and 25 C the hottest node peaked at 112.2 to 121.5 C at the low contact, 191.3 to 192.4 C at the central one and 225.9 to 226.7 C at the high one. The 200 draws at the central case moved the hottest node by 0.073 K at most in each connection. The central case's lumped neighbour peaked at 159.4 (series, 10 s), 160.1 (series, 30 s), 161.3 (parallel, 10 s) and 162.1 C (parallel, 30 s).
- **The 150 C crossings, D48 (2) (b), the grid and sens sets.** The lumped neighbour crosses 150 C at 145.3 to 174.1 s at the central contact on the grid (11 of 12 inside the window; 145.3 s, parallel, high tabs, 10 s, is not) and at 98.1 to 115.1 s at the high contact (none inside); at the low contact it never does. On the grid, then, it crosses in 24 runs, 11 of them inside the window. The sens set adds four crossings, three inside (146.7 s, parallel at 30 C, is not): 14 of 28. The v3 set, which repeats the central case on a finer mesh and with smaller steps (its lumped neighbour is the central case's, since the lumped model has no mesh), would add four more inside. The probe on the line of contact crosses at 6.8 to 29.8 s wherever it crosses (central and high contacts); the face away never reaches 150 C on the grid or in the sens set. The hottest node is at least as hot as the line of contact, so it crosses no later, and at the low contact it never reaches 150 C.
- **The face away's peaks.** Low contact 97.2 to 108.6 C, central 132.0 to 139.7 C, high 138.8 to 145.9 C over the fact set; 133.2 to 137.5 C over the 200 draws; 92.5 to 140.3 C over the sens set. Judging from these ranges, it exceeds 133 C in about two thirds of the 5,248 runs.

## Definitions used for scoring

- **Clocks** (D51 (2)). The hot spot (the hottest node), the resolved mean, the face away from the trigger at mid-height (the thermocouple's position, used for the comparison) and the lumped neighbour; the line of contact is reported separately.
- **Crossing** (D51 (3)). The first time a history reaches 150 C (or 255.7 C), interpolated within the stored samples. A crossing lies inside the measured window if it falls within 147 to 342 s inclusive.
- **Part A's runs.** The crossing times exist for the 48 runs that kept their series. P1 is scored on the 36 grid runs: one run per configuration of connection, contact, tabs and release, at the posterior-mean kinetics, the set that A3 breaks down by connection, contact and tabs. The sens set varies the central case one input at a time and the v3 set repeats it, so they would weigh the central case thirteen times over; they are reported beside the verdict, as are all 48 together. P2 needs only each run's peak, so it is scored on all 5,248 records.
- **Part B's runs** (D55). The registered sets: body (33.2 kJ), total (107.0 kJ), bracket, draws and v3; the exploratory peak-matched set is reported beside them and enters only P7, which the brief states for every case.
- **Reaching 255.7 C** (D35, D55 (2)). The hot spot reaches it when the resolved run's hottest node first does, within 900 s; the lumped neighbour when its single temperature does. Each run stops at its own crossing.

## The predictions

| | Prediction (the brief's, word for word) | Brief's expectation | Known before registration (above) | Study's expectation |
|---|---|---|---|---|
| P1 | Under the 150 C criterion applied to the Stage 5 runs, the lumped neighbour's crossing time lies inside the measured propagation window (147 to 342 s) in more than half of the runs in which it crosses; the hot spot's crossing time lies below 147 s in every run. | Likely; the Stage 5 central case already shows it. | Yes: on the grid the lumped neighbour crosses inside the window in 11 of the 24 runs in which it crosses; the hot spot crosses before 30 s where it crosses and never at the low contact. | Fails on its first part. |
| P2 | The face away from the trigger, at the thermocouple's position, exceeds 133 C (the largest neighbour maximum of the five non-propagating tests the note quotes) in fewer than half of the Stage 5 runs. | Uncertain. | Nearly: about two thirds of the runs exceed 133 C. | Fails. |
| P3 | With the trigger duration matched to the paper's measured trigger-to-peak times, the lumped neighbour's peak rises above its Stage 5 central value (159 to 162 C) by at least 20 K. | Likely; a longer release keeps the neighbour heated past its Stage 5 peak time. | Nearly: the matched releases lie between Stage 5's 10 and 30 s, which gave 159.4 to 162.1 C. | Fails. |
| P4 | With the trigger energy raised to the Databank's total including the ejected fraction, the model's trigger peak falls inside the measured range of the sixteen trigger peaks. | Uncertain; the Databank's split and the tests' cells need not agree. | Estimated by hand only: near 1,500 to 1,600 C. | Fails. |
| P5 | In the matched case (duration and energy), the resolved hot spot reaches 255.7 C in at least one run, and the lumped neighbour in none. | Close to even on the first part; likely on the second. | Nearly, if 33.2 kJ is the matched energy: at 33.2 kJ the hottest node peaked at 226.7 C at most. | Fails on its first part; holds on its second. |
| P6 | In the matched case over the 200 posterior draws, the share of draws in which the hot spot reaches 255.7 C lies between 10 and 70 % (central 35 %). | Uncertain. | Nearly, likewise: the draws moved the hottest node by under 0.1 K at the central case. | Fails, at 0 %. |
| P7 | In no case does the lumped neighbour reach 255.7 C before the hot spot does. | Likely. | No. | Holds: where both reach 255.7 C (at the total energy, if anywhere), the line of contact leads. |

### How each is scored

- **P1.** On the 36 grid runs. First part: of the runs whose lumped neighbour reaches 150 C, the share whose crossing lies within 147 to 342 s must exceed one half. Second part: in every run whose hot spot reaches 150 C, its crossing lies below 147 s. P1 holds if both parts hold. Reported beside it: the second part read strictly (every grid run must cross before 147 s, a run without a crossing counting against it), and both parts on the sens set, on the v3 set and on all 48 runs with series.
- **P2.** On all 5,248 Stage 5 records: the face away's peak above 133 C. P2 holds if that is so in fewer than half of them. Reported: by set and by contact, and the line of contact.
- **P3.** On the six body runs at the central configuration (the central contact and tabs), three releases, two connections. The reference of each connection is the higher of its two Stage 5 central-case lumped peaks (series 160.1 C, parallel 162.1 C). P3 holds if the lumped neighbour's peak is at least 20 K above its connection's reference in all six. The count is reported.
- **P4.** On cell 1's six histories at the central case with 107.0 kJ (three releases, two connections), from `results/stage6_trigger.json`. P4 holds if all six peaks lie within 164 to 832 C inclusive. The count, and the bracket's peaks (91.2 and 110.8 kJ at the median release), are reported.
- **P5.** On the posterior-mean runs of every qualifying pair (D54 (2)): the 14 runs of each. P5 holds if the hot spot reaches 255.7 C in at least one of them and the lumped neighbour in none. If no pair qualifies, P5 is not scored.
- **P6.** On the 400 runs of the draws set (200 draws × 2 connections, pooled, as Stage 5 pooled its shares). P6 holds if the share of runs in which the hot spot reaches 255.7 C lies within 10 to 70 % inclusive. Its binomial standard error and the share per connection are reported.
- **P7.** On every Part B run, the exploratory set included. In each run whose lumped neighbour reaches 255.7 C, the hot spot must reach it strictly earlier; P7 holds if no run fails that. The number of runs in which the lumped neighbour reaches 255.7 C is reported with the verdict, so that a hold without such a run shows as one, and so is the verdict on the registered sets alone.

## Reported, not scored

- A1 for every Stage 5 record, and A3's counts for every clock, by connection, contact, tabs and release, with the line of contact apart (`results/stage6_crossings.csv`, `.json`).
- For every Part B run: the five histories' peaks, times and 150 C crossings, cell 1's peak, and the 255.7 C crossings of the hot spot and the lumped neighbour (`results/stage6_matched.csv`, `.json`), beside the reference case (Stage 5's grid) and the measured values.
- The bracket set, and the exploratory peak-matched set with its energy.
- V3 (acceptance: under 1 % of the hot spot's peak rise above ambient, or of the time of its 255.7 C crossing where the central matched case reaches it); the energy account of every run (acceptance 1e-9 of the heat taken in); V1 and V2 (D56).
- Runs whose integration failed, if any (D55 (3)).

## Order of work

1. Commit and push this file with D50 to D59 and the code; record the hash and the push time.
2. Part A: `python3 src/stage6_crossings.py`; V1.
3. Part B: `python3 src/stage6_run.py trigger`, then record the run list's hash (D60) before any run of the neighbour; V2; the runs on the laptop.
4. Score with `src/stage6_score.py`; draw the figure; V3 and the energy accounts; an independent read of every registered number and verdict before the note is written.

# Stage 7 predictions: the ignition condition scored test by test

Written on 26 October 2026, before any Stage 7 run. This file, the Stage 7 decisions (DECISIONS.md D63 to D73), the code that will make the runs (`src/stage7_run.py`, `src/stage7_model.py`, `src/stage7_kernel.py`, `src/stage7_criteria.py`), the scoring script (`src/stage7_score.py`) and the checks (`src/stage7_checks.py`) are committed and pushed to the public repository before any Stage 7 run, and the commit hash and push time are recorded in the README and in `provenance/`. The eight predictions are the brief's, word for word, each with the brief's expectation; the rules below fix what the brief leaves open.

When this was written, no Stage 7 trigger energy had been found, no history of cell 1 for a Stage 7 trigger had been computed, and no run of the neighbour in a Stage 7 configuration had been made. The code was tested on synthetic inputs only, and one event run with cell 1 held at the ambient temperature (no trigger) was computed to size the runs (D70 (4)). But the published records of Stages 1, 5 and 6, and an energy balance, already bear on most of these predictions, and the next section says how, prediction by prediction, so that a verdict that was foreseeable is read as one.

## The inputs

- **Measured** (D64; `inputs/fransson2024/m50_tests_stage7.csv`). Fransson et al., Journal of Power Sources 617 (2024) 234916, Tables 3 (parallel) and 4 (series): sixteen tests, nine propagated (five in series, four in parallel) at 147 to 342 s; trigger maxima 164 to 832 C; the propagating neighbours' maxima 381 to 763 C.
- **One trigger per test** (D65). For each test the energy that puts cell 1's peak at the test's trigger maximum, at the central case in the test's connection, over the median release, 21.39 s, by the Stage 6 bisection between 0 J and the Databank's maximum, 110.83 kJ. The same energy at the low and high contacts, and with the 17.53 and 25.24 s releases at the central contact.
- **Levels** (D67 (2)). 255.7 C (the model's propagation, D35); 150 C (the paper's criterion); 138.5 C (the posterior-mean separator melting's peak at 5 C/min, D5).
- **The aged SEI** (D66). The SEI's initial amount 0 instead of 0.15; the SEI enters only its own decomposition.
- **The event** (D68). 65.52 kJ (18.2 Wh, the cell's stored electrical energy in LG Chem's specification) or 63.36 kJ (17.6 Wh, its minimum), released in the neighbour over 21.39 s from its 138.5 C crossing: at the hot spot (C4) or in the lumped neighbour (C5). A modelling choice, not a measurement.

## What was known when these were written

From the published records of Stages 1, 5 and 6 (`results/`, D19, D48, D60 to D62), read and not recomputed, and from hand estimates, which are marked as such:

- **Cell 1.** At the central case with the median release, cell 1 peaks at 531.7 C (series; 531.2 C parallel) with 33.2 kJ and at 704.50 C (series; 703.83 C parallel) with 45.15 kJ (D60), about 15 K per kJ. By that proportion (a hand estimate) the sixteen trigger maxima need about 9 to 54 kJ, all inside 0 to 110.83 kJ, so no test is expected to be out of range.
- **The neighbour at the central contact, median release** (Stage 6's records, `results/stage6_runs/`):
  - with 33.2 kJ the hot spot peaks at 192.2 C (series) and 191.9 C (parallel) and crosses 150 C at 15.9 s; the lumped neighbour peaks at 159.8 and 161.8 C and crosses 150 C at 167.9 and 157.9 s;
  - with 45.15 kJ (cell 1 at 704.5 C, the tests' median) the hot spot peaks at 255.1 and 254.8 C, 0.6 and 0.9 K short of 255.7 C; the lumped neighbour peaks at 196.0 and 199.0 C and crosses 150 C at 92.6 and 89.0 s;
  - at the high contact the hot spot reached 255.7 C at 16.7 s with 45.15 kJ, and the lumped neighbour at 198.2 to 235.9 s; at the low contact the hot spot peaked at 146.1 C at most.
- **What that suggests for each criterion at the central contact** (hand estimates by interpolation in the trigger maximum, between and beyond the two Stage 6 energies):
  - C1: only the tests above the median trigger maximum, 704.5 C, are expected to make the hot spot reach 255.7 C: six in series (723, 728, 755, 756, 788 and 832 C) and two in parallel (728 and 787 C), eight in all;
  - C2: none; the lumped neighbour stays near 225 C even at 832 C;
  - C3: the lumped neighbour reaches 150 C for trigger maxima above about 475 to 485 C, so for 14 tests (all but M50_PT_Exp1, 164 C, and M50_ST_Exp3, 282 C; M50_PT_Exp3, 507 C, is the closest), at about 75 s for the hottest triggers and later, up to about 200 s, near the threshold;
  - C4: the hot spot reaches 138.5 C for trigger maxima above about 385 C, so for the same 14 tests, at about 10 to 17 s;
  - C5: the lumped neighbour reaches 138.5 C for trigger maxima above about 430 C, the same 14 tests, at about 50 to 150 s;
  - C6 and C7: the aged SEI removes the SEI's heat, which in Stage 6's central matched case was 280.3 J in the lumped neighbour by 900 s (4.5 K) and less at the hot spot before its peak; so C6 is expected to predict at most C1's eight, and C7 the same 14 tests as C4.
- **The aged SEI and the first self-heating** (D19, Stage 1, exploratory; README table of the SEI's storage). After 30 days at 25 C, the SEI entirely converted, the hottest node's first self-heating at 0.15 K/min came at 202 and 211 C, by the first cathode reaction, and the lumped neighbour's at 180 C, against 108.4 C with the fresh SEI (SEI decomposition). So the aged SEI is expected to raise the hot spot's first self-heating temperature, not lower it.
- **Monotonicity.** In each connection a larger trigger energy raises cell 1's temperature at every time, and every clock of the neighbour with it (the coupling is a heat flow from the hotter cell), so the neighbour's lumped peak is expected to rise with the energy.
- **The event.** 65.52 kJ in a neighbour of 61.75 J/K is 1,061 K before any loss. For the hot spot's peak to stay below 763 C after a melt at 138.5 C, the cell would have to lose about 27 kJ more than its decomposition releases during the 21.39 s release, while its loss to the room at 1,000 C is of the order of 0.7 kW. In the sizing run (D70 (4); `provenance/stage7_cost_test.json`), with cell 1 held at the ambient temperature, so with no trigger at all and the contact drawing heat away, 65.52 kJ from 1 s took the neighbour's hot spot to 1,494.4 C, its resolved mean to 1,276.8 C, its face away to 1,084.9 C and the lumped neighbour to 1,219.2 C, with about 20.2 kJ of reaction heat. That run is outside every Stage 7 configuration, and none of its numbers enter a verdict.

## Definitions used for scoring

- **Registered contact** (D67 (5)): the central contact. The low and high contacts are the bracket, reported beside every verdict.
- **Criteria** (D67 (3)): C1 to C7 as the brief states them. A criterion predicts propagation for a test when its clock reaches its level within 900 s; its predicted time is that crossing (the run's own stop for C1, C2 and C6; the stored history's crossing for C3, C4, C5 and C7, D67 (1)).
- **Classes** (D67 (4)): hit, miss, false alarm, correct rejection, against the sixteen measured outcomes; the hit rate is the hits and correct rejections over 16; the time error of a hit is the predicted time less the measured time to propagation, with the model's clock from the start of cell 1's release and the paper's from the trigger's runaway (D34).
- **Part C runs** (D68): the event runs at 65.52 kJ at the central contact, C4 and C5 together, are the ones scored; the hot spot's peak after the event is the hottest node's largest temperature after the event's start. The lower bracket (63.36 kJ), the lumped neighbour, the resolved mean and the face away are reported beside it.
- **First self-heating** (P5): Stage 1's quantity (D7 to D9): the posterior-mean kinetics integrated along the run's stored hottest-node history (`src/onset_kinetics.py`, `integrate_along`, unchanged) from the run's own initial state, and the history's temperature when the self-heating rate first reaches 0.15 K/min.

## The predictions

| | Prediction (the brief's, word for word) | Brief's expectation | Known before registration (above) | Study's expectation |
|---|---|---|---|---|
| P1 | At the central contact with per-test triggers, C1 (hot spot at 255.7 C) predicts propagation in fewer than 9 of the 16 tests. | Likely; Stage 6 ignited the hot spot only at the Databank's total energy and, at the median peak, only at the high contact. | Nearly: by interpolation, the eight tests above the median trigger maximum are the candidates. | Holds, with eight. |
| P2 | At the central contact, C3 (lumped at 150 C) predicts propagation in 9 or more of the 16 tests, and its hit rate against the measured outcomes (hits plus correct rejections, over 16) is at least 10 of 16. | Uncertain; the paper's own criterion on the paper's own trigger peaks. | In part: by interpolation, 14 tests are predicted, which would give 8 hits and 1 correct rejection, a hit rate of 9 of 16; 10 if M50_PT_Exp3 falls short. | Fails on its second part, by one test. |
| P3 | Among the propagated tests that C3 predicts, the predicted crossing time lies within 60 s of the measured propagation time in at least half. | Uncertain. | In part: for the propagated tests, whose trigger maxima are 630 C or more but for one, the predicted crossings are expected at about 75 to 130 s; the measured times are 147 to 342 s. | Fails. |
| P4 | C4 (separator at the hot spot) predicts propagation in more tests than were measured (more than 9 of 16) at the central contact. | Likely; the hot spot passed 138.5 C in every Stage 5 run at the central and high contacts. | Nearly: 14 tests by interpolation. | Holds. |
| P5 | The aged SEI lowers the hot spot's first self-heating temperature but changes no C4 or C5 verdict at the central contact. | Likely, conditional on A4. | Yes, for the first part: with the SEI gone, Stage 1's first self-heating rose from 108.4 C to 202 and 211 C. | Fails on its first part; its second part is expected to hold. |
| P6 | Ranking the sixteen tests by trigger energy ranks the neighbour's lumped peak in the same order within each connection (no inversions). | Likely; a check on the mapping, not a result. | By construction, unless the integration breaks it. | Holds. |
| P7 | The series and parallel halves receive the same predicted propagation count within one, for every criterion, at the central contact. | Likely; the model distinguishes the connections by a tab only, and the measured counts (5 of 8 and 4 of 8) differ by one. | In part: the trigger maxima differ between the halves, six series tests and two parallel ones lying above the median. | Fails, on C1 (and C6). |
| P8 | In the Part C event runs at the central contact, the neighbour's resolved peak after the event lies inside the measured range of propagating neighbour maxima (381 to 763 C) in at least half of the runs. | Uncertain. | Nearly: by the energy balance, and in the sizing run with no trigger, the hot spot peaks near 1,500 C. | Fails, with no run inside. |

### How each is scored

- **P1.** C1 at the central contact: the number of the sixteen tests whose hot spot reaches 255.7 C (the run's own stop, within 900 s). P1 holds if it is 8 or fewer. Reported: the count at the low and high contacts, and the classes.
- **P2.** C3 at the central contact. First part: the number of tests whose lumped neighbour reaches 150 C is 9 or more. Second part: hits plus correct rejections are 10 or more of 16. P2 holds if both hold; each part is reported.
- **P3.** The hits of C3 at the central contact. For each, the absolute time error; P3 holds if at least half of them (twice the number within 60 s at least the number of hits) lie within 60 s inclusive, and fails if C3 has no hit. Every error is reported, signed.
- **P4.** C4 at the central contact: the number of tests whose hot spot reaches 138.5 C. P4 holds if it is 10 or more.
- **P5.** At the central contact, both parts over the sixteen tests. First part: for each test where the fresh or the aged run's hot spot self-heats at 0.15 K/min, the aged run's temperature at that rate exists and is lower than the fresh run's (a test where only the aged run self-heats counts as lowered; a test where neither does is left out); it holds if every compared test is lowered. Second part: the aged runs' C4 verdicts (C7) and their C5 verdicts (the aged lumped neighbour's 138.5 C crossing) equal the fresh runs' C4 and C5 verdicts in all sixteen tests. P5 holds if both parts hold. Reported: each test's two temperatures and the reaction then dominant.
- **P6.** At the central contact, within each connection, every pair of tests with the lower energy first: an inversion if the lower-energy test's lumped neighbour is strictly hotter, its peak higher, or, since a lumped neighbour that reaches 255.7 C stops there (D35), it reaches 255.7 C and the other does not, or both do and it does first. P6 holds if there is no inversion in either connection. Ties and the low and high contacts are reported.
- **P7.** For each of C1 to C7 at the central contact, the predicted propagations among the eight series tests and among the eight parallel tests. P7 holds if the two counts differ by at most one for every criterion. Every count is reported.
- **P8.** The event runs at 65.52 kJ at the central contact, those timed by C4 and those timed by C5 together. P8 holds if the hot spot's peak after the event lies within 381 to 763 C inclusive in at least half of them. Reported: by criterion; the lumped neighbour's, the resolved mean's and the face away's peaks; the lower bracket; and whether every clock peaked before the run's end.

## Reported, not scored

- The scorecard of seven criteria by three contacts (`results/stage7_scorecard.json`): for each, the predicted count, hits, misses, false alarms, correct rejections, the hit rate, the predicted times and the signed time errors; and one row per test, contact and criterion (`results/stage7_pertest.csv`).
- Every run's clocks: peaks, their times and the crossings of 138.5, 150 and 255.7 C (`results/stage7_crossings.csv`).
- C1 to C5 at the central contact with the 17.53 and 25.24 s releases, and C4, C5 and C7 at the 2.5 and 97.5 % points of the posterior's separator melting temperatures (D67 (6), D71).
- Part C: every event run's peaks after the event, beside the measured neighbour maxima (`results/stage7_events.csv`).
- The triggers: the sixteen energies, the peak-to-energy table, and cell 1's peaks at the other contacts and releases (`results/stage7_triggers.csv`).
- V1 to V4 (D70), and any run that failed.

## Order of work

1. Commit and push this file with D63 to D73 and the code; record the hash and the push time.
2. `python3 src/stage7_run.py triggers`: the sixteen energies, the peak-to-energy table and the separator's spread; record the run list's hash; V1.
3. The runs on the laptop: Part A, then the Part C list (its hash recorded) and Part C.
4. Score with `src/stage7_score.py`; draw the figure; V2, V3 and V4; an independent read of every registered number and verdict; then the note's Stage 7 lines.

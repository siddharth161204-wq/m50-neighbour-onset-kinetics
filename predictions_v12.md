# Stage 5 predictions (version 1.2.0): the resolved and the lumped neighbour against measured two-cell propagation

Written on 21 October 2026, before any Stage 5 run. This file, the Stage 5 decisions (DECISIONS.md D33 to D44), the model and harness that will run it (`src/v12_model.py`, `src/v12_mesh.py`, `src/v12_kernel.py`, `src/v12_run.py`) and the scoring script (`src/v12_score.py`) are committed and pushed to the public repository before any Stage 5 run, and the commit hash is recorded in the README. The seven predictions are the Stage 5 brief's, word for word; the rules below fix what the brief leaves open. The study's expectation stands beside each, reasoned by hand from the inputs. When this was written no Stage 5 quantity had been computed: no history of cell 1 in the contact configuration, and no run of either neighbour in it. The checks made before (V1, V2 and the kernel check, D41 and D44) used none.

## The measurements

Fransson, Pfaff, Broche, Buckwell, Kirchner-Burles, Reid, Schopferer, Rack, Finegan and Shearing, Journal of Power Sources 617 (2024) 234916 (CC BY 4.0), Tables 3 and 4, as recorded in `inputs/fransson2024/m50_tests.csv` (D33). Two LG M50 cells in direct contact, joined by welded tabs, the trigger cell penetrated by a nail, a thermocouple at the middle of each cell's surface.

| Connection | Propagated | Times to propagation (s) | Mean and SD (s) |
|---|---|---|---|
| Parallel | 4 of 8 | 272, 152, 147, 275 | 211.5, 71.6 |
| Series | 5 of 8 | 177, 342, 223, 149, 210 | 220.2, 74.0 |
| Both | 9 of 16 (56 %) | 147 to 342 | 216.3 |

- "a minimum of 150 ◦C is required in the neighboring cell in order for propagation to occur";
- "the average heat rate for propagation to occur was 0.4 ◦C/s compared to 0.1 for non propagating cells", averaged over Section 2, from the trigger cell's maximum to the neighbour's runaway onset;
- the time to propagation is read from the trigger cell's thermal runaway to the onset of the neighbour's (D34);
- the failure categories, the four "cell movement" tests and the two non-propagating tests with high neighbour maxima are kept as the paper classifies them (D33 (3)).

The tests include venting, ejecta and flame. The model has conduction and radiation only, so it should, if anything, propagate later than the tests did.

## What was known when these were written

- **The paths of the central case** (D36 to D38). Contact and wedge 0.1701 W/K (low 0.0503, high 0.2332), about ten times the two-cell study's 2 mm gap (0.0174 W/K). Tabs 6.8 mW/K at the neighbour's base in series, at its cap and base in parallel. Radiation between the cans (view factor 0.1817), as heat exchanged per kelvin of difference: 0.014 W/K with both cans near 200 to 230 C, 0.02 to 0.03 W/K with cell 1 at 400 to 500 C. Room losses per cell, as heat lost per kelvin above ambient: 0.074 W/K at 100 C and 0.10 W/K at 230 C (0.15 W/K for a small change around 230 C).
- **Hand estimates, not runs.** Cell 1's release of 33.2 kJ would raise it 538 K adiabatically; shared equally by both cells it would raise them 269 K. With the contact alone, the pair evens out on a time scale C/(2G) of 181 s (614 s and 132 s at the low and high contact). That is the scale of the measured times. The room losses per cell are of the order of the contact itself, so the lumped neighbour should peak well below the pair's shared temperature: a linear two-node estimate (an impulse of 33.2 kJ; contact, radiation and tabs about 0.20 W/K; room losses 0.10 or 0.15 W/K per cell, or 0.17 W/K for the hot cell 1 and 0.08 W/K for the neighbour) has time constants of about 110 to 125 s and 410 to 620 s, and puts the neighbour's passive peak near 145 to 170 C, 200 to 250 s after the release (about 100 C at the low contact and 170 C at the high one). If the line of contact rises about a third of the way from the neighbour's bulk to cell 1 (a contact path of 2.4 W/(m K) against a spreading path into the roll of roughly 5 W/(m K)), the resolved hot spot sits near 190 to 200 C for the first few minutes. The posterior-mean kinetics of the fresh cell self-heat at 0.15 K/min at 108.4 C and are net endothermic at 150 and 180 C while the separator melts (−1.0 and −50.9 K/min in the fresh state). Room losses cool a lumped cell by some 13 K/min at 175 C and 20 K/min at 230 C; once the separator has melted, the fresh cell's self-heating is 3.7 K/min at 200 C, 21 K/min at 220 C and 56 K/min at 230 C, so the lumped cell must pass about 220 C, by heating from cell 1, before its own reaction can carry it on to 255.7 C, and a node, which also loses heat into the rest of the roll, at least that.
- **The checks** (D41, D44, `results/v12_checks.json`), none of which used a Stage 5 history of cell 1:
  - V1: every boundary path of the Stage 5 cell on a uniform field equals the lumped formula to 2.3e-16; the brief's analytic steady case (cell 1 held at 100 C, the neighbour isothermal, contact and convection) is met to 5.3e-5 of the rise, against the 1 % acceptance; the energy accounts of a passive and a reactive Stage 5 run on synthetic inputs close to 8.9e-12 and 4.5e-10.
  - V2: with the two-cell configuration switched back, the lumped pair reproduces all 42 archived cell-1 histories character for character, and the resolved model's arrays equal the published model's exactly. Through the Stage 5 loop the archived passive series come back within 1.3e-12 K, and Stage 1's onsets from them to the 0.01 s reported. With the published numpy step the Stage 2 headline case comes back with identical band entries (19.23, 20.54 and 22.00 s), peaks, step counts and lumped node; with the compiled step all five Stage 2 cases come back within 3.2e-14 s and 8.0e-13 K.
  - The compiled step against the numpy one on synthetic node states: rates within 1.4e-14 relative, one step identical in the temperatures and within 1.1e-16 in the amounts.
- **The cost.** At about 28 ms a step on the 19,355-node mesh, two runs at a time on this machine's two cores, a run without propagation takes some 4 to 5 minutes of computing and the 5,248 runs some 80 to 190 hours, depending on how many stop early. The author asked that they run on his 24-core laptop, one per core (D43 (4)).

## Definitions used for scoring

- **Central case.** The posterior-mean kinetics, the central contact conductance (2,000 W/(m2 K)), the central tab conductance (6.8 mW/K per tab), 33.2 kJ, 25 C, both releases (10 and 30 s) and both connections: four runs of the grid set (D43 (2)). P1 to P5 are scored on all four.
- **Propagation and its time** (D34, D35). The resolved neighbour propagates when its hottest node first reaches 255.7 C within 900 s of the start of the release; the lumped one when its single temperature does. The time to propagation is the time of that crossing, measured from the start of the release.
- **Mid-surface temperature and heating rate** (D39). The surface temperature at the axial middle on the face toward the trigger (θ = 0, the line of contact) and on the face away from it (θ = 180 degrees), at the resolved propagation time; and its mean heating rate over the 60 s before it.
- **Faces.** The paper does not say which face carried the thermocouple. P3 and P4 are scored on each face. Each holds only if it holds on both faces, fails if it fails on both, and is "split" otherwise; a split is reported as such and counted as not held.
- **Propagation share.** The share of the 4,800 runs of the factorial set (200 draws × 3 contacts × tab 5 and 10 mW/K × 2 releases × 2 connections) in which the resolved neighbour propagates, pooled over both connections, as the measured share is. The share per connection and the lumped neighbour's share are reported.
- **Spread decomposition** (P7), for each connection at the 30 s release. The thermal standard deviation is taken over the nine grid runs at the posterior-mean kinetics (3 contacts × 3 tab conductances); the kinetic one over the 200 draws at the central case. Both use ddof 1 and only the runs that propagate, and the number that do not is reported beside each, as Stage 3 did. The ratio is thermal over kinetic.
- **Runs that do not propagate.** A prediction about a propagation time or a mid-surface value is not met in a run without propagation. P2 holds in a case where the lumped neighbour does not propagate; it fails where the lumped one propagates and the resolved one does not.

## The predictions

| | Prediction (the brief's, word for word) | Study's expectation |
|---|---|---|
| P1 | At the central contact conductance with the posterior-mean kinetics, the resolved neighbour propagates in both connections, and its time to propagation lies within the measured M50 range, 147 to 342 s. | May fail: by the estimates above the hot spot stays below 255.7 C, or, if the line of contact rises further, reaches it within the first minute |
| P2 | In both connections the lumped neighbour propagates more than 20 s later than the resolved one, or not at all within 900 s. | Held, most likely as "not at all": its passive peak should lie near 145 to 170 C |
| P3 | At the resolved model's propagation time, its mid-surface temperature lies between 150 and 255.7 C: the hot spot leads the surface a thermocouple sees. | Toward the trigger, held if propagation occurs (that face is the line of contact); away from it, may fail below 150 C |
| P4 | The resolved model's mean mid-surface heating rate over the 60 s before propagation lies between 0.2 and 0.8 C/s (measured about 0.4). | Uncertain |
| P5 | The predicted series and parallel times differ by less than 30 s (the measured means differ by 8 s). | Held if both propagate: the tabs carry 4 to 8 % of the contact path |
| P6 | The propagation share lies between 30 and 90 % (measured 9 of 16, 56 %). | May fail low: the model lacks the vent, ejecta and flame heat, and the estimates above fall short of 255.7 C at the central contact |
| P7 | The contact and tab range carries more of the spread in the predicted time to propagation than the kinetic posterior does (ratio above 1), the reverse of Stage 3's finding for onset. | Held if enough runs propagate to give both spreads: the contact range changes the path 4.6-fold |

### How each is scored

- **P1.** Held if the resolved neighbour propagates in all four runs of the central case, each within 147 s to 342 s inclusive.
- **P2.** In each of the four runs of the central case, held if the lumped neighbour does not propagate within 900 s, or if both propagate and the lumped time exceeds the resolved one by more than 20 s. P2 holds if it holds in all four.
- **P3.** On each face, held if in all four runs of the central case the resolved neighbour propagates and that face's mid-surface temperature at the propagation time lies between 150 C and 255.7 C inclusive. Faces as defined above.
- **P4.** As P3, with the mean heating rate over the 60 s before propagation, between 0.2 and 0.8 C/s inclusive.
- **P5.** For each release, the absolute difference between the series and the parallel resolved times of the central case. Held if both connections propagate at both releases and both differences are below 30 s.
- **P6.** Held if the propagation share of the factorial set lies between 30 % and 90 % inclusive. Its binomial standard error is reported.
- **P7.** Held if the ratio exceeds 1 in both connections. It is not met in a connection where fewer than two runs of either set propagate.

## Reported, not scored

- The central case and every grid run: both neighbours' times or peaks, the mid-surface values on both faces, where the hottest node is at propagation, cell 1's temperature at that moment and its maximum.
- The time to propagation on the other reading, the length of Section 2 alone (D34), and the mid-surface heating rate over the model's Section 2 analog (D39).
- The propagation shares per connection and of the lumped neighbour, and the factorial's times by connection, beside the measured ones.
- The sensitivities at the central case: ambient 20 and 30 C, and the Databank nail tests' minimum and median energies.
- V3 (D44): every mesh spacing halved, and every step limit halved, at the central case with the 30 s release; acceptance a change of the time to propagation below 2 % (of the peak rise of the hottest node, where the central case does not propagate). The energy account of every run (acceptance 1e-9 of the heat taken in).
- Runs whose integration failed, if any (D43 (3)).

## Order of work

1. Commit and push this file with D33 to D44, the model, the harness and the scoring script; record the hash in the README.
2. Run the sets in the order of D43 (2): grid, sens, v3, draws, fact.
3. Score with `src/v12_score.py`; draw the figure; write the records.
4. V4, an independent read of every registered number and verdict, before the note is written.

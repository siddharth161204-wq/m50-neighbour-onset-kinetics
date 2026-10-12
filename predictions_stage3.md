# Stage 3 predictions: kinetic and thermophysical uncertainty

Written on 12 October 2026, before any kinetic draw is integrated along an archived temperature history of the two-cell study (doi:10.5281/zenodo.23253738). This file is committed and pushed to the public repository before Stage 3a runs, and the commit hash is recorded in the README. The thresholds and the brief's central estimates are those of the Stage 3 brief; the study's own central estimates are added beside them, made as described below.

## What was known when these were written

- Stages 1 and 2, with the posterior-mean kinetics. At 33.2 kJ, 30 s and 500 mW/K the hottest node starts to self-heat at 0.15 K/min at 11.48 s and the lumped node at 37.88 s, both by SEI decomposition at 108.4 C. The smallest busbar conductance at which only the hottest node starts is 100 mW/K (21.5 kJ, both releases), and only the hottest node also starts at 8.75 kJ and 500 mW/K.
- The 200 kinetic draws (DECISIONS.md D22) and V4. Under its registered acceptance (D23) V4 failed (commit f9cabc7). The central 95 % of the main-cluster T_in ran from 146.3 to 191.4 C, against 169.0 to 198.0 C. After the failure was reported, the author chose to amend V4 (D25, commit 1e835d9). Under the amendment V4 passes: the mean plus and minus two standard deviations is 161.9 to 195.7 C, and its edges lie within 2.8 and 2.0 C of the paper's once measured from the emulation's own T_in of the mean model. The main cluster holds 82 % of the draws, against the paper's 76 %. Delayed shorts are 7.5 % against 7 %, and draws with no short 10.5 % against 17 %.
- Each draw's onset temperature on two synthetic linear ramps from 25 C, integrated with the Stage 1 driver, and the archived histories read as temperature series only (no kinetics integrated along them). Script: `src/predictions_stage3_estimates.py`; record: `results/stage3_prediction_estimates.json`.
  - The ramps are 15 K/s, the hottest node's heating rate near 108 C in the headline case, and 3 K/s, the lumped node's.
  - On the 15 K/s ramp the draws start between 59.2 and 209.8 C (2.5 and 97.5 percentiles), median 107.9 C. The mean model starts at 108.4 C, and 173 of the 200 starts are SEI decomposition.
  - On the 3 K/s ramp the draws start between 59.2 and 191.0 C, all by SEI decomposition.
- The thermophysical ranges of Stage 3b are not yet sourced, so P4 and P5 carry the brief's estimates only.

## Definitions used for scoring

- **Onset.** A history's onset is the first time its kinetic self-heating rate reaches 0.15 K/min within 900 s, with Stage 1's numerics (D26).
- **Headline case.** 33.2 kJ, 30 s release, 500 mW/K (`two_E33223_tau30_G0.5`).
- **Draws.** Shares are over all 200 kinetic draws. No draw is dropped: a draw in the paper's outlier classes counts like any other, and its fraction is reported separately.

## The predictions

| | Prediction (the brief's threshold) | Brief's central estimate | Study's central estimate |
|---|---|---|---|
| P1 | At the headline case the hottest node reaches 0.15 K/min before the lumped node in more than 95 % of kinetic draws | 99 % | 100 % |
| P2 | At the headline case the central 95 % interval of the hottest-node onset time is narrower than 20 s, and the lumped node's is wider than 20 s | 8 s and 40 s | 9.2 s and 64 s |
| P3 | The smallest conductance at which only the local chemistry starts is 100 mW/K in more than half the kinetic draws, and never above 200 mW/K | 70 % at 100 mW/K | 18.5 % at 100 mW/K, and 10.5 % at 500 mW/K: expected to fail on both counts |
| P4 | For the hottest-node onset time the thermophysical standard deviation exceeds the kinetic one, ratio above 1.5 | 3 | none made |
| P5 | For the lumped onset time the kinetic standard deviation exceeds the thermophysical one, ratio above 1.5 | 2 | none made |
| P6 | Fewer than 10 % of kinetic draws show the paper's early-SEI outlier behaviour at the hottest node, an onset before the node reaches 100 C | below 10 % | 36.5 %: expected to fail |

### How each is scored

- **P1.** The share of the 200 draws in which the hottest node's onset is earlier than the lumped node's.
  - A lumped node without an onset counts as later.
  - A draw whose hottest node has no onset, or whose two onsets are equal, does not count.
  - Held if the share is above 95 %.
- **P2.** For each node at the headline case, take the 2.5 and 97.5 percentiles of the onset time over all 200 draws (numpy's linear interpolation). A draw without an onset is ranked after every onset.
  - The width is the difference between the two percentiles. It is unbounded when the 97.5 percentile falls among draws without an onset.
  - Held if the hottest node's width is under 20 s and the lumped node's is over 20 s.
- **P3.** For each draw, look across the 42 two-strip cases of Stage 1 (D26, the author's choice). Its value is the smallest busbar conductance among the cases in which the hottest node has an onset and the lumped node has none. A draw with no such case has no value.
  - Held if more than 100 of the 200 draws have 100 mW/K (draws without a value count against this), and no draw has 500 mW/K, the only conductance above 200 mW/K in the sweep.
- **P4.** At the headline case, divide the standard deviation (ddof 1) of the hottest-node onset time over the 30 thermal draws, which use the posterior-mean kinetics (Stage 3b), by its standard deviation over the 200 kinetic draws at the nominal thermal inputs (Stage 3a).
  - Each standard deviation is taken over the draws with an onset, and the number without one is reported.
  - Held if the ratio is above 1.5.
- **P5.** The same for the lumped node, with the kinetic standard deviation divided by the thermophysical one. Held if the ratio is above 1.5.
- **P6.** The share of the 200 draws whose hottest node, at the headline case, reaches its onset while below 100 C. Held if the share is below 10 %. The share is also reported for the other eight cases.

The brief's other metrics are reported, not predicted:
- the lead (lumped onset minus hottest-node onset), at its 2.5, 50 and 97.5 percentiles, with the rule of D26 for a lumped node that does not start;
- the share of draws in which only the hottest node starts;
- the share whose hottest-node onset is an SEI start;
- the share with no onset anywhere.

Stage 3c flags an interaction if the variance over the combined pairs exceeds the sum of the two single-factor variances by more than 20 %.

## Reasoning

**The brief's reasoning, made without data.** The hottest node's history is set by the conduction path. So a shift of the onset temperature by the width of the paper's T_in band, about 15 C, moves its onset by seconds on a fast ramp but by tens of seconds on the slow lumped ramp. The busbar and contact ranges move the fast ramp itself.

**The study's estimates.** In Stage 1 the mean model's onset sat at its fresh-reactant onset temperature, 108.4 C, in every case and on every ramp. So each draw's onset is estimated as the first time each archived history reaches the temperature at which that draw starts on the matching synthetic ramp. Whether a node starts at all is estimated by whether its archived peak reaches that temperature; P3 uses the 3 K/s value for both nodes, since both histories are slow near their peaks.

**P1.** At the headline case the hottest node reaches every temperature up to the lumped node's peak, 212 C, before the lumped node does. So the estimate is that every draw starts there first.

**P2.** The onset temperatures spread from 59 to 210 C. On the hottest node's ramp, of 10 to 20 K/s over that range, this becomes an interval of 7.6 to 16.8 s. On the lumped node's ramp, which slows from 3.5 to 0.6 K/s, it becomes 23.1 to 87.2 s.

**P3.** The estimate moves away from the brief's because the draws' onset temperatures spread across the narrow windows that make a conductance the smallest only-local one.
- At 33.2 kJ and 50 mW/K, only the hottest node starts for onset temperatures between the lumped and hottest peaks, about 111 to 127 C.
- At 21.5 kJ and 100 mW/K, the window is about 104 to 125 C.
- At 8.75 kJ and 500 mW/K, the window is about 80 to 114 C.
- A draw starting between about 97 and 104 C falls only in the last of these windows (the hottest node peaks at 95.7 C at 33.2 kJ and 20 mW/K, and at 96.7 C at 21.5 kJ and 50 mW/K), so its smallest only-local conductance is 500 mW/K.
- The estimated shares are: 3.5 % at 5 mW/K, 13.5 % at 20, 21 % at 50, 18.5 % at 100, 31 % at 200, 10.5 % at 500, and 2 % with none.

**P6.** 73 of the 200 draws start below 100 C on the 15 K/s ramp, all by SEI decomposition; the 27 draws that do not start by SEI on that ramp start by the first cathode reaction at 196 to 213 C. The SEI particles of the anode-electrolyte file spread the fresh SEI onset far more widely than the paper's T_in band, which is set after the slow ARC test has consumed the SEI.

**P4 and P5.** No estimate is made, because the thermophysical ranges are not yet sourced.

**Limits of the estimates.** They ignore reactant consumption along the real histories and the curvature of the histories. The P3 estimate is the least certain, because its windows are a few kelvin wide.

## What would count against the thesis

- **If P1 fails,** kinetic uncertainty alone can reverse which model starts first, and the resolved cell's earlier start is not robust.
- **If the lead's interval spans zero** at the headline case, the timing advantage of the hot spot is within the kinetic uncertainty.
- **If P4 holds and P5 fails,** one source of uncertainty, the thermophysical inputs, sets both onsets. The local and whole-cell thresholds would then not respond to different uncertainties, as the brief's reasoning expects.

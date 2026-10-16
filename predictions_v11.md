# Stage 4 predictions (version 1.1.0): which part of the kinetic posterior sets the onset lead

Written on 16 October 2026, before any grouped run. This file, the Stage 4 design (DECISIONS.md D29) and the harness that will run it (`src/v11_sensitivity.py`) are committed and pushed to the public repository before any grouped run, and the commit hash is recorded in the README. The thresholds and the one central estimate (P1) are the Stage 4 brief's. The study's own expectation stands beside each, reasoned from Stage 3's published results only. When this was written no Stage 4 quantity had been computed: no grouped run, no particle distance and no restricted set.

## What was known when these were written

- **Stage 3a at the headline case** (33.2 kJ, 30 s release, 500 mW/K), over the 200 joint kinetic draws:
  - The hottest-node onset ran from 7.6 to 17.0 s (2.5 to 97.5 %; standard deviation 2.83 s), the lumped onset from 23.1 to 75.9 s (17.2 s), and the lead from 15.4 to 58.9 s (14.4 s).
  - The leads fell in two groups: 142 draws from 12.7 to 30.7 s, and 58 draws from 49.7 to 60.8 s.
  - The second group holds every draw whose hottest node started by the first cathode reaction (37 draws, at 195.9 to 216.6 C) and 21 draws whose SEI started late (184.9 to 203.2 C).
  - The hottest node started by SEI decomposition in 163 draws. 73 draws (36.5 %) started below 100 C, all by SEI decomposition.
- **At 100 mW/K** (same energy and release):
  - The hottest node started by SEI decomposition in all 200 draws. Its history peaks at 174.6 C, below every cathode start of the headline case.
  - The lumped node did not start within the 900 s run in 8 draws.
  - The standard deviations were 9.59 s for the hottest-node onset and 95.4 s for the lumped onset (over the 192 draws in which it starts).
  - 36.5 % of the draws started below 100 C.
- **The posterior-mean model** starts both nodes by SEI decomposition at 108.4 C: at 11.48 and 37.88 s at the headline case, and at 18.75 and 127.91 s at 100 mW/K.
- **The draws.** The 200 draws hold 88 distinct particles of the anode-electrolyte file, 89 of the separator file and 158 of the cathode file (`results/stage3_draws.json`).
- **The anode-electrolyte file.** 57 of its 220 rows vary across its particles. The SEI decomposition holds 7 of them: its order, its two stoichiometric coefficients, ln A, Ea, b and dH.
- **The step 1 checks** (`results/v11_checks.json`):
  - The three particle files match their recorded SHA-256.
  - Loading each draw's rows file by file rebuilds `results/stage3_kinetic_draw_parameters.csv` byte for byte.
  - Every grouped model equals the joint draw's model on the varied file's block and the posterior-mean model elsewhere, exactly.
  - The posterior-mean model built through the Stage 4 path reproduces Stage 1 on both cases (largest relative difference 0).
  - The five V5 draws built jointly through it reproduce Stage 3a (largest relative difference 0).

## Definitions used for scoring

- **Submodels.** The posterior's three submodels are the three supplementary files of Koenig, Zhao and Deng (2025):
  - the anode-electrolyte network (`An_Ele.csv`): electrolyte evaporation and decomposition, the anode-electrolyte reaction, the anode-binder reaction, SEI decomposition, and the two unknown reactions IV and V;
  - the NCM811 cathode (`NCM811.csv`): three sequential reactions;
  - the separator (`Separator.csv`): melting.

  The brief's "SEI submodel" is the anode-electrolyte file. It is the only file that holds the SEI decomposition. Those parameters were inferred together with the file's six other reactions, so they cannot be varied apart from them without breaking the particles.
- **Grouped run.** For a submodel and a Stage 3 draw (D22, `results/stage3_draw_indices.csv`), the kinetics take that draw's particle of the submodel's file and the posterior-mean rows of the other two files (`inputs/kinetics/bcrnn_mean_model.json`, the model of Stage 1). They are integrated as Stage 3a integrated the joint draws (D26 (1)), along the hottest-node and lumped histories. Each submodel has 200 grouped runs, one per Stage 3 draw, so every grouped run pairs with the joint draw of the same number.
- **Cases.** The headline case, 33.2 kJ, 30 s, 500 mW/K (`two_E33223_tau30_G0.5`), and the same at 100 mW/K (`two_E33223_tau30_G0.1`).
- **Outputs.**
  - A node's onset is the first time its kinetic self-heating reaches 0.15 K/min within the 900 s run.
  - The four outputs are the hottest-node onset, the lumped onset, the lead (lumped onset minus hottest-node onset), and the hottest node's temperature at its onset.
  - A grouped run whose integration fails is reported as failed and counts as a draw without its outputs; it is not rerun with other settings.
- **Main-effect share** of a submodel for an output:
  - It is the sample variance (ddof 1) of the output over that submodel's 200 grouped runs, divided by its sample variance over the 200 joint draws of Stage 3a, at the same case.
  - Each variance is taken over the draws in which the output exists. A node without an onset gives no onset time, no lead and no onset temperature. The number of draws without the output is reported beside each share.
  - The sum of the three shares is reported for each output and case. A sum well below one means the submodels act together, or that a submodel held at its mean does not stand for its average effect.
- **Rank-based repeat** (robustness, not scored):
  - It is the square of Spearman's rank correlation between the output of a submodel's grouped run and the output of the joint draw with the same number, over the 200 draws.
  - For an output that is a sum of one part per submodel, this squared correlation estimates the same share as above, so the three again add to about one. The rank form gives every draw the same weight.
  - Before ranking, every value is rounded to 4 significant digits. That is a relative resolution of 1e-3, above the largest numerical change V5 found (6.7e-5), so differences below the numerical resolution are ties; ties take their average rank.
  - A node without an onset ranks after every onset (D26 (5)): its onset time, or its draw's lead, is the largest value. A draw whose hottest node has no onset has no lead and no onset temperature, and is left out of that comparison.
  - A grouped output that takes one value in every draw, after rounding, has a rank share of 0.
- **Early SEI start.** The hottest node reaches its onset below 100 C, with SEI decomposition the dominant reaction at that moment. This is Stage 3's P6 quantity (D26 (4)).
- **Central half and restricted set.**
  - Each particle's distance from the posterior mean is the square root of a sum over the rows of its file that vary across the file's particles: 57 of 220 for the anode-electrolyte file, and all 17 and 6 for the cathode and separator files.
  - Each term is the square of the particle's value minus the posterior-mean value, divided by the row's standard deviation over all the file's particles.
  - The central half is the half of the file's particles with the smallest distances: 50 of 100 for the anode-electrolyte and separator files, 250 of 500 for the cathode file. Ties go by column index.
  - The restricted set is the Stage 3a joint draws whose particle of that file lies in its central half. The other two submodels keep their joint draws.
  - Every varying row counts alike, as it would if a measurement tightened the whole submodel.
- **Dominant submodel.** The submodel with the largest main-effect share of the lead at the headline case.
- **Lead width and narrowing.**
  - The width is the difference between the 2.5 and 97.5 percentiles of the lead (numpy's linear interpolation), with D26 (5)'s rule for a lumped node that does not start.
  - The narrowing is 1 minus the restricted set's width divided by the width over all 200 joint draws. At the headline case the full width is 43.5 s (15.4 to 58.9 s, Stage 3a).
- **Ordering.**
  - The submodels are ranked by their main-effect share of the lead.
  - Two shares that differ by less than 0.01 are tied, and a tie agrees with either order.

## The predictions

| | Prediction (the brief's threshold) | Brief's central estimate | Study's expectation |
|---|---|---|---|
| P1 | The SEI submodel (the anode-electrolyte file) carries more than half of the lead's variance at the headline case | 65 % | Held, by a wide margin |
| P2 | The three main-effect shares of the lead at the headline case sum to between 0.8 and 1.1 (interaction small) | none given | Uncertain, no number |
| P3 | With the SEI submodel held at its mean, the share of draws that start below 100 C falls below 5 % | none given | Held |
| P4 | Restricting the dominant submodel to its central half narrows the lead's 2.5 to 97.5 % width by more than 40 % | none given | May fail |
| P5 | The ordering of the submodels is the same at 100 mW/K as at 500 mW/K | none given | Held, if the anode-electrolyte file leads at 500 mW/K |

### How each is scored

- **P1.** Held if the anode-electrolyte file's main-effect share of the lead at the headline case is above 0.5.
- **P2.** Held if the sum of the three main-effect shares of the lead at the headline case is at least 0.8 and at most 1.1. The sums for the other outputs, and at 100 mW/K, are reported, not scored.
- **P3.** At the headline case, take the share of early SEI starts among the 200 cathode runs, and among the 200 separator runs. Both have the anode-electrolyte file at its mean.
  - Held if each share is below 5 %, that is fewer than 10 of 200 draws.
  - The share in the anode-electrolyte runs is reported beside the joint draws' 36.5 %, and every share is also reported at 100 mW/K.
- **P4.** Held if the narrowing of the lead's width at the headline case, for the dominant submodel, is above 40 %.
- **P5.** Held if the ordering of the three submodels at 100 mW/K agrees with the ordering at 500 mW/K, ties as defined above.

### Reported, not predicted

- The shares and their sums for all four outputs at both cases, with paired bootstrap 95 % intervals. The bootstrap uses 2000 resamples of the 200 draw numbers, drawn with `numpy.random.default_rng(20261016)`.
- The rank-based repeat of every share, and whether it orders the submodels as the variance shares do.
- The share of early SEI starts in every run and case.
- The narrowing for each of the three files, not only the dominant one, each with a bootstrap interval.
- The same restriction applied within the dominant submodel's own grouped runs, where the other two submodels sit at their mean.
- For the dominant file, the narrowing when the distance is taken over the rows of one reaction at a time (its orders, stoichiometric coefficients, ln A, Ea, b and dH). This shows which reaction's measurement would narrow the lead most.
- Every grouped run's other Stage 1 fields (the first times at 1 and 10 K/min, the dominant reaction, the peak rate and the conversions), in `results/v11_onsets.csv`.

## Reasoning behind the study's expectations

**P1.** At the headline case the posterior-mean SEI starts at 108.4 C, and every cathode start of that case in Stage 3 came at 195.9 C or above. With the anode-electrolyte file at its mean, the SEI should therefore start near 108.4 C in every cathode and separator run, unless a cathode or separator particle changes the self-heating near that temperature. Those runs should vary little, and the anode-electrolyte runs should carry most of the variance of every output.

**P2.** The second group of leads came from cathode starts and late SEI starts. A cathode start needs a late SEI particle and a cathode particle in the same draw. In the anode-electrolyte runs a late SEI particle meets the mean cathode instead, whose start along these histories is not known before the runs.
- If the mean cathode starts close to where the draws' own cathode particles started, the anode-electrolyte runs reproduce the joint leads and the sum is near one.
- If it starts much later or earlier, the second group moves and the sum can leave the band in either direction.

**P3.** Every start below 100 C in Stage 3 was an SEI start, and the posterior-mean SEI starts at 108.4 C.

**P4.** The central half is chosen on all 57 varying rows of the anode-electrolyte file, of which the SEI decomposition holds 7. If the lead is set mainly by those 7 rows, a half chosen on all 57 removes the particles with the earliest and latest SEI starts only partly, and the narrowing could fall short of 40 %. The per-reaction restriction reported beside P4 shows how much a measurement aimed at one reaction would buy.

**P5.** At 100 mW/K every hottest-node start in Stage 3 was an SEI start, and the history never reaches the cathode starts, so the cathode should matter less there than at 500 mW/K. The ordering should then agree, with the two minor submodels tied if their shares differ by less than 0.01.

## What the answers would mean

- **P1 and P4 hold.** A measurement that tightens the anode-electrolyte network as a whole would narrow the spread of the lead, and so of a propagation prediction made with these kinetics.
- **P1 holds and P4 fails.** The anode-electrolyte network carries the spread, but tightening it as a whole buys little. The measurement would have to target the reaction that sets the onset, and the per-reaction restriction names it.
- **P2 fails with a sum well below one.** The submodels act together, for example when a cathode start needs a late SEI particle. No single submodel's measurement can then be judged alone.

The joint draws of Stage 3 stay the headline result. Holding two submodels at their posterior mean is this stage's choice, made by the brief, and it does not change the lead's spread over the joint posterior, 15.4 to 58.9 s.

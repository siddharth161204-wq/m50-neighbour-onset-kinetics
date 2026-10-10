# Onset kinetics on a resolved neighbour cell: where a whole-cell threshold and a local one disagree

A pilot study. A published two-cell study (Satte 2026, doi:10.5281/zenodo.23253738) solved the neighbour of a failing LG M50 cell twice with identical inputs, as a single temperature (lumped) and as a resolved three-dimensional field, and compared both with fixed onset temperatures. This study replaces the fixed temperatures with decomposition kinetics: the B-CRNN kinetics of Koenig, Zhao and Deng (Chemical Engineering Journal 507 (2025) 160402), integrated along the archived temperature histories of the resolved hottest node, the resolved mean and the lumped node (Stage 1, passive), and then added as a heat source to both models (Stage 2, reactive, one-way). Conduction and radiation only between the cells: the ejecta and flame paths are excluded. One geometry, the published two-cell case. This is onset in a neighbour, not propagation.

Siddharth Satte, Independent researcher, Pune, India.

## Status and order of work

1. The published study was cloned at v1.0.0 (commit 2b35ac7); its archived series load, and the hottest node of the 33.2 kJ, 30 s, 500 mW/K case first reaches 456.65 K (183.5 C) between the 15.5 s and 16.0 s samples, at 15.51 s by linear interpolation, the published number.
2. Kinetics chosen and recorded (DECISIONS.md D1 to D7), driver filled (`src/onset_kinetics.py`), V0, V1 and V2 run on the source paper's cells and on synthetic histories only.
3. Predictions: `predictions.md`, commit `b09ef1d21a0281b543d0bf1f3b2c95f6cd5c2528`, pushed to this public repository at 2026-10-10 08:09:37 UTC (the repository's `pushed_at` time; it was created at 08:09:05 UTC), before any kinetics were integrated along an archived history of the two-cell study.

## Stage 1 results (passive kinetics along the archived histories)

Computed by `src/onset_kinetics.py` (`results/onset_results.csv` and `.json`, 49 cases) and scored by `src/score_stage1.py` (`results/stage1_scorecard.json`), after the predictions were public (Stage 1 ran from 08:10:09 UTC on 10 October 2026).

1. Every history that self-heats at all first reaches 0.15 K/min at 108.39 to 108.42 C, by SEI decomposition. The same kinetics give T_in = 179 C in the paper's ARC test only because its slow heat-wait-seek consumes the SEI first (V1).
2. Copper busbars (500 mW/K) and 33.2 kJ: the resolved hottest node first self-heats at 0.15 K/min at 4.24 s and 11.48 s (10 and 30 s release), the lumped node at 27.60 s and 37.88 s, the resolved mean at 49.35 s and 59.38 s. The hottest node starts 23.4 s and 26.4 s before the lumped node (84.6 % and 69.7 % earlier).
3. The smallest busbar conductance at which only the hottest node starts is 100 mW/K (21.5 kJ, both releases); it also happens at 8.75 kJ and 500 mW/K.
4. The resolved mean starts in 10 of the 42 two-strip cases, the lumped node in 12 and the hottest node in 16. The hottest node reaches 10 K/min (first cathode reaction) in 6 cases, in 4 of which the lumped node never reaches 1 K/min; passively the lumped node peaks at 8.6 and 9.4 K/min at 500 mW/K and never reaches 10 K/min.

| Prediction | Statement (short form) | Result | Measured |
|---|---|---|---|
| P1 | At 500 mW/K and 33.2 kJ the hottest node reaches 0.15 K/min more than half the lumped time earlier | Held | 4.24 s against 27.60 s (84.6 %) and 11.48 s against 37.88 s (69.7 %); central estimates 4.2 against 29 s and 11.5 against 39 s |
| P2 | The resolved mean reaches 0.15 K/min in exactly 10 named cases | Held | The same 10 cases; at 33.2 kJ and 50 mW/K the mean peaks at 107.0 and 107.3 C, just under 108.4 C |
| P3 | Smallest conductance with only the hottest node starting: 100 mW/K | Held | 100 mW/K (21.5 kJ), and 8.75 kJ at 500 mW/K, as predicted |
| P4 | The hottest node reaches 10 K/min where the lumped node stays under 1 K/min | Held | In the 4 predicted cases (33.2 kJ at 200 mW/K, 21.5 kJ at 500 mW/K, both releases) |

V2 repeated on the archived headline cases after Stage 1 (`results/v2_archived.json`): halving the tolerances, the largest step and the evaluation grid moves no onset time by more than 3.8e-6 of itself.

## Kinetics

Posterior-mean B-CRNN model of Koenig, Zhao and Deng (2025), from the article's supplementary material (every SVGD particle of its NCM811 cathode, anode-electrolyte-SEI-binder and separator submodels): 13 species, 11 reactions, parameters in `inputs/kinetics/bcrnn_mean_model.json`, provenance and hashes in `inputs/kinetics/SOURCE.md`. Reactant masses from the paper's Table 1 (its 720 g, 25 Ah cell), with the anode-electrolyte reaction's mass read from its Fig. A.1(a) (D4). The neighbour's density and heat capacity are the published study's (2938.7 kg/m3, 950 J/(kg K)).

## Checks before any case

| Check | Result |
|---|---|
| V0, DSC at 5 C/min against the paper's figures | Cathode: 0.49 W/g at 223.7 C and 0.15 W/g at 402 C (paper Fig. 3(a): about 0.50 at 223 C and 0.15 at 402 C); ln k of the three cathode reactions at 225, 275 and 410 C: -4.550, -4.310, -5.156 (Table 1 of the cathode source: -4.55, -4.31, -5.16); separator: -0.079 W/g at 138.5 C (Fig. 3(e): -0.080 at 139 C) |
| V1, the paper's ARC test of its own cell with these kinetics (acceptance: T_in within 169.0 to 198.0 C) | T_in = 179.3 C, pass; 179.1 to 186.6 C for 8 of 9 heat-wait-seek settings, 124.6 C for a 2 C/min ramp with a 5 min seek (early SEI trigger, the paper's own outlier mechanism); 1 C/s reached at 272.7 C, inside the paper's T_on band of 255.7 to 302.1 C |
| Fig. A.1(a) of the paper, read with `inputs/kinetics/digitize_figA1.py` | Its SEI curve between 25 and 60 C corresponds to an SEI mass of 99.4 g against Table 1's 100.58 g (a 1.2 % reading bias); its anode-electrolyte curve between 133 and 168 C to 205.5 g after that bias, the anode plus electrolyte mass of 208.58 g (D4) |
| V2, synthetic holds, ramps of 0.3 to 30 K/s and pulses, tolerances, largest step and evaluation grid halved | Onset times move by at most 1.1e-4 of themselves (acceptance 1e-2) |

The neighbour (cp 950 J/(kg K)) with fresh reactants self-heats at 0.15 K/min from 108.4 C (SEI decomposition), at 1 K/min from 174 to 205 C depending on the heating rate, and at 10 K/min from 212 to 219 C (first cathode reaction).

## Running

Python 3.11 or newer. `pip install -r requirements.txt`, then `./get_published_study.sh` (clones the published study at v1.0.0 into `external/`). From `src/`:

    python3 v0_dsc_check.py --out ../results
    python3 v1_arc_check.py --out ../results --sensitivity
    python3 v2_synthetic.py --out ../results
    python3 onset_kinetics.py --series ../external/m50-two-cell-pilot/results/resolved_series --out ../results
    python3 score_stage1.py --out ../results
    python3 v2_archived.py --out ../results

To recompute the kinetic parameters from the publisher's files: `python3 inputs/kinetics/fetch_supplementary.py` and `python3 inputs/kinetics/extract_mean_model.py`.

## Sources

- B.C. Koenig, P. Zhao, S. Deng, Comprehensive thermal-kinetic uncertainty quantification of lithium-ion battery thermal runaway via Bayesian chemical reaction neural networks, Chemical Engineering Journal 507 (2025) 160402, doi:10.1016/j.cej.2025.160402, and its supplementary material.
- S. Satte, Where and when a neighbour cell first reaches thermal-runaway onset temperatures: resolved against lumped, a pre-registered two-cell LG M50 pilot (v1.0.0), Zenodo (2026), doi:10.5281/zenodo.23253738.

## Licence

Code: MIT (see LICENSE). The note, the figure and the results: CC BY 4.0.

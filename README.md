# Onset kinetics on a resolved neighbour cell: where a whole-cell threshold and a local one disagree

A pilot study. A published two-cell study (Satte 2026, doi:10.5281/zenodo.23253738) solved the neighbour of a failing LG M50 cell twice with identical inputs, as a single temperature (lumped) and as a resolved three-dimensional field, and compared both with fixed onset temperatures. This study replaces the fixed temperatures with decomposition kinetics: the posterior-mean B-CRNN kinetics of Koenig, Zhao and Deng (Chemical Engineering Journal 507 (2025) 160402), integrated along the archived temperature histories of the resolved hottest node, the resolved mean and the lumped node (Stage 1, passive), and then added as a heat source to both models (Stage 2, reactive, one-way). Conduction and radiation only between the cells: the ejecta and flame paths are excluded. One geometry, the published two-cell case. This is onset in a neighbour, not propagation.

Siddharth Satte, Independent researcher, Pune, India.

Zenodo DOI, reserved for version v1.0.0: https://doi.org/10.5281/zenodo.23279456 (it resolves once the record is published). Cite as: Satte, S. (2026). Onset kinetics on a resolved neighbour cell: where a whole-cell threshold and a local one disagree (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.23279456

The one-page note is `note/neighbour_onset_note.pdf` (source `note/neighbour_onset_note.md`).

## Status and order of work

1. The published study was cloned at v1.0.0 (commit 2b35ac7); its archived series load, and the hottest node of the 33.2 kJ, 30 s, 500 mW/K case first reaches 456.65 K (183.5 C) between the 15.5 s and 16.0 s samples, at 15.51 s by linear interpolation, the published number.
2. Kinetics chosen and recorded (DECISIONS.md D1 to D12), driver filled (`src/onset_kinetics.py`), V0, V1 and V2 run on the source paper's cells and on synthetic histories only (commit 78c1321).
3. Predictions: `predictions.md`, commit `b09ef1d21a0281b543d0bf1f3b2c95f6cd5c2528`, first pushed to this public repository at 2026-10-10 08:09:37 UTC, when the main branch was created with b7ba0f5, a descendant of b09ef1d, as its head (the repository's activity log, `provenance/github_activity.json`; the repository was created at 08:09:05 UTC). That was before any kinetics were integrated along an archived history of the two-cell study. Its text has not changed since.
4. Stage 1 ran from 08:10:09 UTC, after the README recording that hash was pushed (08:10:02 UTC); its results and the scorecard of P1 to P4 were committed and pushed (commit 080e779, 08:17:13 UTC) before Stage 2 ran.
5. The Stage 2 scheme and checks (DECISIONS.md D13 to D15, commit b6ba9bd, pushed 08:17:23 UTC) were public before Stage 2 ran from 08:17:31 UTC.
6. Stage 2, the scoring of P5, the checks of D15, the figure and the note make up release v1.0.0. An independent review of that material, before release, led to D19 to D21: two exploratory analyses and fuller records. No registered result changed.
7. Stage 3, kinetic and thermophysical uncertainty (brief of 12 October): the 200 kinetic draws and their loader (D22, commit db29932); V4, the draws through the source paper's ARC test, failed under its registered acceptance (D23, commit f9cabc7) and was amended after the failure by the author's choice (D25, commit 1e835d9), under which it passes; the Stage 3a design (D26) and the predictions, `predictions_stage3.md`, commit `2657aeece0c2137af47aaae4abd9319bdd24ab40`, first pushed to this repository at 2026-10-12 13:01:52 UTC (`provenance/github_activity_stage3.json`), before any kinetic draw was integrated along an archived history of the two-cell study. Its text has not changed since.

## Results

Every number in the Results and Exploratory sections is computed from the result files by `src/note_numbers.py` (`results/note_numbers.json`), central estimates are quoted from `predictions.md`, and the Verification table quotes the check records it names.

Stage 1, passive kinetics along the archived histories (`results/onset_results.csv` and `.json`, 49 cases; `results/stage1_scorecard.json`):

1. Every history that self-heats at all first reaches 0.15 K/min at 108.39 to 108.42 C, by decomposition of the fresh SEI each history starts with. The same kinetics give T_in = 179.3 C in the source paper's ARC test only because its slow heat-wait-seek, about 25 h of it, consumes the SEI first (V1). How much rests on the fresh SEI is in the exploratory section below.
2. Copper busbars (500 mW/K in all) and 33.2 kJ: the resolved hottest node first self-heats at 0.15 K/min at 4.24 s and 11.48 s (10 and 30 s release), the lumped node at 27.60 s and 37.88 s, the resolved mean at 49.35 s and 59.38 s. The hottest node starts 23.4 s and 26.4 s before the lumped node (84.6 % and 69.7 % earlier).
3. The smallest busbar conductance at which only the hottest node starts is 100 mW/K (21.5 kJ, both releases); it also happens at 8.75 kJ and 500 mW/K.
4. The resolved mean starts in 10 of the 42 two-strip cases, the lumped node in 12 and the hottest node in 16. The hottest node reaches 10 K/min (first cathode reaction) in 6 cases, in 4 of which the lumped node never reaches 1 K/min; passively the lumped node peaks at 8.6 and 9.4 K/min at 33.2 kJ and 500 mW/K.

Stage 2, reaction heat fed back, one-way (`results/stage2_table.csv`, `results/stage2/`, `results/stage2_scorecard.json`):

5. At 33.2 kJ and 500 mW/K the hottest node enters the internal-short band (255.7 C) at 7.13 s and 19.23 s, at the same moment as without the reaction heat (7.13 s and 19.24 s in the two-cell study's passive runs): the entry is set by conduction from the busbar, not by the reaction. The reaction heat raises the hottest node's peak by 9.9 and 8.6 K (to 365.8 and 356.9 C), and a node's layered NCM cathode is 99 % consumed 1.3 s and 2.8 s after entry; at most 0.505 and 0.503 % of the cell's volume gets above 255.7 C. The resolved mean peaks 1.1 K higher (168.2 and 169.0 C).
6. The reactive lumped cell never enters the band: it peaks at 222.1 and 226.1 C (211.2 and 212.2 C without the source) and cools. It converts 51 and 63 % of its layered cathode, against 1.2 % over the resolved cell's volume, and releases 2.51 and 3.02 kJ of reaction heat, 6.0 and 7.1 times the resolved cell's 0.42 kJ: the lumped node, which holds the whole inventory at one temperature, peaks 44 K above the resolved mean even without the source.
7. At 33.2 kJ and 200 mW/K the reaction heat raises the hottest node's peak by only 0.6 and 0.7 K, to 251.4 and 251.5 C, short of the band, and the lumped cell's by 0.9 and 1.0 K, to 169.1 and 169.9 C. At 21.5 kJ, 500 mW/K and 30 s neither model enters the band (hottest node 236.8 C, lumped 152.9 C, each within 0.2 K of its passive peak). In these three runs the lumped cell releases 1.45 to 1.50 times the resolved cell's reaction heat.

| Prediction | Statement (short form) | Result | Measured |
|---|---|---|---|
| P1 | At 500 mW/K and 33.2 kJ the hottest node reaches 0.15 K/min more than half the lumped time earlier | Held | 4.24 s against 27.60 s (84.6 %) and 11.48 s against 37.88 s (69.7 %); central estimates 4.2 against 29 s and 11.5 against 39 s |
| P2 | The resolved mean reaches 0.15 K/min in exactly 10 named cases | Held | The same 10 cases; at 33.2 kJ and 50 mW/K the mean peaks at 107.0 and 107.3 C, just under 108.4 C |
| P3 | Smallest conductance with only the hottest node starting: 100 mW/K | Held | 100 mW/K (21.5 kJ), and 8.75 kJ at 500 mW/K, as predicted |
| P4 | The hottest node reaches 10 K/min where the lumped node stays under 1 K/min | Held | In the 4 predicted cases (33.2 kJ at 200 mW/K, 21.5 kJ at 500 mW/K, both releases) |
| P5(a) | Stage 2, 33.2 kJ and 500 mW/K: the resolved hottest region enters the internal-short band and the reactive lumped cell does not | Held, against the registered expectation | Entry at 7.13 s and 19.23 s (central estimate 7.1 and 19.0 s), at the same moment as without the reaction heat, so set by conduction; lumped peaks 222.1 and 226.1 C. The registered expectation was that P5(a) would fail on its lumped half (lumped runaway at about 170 and 180 s; about one chance in three of holding): wrong |
| P5(b) | Stage 2, 33.2 kJ and 200 mW/K: the hottest region is pushed into the band by its own reaction heat, the lumped cell stays out | Failed | The hottest node peaks at 251.4 and 251.5 C, 0.6 and 0.7 K above its passive peak (central estimate 5 to 10 K; registered odds about even); the lumped half held, 169.1 and 169.9 C, 0.9 and 1.0 K above passive (central estimate 4 K) |
| P5(c) | Stage 2, 21.5 kJ, 500 mW/K, 30 s: neither enters the band | Held | 236.8 C and 152.9 C, 0.17 and 0.20 K above passive (central estimates about 2 K and a few kelvin) |

## Exploratory, not pre-registered (DECISIONS.md D19 and D20)

Fresh SEI (`src/explore_sei_storage.py`, `results/explore_sei_storage.json`). The mean model's SEI decomposes even at 25 C: stored there under the same kinetics, the neighbour loses 12 % of its SEI in a day, 36 % in three days, 80 % in a week and all of it in a month. Kinetics this slow are beyond what DSC data resolve, as the source paper's Appendix A notes; like the source's own ARC simulation, Stage 1 starts from a fresh SEI. Repeated from the stored states, at 33.2 kJ and 500 mW/K:

| SEI stored at 25 C | SEI gone | Hottest node starts (10 s, 30 s) | Lumped node starts (10 s, 30 s) | Lead |
|---|---|---|---|---|
| fresh (Stage 1) | 0 % | 4.24 s, 11.48 s at 108.4 C, SEI | 27.60 s, 37.88 s at 108.4 C, SEI | 23.4 s, 26.4 s |
| 3 days | 36 % | 4.31 s, 11.66 s at 111.3 C, SEI | 28.63 s, 38.90 s at 111.3 C, SEI | 24.3 s, 27.2 s |
| 7 days | 80 % | 6.20 s, 16.34 s at 210 and 201 C, first cathode reaction | 60.32 s, 70.23 s at 173 C, SEI | 54.1 s, 53.9 s |
| 30 days | 100 % | 6.21 s, 16.40 s at 211 and 202 C, first cathode reaction | 66.18 s, 75.91 s at 180 C, first cathode reaction | 60.0 s, 59.5 s |

With the SEI gone, at 33.2 kJ and 200 mW/K and at 21.5 kJ and 500 mW/K only the hottest node starts, and at 21.5 kJ and 100 mW/K nothing starts (all with the 30 s release). Wherever a history starts, the hottest node starts first, in every stored state; at 33.2 kJ and 500 mW/K the fresh SEI gives the shortest lead.

The source's own internal-short trigger. The source paper switches its internal short on when the rate of the battery's temperature rise surpasses 1 C/min (its Eq. 19, Table 1 and Section 3.2.2), which in its adiabatic calorimeter is the self-heating rate. A neighbour heated by conduction rises far faster than that from the busbar alone (up to 215 to 255 K/min at the lumped node and 1258 to 3305 K/min at the hottest node, 33.2 kJ and 500 mW/K), so here the trigger is applied to the kinetic self-heating only: the 1 K/min level of Stage 1. At 33.2 kJ and 500 mW/K the hottest node reaches it at 6.20 s and 16.36 s and the lumped node at 64.31 s and 74.09 s (177.7 and 177.9 C), 58.1 s and 57.7 s later. In 5 two-strip cases only the hottest node reaches it (33.2 kJ at 200 mW/K, both releases, and at 100 mW/K, 30 s; 21.5 kJ at 500 mW/K, both releases); the resolved mean reaches it in none. Read with that trigger, the reactive lumped cell of P5(a) would short too; P5 is scored on the brief's temperature band, as registered (D12).

## Verification

| Check | Result |
|---|---|
| V0, the source paper's DSC curves at 5 C/min | Cathode 0.49 W/g at 223.7 C and 0.15 W/g at 402 C (paper Fig. 3(a): about 0.50 at 223 C and 0.15 at 402 C); ln k of the three cathode reactions at 225, 275 and 410 C: -4.550, -4.310, -5.156 (Table 1 of the cathode source: -4.55, -4.31, -5.16); separator -0.079 W/g at 138.5 C (Fig. 3(e): -0.080 at 139 C), which fixes the sign of its heat (D5) |
| Fig. A.1(a) of the paper, read with `inputs/kinetics/digitize_figA1.py` | Its SEI curve between 25 and 60 C corresponds to an SEI mass of 99.4 g against Table 1's 100.58 g (a 1.2 % reading bias); its anode-electrolyte curve between 133 and 168 C to 205.5 g after that bias, the anode plus electrolyte mass of 208.58 g (D4) |
| V1, our emulation of the paper's ARC test of its own cell with the mean model (acceptance: T_in within the main-cluster two-sigma band, 169.0 to 198.0 C) | T_in = 179.3 C, pass (the paper's main-cluster mean, over its posterior samples, is 183.5 C); 179.2 to 186.6 C for 8 of 9 heat-wait-seek settings and 124.6 C for a 2 C/min ramp with a 5 min seek (an early SEI trigger, the paper's own outlier mechanism); 184.2 C with the anode alone as the anode-electrolyte mass |
| V1, T_on, the paper's internal-short trigger temperature (D6, D21; not part of the acceptance) | At the paper's stated trigger, 1 C/min: 199.8 C, 56 K below its main-cluster band of 255.7 to 302.1 C (mean 278.9 C), so this check fails. At 1 C/s: 272.7 C, inside the band. The paper gives 1 C/min in both its Table 1 and its Section 3.2.2; the cause of the mismatch is not resolved here |
| V2 before the predictions: synthetic holds, ramps of 0.3 to 30 K/s and pulses, tolerances, largest step and evaluation grid halved | Onset times move by at most 1.1e-4 of themselves (acceptance 1e-2) |
| V2 after Stage 1, archived headline cases (33.2 kJ, 500 mW/K, both releases) | At most 3.8e-6 |
| V3, energy account of every Stage 2 run at the published conductivity (the seven runs in `results/stage2/`) | Residual at most 1.35e-12 of the heat taken in (acceptance 1e-9) |
| V3, roll conductivity 1e4 W/mK, reactive resolved cell against the reactive lumped cell (acceptance 1 K) | 33.2 kJ, 30 s, 500 mW/K: mean within 0.47 K, hottest node within 0.77 K, peaks 225.7 and 226.1 C; 200 mW/K: mean within 0.045 K, hottest node within 0.36 K, both peaks 169.9 C; pass. Energy residuals of these two runs 7.9e-10 and 8.8e-10 |
| Stage 2 loops without the source, headline case | Reproduce the archived resolved series to 1.3e-12 K (hottest node) and 2.3e-13 K (mean), and the archived lumped node exactly |
| Stage 2 step check: the 1 K and 4 K limits of D13 halved, headline case (acceptance: no band-entry time moves by more than 1 %) | Band-entry times move by at most 7.5e-5 of themselves (255.7 C at 19.226 s and 19.225 s), pass; the hottest node's peak moves by 0.006 K, the reaction heat by 2e-6 of itself, the moment a node's layered cathode is consumed by one half step (22.025 s and 22.0125 s); the lumped node is unchanged to all digits |
| V0 to V2 re-run with the final code (the vectorised `rates()` that Stage 1 and Stage 2 use) | The committed records, kept unchanged, are reproduced to 6.4e-8 (V0), 2.4e-9 (V1 record) and 1.8e-8 (its trace), and 6e-15 (V2) of themselves (`results/rerun_final_code.json`, `src/compare_records.py`) |
| The mean model, `inputs/kinetics/bcrnn_mean_model.json` | Computed from the publisher's supplementary files in a browser session, because the machine this study ran on cannot reach the publisher's file server (`inputs/kinetics/SOURCE.md`); `extract_mean_model.py` recomputes it from those files and has been run here only on synthetic files. V0's ln k values round to the cathode source's two-decimal values |

## Contents

- `DECISIONS.md`: every analysis choice not fixed by the brief, with its reason, numbered; D13 to D15 were added after the predictions were public, before Stage 2 ran, and D16 to D21 after it (presentation, records and two exploratory analyses).
- `predictions.md`: the pre-registered predictions and the hand reasoning behind them.
- `inputs/kinetics/`: the kinetics' source, hashes and page references (`SOURCE.md`), the posterior-mean parameters (`bcrnn_mean_model.json`, and readable as `bcrnn_mean_model_table.md` and `.csv`), the scripts that fetch the supplementary files, recompute the mean model and read Fig. A.1(a), and that reading (`figA1a_mass_basis.json`).
- `inputs/databank/`: the Battery Failure Databank rows behind the energies, with the Databank's notice (`SOURCE.md` says where they come from).
- `src/bcrnn.py`: the kinetic model. `src/onset_kinetics.py`: Stage 1, the brief's driver. `src/reactive.py`, `src/run_stage2.py`: Stage 2. `src/v0_dsc_check.py`, `src/v1_arc_check.py`, `src/v2_synthetic.py`, `src/v2_archived.py`, `src/v3_stage2.py`: the checks. `src/score_stage1.py`, `src/score_stage2.py`, `src/note_numbers.py`, `src/make_figure.py`: scoring, the quoted numbers and the figure. `src/explore_sei_storage.py`: the exploratory SEI analysis. `src/compare_records.py`: compares two sets of check records.
- `results/`: `onset_results.csv` and `.json` (Stage 1), `stage1_scorecard.json`, `stage2_table.csv`, `stage2_scorecard.json`, `stage2_checks.json`, `stage2/` (each Stage 2 run's record and time series), the check records (`v0_dsc_check.json`, `v1_arc_check.json` with `v1_arc_trace.csv`, `v2_synthetic.json`, `v2_archived.json`, `v3_stage2.json`, `rerun_final_code.json`), `explore_sei_storage.json`, `note_numbers.json`, `neighbour_onset_figure.png` and `.pdf`, and the run logs.
- `note/`: the note, its Markdown source, stylesheet and render script (pandoc and headless Chromium).
- `provenance/github_activity.json`: the repository's push log before the release push (GitHub activity API).

## Running

Python 3.11 or newer. `pip install -r requirements.txt`, then `./get_published_study.sh` (clones the published study at v1.0.0 into `external/`, where the scripts find its archived series and its solver). From `src/`, with `MKL_NUM_THREADS=1`:

    python3 v0_dsc_check.py --out ../results
    python3 v1_arc_check.py --out ../results --sensitivity
    python3 v2_synthetic.py --out ../results
    python3 onset_kinetics.py --series ../external/m50-two-cell-pilot/results/resolved_series --out ../results
    python3 score_stage1.py --out ../results
    python3 v2_archived.py --out ../results
    python3 run_stage2.py --out ../results --cases max:30:0.5 max:30:0.2 median:30:0.5
    python3 run_stage2.py --out ../results --cases max:10:0.5 max:10:0.2
    python3 run_stage2.py --out ../results --cases max:30:0.5 --no-reaction --tag _no_source
    python3 run_stage2.py --out ../results --cases max:30:0.5 --dt-scale 0.5 --tag _step_halved
    python3 v3_stage2.py --out ../results --cases max:30:0.5 max:30:0.2
    python3 score_stage2.py --out ../results
    python3 explore_sei_storage.py --out ../results
    python3 note_numbers.py --out ../results
    python3 make_figure.py --out ../results
    cd ../note && ./render_note.sh

To compare a re-run of V0 to V2 with the committed records, run those three scripts with `--out` set to another folder, then `python3 compare_records.py --a ../results --b <that folder> --files v0_dsc_check.json v1_arc_check.json v1_arc_trace.csv v2_synthetic.json --out ../results/rerun_final_code.json`.

To recompute the kinetic parameters from the publisher's files: `python3 inputs/kinetics/fetch_supplementary.py`, then `python3 inputs/kinetics/extract_mean_model.py`. PARDISO (`pypardiso`, which needs MKL) is used for the sparse solves when installed; SuperLU is the fallback.

## Sources and credits

- B.C. Koenig, P. Zhao, S. Deng, Comprehensive thermal-kinetic uncertainty quantification of lithium-ion battery thermal runaway via Bayesian chemical reaction neural networks, Chemical Engineering Journal 507 (2025) 160402, doi:10.1016/j.cej.2025.160402, and its supplementary material (the trained B-CRNN particles), which is not redistributed here.
- S. Satte, Where and when a neighbour cell first reaches thermal-runaway onset temperatures: resolved against lumped, a pre-registered two-cell LG M50 pilot (v1.0.0), Zenodo (2026), doi:10.5281/zenodo.23253738: the archived temperature histories, the resolved and lumped solvers, the cell properties and the Battery Failure Databank energies.
- Battery Failure Databank, revision 2 (February 2024), National Renewable Energy Laboratory (now National Laboratory of the Rockies), U.S. Department of Energy; described in D.P. Finegan et al., Journal of Power Sources 597 (2024) 234106. The energies here (8.75, 21.5 and 33.2 kJ through the cell body) come from it through the two-cell study's archived histories; the rows used are copied unchanged from that study into `inputs/databank/` with the Databank's notice, which must accompany every copy (`inputs/databank/SOURCE.md`). The Battery Failure Databank is provided by the U.S. Department of Energy's National Renewable Energy Laboratory, operated by Alliance for Sustainable Energy, LLC (DOE/NREL/ALLIANCE); its notice accompanies the rows used, in `inputs/databank/`.

## Licence

The code is under the MIT licence (LICENSE). The note, the figure and the result files are under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). The Databank rows remain under the Databank's own notice (`inputs/databank/DATABANK_NOTICE.txt`), which accompanies every copy.

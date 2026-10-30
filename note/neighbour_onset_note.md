# Onset kinetics on a resolved neighbour cell: where a whole-cell threshold and a local one disagree

::: byline
Siddharth Satte, Independent researcher, Pune, India, 30 October 2026. A pre-registered pilot: predictions commits b09ef1d (Stages 1, 2) and 2657aee (Stage 3), each public before its kinetics ran on an archived history. [doi.org/10.5281/zenodo.23279455](https://doi.org/10.5281/zenodo.23279455){.nobr}; [github.com/siddharth161204-wq/m50-neighbour-onset-kinetics](https://github.com/siddharth161204-wq/m50-neighbour-onset-kinetics){.nobr}.
:::

<div class="headline">

1. With copper busbars (500 mW/K in all) and the largest Databank energy (33.2 kJ), the resolved neighbour's hottest node starts to self-heat at 0.15 K/min 23.4 and 26.4 s before the lumped node (10 and 30 s releases); under the posterior-mean B-CRNN kinetics of Koenig, Zhao and Deng each start is a fresh SEI decomposing at 108.4 C.
2. The smallest busbar conductance at which only the local chemistry starts is 100 mW/K under those kinetics (21.5 kJ).
3. Over 200 draws of their kinetic posterior the lumped node never starts first in any of the 42 cases; at 33.2 kJ, 30 s and 500 mW/K the lead runs from 15.4 to 58.9 s (2.5 to 97.5 %, median 26.3 s).
4. There, over the published spread of the roll's conductivity and heat capacity the hottest node's onset varies 0.027 times as much as over the kinetic posterior (standard deviations; the lumped node's 0.11 times): the kinetics set both.

</div>

![](../results/neighbour_onset_figure.png)

Figure 1. (a) First time each history self-heats at 0.15 K/min, 30 s release, 33.2 kJ (filled) and 21.5 kJ (hollow); ringed where only the hottest node starts. (b) Kinetic self-heating rate along the three histories, 33.2 kJ, 30 s, 500 mW/K; gaps: net endothermic (separator melting). (c) With the reaction heat (solid) and without (dashed): the hottest node enters the internal-short band at 19.2 s either way; the lumped node peaks at 226 C.

## Method

1. Kinetics: the B-CRNN of Koenig, Zhao and Deng (Chem. Eng. J. 507 (2025) 160402), averaged over its trained particles: three NCM811 cathode, seven anode-electrolyte-SEI-binder and one separator reaction, at their cell's reactant mass fractions.
2. Checks against the source: their DSC curves at 5 C/min are reproduced; our emulation of their ARC test gives T~in~ = 179.3 C, inside their main-cluster band of 169.0 to 198.0 C, but T~on~ = 199.8 C at their stated 1 C/min trigger, below their band of 255.7 to 302.1 C.
3. Stage 1, passive: BDF along three archived 0.5 s histories (hottest node, resolved mean, lumped node) of the 49 cases of the two-cell study (doi:10.5281/zenodo.23253738). Stage 2, reactive, one-way, five cases: the reaction heat fed into its solver.
4. Stage 3: 200 joint draws of the posterior's particles on nine cases (42 for P3); 30 Latin hypercube draws of the roll's conductivities and specific heat (O'Regan et al. 2022; Chen et al. 2021) in the published solver; 210 pairs (Figure 2, README).
5. Checks: halving tolerances, steps and grids moves the onsets by at most 7 × 10^−5^ of themselves; energy accounts close to 10^−11^ at the published conductivities; with a 10^4^ W/mK roll resolved and lumped agree within 0.8 K.

## Limits

1. The kinetics come from other cells (NCM811 and graphite DSC data, not the M50's silicon-graphite negative). The SEI is fresh; the mean model decomposes it even at 25 C, and with it gone the lead grows to 60 s (exploratory).
2. Stage 1 ignores the reaction heat; Stage 2 is one-way; conduction and radiation only, so ejecta, flame and venting are excluded and none of this is propagation. The internal short is the source's T~on~ band as a temperature, not a model; at its own 1 K/min trigger the lumped node would short too.
3. One geometry without the cap and tabs, constant properties, and a hottest node that is the envelope of local histories.
4. Stage 3 treats the three submodels' particles as independent; its thermal ranges are literature spreads, not measured uncertainties of this cell (contact, busbar, emissivity fixed); its ARC check failed the brief's acceptance, passing only as amended.

## Prediction scorecard

| | Prediction | Result | Measured |
|---|----------------------------------------------------|---------|------------------------------------|
| P1 | Hottest node over half the lumped time earlier | Held | 85 and 70 % earlier (central 86, 71 %) |
| P2 | The resolved mean starts in exactly 10 named cases | Held | The same 10 |
| P3 | Smallest only-local conductance 100 mW/K | Held | 100 mW/K; also 8.75 kJ at 500, as named |
| P4 | Hottest node at 10 K/min, lumped under 1 K/min | Held | In the 4 named cases |
| P5 | Stage 2: (a) only the hot spot shorts; (b) at 200 mW/K too; (c) neither at 21.5 kJ | (b) failed | (a), (c) held; (b) +0.6, +0.7 K (central 5 to 10 K) |
| | **Stage 3** (33.2 kJ, 30 s, 500 mW/K; P3 over the 42 cases) | | |
| P1 | Hottest node first in over 95 % of draws | Held | 100 % (central 99 %) |
| P2 | 95 % onset interval: hottest under 20 s, lumped over 20 s | Held | 9.3 and 52.9 s (central 8 and 40 s) |
| P3 | Only-local conductance 100 mW/K in over half, never above 200 | Failed | 21 %; 500 mW/K in 10.5 % |
| P4 | Hottest onset: thermal SD over 1.5 times kinetic | Failed | 0.027 (central 3) |
| P5 | Lumped onset: kinetic SD over 1.5 times thermal | Held | 9.5 (central 2) |
| P6 | Under 10 % start below 100 C (early SEI) | Failed | 36.5 %, in all nine cases |

## Stage 4 (v1.1)

1. Each of the posterior's three submodels varied alone over the same 200 draws, the other two at their posterior mean (a choice; the joint draws stay the headline); 33.2 kJ, 30 s, 500 and 100 mW/K; predictions commit a975f20.
2. The anode-electrolyte submodel, holding the SEI, carries essentially all of the variance: 0.997 of the lead's at 500 mW/K (0.89 to 1.09 for every output at both); NCM811 cathode 0.000, separator at most 0.002.
3. With it at its mean no draw starts below 100 C; varied, 37.5 % do.
4. Its central half (a parameter-space proxy for a tighter posterior, on all 57 varying parameters) narrows the lead's 95 % width only from 43.5 to 37.1 s (14.6 %); on the SEI's own parameters, 18.1 %.
5. Exploratory: the lead has two modes (starts by 122.4 C, or at 184.9 C and above) and a tighter posterior keeps both; in marginal draws the SEI's heat net of the separator's melting sets the mode.
6. Scorecard: P1 (SEI submodel over half the lead's variance) held, 0.997 (central 65 %); P2 (shares sum to 0.8 to 1.1) held, 0.998; P3 (under 5 % below 100 C) held, 0 %; P4 (over 40 % narrower) failed, 14.6 %; P5 (same ranking at 100 mW/K) held.

## Stage 5 (v1.2)

1. Against two-cell LG M50 tests of Fransson et al. (J. Power Sources 617 (2024) 234916; 9 of 16 propagated in 147 to 342 s): steel-on-steel contact 200 to 3,700 W/(m^2^ K), nickel-strip tabs, 33.2 kJ; conduction and radiation only (no venting, ejecta or flame); predictions b4883ba.
2. In none of 5,248 runs, the brief's 4,800-run factorial among them, does either neighbour reach 255.7 C within 900 s.
3. In the central case the resolved hot spot, on the line of contact, peaks at 192 C by 41 s; the lumped neighbour at 159 to 162 C at 255 to 270 s.
4. In any run at most 226.7 C (resolved) and 180.6 C (lumped); 13 of 16 trigger cells peaked above the central case's cell 1 (548 C).
5. Exploratory: over the paper's Section 2, in the central case, the face away and the lumped neighbour heat at 0.35 to 0.52 C/s (the line of contact faster), 3.5 to 5.2 times the tests without propagation (0.1 C/s) and near those with it (0.4), but not as hot.
6. Scorecard: P1 (in 147 to 342 s) failed; P6 (30 to 90 %) failed at 0 %; P2 (lumped later or never) held; P3 to P5 and P7 not met, so failed.
7. Lacking the tests' venting, ejecta and flame, the model was expected to propagate later than they did, if at all; it never does. Conduction and radiation alone do not suffice here, and P2 holds only because nothing propagates: whether a lumped cell can be trusted in a pack stays open.

## Stage 6 (v1.2)

1. The paper's 150 C criterion on the 36 Stage 5 grid runs (predictions c9586a8): only the lumped neighbour at the central contact crosses inside the measured 147 to 342 s, in 11 of 12 runs; the hot spot crosses at 7 to 22 s; the face away and the resolved mean never reach 150 C.
2. Trigger matched to the tests (releases of 17.5 to 25.2 s from the paper's supplementary Figure 10, conditional): at 33.2 kJ cell 1 peaks at 526 to 537 C in the central case, inside the measured 164 to 832 C; at the Databank's total with ejecta, 107 kJ, at 1,424 to 1,494 C (P4 failed).
3. Matched case, 442 runs with the 200 draws: neither neighbour reaches 255.7 C (hot spot at most 227 C, lumped 179 C), as in Stage 5.
4. At 107 kJ the hot spot reaches 255.7 C in every run at 8 to 17 s, the lumped neighbour 32 to 168 s later (P7 held); exploratory, at the tests' median trigger peak (704.5 C, 45.2 kJ) only the high contact ignites (hot spot 17 s, lumped 198 to 236 s).
5. Scorecard: P1 to P6 failed, five of them foreseeable from Stage 5's records, as the predictions state; P7 held.
6. The matched trigger does not ignite the neighbour by conduction and radiation; where the hot spot ignites it does so before any test propagated, the lumped neighbour inside their window in 13 of 50 runs. Next: the ignition condition (aged SEI, internal short as an event), set up, not run.

## Stage 7 (v1.3)

1. One trigger per test (predictions 714b1fd): the energy that puts cell 1 at each test's measured maximum (9.0 to 54.3 kJ for 164 to 832 C, central case, 21.39 s release); seven ignition conditions read from 96 runs (the sixteen tests at three contacts, fresh and aged SEI) and scored against the sixteen outcomes, the central contact registered.
2. At the central contact the hot spot at 255.7 C (C1) predicts 8 tests: 6 hits and 2 false alarms, 11 of 16 right, but every hit 130 to 323 s before the measured time; the lumped neighbour at 255.7 C (C2) predicts 2, both hits.
3. There the lumped neighbour at the paper's 150 C (C3) and the separator's melting, 138.5 C, at the hot spot (C4) or in the lumped neighbour (C5) each predict the same 14 tests: 8 hits and 6 false alarms, 9 of 16 right; C3's hits come 43 to 260 s early.
4. An aged SEI (none left) changes no hot-spot verdict at the central contact and raises the first self-heating from 108.4 C to 181.5 to 202.1 C (a cathode reaction); the other two releases and the separator's spread change no verdict.
5. At the central contact the internal short as an event (the cell's stored 65.52 kJ released over 21.39 s from the melt, a modelling choice) takes the hot spot to 1,504 to 1,584 C, about twice the hottest propagating neighbour (763 C): none of 28 runs lies in the measured 381 to 763 C, nor any at 63.36 kJ. Nothing in it is a source to a further cell; the geometry ends at the neighbour.
6. Scorecard: P1 (C1 in fewer than 9), P4 (C4 in more than 9) and P6 (no inversion) held; P2 (9 of 16, one short), P3 (1 of 8 within 60 s), P5 (raised, not lowered), P7 (C1 6 to 2) and P8 (0 of 28) failed, each as its predictions expected.
7. No criterion reproduces the tests: the whole cell's clocks predict too many (C3, C5) or too few (C2), the hot spot's come minutes early, and the event overshoots without venting or ejecta (in the Databank's nail tests the cell body kept 19 to 31 % of the energy). Exploratory: the hot spot's 255.7 C is a passing peak (262 to 307 C, then cooling), and no threshold on the trigger's peak gets more than 12 of 16 right.

## Stage 8 (v1.4)

1. The inverse question (predictions b8dafb4): what fraction f of each trigger's ejected energy (its body energy times the median ejected-to-body ratio of the Databank's ten M50 nail tests, 3.11: 27.9 to 168.6 kJ), delivered over 21.39 s as a flux through the half of the neighbour's can facing the trigger, would the model need to reproduce each test's outcome? A search finds f\*, the smallest fraction at which the neighbour meets a criterion; it is a model quantity, not a measurement of what reached the neighbour.
2. For the hot spot at 255.7 C (C1) f\* is 0 in eight tests (Stage 7's runs) and at most 0.1625 in every test; for the lumped neighbour (C2) at most 0.05 in thirteen and at most 0.4625 in all, both highest in M50_PT_Exp1, the smallest trigger.
3. The two groups overlap: the nine propagated tests need f\*(C1) of 0 to 0.0875, while the seven that did not propagate reach it at 0 to 0.1625 (C2: 0 to 0.2375 against 0 to 0.4625), so no single fraction reproduces the sixteen outcomes. If a delivered fraction set them, it would have had to vary from test to test, a quantity the tests did not control, and propagation at a given trigger would be a probability.
4. At f = 0.1, 0.2 and 0.3 for every test, C1, C2 and the lumped neighbour at 150 C (C3) each predict 14 to 16 tests and get 9 or 10 of 16 right; every clock crosses by 88.3 s after the release, and every hit comes 126 to 339 s early.
5. Not registered: a 10 or 60 s delivery puts M50_PT_Exp1's f\*(C1) at 0.1 to 0.1125 or 0.275 to 0.2875, the quarter of the facing half nearest the cap at 0.0375 to 0.05, and the ratio's bracket scales every f\* by 0.75 to 1.40. In the parallel tests, 20 % of the stored 65.52 kJ as Joule heat in the neighbour takes every hot spot to 255.7 C with no delivery.
6. Part D: Hoelle, Zimmermann and Hinrichsen's gas layer (J. Electrochem. Soc. 170 (2023) 060516; Eq. 28 and 29, Tables V and VI) between the roll and the can, at f = 0.2 in the three tests nearest the median trigger: the hot spot peaks at 192.4 to 196.5 C and does not reach 255.7 C within 900 s, where without the layer it does at 3.5 to 3.7 s, while the can reaches 1,886 to 1,924 C (with no melting or venting in the model). So with the layer f\*(C1) lies above 0.2 there, against 0 to 0.0125 without it; the lumped neighbour, one node, is unchanged by construction.
7. Scorecard: P1 (Stage 7's hits at 0, its misses below 0.3), P2 (the overlap), P5 (none above 12 of 16), P6 (no inversion, two tests at 0 read as equal) and P8 (the cap end lowers f\*(C1)) held; P3 (3 of 16 between 0.05 and 0.5), P4 (none within 60 s) and P7 (M50_PT_Exp1 lowered by 0.15 to 0.1625) failed, each as its predictions expected.
8. Exploratory: a fraction drawn for each test from one log-normal (median 0.027, against f\*(C2)) fits the outcomes not significantly better than one probability for every test (likelihood ratio 3.16, p = 0.075), nor does a logistic in the trigger energy (p = 0.32): sixteen tests do not resolve how the probability depends on the trigger.

## Stage 9 (v1.5)

1. Each test's own measurement read as a delivered fraction (predictions f4b25e6): f_t, at which a criterion is met at the measured time, for the nine tests that propagated; f_max, at which the thermocouple's node (the face away from the trigger, at mid-length) peaks at the measured maximum, for the seven that did not; each by bisection to a bracket of 0.005, or to a run within 10 s or 5 K. The propagated tests are read by their times only and the non-propagated by their peaks only: after ignition the model's temperatures are not comparable with the measured maxima (Stage 7's event overshot them about twofold).
2. With Stage 8's 21.39 s delivery the hot spot (C1) reproduces no measured time: wherever it crosses 255.7 C, it does so by 21.1 s. The lumped neighbour (C2) reproduces six of the nine within 10 s, at f_t = 0.0016 to 0.047 of the ejected energy (0.27 to 5.96 kJ), at most 0.019 above Stage 8's f\*(C2). In M50_PT_Exp4, ST_Exp3 and ST_Exp4 it goes, within 0.0031 of f, from not crossing to crossing 56.4 to 81.9 s before the measured time.
3. Conduction alone takes the thermocouple's node 13.8 to 56.3 K above four of the five low maxima of the tests that did not propagate (f_max = 0); M50_PT_Exp1, the smallest trigger, needs 0.075 (2.09 kJ) for its 71 C. So the fractions do not separate the two groups either: that 0.075 lies above the smallest f_t(C2), M50_SP_Exp3's 0.0016, while the four zeros lie below every f_t. Exploratory: 0.27 and 0.56 for the maxima of 626 and 808 C.
4. Delivered instead as a constant power over 120, 240 or 360 s (conditional), 1.1 to 70.0 W reproduces seven or eight of the nine times through C2, and over 240 or 360 s one or two through C1 as well, with up to 25.2 kJ. A long delivery can often place a crossing inside its own duration by its power, though not always, so what it yields is the energy and power needed, against 0.27 to 5.96 kJ in 21.39 s under the near-threshold reading.
5. Not registered: in the runs at f_t(C2) the thermocouple's node reads 171.6 to 204.6 C at the measured time, within the onset temperatures of the paper's Fig. 3(a), about 168 to 205 C. What would tell the two readings apart is the neighbour's surface history before propagation, which the paper publishes for one test, M50_PT_Exp4.
6. Scorecard: P1 (no C1 time within 30 s), P2 (six of nine), P3 (every f_t(C2) at most 0.019 above f\*_hi), P7 (factors 0.75 and 1.40, P5 unchanged) and P8 (the aged SEI moves f_t(C2) by at most 0.0031) held; P4 (M50_ST_Exp1 and ST_Exp2 are met by C1 at f = 0), P5 and P6 (under 240 s only M50_ST_Exp3's hot spot reproduces its time, at 0.325; M50_PT_Exp4's 272 s lies after the delivery, and M50_PP_Exp2's crossing jumps past its 147 s) failed, each as its predictions expected.
7. Near its threshold the whole cell's clock has an induction of the measured order and the hot spot's has none; a few kJ in 21.39 s and 1 to 70 W for minutes each reproduce most measured times, and neither reading separates the tests that propagated from those that did not. f_t and f_max are fractions a conduction-and-delivery model needs, not measurements of what reached the neighbour.

## What it means for the thesis

Under DSC-trained kinetics a neighbour heated through copper busbars at 33.2 kJ starts to react where the busbar enters, before a lumped model in all 200 draws of the kinetic posterior (by 15 to 59 s in 95 % of them at the 30 s release); the uncertain kinetics, not the roll's published properties, set when. Next: an aged SEI in a resolved, two-way coupled cell with the cap and tabs.

<p class="credit">Credit: The Battery Failure Databank is provided by the U.S. Department of Energy's National Renewable Energy Laboratory, operated by Alliance for Sustainable Energy, LLC (DOE/NREL/ALLIANCE); its notice accompanies the rows used, in inputs/databank/.</p>

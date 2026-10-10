# Onset kinetics on a resolved neighbour cell: where a whole-cell threshold and a local one disagree

::: byline
Siddharth Satte, Independent researcher, Pune, India, 10 October 2026. A pre-registered pilot: predictions commit b09ef1d, public before any kinetics ran on an archived history. [doi.org/10.5281/zenodo.23279456](https://doi.org/10.5281/zenodo.23279456){.nobr}; [github.com/siddharth161204-wq/m50-neighbour-onset-kinetics](https://github.com/siddharth161204-wq/m50-neighbour-onset-kinetics){.nobr}.
:::

<div class="headline">

1. With copper busbars (500 mW/K in all) and the largest Databank energy (33.2 kJ), the resolved neighbour's hottest node starts to self-heat at 0.15 K/min 23.4 s and 26.4 s before the lumped node: 4.2 against 27.6 s for a 10 s release, 11.5 against 37.9 s for 30 s. Under the posterior-mean B-CRNN kinetics of Koenig, Zhao and Deng every such start is a fresh SEI decomposing at 108.4 C; in our emulation of their slow ARC test, which consumes the SEI first, they give 179 C.
2. The smallest busbar conductance at which only the local chemistry starts is 100 mW/K (21.5 kJ, both releases, fresh SEI).

</div>

![](../results/neighbour_onset_figure.png)

Figure 1. (a) First time each history self-heats at 0.15 K/min, 30 s release, 33.2 kJ (filled) and 21.5 kJ (hollow); ringed where only the hottest node starts. (b) Kinetic self-heating rate along the three histories, 33.2 kJ, 30 s, 500 mW/K (passive); gaps are where separator melting makes the net rate endothermic. (c) The same case with the reaction heat (solid) and without it (dashed): the hottest node enters the internal-short band at 19.2 s, as it does without the reaction heat, and a node's layered cathode is 99 % consumed 2.8 s later, with about 0.5 % of the cell above 255.7 C; the lumped node peaks at 226 C, yet converts 63 % of its layered cathode and releases 7.1 times the resolved cell's reaction heat.

## Method

1. Kinetics: the B-CRNN of Koenig, Zhao and Deng (Chem. Eng. J. 507 (2025) 160402), each parameter averaged over the trained particles of its supplementary material: three NCM811 cathode reactions, seven anode-electrolyte-SEI-binder reactions and separator melting, with their 720 g cell's reactant masses as mass fractions of the M50 neighbour.
2. Checks against the source: their DSC curves at 5 C/min are reproduced (cathode 0.49 W/g at 223.7 C, separator −0.079 W/g at 138.5 C); our emulation of their ARC test gives T~in~ = 179.3 C, inside their main-cluster band of 169.0 to 198.0 C, but T~on~ = 199.8 C at their stated 1 C/min trigger, below their band of 255.7 to 302.1 C (272.7 C at 1 C/s).
3. Stage 1, passive (no heat fed back): BDF along three archived 0.5 s histories of each case of the two-cell study (doi:10.5281/zenodo.23253738; 42 two-strip, 7 one-strip cases): resolved hottest node, resolved mean, lumped node.
4. Stage 2, reactive and one-way, five cases: the reaction heat is a nodal source in the published resolved solver (scikit-fem; anisotropic roll, steel can, strip contacts, gap conduction and radiation) and the lumped node, split with an adaptive step.
5. Checks: halving every tolerance, step and grid moves the headline onsets by at most 4 × 10^−6^ of themselves; Stage 2 energy accounts close to 1.3 × 10^−12^; with a 10^4^ W/mK roll the two reactive models agree within 0.8 K; without the source Stage 2 reproduces the archived histories to 1.3 × 10^−12^ K; halving its step limits moves the band entry by under 10^−4^.
6. Predictions public before any kinetics ran on an archived history; P1 to P4 scored and pushed before Stage 2 ran.

## Limits

1. The kinetics belong to other cells: a posterior mean trained on NCM811 and graphite DSC data, with the source cell's reactant fractions, not the M50's silicon-graphite negative, and no kinetic uncertainty. Every start is decomposition of a fresh SEI, which the model also decomposes at 25 C (80 % in a week); with the SEI gone, starts move to the first cathode reaction (180 to 211 C) and the lead grows to 60 s (exploratory).
2. Stage 1 ignores the reaction heat; Stage 2 is one-way; conduction and radiation only, so ejecta, flame and venting are excluded and none of this is propagation. The internal short is the source's T~on~ band as a temperature, not a model: at its own trigger, 1 K/min of self-heating, the lumped node would short too, 58 s after the hottest node.
3. One geometry without the cap and tabs, constant properties, and a hottest node that is the envelope of local histories.

## Prediction scorecard

| | Prediction | Result | Measured |
|---|---------------------------------------------|----------|-----------------------------------------|
| P1 | 33.2 kJ, 500 mW/K: the hottest node starts over half the lumped time earlier | Held | 85 % and 70 % earlier (central 86 % and 71 %) |
| P2 | The resolved mean starts in exactly 10 named cases | Held | The same 10 |
| P3 | Smallest conductance with only the hottest node starting: 100 mW/K | Held | 100 mW/K; also 8.75 kJ at 500 mW/K, as named |
| P4 | The hottest node reaches 10 K/min where the lumped node stays under 1 K/min | Held | In the 4 named cases |
| P5 | Stage 2: (a) 500 mW/K, only the resolved hottest region enters the internal-short band; (b) 200 mW/K, its own heat pushes it in; (c) 21.5 kJ, neither enters | (a) Held<br>(b) Failed<br>(c) Held | (a) 7.1 and 19.2 s, as without the reaction heat; lumped peaks 222 and 226 C (expected: lumped runaway); (b) +0.6 and +0.7 K (central 5 to 10 K); (c) +0.2 K each (central about 2 K and a few K) |

## What it means for the thesis

Under DSC-trained kinetics with a fresh SEI, a neighbour heated through copper busbars at 33.2 kJ starts to react where the busbar enters, at 108 C and 23 to 26 s before a lumped model does, while the reaction heat barely moves that hot spot, which reaches the internal-short band by conduction. The lumped model errs the other way in the bulk, with six to seven times the resolved reaction heat, so next comes the B-CRNN posterior, with an aged SEI, in a resolved, two-way coupled cell with the cap and tabs.

<p class="credit">Credit: The Battery Failure Databank is provided by the U.S. Department of Energy's National Renewable Energy Laboratory, operated by Alliance for Sustainable Energy, LLC (DOE/NREL/ALLIANCE); its notice accompanies the rows used, in inputs/databank/.</p>

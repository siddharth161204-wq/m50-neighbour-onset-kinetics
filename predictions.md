# Predictions

Written on 10 October 2026, before any kinetics were integrated along an archived temperature history of the two-cell study (doi:10.5281/zenodo.23253738, v1.0.0). The information used: that study's published result tables (`results/resolved_summary.csv` and `results/lumped_results.csv` at v1.0.0, which give each case's peak temperatures and the times at which each history first reaches 169.0, 183.5, 198.0 and 255.7 C), and this study's checks V0, V1 and V2, which use only the source paper's own cells and synthetic temperature histories. The only archived series opened before this file was committed is the headline case (33.2 kJ, 30 s, 500 mW/K), to confirm that its hottest node first reaches 183.5 C at 15.51 s; nothing else in it was read. This file is committed and pushed to the public repository before Stage 1 runs, and the commit hash is recorded in the README.

## Definitions used for scoring

Kinetics: the posterior-mean B-CRNN model of Koenig, Zhao and Deng (2025) (DECISIONS.md D1 to D7). Self-heating rate: the reaction heat per unit volume divided by the neighbour's volumetric heat capacity (passive in Stage 1). Histories: the resolved hottest node (`Tmax`), the resolved mean (`Tmean`) and the lumped node (`T2_be`). A history "reaches" a level when its self-heating rate first equals or exceeds it within 900 s. P2 to P4 are scored on the 42 two-strip cases (D11). Stage 2 (D12): the hottest region is the hottest node of the reactive resolved cell; it enters the internal-short band when it first reaches 255.7 C; the reactive lumped cell is the lumped node with the same reaction source per unit mass; cell 1's history is the archived one.

## What V1 and V2 already show (known when these were written)

- With fresh reactants the neighbour self-heats at 0.15 K/min from 108.4 C, by SEI decomposition. On every rising synthetic history (ramps of 0.3 to 30 K/s and smooth pulses) the 0.15 K/min level is reached at 108.39 C, with no measurable kinetic delay, because SEI consumption below that temperature is negligible over seconds to minutes.
- In the paper's own ARC test the same kinetics give T_in = 179.3 C (V1, within the band 169.0 to 198.0 C), because about 25 hours of heat-wait-seek consume the SEI before the cell gets there. So in this study the 0.15 K/min level marks SEI decomposition near 108 C, not the T_in of 183.5 C used as a fixed threshold in the two-cell study.
- 1 K/min is reached between 174 C (ramp of 0.3 K/s, SEI decomposition) and 205 C (ramp of 30 K/s, where the endothermic separator melting overlaps the exotherms); 10 K/min between 212 and 219 C on every ramp, led by the first cathode reaction.

The predictions follow from when each history crosses about 108 C, 175 to 205 C and 212 C.

## The predictions

P1. At 33.2 kJ and 500 mW/K, for both release durations, the hottest node reaches 0.15 K/min before the lumped node does, by more than half of the lumped time. Central estimate: 4.2 s against 29 s for the 10 s release (86 % earlier) and 11.5 s against 39 s for the 30 s release (71 % earlier).

P2. The resolved mean reaches 0.15 K/min in exactly 10 of the 42 cases: 33.2 kJ at 100, 200 and 500 mW/K, and 21.5 kJ at 200 and 500 mW/K, each with both release durations. It does not reach it at 8.75 kJ, nor at 33.2 kJ and 50 mW/K, where the resolved mean peaks at 107.0 and 107.3 C, just under the 108.4 C onset. P2 holds if the set of cases is exactly this one.

P3. The smallest busbar conductance at which the hottest node reaches 0.15 K/min while the lumped node does not is 100 mW/K (21.5 kJ, both release durations; central estimate 100 mW/K). The other cases in which only the hottest node starts are 8.75 kJ at 500 mW/K, both durations. At 50 mW/K and 33.2 kJ both start (lumped peaks 110.7 and 111.1 C), and at 20 mW/K neither does. P3 holds if the smallest such conductance is 100 mW/K.

P4. The hottest node reaches 10 K/min in at least one case in which the lumped node does not reach 1 K/min. Predicted cases: 33.2 kJ at 200 mW/K and 21.5 kJ at 500 mW/K, both release durations, four cases in all (hottest-node peaks of 237 to 251 C against lumped peaks of 152 to 169 C). At 33.2 kJ and 500 mW/K the lumped node, peaking at 211 to 212 C, also reaches 1 K/min, so those two cases are not among them. P4 holds if the statement's first sentence holds; the case list is scored separately.

P5. Stage 2, reactive coupling.
(a) As the brief states it: at 33.2 kJ and 500 mW/K the reactive resolved cell's hottest region enters the internal-short band while the reactive lumped cell does not. Central estimate: the hottest region enters at about 7.1 s (10 s release) and 19.0 s (30 s release), slightly before the passive 7.13 and 19.24 s, and then runs away locally. The reactive lumped cell is expected to run away too, because its passive peak, 211 to 212 C, lies above the temperature at which the reaction heat grows faster with temperature than the losses and the strip exchange do (about 205 to 208 C); expected entry into the band at about 170 s (10 s release) and 180 s (30 s release). P5(a) is therefore expected to fail on its second half (probability that the lumped cell stays out of the band: about one in three).
(b) At 33.2 kJ and 200 mW/K the hottest region, whose passive peak is 250.7 to 250.8 C, is pushed into the band by its own reaction heat at about 20 s (10 s release) and 33 s (30 s release), while the reactive lumped cell, passive peak 168 to 169 C, peaks about 4 K higher and stays out of it. The lumped half is near certain; the resolved half is about even odds.
(c) At 21.5 kJ, 500 mW/K and 30 s neither enters the band: the hottest region peaks about 2 K above its passive 236.7 C, the lumped cell a few kelvin above its passive 152.8 C.

## Reasoning behind the central estimates (hand calculation, no kinetics run on an archived history)

Onset of 0.15 K/min. V2 shows that every rising history reaches 0.15 K/min at 108.4 C, so each prediction about this level reduces to when, and whether, a history passes 108.4 C. Whether it does follows from the published peaks (P2, P3). When it does follows from the published crossing times of the higher levels.

Hottest node, 33.2 kJ and 500 mW/K. The positive-terminal patch runs at a fraction f of cell 1's rise (the two-cell study's predictions.md). Before the release peaks, cell 1 rises as 25 + (2E/(tau C)) t^2/tau: 25 + 10.76 t^2 for tau = 10 s and 25 + 1.20 t^2 for tau = 30 s. The published crossings of 169.0 C at 5.43 s and 14.82 s give f of about 0.45 and 0.55 there, so the patch passes 108.4 C at about 4.1 s and 11.3 s; f is smaller earlier, which moves both a little later: 4.2 s and 11.5 s.

Lumped node, same case. Its published crossings (169.0, 183.5 and 198.0 C at 57.5, 69.6 and 88.0 s for the 10 s release; 67.3, 79.2 and 96.8 s for 30 s) show its heating rate falling from 1.2 to 0.8 K/s with an e-folding time of about 37 s, as cells 1 and 2 approach each other. Extrapolated back to 108.4 C this gives 28.7 s and 39.1 s; an independent estimate from the strip exchange after cell 1 peaks, 0.517 W/K times (T1 minus T2) over 61.75 J/K, gives 29.8 s and about 38 s. Central: 29 s and 39 s.

P4. 10 K/min needs the hottest node above about 212 to 219 C, which only the cases with hottest-node peaks of 237 C and above reach; 1 K/min needs the slowly heated lumped node above about 174 to 184 C, which only the two 33.2 kJ, 500 mW/K cases reach.

P5. Lumped cell: near 212 C the fresh-reactant self-heating is about 10 K/min, 0.17 K/s, and grows by about 11 % per kelvin (mostly the first cathode reaction, Ea about 220 kJ/mol), 0.019 K/s per K, while the cooling of the lumped node grows by (G_bus + G_gap + h A_conv + 4 eps sigma A_rad T^3) / C, about 0.011 K/s per K. Above about 205 to 208 C the reaction therefore outgrows the cooling, and a node held near 211 C by cell 1 should run away; from 212 C the growth time of about 120 s shortens as the rate doubles every 6 K, giving about 60 s to reach 255.7 C, and the node is expected near 212 C at about 110 s (10 s release). Hot spot: the heated layer under the 8 mm disc relaxes by axial conduction (25 W/mK) over d^2/alpha, 0.4 to 0.8 s for d of 2 to 3 mm. The local reaction heating runs away when its growth per kelvin times that time exceeds 1, which needs about 10 to 15 K/s of local heating, reached near 255 to 265 C. At 500 mW/K the passive hot spot reaches 348 to 356 C, so local runaway is certain once it passes about 260 C; at 200 mW/K (250.7 C) the reaction raises the peak by about q tau / (1 - q' tau), 5 to 10 K, which puts it at the band's edge; at 236.7 C (21.5 kJ) by about 2 K.

## What would count against the thesis

If P1 and P3 fail, so that the hottest node starts no earlier than the lumped node and no case starts only locally, the resolved field adds nothing to the timing of onset under these kinetics. If P5(a) holds as stated, the lumped cell is more stable than this reasoning gives, and a local start that runs away is something only the resolved model can show at copper busbars.

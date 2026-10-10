# Posterior-mean B-CRNN model used (Koenig, Zhao and Deng 2025, supplementary material)

Rate r = exp(sum of n ln c + ln A + b ln T - Ea / (R T)), T in K, A in 1/s; heat = dH r per gram of the reaction's mass; initial amounts: liquid electrolyte, intercalated lithium, binder, layered cathode and separator 1, SEI 0.15, all others 0 (paper Fig. 2, Eq. 10 and 11). Each value is the arithmetic mean over the trained (SVGD) particles of the supplementary files (D3). Separator melting is endothermic (DECISIONS.md D5): its dH is shown with that sign applied, while the supplementary file stores the magnitude. The anode-electrolyte reaction's mass is the anode plus electrolyte mass (D4); the masses are those of the paper's Table 1, whose cell is that of Feng et al., Applied Energy 154 (2015) 74 to 91.

| Reaction | Rate orders | Stoichiometry | ln A (1/s) | Ea (kJ/mol) | b | dH (J/g) | Mass in the 720 g cell (g) |
|---|---|---|---|---|---|---|---|
| Electrolyte evaporation | ele_liq order 1.0343 | -1.0178 ele_liq; +1.4063 ele_gas | 34.178647 | 177.5992 | 0.333100 | -112.3733 | 108.00 |
| Electrolyte (vapour) decomposition | ele_gas order 3.5229 | -0.3703 ele_gas; +1.0002 p_ele_d | 23.672969 | 119.4713 | -0.348436 | 142.4953 | 108.00 |
| Anode (intercalated Li) with liquid electrolyte | ele_liq order 0.4161 * li_an order 0.9271 | -0.0500 ele_liq; -0.1860 li_an; +1.1653 p_an_ele | 32.964714 | 165.8580 | 0.099993 | 204.3350 | 208.58 |
| Anode (intercalated Li) with binder | li_an order 1.1885 * binder order 1.1891 | -0.5715 li_an; -0.5708 binder; +1.0000 p_an_bin | 66.287217 | 323.4902 | -0.428398 | 107.0021 | 100.58 |
| SEI decomposition | sei order 0.1634 | -0.6148 sei; +1.2770 p_sei_d | 12.633622 | 43.7592 | -1.671165 | 1573.6373 | 100.58 |
| Reaction IV | ele_gas order 0.9230 * p_an_ele order 1.5432 * p_sei_d order 0.7690 | -0.1410 ele_gas; -0.5929 p_an_ele; -0.0800 p_sei_d | 67.009763 | 347.5076 | 0.514061 | 156.9574 | 104.30 |
| Reaction V | p_ele_d order 0.5690 * p_an_bin order 0.6430 | -0.9919 p_ele_d; -0.8890 p_an_bin | 24.919768 | 164.0702 | 0.368032 | 115.5153 | 104.30 |
| NCM811 layered to spinel | cat1 order 1.3419 | -1.0000 cat1; +0.4887 cat2 | 43.488873 | 220.2341 | 0.826665 | 164.9416 | 179.12 |
| NCM811 spinel to second spinel | cat2 order 1.3272 | -1.0000 cat2; +1.3235 cat3 | 29.223402 | 150.3458 | -0.086434 | 35.3961 | 179.12 |
| NCM811 second spinel to rock salt | cat3 order 1.2251 | -1.0000 cat3 | 24.850376 | 171.0062 | 0.015279 | 177.0778 | 179.12 |
| Separator melting | sep order 1.2311 | -2.0879 sep | 48.297022 | 186.1691 | 0.141004 | -43.4693 | 17.60 |

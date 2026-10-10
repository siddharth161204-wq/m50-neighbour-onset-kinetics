# Kinetics source

Paper: B.C. Koenig, P. Zhao, S. Deng, Comprehensive thermal-kinetic uncertainty quantification of lithium-ion battery thermal runaway via Bayesian chemical reaction neural networks, Chemical Engineering Journal 507 (2025) 160402, doi:10.1016/j.cej.2025.160402. The paper states (Section 3.2.1) that "a complete report of the B-CRNN kinetic models is provided in the supplementary materials".

Supplementary material (Appendix B of the paper): `https://ars.els-cdn.com/content/image/1-s2.0-S1385894725012070-mmc1.zip`, 155,515 bytes, retrieved 10 October 2026. It is not redistributed here; `fetch_supplementary.py` downloads it and checks it against these SHA-256 values:

| File | Bytes | SHA-256 |
|---|---|---|
| mmc1.zip | 155,515 | 021d012941ad0b77f69748667f9c2b37530e888c025e2227e340437b5cc24fa6 |
| An_Ele.csv | 102,107 | 116ba9222f9841d6f1260960f74fcc50a4ac0aa8f73cd2bb8edf9d2cff4e57bd |
| NCM811.csv | 160,822 | 6edcf2579afc61eeb06f2d85b32708974aeeea37a0ff8f38bc8f492d77f88c5e |
| Separator.csv | 11,299 | b6db19b96a720849df9109f583effde6927dfb603d5e826f122f43fe3681be93 |
| CSV_model_key.docx | 50,242 | 56276337b5332a8596e66ee5a8144719ac9345f1f12bb5d2ef6212e4187a876b |

Layout, from `CSV_model_key.docx` and the legend image inside it: each CSV holds one parameter per row and one SVGD particle per column (100 particles for An_Ele.csv and Separator.csv, 500 for NCM811.csv).

- `NCM811.csv`, 17 rows: ln A1 to A3, Ea1 to Ea3 divided by 1e5, b1 to b3, dH1 to dH3, n1 to n3, v1 and v2 (the three sequential cathode reactions of the paper's Eq. 10).
- `Separator.csv`, 6 rows: ln A, v, n, Ea divided by 1e5, b, dH (Eq. 11).
- `An_Ele.csv`, 220 rows: rows 1 to 90 are reaction orders and rows 91 to 180 stoichiometric coefficients, each as 9 species by 10 reactions, row = 10 x species + reaction + 1 (plus 90 for the coefficients), with the species in the order liquid electrolyte, vapour electrolyte, intercalated lithium of the anode, binder, SEI, and the products of electrolyte decomposition, of the anode-electrolyte reaction, of the anode-binder reaction and of SEI decomposition, and the reactions in the order electrolyte evaporation, electrolyte decomposition, anode-electrolyte, anode-binder, SEI decomposition, SEI regeneration, IV, IV', V, V' (SEI regeneration, IV' and V' are zero in every particle, as the key states); rows 181 to 190 ln A, 191 to 200 Ea divided by 1e5, 201 to 210 b, 211 to 220 dH.

Units, confirmed by reproducing the source papers' own numbers (`results/v0_dsc_check.json`, `results/v1_arc_check.json`): A in 1/s (the ln A row), Ea in J/mol after multiplying by 1e5, b multiplies ln T with T in kelvin, dH in J/g. With these, the mean cathode model gives ln k1 = -4.55 at 225 C, ln k2 = -4.31 at 275 C and ln k3 = -5.16 at 410 C, the values in Table 1 of Koenig et al., Proc. Combust. Inst. 40 (2024) 105243, from which the cathode particles come.

Initial dimensionless amounts (paper Fig. 2): liquid electrolyte, intercalated lithium and binder 1; SEI 0.15; vapour electrolyte and the four products 0. Cathode: the layered phase 1, the two spinel phases 0. Separator 1.

`bcrnn_mean_model.json`: the arithmetic mean of every row over its particles (DECISIONS.md D3), to 17 significant digits. These values were computed from the files above in a browser session on 10 October 2026, because the cloud machine on which this study ran could not reach the publisher's file server; `extract_mean_model.py` recomputes them from the downloaded files and must agree to 1e-12 of each value.

`digitize_figA1.py` and `figA1a_mass_basis.json`: the reading of the paper's Fig. A.1(a) that fixes the mass multiplying the anode-electrolyte reaction (DECISIONS.md D4). The script needs the paper's PDF, which is not redistributed.

Cell parameters of the paper's ARC simulation (its Table 1, taken there from Feng et al., Applied Energy 154 (2015) 74 to 91, a 25 Ah NCM cell): complete battery mass 720 g; cathode 179.12 g; anode including binder 100.58 g; electrolyte 108 g; SEI 100.58 g; separator 17.6 g; unknown IV and V reactant 104.3 g (average of anode and electrolyte); external area 0.04 m2; specific heat 1100 J/(kg K); battery to ARC heat transfer coefficient 25 W/(m2 K); exotherm mode trigger 0.15 C/min; ISC trigger temperature gradient 1 C/min; initial temperature 25 C.

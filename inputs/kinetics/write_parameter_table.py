#!/usr/bin/env python3
"""The parameter table used (posterior-mean B-CRNN, DECISIONS.md D3 to D5), in readable form.

Usage: python3 write_parameter_table.py      (writes bcrnn_mean_model_table.csv and bcrnn_mean_model_table.md)
"""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
import bcrnn  # noqa: E402

kin = bcrnn.Kinetics()
NAMES = {"elec_evap": "Electrolyte evaporation", "elec_decomp": "Electrolyte (vapour) decomposition",
         "an_ele": "Anode (intercalated Li) with liquid electrolyte", "an_bin": "Anode (intercalated Li) with binder",
         "sei_decomp": "SEI decomposition", "IV": "Reaction IV", "V": "Reaction V", "cat1": "NCM811 layered to spinel",
         "cat2": "NCM811 spinel to second spinel", "cat3": "NCM811 second spinel to rock salt", "sep_melt": "Separator melting"}
rows = []
for j, r in enumerate(bcrnn.REACTIONS):
    reac = [f"{bcrnn.SPECIES[s]}^{kin.order[s, j]:.4f}" for s in range(bcrnn.NS) if kin.order[s, j] != 0]
    stoi = [f"{kin.stoich[s, j]:+.4f} {bcrnn.SPECIES[s]}" for s in range(bcrnn.NS) if kin.stoich[s, j] != 0]
    rows.append({"reaction": r, "description": NAMES[r], "rate_orders": " * ".join(reac), "stoichiometry": "; ".join(stoi),
                 "ln_A_per_s": f"{kin.lnA[j]:.6f}", "Ea_kJ_per_mol": f"{kin.Ea[j] / 1e3:.4f}", "b": f"{kin.b[j]:.6f}",
                 "dH_J_per_g": f"{kin.dH[j]:.4f}", "mass_in_720g_cell_g": f"{kin.mass_g[j]:.2f}",
                 "mass_fraction": f"{kin.w[j]:.6f}"})
with open(os.path.join(HERE, "bcrnn_mean_model_table.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(os.path.join(HERE, "bcrnn_mean_model_table.md"), "w") as f:
    f.write("# Posterior-mean B-CRNN model used (Koenig, Zhao and Deng 2025, supplementary material)\n\n")
    f.write("Rate r = exp(sum of n ln c + ln A + b ln T - Ea / (R T)), T in K, A in 1/s; heat = dH r per gram of the reaction's mass; "
            "initial amounts: liquid electrolyte, intercalated lithium, binder, layered cathode and separator 1, SEI 0.15, all others 0 "
            "(paper Fig. 2, Eq. 10 and 11). Each value is the arithmetic mean over the trained (SVGD) particles of the supplementary files (D3). "
            "Separator melting is endothermic (DECISIONS.md D5): its dH is shown with that sign applied, while the supplementary file "
            "stores the magnitude. The anode-electrolyte reaction's mass is the anode plus electrolyte mass (D4); the masses are those of "
            "the paper's Table 1, whose cell is that of Feng et al., Applied Energy 154 (2015) 74 to 91.\n\n")
    f.write("| Reaction | Rate orders | Stoichiometry | ln A (1/s) | Ea (kJ/mol) | b | dH (J/g) | Mass in the 720 g cell (g) |\n|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        f.write(f"| {r['description']} | {r['rate_orders'].replace('^', ' order ')} | {r['stoichiometry']} | {r['ln_A_per_s']} | {r['Ea_kJ_per_mol']} | {r['b']} | {r['dH_J_per_g']} | {r['mass_in_720g_cell_g']} |\n")
print(open(os.path.join(HERE, "bcrnn_mean_model_table.md")).read())

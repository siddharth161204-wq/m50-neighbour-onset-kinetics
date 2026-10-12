#!/usr/bin/env python3
"""Every Stage 3 number quoted in the README, the note and the release text, computed from the result files
(results/stage3_numbers.json), as src/note_numbers.py does for Stages 1 and 2.

Usage: python3 stage3_numbers.py --out ../results
"""
import argparse, json, os

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="../results")
a = ap.parse_args()
o = a.out
J = lambda f: json.load(open(os.path.join(o, f)))
v4, v4a, m3a, sc, v5, bc, est = (J("stage3_v4.json"), J("stage3_v4_amended.json"), J("stage3a_metrics.json"),
                                 J("stage3_scorecard.json"), J("stage3a_v5.json"), J("stage3bc_metrics.json"),
                                 J("stage3_prediction_estimates.json"))
H = "two_E33223_tau30_G0.5"
r1 = lambda x, n=1: None if x is None else round(x, n)
mh = m3a["metrics"][H]
out = {
    "V4_registered": {"main_cluster_share": v4["fractions"]["main_cluster"], "delayed_share": v4["fractions"]["delayed_short"],
                      "no_short_share": v4["fractions"]["no_short"], "T_in_p2.5_C": r1(v4["main_cluster_T_in_C"]["p2.5"]),
                      "T_in_p97.5_C": r1(v4["main_cluster_T_in_C"]["p97.5"]), "T_in_mean_C": r1(v4["main_cluster_T_in_C"]["mean"]),
                      "pass": v4["acceptance"]["pass"]},
    "V4_amended_D25": {k: r1(v4a["D25"][k]) for k in ("lower_edge_C", "upper_edge_C", "mean_C", "sd_C", "lower_edge_offset_C",
                                                     "upper_edge_offset_C", "mean_offset_C")} | {"pass": v4a["D25"]["pass"]},
    "headline_3a": {
        "hottest_onset_s": {k: r1(mh["onset_s"]["hottest_node"][k]) for k in ("p2.5", "p50", "p97.5", "mean", "sd")},
        "lumped_onset_s": {k: r1(mh["onset_s"]["lumped"][k]) for k in ("p2.5", "p50", "p97.5", "mean", "sd")},
        "hottest_onset_T_C": {k: r1(mh["onset_temperature_C"]["hottest_node"][k]) for k in ("p2.5", "p50", "p97.5")},
        "lead_s": {k: r1(mh["lead_s"][k]) for k in ("p2.5", "p50", "p97.5")} | {"n_lumped_not_started": mh["lead_s"]["n_lumped_not_started"]},
        "share_hottest_first": mh["share_hottest_before_lumped"], "share_only_hottest": mh["share_only_hottest_starts"],
        "share_sei_start": mh["share_hottest_onset_sei"], "reactions": mh["hottest_onset_reactions"],
        "share_below_100C": mh["share_hottest_onset_below_100C"], "share_no_onset": mh["share_no_onset_anywhere"]},
    "nine_cases_3a": {c: {"lead_p2.5_s": r1(m["lead_s"]["p2.5"]), "lead_p50_s": r1(m["lead_s"]["p50"]), "lead_p97.5_s": r1(m["lead_s"]["p97.5"]),
                          "share_hottest_first": m["share_hottest_before_lumped"], "share_only_hottest": m["share_only_hottest_starts"],
                          "share_sei_start": m["share_hottest_onset_sei"], "share_below_100C": m["share_hottest_onset_below_100C"],
                          "share_no_onset": m["share_no_onset_anywhere"]} for c, m in m3a["metrics"].items()},
    "P3_distribution": m3a["P3_distribution_42_cases"],
    "scorecard": {k: (sc[k]["held"] if isinstance(sc[k], dict) and "held" in sc[k] else sc[k]) for k in ("P1", "P2", "P3", "P4", "P5", "P6")},
    "P2_widths_s": [r1(sc["P2"]["hottest_width_s"]), r1(sc["P2"]["lumped_width_s"])],
    "V5": {"pass": v5["pass"], "worst_relative_change": v5["worst_relative_change"], "compared": v5["first_times_compared"]},
    "V6": bc["V6"],
    "decomposition": {q: {k: (r1(v[k], 3) if isinstance(v[k], float) else v[k]) for k in v} for q, v in bc["decomposition"].items()},
    "thermal_30": {q: {k: r1(bc["thermal_30_at_mean_kinetics"][q][k]) for k in ("p2.5", "p50", "p97.5", "mean", "sd")}
                   for q in ("hottest_onset_s", "lumped_onset_s", "lead_s")},
    "combined_210": {q: {k: r1(bc["combined_210_pairs"][q][k]) for k in ("p2.5", "p50", "p97.5", "mean", "sd")}
                     for q in ("hottest_onset_s", "lumped_onset_s", "lead_s")},
    "study_estimates": {"P1": est["P1_share_hottest_first"], "P2_s": [r1(est["P2_width_s"]["hottest"]), r1(est["P2_width_s"]["lumped"])],
                        "P3_share_100": est["P3_distribution"].get("100 mW/K"), "P6": est["P6_share_onset_below_100C"]},
}
# quantities the README quotes that no other result file holds
import csv
import numpy as np
rows = [r for r in csv.DictReader(open(os.path.join(o, "stage3a_onsets.csv"))) if r["case"] == H]
on = {(int(r["draw"]), r["history"]): r for r in rows}
D = sorted({k[0] for k in on})
lead = np.array([float(on[(d, "lumped")]["t_0.15Kpm_s"]) - float(on[(d, "hottest_node")]["t_0.15Kpm_s"]) for d in D])
rxn = [on[(d, "hottest_node")]["rxn_at_0.15Kpm"] for d in D]
Th = np.array([float(on[(d, "hottest_node")]["T_at_0.15Kpm_C"]) for d in D])
srt = np.sort(lead); k = int(np.argmax(np.diff(srt))); cut = (srt[k] + srt[k + 1]) / 2
second = lead > cut
cls = {int(r["draw"]): r["class"] for r in csv.DictReader(open(os.path.join(o, "stage3_v4_arc_draws.csv")))}
early = Th < 100.0
out["headline_3a_extra"] = {
    "hottest_onset_T_min_max_C": [r1(Th.min()), r1(Th.max())],
    "lead_modes": {"gap_s": [r1(srt[k]), r1(srt[k + 1])],
                   "first": {"n": int((~second).sum()), "lead_s": [r1(lead[~second].min()), r1(lead[~second].max())]},
                   "second": {"n": int(second.sum()), "lead_s": [r1(lead[second].min()), r1(lead[second].max())],
                              "n_cathode_start": int(sum(1 for i in range(len(D)) if second[i] and rxn[i] == "cat1")),
                              "n_sei_start": int(sum(1 for i in range(len(D)) if second[i] and rxn[i] == "sei_decomp")),
                              "sei_start_T_C": [r1(Th[[i for i in range(len(D)) if second[i] and rxn[i] == "sei_decomp"]].min()),
                                                r1(Th[[i for i in range(len(D)) if second[i] and rxn[i] == "sei_decomp"]].max())]}},
    "cathode_starts": {"n": int(sum(x == "cat1" for x in rxn)), "T_C": [r1(Th[[i for i in range(len(D)) if rxn[i] == "cat1"]].min()),
                                                                       r1(Th[[i for i in range(len(D)) if rxn[i] == "cat1"]].max())],
                       "lead_s": [r1(lead[[i for i in range(len(D)) if rxn[i] == "cat1"]].min()), r1(lead[[i for i in range(len(D)) if rxn[i] == "cat1"]].max())]},
    "sei_starts_lead_s": [r1(lead[[i for i in range(len(D)) if rxn[i] == "sei_decomp"]].min()), r1(lead[[i for i in range(len(D)) if rxn[i] == "sei_decomp"]].max())],
    "early_sei_by_V4_class": {c: int(sum(1 for i, d in enumerate(D) if early[i] and cls[d] == c)) for c in ("main_cluster", "delayed_short", "no_short")},
    "by_V4_class_medians_s": {c: {"n": v["n"], "hottest": r1(v["hottest_onset_s_median"]), "lumped": r1(v["lumped_onset_s_median"])}
                              for c, v in mh["by_V4_class"].items()},
    "mean_model_lead_s": r1(m3a["mean_model_stage1_onsets_s"][H]["lumped"] - m3a["mean_model_stage1_onsets_s"][H]["hottest_node"]),
}
td = bc["thermal_draws"]
c_roll = np.array([t["c_roll_J_per_kgK"] for t in td]); k_r = np.array([t["k_radial_W_per_mK"] for t in td])
hot = np.array([t["hottest_onset_s"] for t in td]); lump = np.array([t["lumped_onset_s"] for t in td])
out["thermal_30_extra"] = {"corr_lumped_onset_c_roll": round(float(np.corrcoef(c_roll, lump)[0, 1]), 5),
                           "corr_hottest_onset_c_roll": round(float(np.corrcoef(c_roll, hot)[0, 1]), 3),
                           "corr_hottest_onset_k_radial": round(float(np.corrcoef(k_r, hot)[0, 1]), 3)}
dec = bc["decomposition"]
out["variance_share_thermal_over_kinetic"] = {q: round((v["sd_thermal"] / v["sd_kinetic"]) ** 2, 4) for q, v in dec.items()}
hk = bc["V6"]["high_k"]
out["V6_high_k"] = {"max_abs_Tmax_minus_lumped_K": [r1(min(v["max_abs_Tmax_minus_lumped_K"] for v in hk.values()), 2), r1(max(v["max_abs_Tmax_minus_lumped_K"] for v in hk.values()), 2)],
                    "max_abs_Tmean_minus_lumped_K": [r1(min(v["max_abs_Tmean_minus_lumped_K"] for v in hk.values()), 2), r1(max(v["max_abs_Tmean_minus_lumped_K"] for v in hk.values()), 2)],
                    "energy_residuals": {t: float(f"{v['energy_residual_rel']:.2g}") for t, v in hk.items()}}
json.dump(out, open(os.path.join(o, "stage3_numbers.json"), "w"), indent=1)
print(json.dumps(out, indent=1)[:6000])

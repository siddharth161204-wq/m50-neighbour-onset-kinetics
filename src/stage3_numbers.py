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
json.dump(out, open(os.path.join(o, "stage3_numbers.json"), "w"), indent=1)
print(json.dumps(out, indent=1)[:6000])

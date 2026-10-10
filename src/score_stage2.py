#!/usr/bin/env python3
"""Stage 2 table and the scoring of P5 (predictions.md) from results/stage2/<case>.json, and the checks of D15.

Usage: python3 score_stage2.py --out ../results
Writes results/stage2_table.csv, results/stage2_scorecard.json and results/stage2_checks.json.
"""
import argparse, csv, json, os
import numpy as np

CASES = ["two_E33223_tau10_G0.5", "two_E33223_tau30_G0.5", "two_E33223_tau10_G0.2", "two_E33223_tau30_G0.2",
         "two_E21495_tau30_G0.5"]


def entry(d, key):
    return d["resolved"]["cross_s"][key]


PUBLISHED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "external", "m50-two-cell-pilot", "results",
                         "resolved_summary.csv")


def published_entry(case):
    """The two-cell study's own passive crossing of 255.7 C by the resolved hottest node (its resolved_summary.csv)."""
    E, tau, G = case.split("_")[1:]
    for r in csv.DictReader(open(PUBLISHED)):
        if (round(float(r["E_body_J"])) == int(E[1:]) and float(r["tau_rel_s"]) == float(tau[3:])
                and float(r["G_bus_WK"]) == float(G[1:])):
            v = r["T_onset_low_resolved_max_s"]
            return None if v == "never" else float(v)
    return None


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="../results"); a = ap.parse_args()
    rows, recs = [], {}
    for c in CASES:
        p = os.path.join(a.out, "stage2", c + ".json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p)); recs[c] = d
        z = np.load(os.path.join(a.out, "stage2", c + ".npz"))
        r, l, lp, pa = d["resolved"], d["lumped_reactive"], d["lumped_passive"], d["passive_archived"]
        rows.append({
            "case": c, "E_body_kJ": round(d["E_body_J"] / 1e3, 2), "tau_rel_s": d["tau_rel_s"], "G_bus_mWK": d["G_bus_WK"] * 1e3,
            "hottest_enters_255.7C_s": entry(d, "T_onset_low"), "hottest_reaches_278.9C_s": entry(d, "T_onset_mean"),
            "hottest_reaches_302.1C_s": entry(d, "T_onset_high"),
            "hottest_peak_reactive_C": round(r["peak"]["Tmax_C"], 2), "hottest_peak_passive_C": round(pa["Tmax_peak_C"], 2),
            "mean_peak_reactive_C": round(float(r["peak"]["Tmean_C"]), 2), "mean_peak_passive_C": round(pa["Tmean_peak_C"], 2),
            "layered_cathode_consumed_at_a_node_s": r["t_cat1_consumed_at_a_node_s"],
            "max_volume_fraction_above_255.7C_percent": round(100 * float(z["vol_frac_above_255p7"].max()), 3),
            "resolved_reaction_heat_J": round(r["energy_J"]["in_rxn"], 1),
            "resolved_layered_cathode_conversion_volume_mean_900s": round(r["conversion_volume_mean_900s"]["cat1"], 4),
            "lumped_peak_reactive_C": round(l["peak"]["T_C"], 2), "lumped_peak_passive_C": round(lp["peak"]["T_C"], 2),
            "lumped_enters_255.7C_s": l["cross_s"]["T_onset_low"], "lumped_reaction_heat_J": round(l["reaction_heat_J"], 1),
            "lumped_layered_cathode_conversion_900s": round(l["conversion_900s"]["cat1"], 4),
            "energy_residual_rel": r["energy_residual_rel"], "steps": r["steps"], "rejected_steps": r["rejected"]})
    with open(os.path.join(a.out, "stage2_table.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    def res_in(c):
        return recs[c]["resolved"]["cross_s"]["T_onset_low"] is not None if c in recs else None

    def lum_in(c):
        return recs[c]["lumped_reactive"]["cross_s"]["T_onset_low"] is not None if c in recs else None
    card = {}
    a1 = [res_in(c) and not lum_in(c) for c in CASES[:2]]
    card["P5a"] = {"statement": "33.2 kJ, 500 mW/K: the hottest region enters the band, the lumped cell does not",
                   "result": "held" if all(a1) else "failed",
                   "hottest_entry_s": [recs[c]["resolved"]["cross_s"]["T_onset_low"] for c in CASES[:2]],
                   "central_estimate_hottest_entry_s": [7.1, 19.0],
                   "lumped_peak_C": [recs[c]["lumped_reactive"]["peak"]["T_C"] for c in CASES[:2]],
                   "central_estimate_lumped": "expected to run away too, entering the band at about 170 s and 180 s (wrong)",
                   "registered_expectation": "P5(a) expected to fail on its second half; probability that the lumped cell stays out of the band about one in three",
                   "hottest_entry_without_reaction_heat_s": [published_entry(c) for c in CASES[:2]],
                   "note": "the hottest region enters the band at the same moment without the reaction heat (archived passive series, "
                           "and the no-source check run of the 30 s case at 19.244 s): its entry is set by conduction from the busbar"}
    if all(c in recs for c in CASES[2:4]):
        card["P5b"] = {"statement": "33.2 kJ, 200 mW/K: the hottest region is pushed into the band, the lumped cell stays out",
                       "result": "held" if all(res_in(c) and not lum_in(c) for c in CASES[2:4]) else "failed",
                       "hottest_peak_C": [recs[c]["resolved"]["peak"]["Tmax_C"] for c in CASES[2:4]],
                       "hottest_peak_passive_C": [recs[c]["passive_archived"]["Tmax_peak_C"] for c in CASES[2:4]],
                       "lumped_peak_C": [recs[c]["lumped_reactive"]["peak"]["T_C"] for c in CASES[2:4]],
                       "lumped_half_held": all(not lum_in(c) for c in CASES[2:4]),
                       "central_estimate_hottest_rise_K": "5 to 10", "central_estimate_lumped_rise_K": 4,
                       "registered_odds": "lumped half near certain; resolved half about even",
                       "hottest_rise_K": [recs[c]["resolved"]["peak"]["Tmax_C"] - recs[c]["passive_archived"]["Tmax_peak_C"] for c in CASES[2:4]],
                       "lumped_rise_K": [recs[c]["lumped_reactive"]["peak"]["T_C"] - recs[c]["lumped_passive"]["peak"]["T_C"] for c in CASES[2:4]]}
    if CASES[4] in recs:
        card["P5c"] = {"statement": "21.5 kJ, 500 mW/K, 30 s: neither enters the band",
                       "result": "held" if (not res_in(CASES[4]) and not lum_in(CASES[4])) else "failed",
                       "hottest_peak_C": recs[CASES[4]]["resolved"]["peak"]["Tmax_C"],
                       "hottest_peak_passive_C": recs[CASES[4]]["passive_archived"]["Tmax_peak_C"],
                       "lumped_peak_C": recs[CASES[4]]["lumped_reactive"]["peak"]["T_C"],
                       "central_estimate": "hottest region about 2 K above its passive peak, lumped cell a few kelvin above its own",
                       "hottest_rise_K": recs[CASES[4]]["resolved"]["peak"]["Tmax_C"] - recs[CASES[4]]["passive_archived"]["Tmax_peak_C"],
                       "lumped_rise_K": recs[CASES[4]]["lumped_reactive"]["peak"]["T_C"] - recs[CASES[4]]["lumped_passive"]["peak"]["T_C"]}
    json.dump(card, open(os.path.join(a.out, "stage2_scorecard.json"), "w"), indent=1, default=float)
    print(json.dumps(card, indent=1, default=float))

    # The checks of DECISIONS.md D15, gathered from their records (results/stage2_checks.json)
    S2 = os.path.join(a.out, "stage2")
    chk, runs = {}, {}
    for f in sorted(os.listdir(S2)):
        if f.endswith(".json"):
            runs[f[:-5]] = json.load(open(os.path.join(S2, f)))["resolved"]["energy_residual_rel"]
    worst = max(abs(v) for v in runs.values())
    chk["energy_account"] = {"acceptance": 1e-9, "residual_rel_by_run": runs, "max_abs": worst, "pass": worst < 1e-9}
    base = recs.get("two_E33223_tau30_G0.5")
    p = os.path.join(S2, "two_E33223_tau30_G0.5_no_source.json")
    if os.path.exists(p):
        ns = json.load(open(p))
        chk["no_source"] = {"case": "two_E33223_tau30_G0.5",
                            "resolved_vs_archived_max_abs_K": ns["resolved_passive_vs_archived_max_abs_K"],
                            "lumped_vs_archived_max_abs_K": ns["lumped_passive_vs_archived_T2_be_max_abs_K"],
                            "band_entry_s": ns["resolved"]["cross_s"]}
    p = os.path.join(S2, "two_E33223_tau30_G0.5_step_halved.json")
    if os.path.exists(p) and base:
        sh = json.load(open(p))
        b0, b1 = base["resolved"]["cross_s"], sh["resolved"]["cross_s"]
        moves = {k: abs(b1[k] - b0[k]) / b0[k] for k in b0 if b0[k] is not None and b1[k] is not None}
        missing = [k for k in b0 if (b0[k] is None) != (b1[k] is None)]
        chk["step_halved"] = {"case": "two_E33223_tau30_G0.5", "dt_target_K": sh["dt_target_K"], "dt_accept_K": sh["dt_accept_K"],
                              "acceptance": 0.01, "band_entry_s_base": b0, "band_entry_s_halved": b1, "relative_move": moves,
                              "max_relative_move": max(moves.values()), "pass": (max(moves.values()) < 0.01) and not missing,
                              "hottest_peak_C": [base["resolved"]["peak"]["Tmax_C"], sh["resolved"]["peak"]["Tmax_C"]],
                              "mean_peak_C": [base["resolved"]["peak"]["Tmean_C"], sh["resolved"]["peak"]["Tmean_C"]],
                              "t_cat1_consumed_at_a_node_s": [base["resolved"]["t_cat1_consumed_at_a_node_s"],
                                                              sh["resolved"]["t_cat1_consumed_at_a_node_s"]],
                              "resolved_reaction_heat_J": [base["resolved"]["energy_J"]["in_rxn"], sh["resolved"]["energy_J"]["in_rxn"]],
                              "lumped_peak_C": [base["lumped_reactive"]["peak"]["T_C"], sh["lumped_reactive"]["peak"]["T_C"]]}
    p = os.path.join(a.out, "v3_stage2.json")
    if os.path.exists(p):
        v3 = json.load(open(p))
        chk["V3_high_k"] = {c: v3[c] for c in ("two_E33223_tau30_G0.5", "two_E33223_tau30_G0.2") if c in v3}
    json.dump(chk, open(os.path.join(a.out, "stage2_checks.json"), "w"), indent=1, default=float)
    print(json.dumps({k: (v if k != "energy_account" else {kk: vv for kk, vv in v.items() if kk != "residual_rel_by_run"})
                      for k, v in chk.items()}, indent=1, default=float))
    for r in rows:
        print({k: r[k] for k in ("case", "hottest_enters_255.7C_s", "hottest_peak_reactive_C", "hottest_peak_passive_C",
                                 "mean_peak_reactive_C", "lumped_peak_reactive_C", "lumped_peak_passive_C",
                                 "resolved_reaction_heat_J", "lumped_reaction_heat_J", "lumped_layered_cathode_conversion_900s",
                                 "max_volume_fraction_above_255.7C_percent", "layered_cathode_consumed_at_a_node_s")})

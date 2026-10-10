#!/usr/bin/env python3
"""Score P1 to P4 of predictions.md against results/onset_results.json (Stage 1), and write the scorecard.

Usage: python3 score_stage1.py --out ../results
"""
import argparse, json, os

E_NAME = {8751: "8.75 kJ", 21495: "21.5 kJ", 33223: "33.2 kJ"}


def parse(case):
    arr, e, tau, g = case.split("_")
    return arr, int(e[1:]), float(tau[3:]), float(g[1:])


def label(case):
    arr, e, tau, g = parse(case)
    return f"{E_NAME[e]}, {tau:g} s, {g * 1000:g} mW/K"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="../results"); a = ap.parse_args()
    d = json.load(open(os.path.join(a.out, "onset_results.json")))
    rows = {r["case"]: r for r in d["cases"]}
    two = {k: v for k, v in rows.items() if k.startswith("two_")}
    assert len(two) == 42, len(two)
    card = {}

    # P1
    p1 = {}
    central = {10.0: (4.2, 29.0), 30.0: (11.5, 39.0)}
    ok = True
    for tau in (10.0, 30.0):
        r = two[f"two_E33223_tau{int(tau)}_G0.5"]
        th, tl = r["hottest_node_t_0.15Kpm_s"], r["lumped_t_0.15Kpm_s"]
        holds = th is not None and tl is not None and th < 0.5 * tl
        ok &= holds
        p1[f"tau{int(tau)}"] = {"hottest_s": th, "lumped_s": tl, "lead_s": None if None in (th, tl) else tl - th,
                                "earlier_percent": None if None in (th, tl) else 100 * (1 - th / tl),
                                "central_estimate_s": central[tau], "holds": holds}
    card["P1"] = {"result": "held" if ok else "failed", **p1}

    # P2
    predicted = {f"two_E{e}_tau{t}_G{g}" for e, gs in ((33223, ("0.1", "0.2", "0.5")), (21495, ("0.2", "0.5"))) for g in gs for t in (10, 30)}
    actual = {k for k, r in two.items() if r["resolved_mean_t_0.15Kpm_s"] is not None}
    card["P2"] = {"result": "held" if actual == predicted else "failed",
                  "cases_reached": sorted(label(k) for k in actual), "count": len(actual),
                  "predicted_but_not_reached": sorted(label(k) for k in predicted - actual),
                  "reached_but_not_predicted": sorted(label(k) for k in actual - predicted),
                  "mean_peak_C_at_33kJ_50mWK": [two[f"two_E33223_tau{t}_G0.05"]["resolved_mean_Tpeak_C"] for t in (10, 30)]}

    # P3
    only_local = sorted((parse(k)[3], k) for k, r in two.items()
                        if r["hottest_node_t_0.15Kpm_s"] is not None and r["lumped_t_0.15Kpm_s"] is None)
    g_min = only_local[0][0] if only_local else None
    card["P3"] = {"result": "held" if g_min == 0.1 else "failed", "smallest_G_mWK": None if g_min is None else g_min * 1000,
                  "central_estimate_mWK": 100, "only_hottest_cases": [label(k) for _, k in only_local]}

    # P4
    p4_cases = sorted(k for k, r in two.items() if r["hottest_node_t_10.0Kpm_s"] is not None and r["lumped_t_1.0Kpm_s"] is None)
    pred4 = {"two_E33223_tau10_G0.2", "two_E33223_tau30_G0.2", "two_E21495_tau10_G0.5", "two_E21495_tau30_G0.5"}
    card["P4"] = {"result": "held" if p4_cases else "failed", "cases": [label(k) for k in p4_cases],
                  "case_list_as_predicted": set(p4_cases) == pred4,
                  "predicted_cases": sorted(label(k) for k in pred4)}

    # descriptive, not scored
    card["summary"] = {
        "levels_reached_two_strip": {h: {str(lv): sum(r[f"{h}_t_{lv}Kpm_s"] is not None for r in two.values()) for lv in (0.15, 1.0, 10.0)}
                                     for h in ("hottest_node", "resolved_mean", "lumped")},
        "temperature_at_0.15Kpm_C_range": {h: [min(r[f"{h}_T_at_0.15Kpm_C"] for r in two.values() if r[f"{h}_T_at_0.15Kpm_C"] is not None),
                                               max(r[f"{h}_T_at_0.15Kpm_C"] for r in two.values() if r[f"{h}_T_at_0.15Kpm_C"] is not None)]
                                           for h in ("hottest_node", "resolved_mean", "lumped")},
        "reaction_at_0.15Kpm": sorted({r[f"{h}_rxn_at_0.15Kpm"] for r in two.values() for h in ("hottest_node", "resolved_mean", "lumped") if r[f"{h}_rxn_at_0.15Kpm"]}),
    }
    json.dump(card, open(os.path.join(a.out, "stage1_scorecard.json"), "w"), indent=1)
    print(json.dumps(card, indent=1))

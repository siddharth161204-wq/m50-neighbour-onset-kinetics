#!/usr/bin/env python3
"""Stage 4, exploratory and post hoc (DECISIONS.md D30 (4)): which submodel decides the draws whose mode changes.

Written after the Stage 4 results, after an independent check of the documents found that the draw-level
differences between the joint draws and the anode-electrolyte runs could not be read off the variance shares. At the
headline case (33.2 kJ, 30 s, 500 mW/K), take every draw whose lead mode (short or long, split at the largest gap of
the joint leads, as in D30 (1)) or hottest-node starting reaction differs between its joint draw (Stage 3a) and its
anode-electrolyte run (Stage 4). For each, integrate two more combinations along the headline's hottest-node and
lumped histories, with the Stage 1 driver and numerics unchanged:
  anode-electrolyte and separator particles from the draw, cathode at the posterior mean;
  anode-electrolyte and cathode particles from the draw, separator at the posterior mean.
Record whether each restores the joint draw's mode and starting reaction, and each draw's separator melting
self-heating in the fresh state at 108.4 C against the posterior mean's. Nothing is scored; no registered result
changes. Writes results/v11_explore.json.

Usage: python3 v11_explore.py --series <clone>/results/resolved_series --out ../results
"""
import argparse, csv, json, os
import numpy as np
import bcrnn
import onset_kinetics as OK
import stage3_draws as S
import stage3a as A
from v11_sensitivity import mean_rows, columns

HEAD = "two_E33223_tau30_G0.5"
HISTS = ("hottest_node", "lumped")
FILES = ("An_Ele.csv", "NCM811.csv", "Separator.csv")
LV = "0.15Kpm"


def num(v):
    return None if v in ("", "None", None) else float(v)


def rows_combo(P, M, varied, ae, sep, cat):
    col = columns(ae, sep, cat)
    return tuple(P[f][:, col[f] - 1] if f in varied else M[f] for f in FILES)


def onsets(kin, path):
    OK.KIN = kin
    out = OK.run_case(path, histories=HISTS)
    h, l = out[f"hottest_node_t_{LV}_s"], out[f"lumped_t_{LV}_s"]
    return {"hottest_onset_s": h, "lumped_onset_s": l, "lead_s": None if h is None or l is None else l - h,
            "hottest_onset_T_C": out[f"hottest_node_T_at_{LV}_C"], "hottest_onset_reaction": out[f"hottest_node_rxn_at_{LV}"]}


def sep_self_heating(kin, T_C=108.4):
    """The separator's melting term of the kinetic self-heating, K/min, in the fresh state at T_C (negative: absorbs)."""
    r = kin.rates(np.array([T_C + 273.15]), bcrnn.C0[:, None])[:, 0]
    j = bcrnn.REACTIONS.index("sep_melt")
    return float(kin.h_mass[j] * r[j] / OK.CP * 60.0)


def main(series, out):
    P, M = S.load_particles(), mean_rows()
    path = os.path.join(series, HEAD + ".npz")
    joint, grp = {}, {}
    for r in csv.DictReader(open(os.path.join(out, "stage3a_onsets.csv"))):
        if r["case"] == HEAD and r["history"] in HISTS:
            joint.setdefault(int(r["draw"]), {})[r["history"]] = r
    for r in csv.DictReader(open(os.path.join(out, "v11_onsets.csv"))):
        if r["group"] == "an_ele" and r["case"] == HEAD and r["history"] in HISTS:
            grp.setdefault(int(r["draw"]), {})[r["history"]] = r

    def summary(rec):
        h, l = num(rec["hottest_node"][f"t_{LV}_s"]), num(rec["lumped"][f"t_{LV}_s"])
        return {"lead_s": l - h, "reaction": rec["hottest_node"][f"rxn_at_{LV}"]}
    J = {d: summary(joint[d]) for d in joint}
    G = {d: summary(grp[d]) for d in grp}
    srt = np.sort([J[d]["lead_s"] for d in J]); k = int(np.argmax(np.diff(srt))); cut = 0.5 * (srt[k] + srt[k + 1])
    mode = lambda lead: "long" if lead > cut else "short"
    cols = {int(r["draw"]): (int(r["an_ele_column"]), int(r["separator_column"]), int(r["ncm811_column"]))
            for r in csv.DictReader(open(os.path.join(out, "stage3_draw_indices.csv")))}
    sep_mean = sep_self_heating(bcrnn.Kinetics(model=bcrnn.rows_to_model(*rows_combo(P, M, (), 0, 0, 0))))
    differ = [d for d in sorted(J) if mode(J[d]["lead_s"]) != mode(G[d]["lead_s"]) or J[d]["reaction"] != G[d]["reaction"]]
    recs = []
    for d in differ:
        ae, sep, cat = cols[d]
        res = {"draw": d, "joint": {"mode": mode(J[d]["lead_s"]), "reaction": J[d]["reaction"], "lead_s": J[d]["lead_s"]},
               "an_ele_run": {"mode": mode(G[d]["lead_s"]), "reaction": G[d]["reaction"], "lead_s": G[d]["lead_s"]}}
        for name, varied in (("an_ele_and_separator", ("An_Ele.csv", "Separator.csv")), ("an_ele_and_ncm811", ("An_Ele.csv", "NCM811.csv"))):
            kin = bcrnn.Kinetics(model=bcrnn.rows_to_model(*rows_combo(P, M, varied, ae, sep, cat)))
            o = onsets(kin, path)
            res[name] = {**o, "mode": mode(o["lead_s"]), "restores_joint_mode": mode(o["lead_s"]) == res["joint"]["mode"],
                         "restores_joint_reaction": o["hottest_onset_reaction"] == res["joint"]["reaction"]}
        res["separator_melting_K_per_min_at_108.4C_fresh"] = sep_self_heating(
            bcrnn.Kinetics(model=bcrnn.rows_to_model(*rows_combo(P, M, ("Separator.csv",), ae, sep, cat))))
        res["mode_changes"] = res["joint"]["mode"] != res["an_ele_run"]["mode"]
        recs.append(res)
    mc = [r for r in recs if r["mode_changes"]]
    rc = [r for r in recs if not r["mode_changes"]]
    summ = {
        "note": "exploratory and post hoc (DECISIONS.md D30 (4)); nothing here is scored",
        "case": HEAD, "mode_cut_s": cut, "posterior_mean_separator_melting_K_per_min_at_108.4C_fresh": sep_mean,
        "n_draws_differing": len(recs), "n_mode_changes": len(mc), "n_reaction_changes_only": len(rc),
        "mode_changes": {
            "n_short_to_long": sum(r["joint"]["mode"] == "short" for r in mc), "n_long_to_short": sum(r["joint"]["mode"] == "long" for r in mc),
            "restored_by_own_separator": sum(r["an_ele_and_separator"]["restores_joint_mode"] for r in mc),
            "restored_by_own_cathode": sum(r["an_ele_and_ncm811"]["restores_joint_mode"] for r in mc),
            "short_to_long_with_weaker_own_separator_melting": sum(
                r["joint"]["mode"] == "short" and abs(r["separator_melting_K_per_min_at_108.4C_fresh"]) < abs(sep_mean) for r in mc),
            "long_to_short_with_stronger_own_separator_melting": sum(
                r["joint"]["mode"] == "long" and abs(r["separator_melting_K_per_min_at_108.4C_fresh"]) > abs(sep_mean) for r in mc)},
        "reaction_changes_only": {
            "restored_by_own_separator": sum(r["an_ele_and_separator"]["restores_joint_reaction"] for r in rc),
            "restored_by_own_cathode": sum(r["an_ele_and_ncm811"]["restores_joint_reaction"] for r in rc)},
        "draws": recs}
    json.dump(summ, open(os.path.join(out, "v11_explore.json"), "w"), indent=1)
    return summ


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True)
    ap.add_argument("--out", default="../results")
    a = ap.parse_args()
    s = main(a.series, a.out)
    print(json.dumps({k: v for k, v in s.items() if k != "draws"}, indent=1))

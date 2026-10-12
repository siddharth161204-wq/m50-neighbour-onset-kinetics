#!/usr/bin/env python3
"""Stage 3b and 3c results, V6, the variance decomposition, and the scoring of P4 and P5 (DECISIONS.md D27).

Reads results/stage3bc_onsets.csv (stage3b.py kinetics), results/stage3b_solves.jsonl, results/stage3b_nominal_check.json,
results/stage3_thermal_draws.csv, results/stage3c_pairs.csv and, for the kinetic factor, results/stage3a_onsets.csv at
the headline case. Writes results/stage3bc_metrics.json and the P4 and P5 entries of results/stage3_scorecard.json.

Usage: python3 stage3bc_score.py --out ../results
"""
import argparse, csv, json, os
import numpy as np

HEADLINE = "two_E33223_tau30_G0.5"
LV = "0.15Kpm"


def num(v):
    return None if v in ("", "None", None) else float(v)


def stats(values):
    v = np.array([x for x in values if x is not None], float)
    return {"n": int(v.size), "n_without_onset": int(sum(x is None for x in values)),
            "mean": float(v.mean()) if v.size else None, "sd": float(v.std(ddof=1)) if v.size > 1 else None,
            "p2.5": float(np.percentile(v, 2.5)) if v.size else None, "p50": float(np.percentile(v, 50)) if v.size else None,
            "p97.5": float(np.percentile(v, 97.5)) if v.size else None}


def quantities(rows, hot_key, lump_key):
    hot = [num(r[hot_key]) for r in rows]
    lump = [num(r[lump_key]) for r in rows]
    lead = [None if (h is None or l is None) else l - h for h, l in zip(hot, lump)]
    return {"hottest_onset_s": stats(hot), "lumped_onset_s": stats(lump), "lead_s": stats(lead),
            "n_hottest_only": int(sum(h is not None and l is None for h, l in zip(hot, lump))),
            "n_lead_negative_or_zero": int(sum(x is not None and x <= 0 for x in lead))}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../results")
    a = ap.parse_args()
    o = a.out
    # V6
    solves = [json.loads(l) for l in open(os.path.join(o, "stage3b_solves.jsonl"))]
    th = [s for s in solves if s["tag"].startswith("thermal_")]
    hk = [s for s in solves if s["tag"].startswith("highk_")]
    nom = json.load(open(os.path.join(o, "stage3b_nominal_check.json")))
    v6 = {"nominal_reproduces_archive_K": nom["max_abs_difference_against_archive_K"],
          "nominal_pass": max(nom["max_abs_difference_against_archive_K"].values()) < 1e-6,
          "energy_residual_max_abs": max(abs(s["energy_residual_rel"]) for s in th),
          "energy_pass": all(abs(s["energy_residual_rel"]) < 1e-9 for s in th), "n_solves": len(th),
          "high_k": {s["tag"]: {"C_cell_J_per_K": s["C_cell_J_per_K"], "max_abs_Tmax_minus_lumped_K": s["max_abs_Tmax_minus_lumped_K"],
                                "max_abs_Tmean_minus_lumped_K": s["max_abs_Tmean_minus_lumped_K"],
                                "energy_residual_rel": s["energy_residual_rel"]} for s in hk},
          "high_k_pass": len(hk) == 3 and all(s["max_abs_Tmax_minus_lumped_K"] < 1.0 and s["max_abs_Tmean_minus_lumped_K"] < 1.0 for s in hk)}
    v6["pass"] = v6["nominal_pass"] and v6["energy_pass"] and v6["high_k_pass"]
    # factors
    rows = list(csv.DictReader(open(os.path.join(o, "stage3bc_onsets.csv"))))
    thermal = [r for r in rows if int(r["kinetic_draw"]) == 0]
    pairs = [r for r in rows if int(r["kinetic_draw"]) != 0]
    assert len(thermal) == 30 and len(pairs) == 210, (len(thermal), len(pairs))
    kin = [r for r in csv.DictReader(open(os.path.join(o, "stage3a_onsets.csv"))) if r["case"] == HEADLINE]
    kin_by = {}
    for r in kin:
        kin_by.setdefault(int(r["draw"]), {})[r["history"]] = r
    kin_rows = [{"h": kin_by[d]["hottest_node"][f"t_{LV}_s"], "l": kin_by[d]["lumped"][f"t_{LV}_s"]} for d in sorted(kin_by)]
    assert len(kin_rows) == 200
    K = quantities(kin_rows, "h", "l")
    T = quantities(thermal, f"hottest_node_t_{LV}_s", f"lumped_t_{LV}_s")
    C = quantities(pairs, f"hottest_node_t_{LV}_s", f"lumped_t_{LV}_s")
    dec = {}
    for q in ("hottest_onset_s", "lumped_onset_s", "lead_s"):
        sk, st, sc = K[q]["sd"], T[q]["sd"], C[q]["sd"]
        excess = (sc ** 2 - (sk ** 2 + st ** 2)) / (sk ** 2 + st ** 2) if None not in (sk, st, sc) else None
        dec[q] = {"sd_kinetic": sk, "sd_thermal": st, "sd_combined": sc,
                  "ratio_thermal_to_kinetic": st / sk if sk else None,
                  "combined_variance_over_sum_minus_1": excess,
                  "interaction_flag": excess is not None and excess > 0.20}
    p4r = dec["hottest_onset_s"]["ratio_thermal_to_kinetic"]
    p5r = 1.0 / dec["lumped_onset_s"]["ratio_thermal_to_kinetic"] if dec["lumped_onset_s"]["ratio_thermal_to_kinetic"] else None
    score = {"P4": {"ratio_thermal_to_kinetic_sd_hottest_onset": p4r, "threshold": "> 1.5", "held": p4r is not None and p4r > 1.5,
                    "brief_central": 3},
             "P5": {"ratio_kinetic_to_thermal_sd_lumped_onset": p5r, "threshold": "> 1.5", "held": p5r is not None and p5r > 1.5,
                    "brief_central": 2}}
    draws = list(csv.DictReader(open(os.path.join(o, "stage3_thermal_draws.csv"))))
    by_draw = []
    for d in draws:
        r = next(x for x in thermal if x["tag"] == f"thermal_{int(d['thermal_draw']):02d}")
        s = next(x for x in th if x["tag"] == f"thermal_{int(d['thermal_draw']):02d}")
        h, l = num(r[f"hottest_node_t_{LV}_s"]), num(r[f"lumped_t_{LV}_s"])
        by_draw.append({**{k: float(v) for k, v in d.items() if k != "thermal_draw"}, "thermal_draw": int(d["thermal_draw"]),
                        "hottest_onset_s": h, "lumped_onset_s": l, "lead_s": None if (h is None or l is None) else l - h,
                        "Tmax_peak_C": s["Tmax_peak_C"], "lumped_peak_C": s["lumped_peak_C"]})
    out = {"case": HEADLINE, "V6": v6, "kinetic_200_at_nominal_inputs": K, "thermal_30_at_mean_kinetics": T,
           "combined_210_pairs": C, "decomposition": dec, "thermal_draws": by_draw}
    json.dump(out, open(os.path.join(o, "stage3bc_metrics.json"), "w"), indent=1)
    sc_path = os.path.join(o, "stage3_scorecard.json")
    sc = json.load(open(sc_path))
    sc.update(score)
    sc["V6"] = {"pass": v6["pass"]}
    json.dump(sc, open(sc_path, "w"), indent=1)
    print(json.dumps({"V6": {k: v6[k] for k in ("nominal_pass", "energy_residual_max_abs", "high_k_pass", "pass")},
                      "decomposition": dec, "P4": score["P4"], "P5": score["P5"]}, indent=1))

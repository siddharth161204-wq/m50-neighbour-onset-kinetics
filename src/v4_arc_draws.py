#!/usr/bin/env python3
"""V4 (brief, Stage 3a, before any case): every kinetic draw through V1's ARC emulation of the paper's own test.

The emulation is V1's (`v1_arc_check.arc_test`): the paper's Table 1 cell (720 g, 1100 J/(kg K), 0.04 m2,
25 W/(m2 K)), heat-wait-seek from 25 C in 5 C steps with D6's settings, exotherm trigger 0.15 C/min, and from the
trigger on adiabatic tracking until the self-heating rate reaches the paper's ISC trigger of 1 C/min (T_on) and then
1 C/s. The ISC energy release and the chamber's cooling above 400 C are not modelled, so T_max is not reported.

Classes (DECISIONS.md D23), from the times the paper's Appendix A gives (p. 15): a draw whose self-heating reaches
1 C/min no later than 4000 min after the test starts is in the main cluster; between 4000 and 8500 min, a delayed
short; not by 8500 min, no short; a draw whose seek never triggers below 400 C, no exotherm.

Acceptance (brief): over the main-cluster draws, the 2.5 and 97.5 percentiles of T_in lie within 5 C of the paper's
two-sigma band edges, 169.0 and 198.0 C, and their mean within 5 C of 183.5 C. If V4 fails, the study stops.

Usage: python3 v4_arc_draws.py --out ../results [--jobs 2]
"""
import argparse, csv, json, os
from multiprocessing import Pool
import numpy as np
import bcrnn
import stage3_draws as S
import v1_arc_check as V1

MAIN_MIN, HORIZON_MIN = 4000.0, 8500.0
BAND, MEAN_REF, TOL = (169.0, 198.0), 183.5, 5.0
PAPER_FRACTIONS = {"main_cluster": 0.76, "delayed_short": 0.07, "no_short": 0.17}   # Fig. 6 caption, p. 12

_P = None


def _init():
    global _P
    _P = S.load_particles()


def one(draw):
    d, ae, sep, cat = draw
    kin = S.draw_kinetics(_P, ae, sep, cat)
    r = V1.arc_test(kin)
    rec = {"draw": d, "an_ele_column": ae, "separator_column": sep, "ncm811_column": cat,
           "T_in_C": r.get("T_in_C"), "t_in_min": None if r.get("T_in_C") is None else 60.0 * r["t_in_h"],
           "T_on_C": r.get("T_on_C"), "t_on_min": None, "T_at_1_C_per_s_C": r.get("T_at_1_C_per_s_C"),
           "sei_converted_at_T_in": None, "class": None}
    if r.get("T_in_C") is None:
        rec["class"] = "no_exotherm"
        return rec
    rec["sei_converted_at_T_in"] = r["conversion_at_T_in"].get("sei")
    if r.get("T_on_C") is not None:
        rec["t_on_min"] = 60.0 * r["t_on_h"]
    t_on = rec["t_on_min"]
    if t_on is None or t_on > HORIZON_MIN:
        rec["class"] = "no_short"
    elif t_on > MAIN_MIN:
        rec["class"] = "delayed_short"
    else:
        rec["class"] = "main_cluster"
    return rec


def summarise(rows):
    n = len(rows)
    frac = {c: sum(r["class"] == c for r in rows) / n for c in ("main_cluster", "delayed_short", "no_short", "no_exotherm")}
    main = np.array([r["T_in_C"] for r in rows if r["class"] == "main_cluster"], dtype=float)
    out = {"n_draws": n, "fractions": frac, "paper_fractions": PAPER_FRACTIONS}
    if main.size:
        p025, p975 = np.percentile(main, [2.5, 97.5])
        mean = float(main.mean())
        out["main_cluster_T_in_C"] = {"n": int(main.size), "p2.5": float(p025), "p97.5": float(p975), "mean": mean,
                                      "median": float(np.median(main)), "min": float(main.min()), "max": float(main.max()),
                                      "std": float(main.std(ddof=1)) if main.size > 1 else None}
        ok = abs(p025 - BAND[0]) <= TOL and abs(p975 - BAND[1]) <= TOL and abs(mean - MEAN_REF) <= TOL
        out["acceptance"] = {"band_C": list(BAND), "mean_ref_C": MEAN_REF, "tolerance_C": TOL,
                             "lower_edge_offset_C": float(p025 - BAND[0]), "upper_edge_offset_C": float(p975 - BAND[1]),
                             "mean_offset_C": float(mean - MEAN_REF), "pass": bool(ok)}
    for c in ("delayed_short", "no_short"):
        v = np.array([r["T_in_C"] for r in rows if r["class"] == c], dtype=float)
        out[f"{c}_T_in_C_mean"] = float(v.mean()) if v.size else None
    on = np.array([r["T_on_C"] for r in rows if r["class"] == "main_cluster" and r["T_on_C"] is not None], dtype=float)
    if on.size:
        out["main_cluster_T_on_C"] = {"p2.5": float(np.percentile(on, 2.5)), "p97.5": float(np.percentile(on, 97.5)),
                                      "mean": float(on.mean()), "paper_mean": 278.9, "paper_band": [255.7, 302.1]}
    s1 = np.array([r["T_at_1_C_per_s_C"] for r in rows if r["class"] == "main_cluster" and r["T_at_1_C_per_s_C"] is not None], dtype=float)
    if s1.size:
        out["main_cluster_T_at_1_C_per_s_C"] = {"p2.5": float(np.percentile(s1, 2.5)), "p97.5": float(np.percentile(s1, 97.5)),
                                                "mean": float(s1.mean())}
    out["T_max"] = "not reported: the emulation does not model the ISC energy release or the chamber's cooling"
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../results")
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    draws, _ = S.all_draws()
    with Pool(a.jobs, initializer=_init) as pool:
        rows = []
        for i, r in enumerate(pool.imap(one, draws, chunksize=4)):
            rows.append(r)
            if (i + 1) % 20 == 0:
                print(f"{i + 1} draws done", flush=True)
    rows.sort(key=lambda r: r["draw"])
    with open(os.path.join(a.out, "stage3_v4_arc_draws.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    summ = summarise(rows)
    summ["mean_model"] = {k: v for k, v in V1.arc_test(bcrnn.Kinetics()).items() if k in ("T_in_C", "T_on_C", "T_at_1_C_per_s_C", "t_in_h", "t_on_h")}
    json.dump(summ, open(os.path.join(a.out, "stage3_v4.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))
